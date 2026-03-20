"""
Questionnaire Interview Orchestrator — runs a single interview session
using the adapted questionnaire, interviewer agent, and persona agent.
"""
import json, os, logging, time, copy
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from src.orchestration.interviewer_agent import QuestionnaireInterviewer
from src.orchestration.persona_agent import PersonaAgent
from src.orchestration.transcript_builder import TranscriptBuilder
from src.questionnaire.ehr_adapter import adapt_questionnaire, adapt_with_universal_probes

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

MAX_RETRIES = 3


def _load_persona(persona_id: str, personas_path: str = "data/composite_personas/composites.jsonl") -> dict:
    """Load a specific persona from the composites JSONL."""
    with open(personas_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            p = json.loads(line)
            if p.get("composite_id") == persona_id:
                return p
    raise ValueError(f"Persona {persona_id} not found in {personas_path}")


def _load_or_generate_adapted_questionnaire(session_config: dict, persona: dict) -> dict:
    """Load adapted questionnaire, generating on-the-fly if needed."""
    adapted_path = session_config.get("adapted_questionnaire_file", "")

    if adapted_path and Path(adapted_path).exists():
        with open(adapted_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Generate on the fly
    version = session_config.get("questionnaire_version", 1)
    q_file = session_config.get("questionnaire_file", f"data/questionnaires/Q_V{version}.json")
    with open(q_file, "r", encoding="utf-8") as f:
        base_q = json.load(f)

    adapted = adapt_questionnaire(base_q.get("questions", []), persona)
    adapted = adapt_with_universal_probes(adapted)

    # Save for reuse
    if adapted_path:
        Path(adapted_path).parent.mkdir(parents=True, exist_ok=True)
        with open(adapted_path, "w", encoding="utf-8") as f:
            json.dump(adapted, f, indent=2, ensure_ascii=False)
        log.info(f"  Generated adapted questionnaire → {adapted_path}")

    return adapted


def _parse_model_string(model_str: str) -> tuple:
    """Parse 'provider/model' string into (provider, model)."""
    if "/" in model_str:
        parts = model_str.split("/", 1)
        return parts[0], parts[1]
    return "google", model_str


def run_questionnaire_interview(session_config: dict, output_dir: str = "data/transcripts/") -> dict:
    """Run a single questionnaire-driven interview session.

    Args:
        session_config: Session definition from administration plan
        output_dir: Directory for transcript output

    Returns:
        Structured transcript dict
    """
    session_id = session_config.get("session_id", "S_000")
    persona_id = session_config.get("persona_id", "unknown")
    version = session_config.get("questionnaire_version", 1)

    log.info(f"  Starting {session_id}: {persona_id} × V{version}")

    errors = []

    # 1. Load persona
    try:
        persona = _load_persona(persona_id)
    except Exception as e:
        log.error(f"  Failed to load persona {persona_id}: {e}")
        return {"session_id": session_id, "status": "failed", "error": str(e)}

    # 2. Load adapted questionnaire
    try:
        adapted_q = _load_or_generate_adapted_questionnaire(session_config, persona)
    except Exception as e:
        log.error(f"  Failed to load questionnaire: {e}")
        return {"session_id": session_id, "status": "failed", "error": str(e)}

    # 3. Create agents
    persona_name = persona.get("name", "Unknown")
    journey_stage = persona.get("journey_stage", "pregnancy")
    persona_summary = persona.get("attributes", "")[:300]

    interviewer = QuestionnaireInterviewer(
        questionnaire=adapted_q,
        persona_summary=persona_summary,
        journey_stage=journey_stage,
    )

    persona_model_str = session_config.get("persona_model", "google/gemini-3.1-flash-lite-preview")
    p_provider, p_model = _parse_model_string(persona_model_str)

    persona_agent = PersonaAgent(persona, p_provider, p_model)

    # 4. Create transcript builder
    tb = TranscriptBuilder(session_config, persona)

    # 5. Run interview loop
    try:
        # Opening
        opening = interviewer.generate_opening(persona_name, journey_stage)
        tb.add_interviewer_turn(opening, turn_type="opening")

        # Persona responds to opening
        resp, in_tok, out_tok = _call_with_retry(persona_agent, opening)
        tb.add_persona_turn(resp, in_tok=in_tok, out_tok=out_tok)

        # Main question loop
        last_response = resp
        while True:
            action = interviewer.get_next_action(last_response)

            if action["action"] == "done":
                break

            if action["action"] == "close_interview":
                # Closing
                tb.add_interviewer_turn(action["text"], turn_type="closing")
                resp, in_tok, out_tok = _call_with_retry(persona_agent, action["text"])
                tb.add_persona_turn(resp, in_tok=in_tok, out_tok=out_tok, is_catch_all=True)
                break

            if action["action"] == "ask_question":
                tb.add_interviewer_turn(
                    action["text"],
                    turn_type="question",
                    question_id=action.get("question_id"),
                    target_dimensions=action.get("target_kbv", []),
                    target_latent=action.get("target_latent", []),
                )
                resp, in_tok, out_tok = _call_with_retry(persona_agent, action["text"])
                tb.add_persona_turn(
                    resp,
                    responding_to=action.get("question_id"),
                    in_tok=in_tok, out_tok=out_tok,
                )
                last_response = resp

            elif action["action"] == "deploy_probe":
                tb.add_interviewer_turn(
                    action["text"],
                    turn_type="probe",
                    probe_id=action.get("probe_id"),
                    target_latent=action.get("target_latent", []),
                )
                resp, in_tok, out_tok = _call_with_retry(persona_agent, action["text"])
                tb.add_persona_turn(
                    resp,
                    responding_to=action.get("probe_id"),
                    in_tok=in_tok, out_tok=out_tok,
                )
                last_response = resp

            # Brief delay between turns to avoid rate limiting
            time.sleep(0.3)

    except Exception as e:
        log.error(f"  Interview error in {session_id}: {e}")
        errors.append(str(e))

    # 6. Build and save transcript
    status = "completed" if not errors else "partial"
    transcript = tb.build(status=status, errors=errors)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    t_path = out_path / f"T_{session_id}.json"
    with open(t_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)

    meta = transcript["metadata"]
    log.info(f"  {session_id} [{persona_id} × V{version}] — "
             f"{meta['total_turns']} turns, {meta['questions_asked']}Q + "
             f"{meta['probes_deployed']}P, "
             f"{meta['total_input_tokens']+meta['total_output_tokens']} tok, "
             f"{meta['duration_seconds']:.0f}s")

    return transcript


def _call_with_retry(agent: PersonaAgent, message: str, max_retries: int = MAX_RETRIES) -> tuple:
    """Call persona agent with retry logic."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return agent.respond(message)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                log.warning(f"  Retry {attempt+1}/{max_retries} after {wait}s: {e}")
                time.sleep(wait)
    raise last_error

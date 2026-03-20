"""
Robustness Tester — tests refined questionnaire against adversarial personas.

Usage:
    PIPELINE_ENV=dev python -m src.refinement.robustness_tester \
        --plan data/refinement/refinement_plan.json \
        --questionnaire data/questionnaires/refined/Q_V4_R1.json \
        --personas data/composite_personas/composites.jsonl \
        --output data/refinement/ \
        --transcript-output data/transcripts/adversarial/
"""
import json, argparse, logging, os, re, time, random
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from src.config.models import get_model, get_provider, get_token_policy, tracker, ENV, MODELS, Tier, get_persona_rotation_models
from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return {}


def _call_llm(prompt: str, system_prompt: str, task_name: str) -> tuple:
    provider = get_provider(task_name)
    model = get_model(task_name)
    policy = get_token_policy()
    max_tokens = max(policy.max_output_tokens, 2048)

    if provider == "google":
        max_tokens = max(max_tokens * 10, 8000)
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        gm = genai.GenerativeModel(model_name=model)
        r = gm.generate_content(full_prompt, generation_config={"max_output_tokens": max_tokens}, request_options={"timeout": 120})
        text = r.text.strip()
        try:
            in_tok = r.usage_metadata.prompt_token_count
            out_tok = r.usage_metadata.candidates_token_count
        except AttributeError:
            in_tok, out_tok = 0, 0
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        r = client.messages.create(model=model, max_tokens=max_tokens, system=system_prompt, messages=[{"role": "user", "content": prompt}])
        text = r.content[0].text.strip()
        in_tok, out_tok = r.usage.input_tokens, r.usage.output_tokens
    elif provider in ("openai", "xai"):
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = None
        if provider == "xai":
            api_key = os.environ.get("XAI_API_KEY")
            base_url = "https://api.x.ai/v1"
        client = OpenAI(api_key=api_key, base_url=base_url)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        token_param = "max_completion_tokens" if "gpt-5" in model or "o3" in model or "o4" in model else "max_tokens"
        r = client.chat.completions.create(model=model, messages=messages, **{token_param: max_tokens})
        text = r.choices[0].message.content.strip()
        in_tok, out_tok = r.usage.prompt_tokens, r.usage.completion_tokens
    else:
        raise ValueError(f"Unknown provider: {provider}")

    tracker.record(task_name, provider, model, in_tok, out_tok)
    return text, in_tok, out_tok


def _call_persona_llm(prompt: str, system_prompt: str, model_str: str) -> tuple:
    """Call LLM for persona role-play with specific model."""
    parts = model_str.split("/")
    provider = parts[0]
    model = parts[1]
    max_tokens = 1500

    if provider == "google":
        max_tokens = 8000
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        gm = genai.GenerativeModel(model_name=model)
        r = gm.generate_content(full_prompt, generation_config={"max_output_tokens": max_tokens}, request_options={"timeout": 120})
        text = r.text.strip()
        try:
            in_tok = r.usage_metadata.prompt_token_count
            out_tok = r.usage_metadata.candidates_token_count
        except AttributeError:
            in_tok, out_tok = 0, 0
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        r = client.messages.create(model=model, max_tokens=max_tokens, system=system_prompt, messages=[{"role": "user", "content": prompt}])
        text = r.content[0].text.strip()
        in_tok, out_tok = r.usage.input_tokens, r.usage.output_tokens
    elif provider in ("openai", "xai"):
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = None
        if provider == "xai":
            api_key = os.environ.get("XAI_API_KEY")
            base_url = "https://api.x.ai/v1"
        client = OpenAI(api_key=api_key, base_url=base_url)
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        token_param = "max_completion_tokens" if "gpt-5" in model or "o3" in model or "o4" in model else "max_tokens"
        r = client.chat.completions.create(model=model, messages=messages, **{token_param: max_tokens})
        text = r.choices[0].message.content.strip()
        in_tok, out_tok = r.usage.prompt_tokens, r.usage.completion_tokens
    else:
        raise ValueError(f"Unknown provider: {provider}")

    tracker.record("persona_roleplay", provider, model, in_tok, out_tok)
    return text, in_tok, out_tok


def generate_adversarial_persona(profile: dict, base_personas: list) -> dict:
    """Generate an adversarial persona based on profile type."""
    profile_type = profile["profile_type"]

    # Pick a base persona to modify
    base = random.choice(base_personas) if base_personas else {}

    system = "You are creating a detailed adversarial test persona for a maternity-care interview study."
    prompt = f"""Create an adversarial persona for testing questionnaire robustness.

Profile type: {profile_type}
Test objective: {profile["test_objective"]}

Base persona context (modify heavily):
  Journey stage: {base.get("journey_stage", "third_trimester")}
  Risk level: {base.get("risk_level", "high")}

Create a persona JSON with these fields:
- composite_id: "ADV_{profile_type[:8].upper()}"
- name: a realistic name
- age: appropriate age
- journey_stage: appropriate stage
- risk_level: appropriate level
- adversarial_profile: true
- profile_type: "{profile_type}"
- test_objective: "{profile["test_objective"]}"
- enriched_narrative: 200-word backstory emphasizing the adversarial characteristics
- latent_dimensions: dict of relevant latent dimensions
- communication_style: how this persona communicates (e.g., "short defensive answers", "simple vocabulary")
- vulnerability_flags: list of relevant flags

Return ONLY the JSON object."""

    text, _, _ = _call_llm(prompt, system, "questionnaire_generation")
    persona = _extract_json(text)
    if not persona.get("composite_id"):
        persona["composite_id"] = f"ADV_{profile_type[:8].upper()}"
    persona["adversarial_profile"] = True
    persona["profile_type"] = profile_type
    persona["test_objective"] = profile["test_objective"]
    return persona


def run_adversarial_interview(persona: dict, questionnaire: dict, session_id: str, timestamp: str) -> dict:
    """Run a single adversarial interview session."""
    questions = questionnaire.get("questions", [])
    persona_models = get_persona_rotation_models()
    model_str = random.choice(persona_models)

    narrative = persona.get("enriched_narrative", "")
    comm_style = persona.get("communication_style", "responds naturally")

    persona_system = f"""You are role-playing as {persona.get('name', 'a participant')} in a maternity-care interview.

BACKSTORY: {narrative[:500]}

COMMUNICATION STYLE: {comm_style}
You must stay in character. Your responses should reflect your background and communication limitations.
If you are distrustful, be guarded. If you have low literacy, use simple words.
If you have a language barrier, use broken/simple English."""

    interviewer_system = """You are a skilled maternity-care interviewer. Ask questions naturally,
adapting your language to the participant's communication level. Use probes when responses are thin."""

    turns = []
    conversation_history = []

    for q in questions[:8]:  # Limit to 8 questions for adversarial
        q_text = q.get("question_text", q.get("text", ""))
        q_id = q.get("question_id", "")

        # Interviewer asks
        if conversation_history:
            context = "\n".join([f"{t['role']}: {t['text'][:200]}" for t in conversation_history[-4:]])
            ask_prompt = f"Previous conversation:\n{context}\n\nNow ask the next question naturally: {q_text}"
        else:
            ask_prompt = f"Start the interview with this question: {q_text}"

        i_text, _, _ = _call_llm(ask_prompt, interviewer_system, "interviewer")
        turns.append({"role": "interviewer", "text": i_text, "question_id": q_id, "type": "question"})
        conversation_history.append({"role": "interviewer", "text": i_text})

        # Persona responds
        resp_prompt = f"The interviewer says: {i_text}\n\nRespond in character."
        p_text, _, _ = _call_persona_llm(resp_prompt, persona_system, model_str)
        turns.append({"role": "persona", "text": p_text, "responding_to_question_id": q_id, "type": "response"})
        conversation_history.append({"role": "persona", "text": p_text})

        # One probe
        probes = q.get("probes", q.get("follow_ups", []))
        if probes:
            probe = probes[0]
            probe_text = probe.get("text", probe) if isinstance(probe, dict) else str(probe)
            probe_prompt = f"Previous response: {p_text[:300]}\n\nProbe gently: {probe_text}"
            pi_text, _, _ = _call_llm(probe_prompt, interviewer_system, "interviewer")
            turns.append({"role": "interviewer", "text": pi_text, "question_id": q_id, "type": "probe"})

            pp_text, _, _ = _call_persona_llm(f"The interviewer probes: {pi_text}\n\nRespond in character.", persona_system, model_str)
            turns.append({"role": "persona", "text": pp_text, "responding_to_question_id": q_id, "type": "response"})

        time.sleep(0.3)

    transcript = {
        "session_id": session_id,
        "persona_id": persona.get("composite_id", ""),
        "questionnaire_version": questionnaire.get("version", 0),
        "persona_journey_stage": persona.get("journey_stage", ""),
        "persona_risk_level": persona.get("risk_level", ""),
        "persona_model": model_str,
        "adversarial_profile": True,
        "profile_type": persona.get("profile_type", ""),
        "test_objective": persona.get("test_objective", ""),
        "turns": turns,
        "metadata": {
            "total_turns": len(turns),
            "questions_asked": sum(1 for t in turns if t.get("type") == "question"),
            "probes_deployed": sum(1 for t in turns if t.get("type") == "probe"),
            "timestamp": timestamp,
        },
    }

    return transcript


def main():
    parser = argparse.ArgumentParser(description="Robustness Tester")
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--questionnaire", type=str, required=True)
    parser.add_argument("--personas", type=str, default="data/composite_personas/composites.jsonl")
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--transcript-output", type=str, required=True)
    args = parser.parse_args()

    run = TimestampedRun(args.output)
    run.record_read(args.plan)
    run.record_read(args.questionnaire)

    log.info(f"Environment: {ENV.value}")

    with open(args.plan) as f:
        plan = json.load(f)
    with open(args.questionnaire) as f:
        questionnaire = json.load(f)

    base_personas = []
    if Path(args.personas).exists():
        with open(args.personas) as f:
            for line in f:
                if line.strip():
                    base_personas.append(json.loads(line))

    profiles = plan.get("adversarial_test_config", {}).get("profiles", [])
    log.info(f"Generating {len(profiles)} adversarial personas")

    # Step A: Generate adversarial personas
    adversarial_personas = []
    for profile in profiles:
        log.info(f"  Creating persona: {profile['profile_type']}")
        persona = generate_adversarial_persona(profile, base_personas)
        adversarial_personas.append(persona)
        time.sleep(0.5)

    # Write personas
    personas_path = run.output_path("adversarial_personas.jsonl")
    with open(personas_path, "w") as f:
        for p in adversarial_personas:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    run.stable_pointer("adversarial_personas.jsonl", personas_path)

    # Step B: Run adversarial interviews
    t_dir = Path(args.transcript_output)
    t_dir.mkdir(parents=True, exist_ok=True)

    transcripts = []
    for i, persona in enumerate(adversarial_personas):
        sid = f"S_ADV_{i+1:03d}"
        log.info(f"  Interview {sid}: {persona.get('profile_type', 'unknown')}")
        transcript = run_adversarial_interview(persona, questionnaire, sid, run.timestamp)
        transcripts.append(transcript)

        t_path = t_dir / f"T_ADV_{i+1:03d}_{run.timestamp}.json"
        with open(t_path, "w") as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        run.files_written.append(str(t_path))

    cost = tracker.summary()
    run.write_manifest("robustness_tester", config={
        "n_profiles": len(profiles),
        "profiles": [p["profile_type"] for p in profiles],
    }, cost=cost["total_cost_usd"])

    log.info(f"Adversarial personas → {personas_path}")
    log.info(f"Transcripts → {t_dir}")
    log.info(f"Cost: ${cost['total_cost_usd']:.4f}")


if __name__ == "__main__":
    main()

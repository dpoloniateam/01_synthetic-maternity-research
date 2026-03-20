"""
Blind Spot Fixer — generates targeted probes for each blind spot.

Usage:
    PIPELINE_ENV=dev python -m src.refinement.blind_spot_fixer \
        --plan data/refinement/refinement_plan.json \
        --questionnaires data/questionnaires/ \
        --output data/refinement/
"""
import json, argparse, logging, os, re, time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from src.config.models import get_model, get_provider, get_token_policy, tracker, ENV
from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

TASK_NAME = "questionnaire_generation"


def _extract_json(text: str):
    text = text.strip()
    # Try direct parse as array
    if text.startswith("["):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m = re.search(r"(\[.*\])", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return []


def _call_llm(prompt: str, system_prompt: str = "") -> tuple:
    provider = get_provider(TASK_NAME)
    model = get_model(TASK_NAME)
    policy = get_token_policy()
    max_tokens = max(policy.max_output_tokens, 4096)

    if provider == "google":
        max_tokens = max(max_tokens * 15, 16000)
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

    tracker.record(TASK_NAME, provider, model, in_tok, out_tok)
    return text, in_tok, out_tok


def generate_probes(blind_spot: dict, strategy: str, top_questions: list, questionnaire: dict) -> list:
    """Generate probes for a single blind spot."""
    dimension = blind_spot["dimension"]
    rate = blind_spot["surfacing_rate"]
    diagnosis = blind_spot["diagnosis"]
    targeting_ids = blind_spot.get("questions_targeting", [])

    # Build context from top questions
    top_examples = []
    for tq in top_questions[:3]:
        qid = tq["question_id"]
        for q in questionnaire.get("questions", []):
            if q.get("question_id") == qid:
                probes = q.get("probes", q.get("follow_ups", []))
                top_examples.append(f"Q: {q.get('question_text', q.get('text', ''))}\nProbes: {json.dumps(probes[:3])}")
                break

    # Build failing probes context
    failing = []
    for qid in targeting_ids[:3]:
        for q in questionnaire.get("questions", []):
            if q.get("question_id") == qid:
                probes = q.get("probes", q.get("follow_ups", []))
                failing.append(f"Q ({qid}): {q.get('question_text', q.get('text', ''))}\nProbes: {json.dumps(probes[:3])}")
                break

    if diagnosis == "no_questions_target":
        n_probes = 4
        task = f"Generate {n_probes} NEW questions with probes targeting '{dimension}'. Place each in the most relevant journey phase."
    elif diagnosis == "probes_ineffective":
        n_probes = 6
        task = f"Redesign probes for existing questions targeting '{dimension}'. Generate {n_probes} alternative probes using patterns from top-performing questions."
    else:
        n_probes = 4
        task = f"Generate {n_probes} scenario-based probes for '{dimension}' that create situations where this dimension MUST surface through lived experience."

    system = """You are designing probes for a maternity-care interview guide.
Your probes must be empathetic, never clinical or interrogative, and use indirect elicitation."""

    prompt = f"""CONTEXT: The questionnaire uses a "{strategy}" approach.
The latent dimension "{dimension}" was surfaced in only {rate*100:.1f}% of interviews.
Diagnosis: {diagnosis}

WHAT WORKS (from highest-performing questions):
{chr(10).join(top_examples) if top_examples else "No examples available"}

WHAT DOESN'T WORK (current probes targeting this dimension):
{chr(10).join(failing) if failing else "No current probes targeting this dimension"}

TASK: {task}

Principles:
1. Use indirect elicitation — do NOT name the dimension explicitly
2. Use the style/register of "{strategy}"
3. Each probe should create a conversational opening where the dimension naturally surfaces
4. Reference concrete maternity-care situations
5. Be empathetic, never clinical or interrogative

Respond as JSON array: [{{"probe_text": "...", "target_journey_phase": "...",
"attach_to_question": "existing_question_id or NEW", "probe_type": "{diagnosis}",
"rationale": "why this should surface the dimension"}}]"""

    text, in_tok, out_tok = _call_llm(prompt, system)
    probes = _extract_json(text)
    if isinstance(probes, dict):
        probes = probes.get("probes", [probes])
    for p in probes:
        p["target_dimension"] = dimension
        p["severity"] = blind_spot["severity"]
    return probes


def main():
    parser = argparse.ArgumentParser(description="Blind Spot Fixer")
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--questionnaires", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    run = TimestampedRun(args.output)
    run.record_read(args.plan)

    log.info(f"Environment: {ENV.value}")
    log.info(f"Model: {get_provider(TASK_NAME)}/{get_model(TASK_NAME)}")

    with open(args.plan) as f:
        plan = json.load(f)

    winner_v = plan["winner"]["version"]
    strategy = plan["winner"]["strategy"]

    q_file = Path(args.questionnaires) / f"Q_V{winner_v}.json"
    run.record_read(str(q_file))
    with open(q_file) as f:
        questionnaire = json.load(f)

    all_probes = []

    # Fix blind spots
    for spot in plan["blind_spots"]:
        log.info(f"  Fixing blind spot: {spot['dimension']} ({spot['severity']}, {spot['surfacing_rate']*100:.1f}%)")
        probes = generate_probes(spot, strategy, plan.get("top_questions", []), questionnaire)
        all_probes.extend(probes)
        log.info(f"    Generated {len(probes)} probes")
        time.sleep(0.5)

    # Supplementary probes for at-risk dimensions
    for ar in plan.get("at_risk_dimensions", []):
        log.info(f"  Supplementary probes for at-risk: {ar['dimension']} ({ar['surfacing_rate']*100:.1f}%)")
        fake_spot = {
            "dimension": ar["dimension"],
            "surfacing_rate": ar["surfacing_rate"],
            "severity": "at_risk",
            "questions_targeting": [],
            "diagnosis": "dimension_too_latent",
        }
        probes = generate_probes(fake_spot, strategy, plan.get("top_questions", []), questionnaire)
        all_probes.extend(probes[:2])
        log.info(f"    Generated {min(len(probes), 2)} supplementary probes")
        time.sleep(0.5)

    # Write output
    fixes = {
        "version": winner_v,
        "strategy": strategy,
        "total_probes": len(all_probes),
        "probes": all_probes,
    }

    fixes_path = run.output_path("probe_fixes.json")
    with open(fixes_path, "w") as f:
        json.dump(fixes, f, indent=2, ensure_ascii=False)
    run.stable_pointer("probe_fixes.json", fixes_path)

    cost = tracker.summary()
    run.write_manifest("blind_spot_fixer", config={"version": winner_v, "n_blind_spots": len(plan["blind_spots"])}, cost=cost["total_cost_usd"])

    log.info(f"Total probes generated: {len(all_probes)}")
    log.info(f"Cost: ${cost['total_cost_usd']:.4f}")
    log.info(f"Fixes → {fixes_path}")


if __name__ == "__main__":
    main()

"""
Service Mapper — extracts expectations, perceptions, gaps, and innovation
opportunities from transcripts using LLM analysis.

Usage:
    PIPELINE_ENV=dev python -m src.evaluation.service_mapper \
        --transcripts data/transcripts/ \
        --output data/evaluation/ \
        --limit 10
"""
import json, argparse, logging, os, re, time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from src.config.models import get_model, get_provider, get_token_policy, tracker, ENV

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

TASK_NAME = "service_mapping"

SERVICE_CATEGORIES = [
    "continuity_of_care", "information_quality", "emotional_support",
    "clinical_competence", "communication", "partner_involvement",
    "postnatal_mental_health", "birth_environment", "pain_management",
    "breastfeeding_support", "digital_tools", "cultural_sensitivity",
    "accessibility", "privacy_dignity", "shared_decision_making",
    "care_coordination", "financial_accessibility", "transport_access",
]


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
        r = gm.generate_content(full_prompt, generation_config={"max_output_tokens": max_tokens})
        text = r.text.strip()
        try:
            in_tok = r.usage_metadata.prompt_token_count
            out_tok = r.usage_metadata.candidates_token_count
        except AttributeError:
            in_tok, out_tok = 0, 0
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        r = client.messages.create(
            model=model, max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
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


def build_transcript_text(transcript: dict) -> str:
    """Build readable transcript text for LLM analysis."""
    lines = []
    for turn in transcript.get("turns", []):
        role = "Interviewer" if turn["role"] == "interviewer" else "Participant"
        lines.append(f"{role}: {turn.get('text', '')}")
    return "\n\n".join(lines)


def map_transcript(transcript: dict) -> dict:
    """Extract service provision insights from a single transcript."""
    text = build_transcript_text(transcript)
    # Truncate to ~6000 words to stay within token limits
    words = text.split()
    if len(words) > 6000:
        text = " ".join(words[:6000])

    system = """You are an expert in health service innovation analysing a maternity-care interview.
Extract the following from this transcript:

1. EXPECTATIONS: What did the person expect from maternity services? (quote + category)
2. PERCEPTIONS: How did they perceive actual service delivery? (quote + valence: positive/negative/mixed)
3. VALUED ITEMS: What did they value most? (quote + category)
4. MISSING ITEMS: What was missing or unmet? (quote + category)
5. SERVICE GAPS: Where expectations and perceptions diverge (pair them, rate gap_severity: high/medium/low)
6. INNOVATION OPPORTUNITIES: Concrete ideas for new/improved services, tools, processes

Categories: continuity_of_care, information_quality, emotional_support, clinical_competence,
communication, partner_involvement, postnatal_mental_health, birth_environment, pain_management,
breastfeeding_support, digital_tools, cultural_sensitivity, accessibility, privacy_dignity,
shared_decision_making, care_coordination, financial_accessibility, transport_access"""

    prompt = f"""TRANSCRIPT (session {transcript.get('session_id', '')}, {transcript.get('persona_journey_stage', '')} stage):

{text}

Respond ONLY as JSON:
{{"expectations": [{{"text": "...", "category": "...", "journey_phase": "...", "strength": "strong|moderate|weak"}}],
  "perceptions": [{{"text": "...", "category": "...", "journey_phase": "...", "valence": "positive|negative|mixed"}}],
  "valued_items": [{{"text": "...", "category": "...", "journey_phase": "..."}}],
  "missing_items": [{{"text": "...", "category": "...", "journey_phase": "..."}}],
  "service_gaps": [{{"expectation": "...", "perception": "...", "gap_category": "...", "gap_severity": "high|medium|low", "innovation_potential": "..."}}],
  "innovation_opportunities": [{{"description": "...", "source_quote": "...", "category": "...", "journey_phase": "..."}}]
}}"""

    try:
        response, in_tok, out_tok = _call_llm(prompt, system)
        result = _extract_json(response)
        result["session_id"] = transcript.get("session_id", "")
        result["questionnaire_version"] = transcript.get("questionnaire_version", 0)
        result["persona_journey_stage"] = transcript.get("persona_journey_stage", "")
        result["persona_risk_level"] = transcript.get("persona_risk_level", "")
        return result
    except Exception as e:
        log.error(f"  Service mapping error for {transcript.get('session_id', '')}: {e}")
        return {
            "session_id": transcript.get("session_id", ""),
            "questionnaire_version": transcript.get("questionnaire_version", 0),
            "expectations": [], "perceptions": [], "valued_items": [],
            "missing_items": [], "service_gaps": [], "innovation_opportunities": [],
            "error": str(e),
        }


def aggregate_results(maps: list) -> dict:
    """Aggregate service mappings across all transcripts."""
    # Frequency counts
    cat_counts = defaultdict(lambda: {"expectations": 0, "perceptions": 0, "gaps": 0, "innovations": 0, "valued": 0, "missing": 0})
    gap_severity = defaultdict(lambda: {"high": 0, "medium": 0, "low": 0})
    innovation_cats = defaultdict(int)
    by_version = defaultdict(lambda: {"gaps": 0, "innovations": 0, "categories": set()})
    by_phase = defaultdict(lambda: {"gaps": 0, "innovations": 0})

    for m in maps:
        v = m.get("questionnaire_version", 0)
        for e in m.get("expectations", []):
            cat = e.get("category", "other")
            cat_counts[cat]["expectations"] += 1
        for p in m.get("perceptions", []):
            cat = p.get("category", "other")
            cat_counts[cat]["perceptions"] += 1
        for vi in m.get("valued_items", []):
            cat = vi.get("category", "other")
            cat_counts[cat]["valued"] += 1
        for mi in m.get("missing_items", []):
            cat = mi.get("category", "other")
            cat_counts[cat]["missing"] += 1
        for g in m.get("service_gaps", []):
            cat = g.get("gap_category", "other")
            sev = g.get("gap_severity", "medium")
            cat_counts[cat]["gaps"] += 1
            gap_severity[cat][sev] += 1
            by_version[v]["gaps"] += 1
            by_version[v]["categories"].add(cat)
        for inn in m.get("innovation_opportunities", []):
            cat = inn.get("category", "other")
            cat_counts[cat]["innovations"] += 1
            innovation_cats[cat] += 1
            by_version[v]["innovations"] += 1
            phase = inn.get("journey_phase", "")
            if phase:
                by_phase[phase]["innovations"] += 1

    # Version comparison
    version_comp = {}
    for v, data in sorted(by_version.items()):
        version_comp[f"V{v}"] = {
            "total_gaps": data["gaps"],
            "total_innovations": data["innovations"],
            "unique_categories": len(data["categories"]),
        }

    return {
        "total_transcripts": len(maps),
        "category_frequencies": dict(cat_counts),
        "gap_severity_distribution": dict(gap_severity),
        "innovation_categories": dict(sorted(innovation_cats.items(), key=lambda x: -x[1])),
        "version_comparison": version_comp,
        "phase_distribution": dict(by_phase),
        "generated_at": datetime.now().isoformat(),
    }


def export_innovation_md(maps: list, output_path: Path):
    """Export ranked innovation opportunities as markdown."""
    all_innovations = []
    for m in maps:
        for inn in m.get("innovation_opportunities", []):
            inn["session_id"] = m.get("session_id", "")
            inn["version"] = m.get("questionnaire_version", 0)
            all_innovations.append(inn)

    # Group by category
    by_cat = defaultdict(list)
    for inn in all_innovations:
        by_cat[inn.get("category", "other")].append(inn)

    with open(output_path, "w") as f:
        f.write("# Innovation Opportunities from Synthetic Interviews\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Total: {len(all_innovations)} opportunities from {len(maps)} transcripts\n\n")

        for cat, innovations in sorted(by_cat.items(), key=lambda x: -len(x[1])):
            f.write(f"## {cat.replace('_', ' ').title()} ({len(innovations)} mentions)\n\n")
            for inn in innovations[:5]:
                f.write(f"- **{inn.get('description', '')}**\n")
                quote = inn.get("source_quote", "")
                if quote:
                    f.write(f"  > \"{quote[:200]}\"\n")
                f.write(f"  _(Session {inn.get('session_id', '')}, V{inn.get('version', '')})_\n\n")

    log.info(f"  Innovations → {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Service Mapper")
    parser.add_argument("--transcripts", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    log.info(f"Environment: {ENV.value}")
    log.info(f"Model: {get_provider(TASK_NAME)}/{get_model(TASK_NAME)}")

    t_dir = Path(args.transcripts)
    t_files = sorted(list(t_dir.glob("T_S_*.json")) + list(t_dir.glob("T_ADV_*.json")))
    if args.limit > 0:
        t_files = t_files[:args.limit]
    log.info(f"Will map {len(t_files)} transcripts")

    maps = []
    for i, tf in enumerate(t_files):
        with open(tf) as f:
            transcript = json.load(f)
        result = map_transcript(transcript)
        maps.append(result)

        if (i + 1) % 10 == 0 or (i + 1) == len(t_files):
            cost = tracker.summary()
            log.info(f"  Mapped {i+1}/{len(t_files)}, ${cost['total_cost_usd']:.4f}")
        time.sleep(0.3)

    # Export per-transcript maps
    maps_path = out / "service_maps.jsonl"
    with open(maps_path, "w") as f:
        for m in maps:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    log.info(f"Maps → {maps_path}")

    # Aggregate
    aggregate = aggregate_results(maps)
    with open(out / "service_aggregate.json", "w") as f:
        json.dump(aggregate, f, indent=2, ensure_ascii=False)

    # Innovation opportunities markdown
    export_innovation_md(maps, out / "innovation_opportunities.md")

    # Gap heatmap (version × category)
    gap_heatmap = defaultdict(lambda: defaultdict(int))
    for m in maps:
        v = f"V{m.get('questionnaire_version', 0)}"
        for g in m.get("service_gaps", []):
            gap_heatmap[v][g.get("gap_category", "other")] += 1
    with open(out / "gap_heatmap.json", "w") as f:
        json.dump({k: dict(v) for k, v in sorted(gap_heatmap.items())}, f, indent=2)

    # Console
    log.info(f"\n{'='*60}")
    log.info("SERVICE MAPPING SUMMARY")
    log.info(f"{'='*60}")
    log.info(f"  Transcripts: {len(maps)}")
    total_gaps = sum(len(m.get("service_gaps", [])) for m in maps)
    total_inn = sum(len(m.get("innovation_opportunities", [])) for m in maps)
    log.info(f"  Total gaps: {total_gaps}")
    log.info(f"  Total innovations: {total_inn}")
    cost = tracker.summary()
    log.info(f"  Cost: ${cost['total_cost_usd']:.4f}")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()

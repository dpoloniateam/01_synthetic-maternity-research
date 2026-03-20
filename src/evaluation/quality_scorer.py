"""
Quality Scorer — LLM-based evaluation of each question-response pair in transcripts.

Scores on 5 dimensions: emotional_depth, specificity, latent_surfacing,
narrative_quality, clinical_grounding. Batches 10 Q-R pairs per LLM call.

Usage:
    PIPELINE_ENV=dev python -m src.evaluation.quality_scorer \
        --transcripts data/transcripts/ \
        --personas data/composite_personas/composites.jsonl \
        --questionnaires data/questionnaires/ \
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

TASK_NAME = "quality_scoring"
BATCH_SIZE = 10


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response."""
    # Try direct parse
    text = text.strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    # Try extracting from markdown code blocks
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Try extracting JSON array wrapper
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return {}


def _call_llm(prompt: str, system_prompt: str = "") -> tuple:
    """Call LLM for quality scoring. Returns (text, in_tok, out_tok)."""
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
        r = gm.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": max_tokens},
            request_options={"timeout": 120},
        )
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
        r = client.chat.completions.create(
            model=model, messages=messages,
            **{token_param: max_tokens},
        )
        text = r.choices[0].message.content.strip()
        in_tok, out_tok = r.usage.prompt_tokens, r.usage.completion_tokens
    else:
        raise ValueError(f"Unknown provider: {provider}")

    tracker.record(TASK_NAME, provider, model, in_tok, out_tok)
    return text, in_tok, out_tok


def build_batch_prompt(pairs: list) -> str:
    """Build prompt for batch quality scoring of multiple Q-R pairs."""
    system = """You are an expert qualitative researcher evaluating interview responses for a
maternity-care user research study. You will score multiple question-response pairs.

For EACH pair, score on 5 dimensions (0-5 each):
1. emotional_depth: Presence of emotional language, hedging, contradiction, vulnerability
   0=none, 3=some emotion, 5=deeply layered emotional expression
2. specificity: Concrete examples, names, dates, places vs. generic statements
   0=entirely generic, 3=some specifics, 5=vivid concrete detail
3. latent_surfacing: How many of the encoded latent dimensions are visible in response?
   0=none surfaced, 3=some implicit, 5=multiple explicitly manifested
4. narrative_quality: Storytelling, temporal flow, personal detail, coherence
   0=fragmented/empty, 3=adequate narrative, 5=compelling personal story
5. clinical_grounding: References to actual medical experiences consistent with context
   0=no clinical content, 3=some medical reference, 5=deeply integrated clinical detail

Also identify for each:
- kbv_dimensions_present: which of [goals, motivations, behaviours, latent_needs] are present
- latent_dimensions_surfaced: which encoded dimensions are visible
- thematic_areas_covered: which themes are addressed"""

    items = []
    for i, p in enumerate(pairs):
        items.append(f"""--- PAIR {i+1} ---
QUESTION_ID: {p['question_id']}
QUESTION: {p['question_text']}
RESPONSE: {p['response_text'][:1500]}
PERSONA: {p['journey_stage']}, {p['risk_level']}
ENCODED LATENT DIMENSIONS: {', '.join(p['encoded_latent'])}
TARGET DIMENSIONS: {', '.join(p['target_dimensions'])}""")

    prompt = "\n\n".join(items)
    prompt += f"""

Respond ONLY as a JSON object with this structure:
{{"results": [
  {{"pair_index": 1, "question_id": "...",
    "scores": {{
      "emotional_depth": {{"score": N, "evidence": "..."}},
      "specificity": {{"score": N, "evidence": "..."}},
      "latent_surfacing": {{"score": N, "evidence": "..."}},
      "narrative_quality": {{"score": N, "evidence": "..."}},
      "clinical_grounding": {{"score": N, "evidence": "..."}}
    }},
    "composite_richness": N.N,
    "kbv_dimensions_present": [...],
    "latent_dimensions_surfaced": [...],
    "latent_dimensions_encoded_but_absent": [...],
    "thematic_areas_covered": [...]
  }},
  ...
]}}"""

    return system, prompt


def extract_qr_pairs(transcript: dict, persona: dict, questionnaires: dict) -> list:
    """Extract question-response pairs from a transcript."""
    pairs = []
    version = transcript.get("questionnaire_version", 1)
    q_lookup = {}
    q_data = questionnaires.get(version, {})
    for q in q_data.get("questions", []):
        q_lookup[q.get("question_id", "")] = q

    turns = transcript.get("turns", [])
    for i, turn in enumerate(turns):
        if turn.get("role") != "persona" or turn.get("type") != "response":
            continue
        responding_to = turn.get("responding_to_question_id")
        if not responding_to:
            continue

        # Find the interviewer turn
        question_text = ""
        target_dims = []
        target_latent = []
        for j in range(i - 1, -1, -1):
            prev = turns[j]
            if prev.get("role") == "interviewer":
                question_text = prev.get("text", "")
                target_dims = prev.get("target_dimensions", [])
                target_latent = prev.get("target_latent", [])
                break

        # Get encoded latent dims from questionnaire
        q_info = q_lookup.get(responding_to, {})
        q_target_latent = q_info.get("target_latent_dimensions", [])
        all_targets = list(set(target_latent + q_target_latent))

        pairs.append({
            "question_id": responding_to,
            "question_text": question_text,
            "response_text": turn.get("text", ""),
            "response_text_length": len(turn.get("text", "").split()),
            "journey_stage": transcript.get("persona_journey_stage", ""),
            "risk_level": transcript.get("persona_risk_level", ""),
            "encoded_latent": list(persona.get("latent_dimensions", {}).keys()) if isinstance(persona.get("latent_dimensions"), dict) else persona.get("latent_dimensions", []),
            "target_dimensions": all_targets,
        })

    return pairs


def score_transcript(transcript: dict, persona: dict, questionnaires: dict) -> list:
    """Score all Q-R pairs in a transcript. Returns list of scored records."""
    pairs = extract_qr_pairs(transcript, persona, questionnaires)
    if not pairs:
        return []

    scored = []
    # Process in batches
    for batch_start in range(0, len(pairs), BATCH_SIZE):
        batch = pairs[batch_start:batch_start + BATCH_SIZE]
        system, prompt = build_batch_prompt(batch)

        try:
            text, in_tok, out_tok = _call_llm(prompt, system)
            result = _extract_json(text)
            results_list = result.get("results", [])

            for i, pair in enumerate(batch):
                if i < len(results_list):
                    r = results_list[i]
                    scores = r.get("scores", {})
                    record = {
                        "session_id": transcript["session_id"],
                        "question_id": pair["question_id"],
                        "response_text_length": pair["response_text_length"],
                        "scores": {
                            dim: scores.get(dim, {}).get("score", 0) if isinstance(scores.get(dim), dict) else scores.get(dim, 0)
                            for dim in ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]
                        },
                        "evidence": {
                            dim: scores.get(dim, {}).get("evidence", "") if isinstance(scores.get(dim), dict) else ""
                            for dim in ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]
                        },
                        "composite_richness": r.get("composite_richness", 0),
                        "kbv_dimensions_present": r.get("kbv_dimensions_present", []),
                        "latent_dimensions_surfaced": r.get("latent_dimensions_surfaced", []),
                        "latent_dimensions_encoded_but_absent": r.get("latent_dimensions_encoded_but_absent", []),
                        "thematic_areas_covered": r.get("thematic_areas_covered", []),
                    }
                    # Compute composite if not provided
                    if not record["composite_richness"]:
                        vals = [v for v in record["scores"].values() if isinstance(v, (int, float))]
                        record["composite_richness"] = round(sum(vals) / max(len(vals), 1), 1)
                    scored.append(record)
                else:
                    # Missing result — use defaults
                    scored.append({
                        "session_id": transcript["session_id"],
                        "question_id": pair["question_id"],
                        "response_text_length": pair["response_text_length"],
                        "scores": {d: 0 for d in ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]},
                        "evidence": {},
                        "composite_richness": 0,
                        "kbv_dimensions_present": [],
                        "latent_dimensions_surfaced": [],
                        "latent_dimensions_encoded_but_absent": [],
                        "thematic_areas_covered": [],
                    })
        except Exception as e:
            log.error(f"  Scoring error for {transcript['session_id']} batch {batch_start}: {e}")
            for pair in batch:
                scored.append({
                    "session_id": transcript["session_id"],
                    "question_id": pair["question_id"],
                    "response_text_length": pair["response_text_length"],
                    "scores": {d: 0 for d in ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]},
                    "evidence": {},
                    "composite_richness": 0,
                    "kbv_dimensions_present": [],
                    "latent_dimensions_surfaced": [],
                    "latent_dimensions_encoded_but_absent": [],
                    "thematic_areas_covered": [],
                })

        time.sleep(0.3)

    return scored


def build_transcript_summary(session_id: str, transcript: dict, scored_responses: list) -> dict:
    """Build per-transcript aggregate summary."""
    if not scored_responses:
        return {"session_id": session_id, "n_responses": 0}

    n = len(scored_responses)
    dims = ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]

    mean_scores = {}
    for d in dims:
        vals = [r["scores"].get(d, 0) for r in scored_responses if isinstance(r["scores"].get(d), (int, float))]
        mean_scores[d] = round(sum(vals) / max(len(vals), 1), 2)

    all_richness = [r.get("composite_richness", 0) for r in scored_responses]
    mean_richness = round(sum(all_richness) / max(len(all_richness), 1), 2)

    # Surfacing rate: proportion of encoded latent dims that were surfaced
    all_surfaced = set()
    for r in scored_responses:
        all_surfaced.update(r.get("latent_dimensions_surfaced", []))

    encoded = set(transcript.get("persona_latent_dimensions", []))
    surfacing_rate = round(len(all_surfaced & encoded) / max(len(encoded), 1), 3) if encoded else 0

    # KBV coverage
    kbv_seen = set()
    for r in scored_responses:
        kbv_seen.update(r.get("kbv_dimensions_present", []))

    # Thematic coverage
    thematic_seen = set()
    for r in scored_responses:
        thematic_seen.update(r.get("thematic_areas_covered", []))

    return {
        "session_id": session_id,
        "persona_id": transcript.get("persona_id", ""),
        "questionnaire_version": transcript.get("questionnaire_version", 0),
        "persona_journey_stage": transcript.get("persona_journey_stage", ""),
        "persona_risk_level": transcript.get("persona_risk_level", ""),
        "persona_model": transcript.get("persona_model", ""),
        "n_responses": n,
        "mean_scores": mean_scores,
        "mean_composite_richness": mean_richness,
        "surfacing_rate": surfacing_rate,
        "latent_dimensions_surfaced": sorted(all_surfaced),
        "latent_dimensions_encoded": sorted(encoded),
        "kbv_dimensions_covered": sorted(kbv_seen),
        "thematic_areas_covered": sorted(thematic_seen),
        "total_turns": transcript.get("metadata", {}).get("total_turns", 0),
        "questions_asked": transcript.get("metadata", {}).get("questions_asked", 0),
        "probes_deployed": transcript.get("metadata", {}).get("probes_deployed", 0),
    }


def main():
    parser = argparse.ArgumentParser(description="Quality Scorer")
    parser.add_argument("--transcripts", type=str, required=True)
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--questionnaires", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    log.info(f"Environment: {ENV.value}")
    log.info(f"Model: {get_provider(TASK_NAME)}/{get_model(TASK_NAME)}")

    # Load personas
    persona_map = {}
    with open(args.personas) as f:
        for line in f:
            line = line.strip()
            if line:
                p = json.loads(line)
                persona_map[p.get("composite_id", "")] = p
    log.info(f"Loaded {len(persona_map)} personas")

    # Load questionnaires
    questionnaires = {}
    q_dir = Path(args.questionnaires)
    for v in range(1, 6):
        qf = q_dir / f"Q_V{v}.json"
        if qf.exists():
            with open(qf) as f:
                questionnaires[v] = json.load(f)
    log.info(f"Loaded {len(questionnaires)} questionnaire versions")

    # Load transcripts
    t_dir = Path(args.transcripts)
    t_files = sorted(list(t_dir.glob("T_S_*.json")) + list(t_dir.glob("T_ADV_*.json")))
    if args.limit > 0:
        t_files = t_files[:args.limit]
    log.info(f"Will score {len(t_files)} transcripts")

    # Score (with incremental save every 50 transcripts)
    scores_path = out / "quality_scores.jsonl"
    summaries_path = out / "transcript_summaries.jsonl"
    all_scores = []
    all_summaries = []

    # Resume support: check already-scored sessions
    scored_sessions = set()
    if scores_path.exists():
        with open(scores_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    scored_sessions.add(r.get("session_id", ""))
        if scored_sessions:
            # Reload existing data
            with open(scores_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        all_scores.append(json.loads(line))
            if summaries_path.exists():
                with open(summaries_path) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            all_summaries.append(json.loads(line))
            log.info(f"Resuming: {len(scored_sessions)} sessions already scored")

    for i, tf in enumerate(t_files):
        with open(tf) as f:
            transcript = json.load(f)

        sid = transcript.get("session_id", "")
        if sid in scored_sessions:
            continue

        pid = transcript.get("persona_id", "")
        persona = persona_map.get(pid, {})

        scored = score_transcript(transcript, persona, questionnaires)
        all_scores.extend(scored)

        summary = build_transcript_summary(sid, transcript, scored)
        all_summaries.append(summary)

        if (i + 1) % 10 == 0 or (i + 1) == len(t_files):
            cost = tracker.summary()
            log.info(f"  Scored {i+1}/{len(t_files)} transcripts, "
                     f"{len(all_scores)} responses, ${cost['total_cost_usd']:.4f}")

        # Incremental save every 50 transcripts
        if (i + 1) % 50 == 0:
            with open(scores_path, "w") as f:
                for s in all_scores:
                    f.write(json.dumps(s, ensure_ascii=False) + "\n")
            with open(summaries_path, "w") as f:
                for s in all_summaries:
                    f.write(json.dumps(s, ensure_ascii=False) + "\n")
            log.info(f"  Checkpoint saved at {i+1} transcripts")

    # Final export scores
    with open(scores_path, "w") as f:
        for s in all_scores:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    log.info(f"Scores → {scores_path} ({len(all_scores)} records)")

    # Final export summaries
    with open(summaries_path, "w") as f:
        for s in all_summaries:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    log.info(f"Summaries → {summaries_path} ({len(all_summaries)} records)")

    # Global summary
    dims = ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]
    global_means = {}
    for d in dims:
        vals = [r["scores"].get(d, 0) for r in all_scores if isinstance(r["scores"].get(d), (int, float))]
        global_means[d] = round(sum(vals) / max(len(vals), 1), 2)

    all_richness = [r.get("composite_richness", 0) for r in all_scores]
    all_surfacing = [s.get("surfacing_rate", 0) for s in all_summaries]

    scoring_summary = {
        "total_transcripts": len(all_summaries),
        "total_responses_scored": len(all_scores),
        "mean_scores_global": global_means,
        "mean_composite_richness": round(sum(all_richness) / max(len(all_richness), 1), 2),
        "mean_surfacing_rate": round(sum(all_surfacing) / max(len(all_surfacing), 1), 3),
        "score_distribution": {
            d: {
                "min": min([v for v in (r["scores"].get(d, 0) for r in all_scores) if isinstance(v, (int, float))] or [0]),
                "max": max([v for v in (r["scores"].get(d, 0) for r in all_scores) if isinstance(v, (int, float))] or [0]),
                "mean": global_means[d],
            }
            for d in dims
        },
        "cost": tracker.summary(),
        "generated_at": datetime.now().isoformat(),
        "environment": ENV.value,
    }

    summary_path = out / "scoring_summary.json"
    with open(summary_path, "w") as f:
        json.dump(scoring_summary, f, indent=2, ensure_ascii=False)
    log.info(f"Summary → {summary_path}")

    # Console
    log.info(f"\n{'='*60}")
    log.info("QUALITY SCORING SUMMARY")
    log.info(f"{'='*60}")
    log.info(f"  Transcripts: {len(all_summaries)}")
    log.info(f"  Responses scored: {len(all_scores)}")
    log.info(f"  Mean composite richness: {scoring_summary['mean_composite_richness']}")
    log.info(f"  Mean surfacing rate: {scoring_summary['mean_surfacing_rate']:.1%}")
    for d in dims:
        log.info(f"  {d:<22s}: {global_means[d]:.2f}")
    cost = tracker.summary()
    log.info(f"  Cost: ${cost['total_cost_usd']:.4f}")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()

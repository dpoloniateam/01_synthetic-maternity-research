"""
Inter-Rater Reliability — multi-model agreement check.
30 transcripts scored by all 3 providers independently.

Usage:
    PIPELINE_ENV=dev python -m src.evaluation.inter_rater \
        --transcripts data/transcripts/ \
        --personas data/composite_personas/composites.jsonl \
        --questionnaires data/questionnaires/ \
        --plan data/config/administration_plan.json \
        --output data/evaluation/ \
        --sample 30
"""
import json, argparse, logging, os, re, time, math, random
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from src.config.models import MODELS, Tier, tracker, ENV

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

TASK_NAME = "inter_rater_reliability"
SCORING_DIMS = ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]

# Provider configs for inter-rater
PROVIDERS = [
    {"provider": "anthropic", "model": MODELS["anthropic"][Tier.BAIXO]},
    {"provider": "google", "model": MODELS["google"][Tier.MODERADO]},
    {"provider": "openai", "model": MODELS["openai"][Tier.BAIXO]},
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


def _call_provider(provider: str, model: str, prompt: str, system_prompt: str) -> tuple:
    """Call a specific provider for scoring."""
    max_tokens = 4096

    if provider == "google":
        max_tokens = max(max_tokens * 15, 16000)
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        full = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        gm = genai.GenerativeModel(model_name=model)
        r = gm.generate_content(full, generation_config={"max_output_tokens": max_tokens})
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
    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        token_param = "max_completion_tokens" if "gpt-5" in model or "o3" in model or "o4" in model else "max_tokens"
        r = client.chat.completions.create(model=model, messages=messages, **{token_param: max_tokens})
        text = r.choices[0].message.content.strip()
        in_tok, out_tok = r.usage.prompt_tokens, r.usage.completion_tokens
    else:
        raise ValueError(f"Unknown provider: {provider}")

    tracker.record(TASK_NAME, provider, model, in_tok, out_tok)
    return text, in_tok, out_tok


def build_scoring_prompt(transcript: dict, persona: dict) -> tuple:
    """Build prompt for scoring a transcript."""
    # Build transcript summary (first 3 Q-R pairs)
    pairs_text = []
    turns = transcript.get("turns", [])
    pair_count = 0
    for i, turn in enumerate(turns):
        if turn.get("role") == "persona" and turn.get("responding_to_question_id"):
            # Find question
            q_text = ""
            for j in range(i - 1, -1, -1):
                if turns[j].get("role") == "interviewer":
                    q_text = turns[j].get("text", "")[:300]
                    break
            r_text = turn.get("text", "")[:500]
            pairs_text.append(f"Q: {q_text}\nA: {r_text}")
            pair_count += 1
            if pair_count >= 5:
                break

    system = """You are an expert qualitative researcher scoring interview responses.
Score EACH response on 5 dimensions (0-5):
1. emotional_depth: 0=none, 5=deeply layered
2. specificity: 0=generic, 5=vivid detail
3. latent_surfacing: 0=none surfaced, 5=multiple dimensions
4. narrative_quality: 0=fragmented, 5=compelling story
5. clinical_grounding: 0=no clinical, 5=deeply integrated

Also compute an overall composite_richness (mean of 5 scores).
Identify latent_dimensions_surfaced from the encoded list."""

    encoded = list(persona.get("latent_dimensions", {}).keys()) if isinstance(persona.get("latent_dimensions"), dict) else persona.get("latent_dimensions", [])

    prompt = f"""TRANSCRIPT: {transcript.get('session_id', '')}
PERSONA: {transcript.get('persona_journey_stage', '')}, {transcript.get('persona_risk_level', '')}
ENCODED LATENT DIMENSIONS: {', '.join(encoded)}

QUESTION-RESPONSE PAIRS:
{'---'.join(pairs_text)}

Respond ONLY as JSON:
{{"scores": {{"emotional_depth": N, "specificity": N, "latent_surfacing": N, "narrative_quality": N, "clinical_grounding": N}},
  "composite_richness": N.N,
  "latent_dimensions_surfaced": [...]}}"""

    return system, prompt


def select_sample(transcripts_dir: Path, plan: list, n: int = 30) -> list:
    """Select stratified sample: 6 per version, balanced by risk."""
    by_version = defaultdict(list)
    for p in plan:
        by_version[p["questionnaire_version"]].append(p)

    selected = []
    rng = random.Random(42)
    per_version = max(n // 5, 1)

    for v in sorted(by_version.keys()):
        sessions = by_version[v]
        rng.shuffle(sessions)
        # Try to get balanced risk levels
        by_risk = defaultdict(list)
        for s in sessions:
            by_risk[s.get("persona_risk_level", "unknown")].append(s)

        chosen = []
        for risk_sessions in by_risk.values():
            take = min(len(risk_sessions), max(per_version // len(by_risk), 1))
            chosen.extend(risk_sessions[:take])

        # Fill up to per_version
        remaining = [s for s in sessions if s not in chosen]
        while len(chosen) < per_version and remaining:
            chosen.append(remaining.pop(0))

        selected.extend(chosen[:per_version])

    return selected[:n]


def compute_icc(ratings_matrix: list) -> float:
    """Compute ICC(2,1) — two-way random, absolute agreement.
    ratings_matrix: list of [rater1, rater2, rater3] per subject."""
    n = len(ratings_matrix)
    k = len(ratings_matrix[0]) if ratings_matrix else 0
    if n < 2 or k < 2:
        return 0

    # Grand mean
    all_vals = [v for row in ratings_matrix for v in row]
    grand_mean = sum(all_vals) / len(all_vals)

    # Row means (subjects)
    row_means = [sum(row) / k for row in ratings_matrix]
    # Col means (raters)
    col_means = [sum(ratings_matrix[i][j] for i in range(n)) / n for j in range(k)]

    # Mean squares
    ms_rows = k * sum((rm - grand_mean) ** 2 for rm in row_means) / max(n - 1, 1)
    ms_cols = n * sum((cm - grand_mean) ** 2 for cm in col_means) / max(k - 1, 1)
    ms_error = sum((ratings_matrix[i][j] - row_means[i] - col_means[j] + grand_mean) ** 2
                    for i in range(n) for j in range(k)) / max((n - 1) * (k - 1), 1)

    # ICC(2,1)
    denom = ms_rows + (k - 1) * ms_error + k * (ms_cols - ms_error) / n
    if denom == 0:
        return 0
    icc = (ms_rows - ms_error) / denom
    return round(max(min(icc, 1.0), -1.0), 3)


def compute_krippendorff_alpha(ratings_matrix: list) -> float:
    """Simplified Krippendorff's alpha for ordinal data."""
    n = len(ratings_matrix)
    k = len(ratings_matrix[0]) if ratings_matrix else 0
    if n < 2 or k < 2:
        return 0

    all_vals = [v for row in ratings_matrix for v in row]
    total = len(all_vals)
    grand_var = sum((v - sum(all_vals) / total) ** 2 for v in all_vals) / max(total - 1, 1)
    if grand_var == 0:
        return 1.0

    # Within-unit variance
    within_var = 0
    for row in ratings_matrix:
        row_mean = sum(row) / k
        within_var += sum((v - row_mean) ** 2 for v in row)
    within_var /= max(n * (k - 1), 1)

    alpha = 1 - within_var / grand_var
    return round(max(min(alpha, 1.0), -1.0), 3)


def spearman_corr(x: list, y: list) -> float:
    """Compute Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0

    # Rank
    def rank(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0] * n
        for r, i in enumerate(indexed):
            ranks[i] = r + 1
        return ranks

    rx, ry = rank(x), rank(y)
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    rho = 1 - 6 * d2 / (n * (n ** 2 - 1))
    return round(rho, 3)


def interpret_icc(icc: float) -> str:
    if icc >= 0.75:
        return "excellent"
    elif icc >= 0.60:
        return "good"
    elif icc >= 0.40:
        return "fair"
    else:
        return "poor"


def main():
    parser = argparse.ArgumentParser(description="Inter-Rater Reliability")
    parser.add_argument("--transcripts", type=str, required=True)
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--questionnaires", type=str, required=True)
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--sample", type=int, default=30)
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    log.info(f"Environment: {ENV.value}")

    # Load
    persona_map = {}
    with open(args.personas) as f:
        for line in f:
            line = line.strip()
            if line:
                p = json.loads(line)
                persona_map[p.get("composite_id", "")] = p

    with open(args.plan) as f:
        plan = json.load(f)

    # Select sample
    sample = select_sample(Path(args.transcripts), plan, args.sample)
    log.info(f"Selected {len(sample)} transcripts for inter-rater check")

    # Score each transcript with all 3 providers
    all_scores = []
    for i, session in enumerate(sample):
        sid = session["session_id"]
        t_path = Path(args.transcripts) / f"T_{sid}.json"
        if not t_path.exists():
            continue

        with open(t_path) as f:
            transcript = json.load(f)

        pid = transcript.get("persona_id", "")
        persona = persona_map.get(pid, {})
        system, prompt = build_scoring_prompt(transcript, persona)

        session_scores = {"session_id": sid, "version": session.get("questionnaire_version", 0)}

        for prov_config in PROVIDERS:
            prov = prov_config["provider"]
            model = prov_config["model"]
            try:
                text, in_tok, out_tok = _call_provider(prov, model, prompt, system)
                result = _extract_json(text)
                scores = result.get("scores", {})
                session_scores[prov] = {
                    "scores": {d: scores.get(d, 0) for d in SCORING_DIMS},
                    "composite": result.get("composite_richness", 0),
                    "latent_surfaced": result.get("latent_dimensions_surfaced", []),
                }
                # Compute composite if missing
                if not session_scores[prov]["composite"]:
                    vals = [v for v in session_scores[prov]["scores"].values() if isinstance(v, (int, float))]
                    session_scores[prov]["composite"] = round(sum(vals) / max(len(vals), 1), 1)
            except Exception as e:
                log.error(f"  {prov} error for {sid}: {e}")
                session_scores[prov] = {
                    "scores": {d: 0 for d in SCORING_DIMS},
                    "composite": 0,
                    "latent_surfaced": [],
                    "error": str(e),
                }
            time.sleep(0.3)

        all_scores.append(session_scores)

        if (i + 1) % 5 == 0 or (i + 1) == len(sample):
            cost = tracker.summary()
            log.info(f"  Scored {i+1}/{len(sample)} transcripts × 3 providers, ${cost['total_cost_usd']:.4f}")

    # Save raw scores
    with open(out / "inter_rater_scores.json", "w") as f:
        json.dump(all_scores, f, indent=2, ensure_ascii=False)

    # Compute agreement metrics
    providers = ["anthropic", "google", "openai"]
    agreement = {}

    for dim in SCORING_DIMS:
        matrix = []
        for s in all_scores:
            row = []
            for prov in providers:
                score = s.get(prov, {}).get("scores", {}).get(dim, 0)
                if isinstance(score, (int, float)):
                    row.append(score)
                else:
                    row.append(0)
            if len(row) == 3:
                matrix.append(row)

        if matrix:
            icc = compute_icc(matrix)
            alpha = compute_krippendorff_alpha(matrix)

            # Pairwise Spearman
            pairwise = {}
            for a in range(3):
                for b in range(a + 1, 3):
                    x = [row[a] for row in matrix]
                    y = [row[b] for row in matrix]
                    rho = spearman_corr(x, y)
                    pairwise[f"{providers[a]}_vs_{providers[b]}"] = rho

            agreement[dim] = {
                "icc": icc,
                "interpretation": interpret_icc(icc),
                "krippendorff_alpha": alpha,
                "pairwise_spearman": pairwise,
                "n_subjects": len(matrix),
            }

    # Composite ICC
    comp_matrix = []
    for s in all_scores:
        row = [s.get(prov, {}).get("composite", 0) for prov in providers]
        comp_matrix.append(row)
    if comp_matrix:
        agreement["composite_richness"] = {
            "icc": compute_icc(comp_matrix),
            "interpretation": interpret_icc(compute_icc(comp_matrix)),
            "n_subjects": len(comp_matrix),
        }

    with open(out / "inter_rater_agreement.json", "w") as f:
        json.dump(agreement, f, indent=2)

    # Report
    with open(out / "inter_rater_report.md", "w") as f:
        f.write("# Inter-Rater Reliability Report\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Sample: {len(all_scores)} transcripts × 3 providers\n")
        providers_str = ', '.join(p["provider"] + "/" + p["model"] for p in PROVIDERS)
        f.write(f"Providers: {providers_str}\n\n")

        f.write("## Agreement by Dimension\n\n")
        f.write("| Dimension | ICC(2,1) | Interpretation | Krippendorff α | N |\n")
        f.write("|-----------|----------|----------------|----------------|---|\n")
        for dim in SCORING_DIMS + ["composite_richness"]:
            data = agreement.get(dim, {})
            icc = data.get("icc", 0)
            interp = data.get("interpretation", "N/A")
            alpha = data.get("krippendorff_alpha", "N/A")
            n = data.get("n_subjects", 0)
            flag = " ⚠️" if isinstance(icc, (int, float)) and icc < 0.60 else ""
            f.write(f"| {dim} | {icc} | {interp}{flag} | {alpha} | {n} |\n")

        f.write("\n## Pairwise Spearman Correlations\n\n")
        f.write("| Dimension | Anthropic-Google | Anthropic-OpenAI | Google-OpenAI |\n")
        f.write("|-----------|------------------|------------------|---------------|\n")
        for dim in SCORING_DIMS:
            pw = agreement.get(dim, {}).get("pairwise_spearman", {})
            ag = pw.get("anthropic_vs_google", "N/A")
            ao = pw.get("anthropic_vs_openai", "N/A")
            go = pw.get("google_vs_openai", "N/A")
            f.write(f"| {dim} | {ag} | {ao} | {go} |\n")

        f.write("\n## Interpretation\n\n")
        f.write("Thresholds (Cicchetti, 1994):\n")
        f.write("- ICC < 0.40 = poor\n")
        f.write("- 0.40-0.59 = fair\n")
        f.write("- 0.60-0.74 = good\n")
        f.write("- 0.75-1.00 = excellent\n\n")

        cautions = [dim for dim in SCORING_DIMS if agreement.get(dim, {}).get("icc", 1) < 0.60]
        if cautions:
            f.write(f"**Dimensions requiring caution:** {', '.join(cautions)}\n")
        else:
            f.write("All dimensions show adequate agreement (ICC >= 0.60).\n")

    log.info(f"\n{'='*60}")
    log.info("INTER-RATER RELIABILITY SUMMARY")
    log.info(f"{'='*60}")
    for dim in SCORING_DIMS + ["composite_richness"]:
        data = agreement.get(dim, {})
        log.info(f"  {dim:<25s}: ICC={data.get('icc', 'N/A'):<6} ({data.get('interpretation', 'N/A')})")
    cost = tracker.summary()
    log.info(f"  Cost: ${cost['total_cost_usd']:.4f}")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()

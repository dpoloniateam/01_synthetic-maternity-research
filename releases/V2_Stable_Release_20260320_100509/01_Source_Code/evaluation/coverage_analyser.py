"""
Coverage Analyser — dimension heatmaps, blind spots, question rankings.
Pure computation on quality_scores.jsonl output. No LLM calls.

Usage:
    python -m src.evaluation.coverage_analyser \
        --scores data/evaluation/quality_scores.jsonl \
        --summaries data/evaluation/transcript_summaries.jsonl \
        --questionnaires data/questionnaires/ \
        --plan data/config/administration_plan.json \
        --output data/evaluation/
"""
import json, argparse, logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from src.questionnaire.frameworks import LATENT_DIMENSIONS, JOURNEY_PHASES

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

ALL_DIMS = sorted(LATENT_DIMENSIONS.keys())
ALL_PHASES = sorted(JOURNEY_PHASES.keys())


def load_jsonl(path: str) -> list:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_dimension_heatmap(summaries: list) -> dict:
    """5×12 matrix: version × latent dimension → surfacing rate."""
    # Group by version
    by_version = defaultdict(list)
    for s in summaries:
        by_version[s.get("questionnaire_version", 0)].append(s)

    matrix = {}
    for v in sorted(by_version.keys()):
        vk = f"V{v}"
        matrix[vk] = {}
        transcripts = by_version[v]
        n = max(len(transcripts), 1)
        for dim in ALL_DIMS:
            count = sum(1 for t in transcripts if dim in t.get("latent_dimensions_surfaced", []))
            rate = round(count / n * 100, 1)
            matrix[vk][dim] = {"surfacing_rate": rate, "count": count, "total": n}

    return matrix


def build_phase_coverage(scores: list, summaries: list, plan: list) -> dict:
    """5×4 matrix: version × journey phase → mean richness."""
    # Map session_id → version + stage
    session_meta = {}
    for s in summaries:
        session_meta[s["session_id"]] = {
            "version": s.get("questionnaire_version", 0),
            "stage": s.get("persona_journey_stage", ""),
        }

    # Map question_id prefix to phase
    prefix_to_phase = {
        "PREC": "preconception", "PREG": "pregnancy",
        "BIRTH": "birth", "BRTH": "birth",
        "POST": "postpartum",
    }

    def get_phase(qid: str) -> str:
        parts = qid.split("_")
        for part in parts:
            for prefix, phase in prefix_to_phase.items():
                if part.startswith(prefix):
                    return phase
        return "unknown"

    # Group scores by (version, phase)
    cells = defaultdict(list)
    for sc in scores:
        meta = session_meta.get(sc.get("session_id", ""), {})
        version = meta.get("version", 0)
        phase = get_phase(sc.get("question_id", ""))
        if phase != "unknown" and version > 0:
            cells[(version, phase)].append(sc.get("composite_richness", 0))

    matrix = {}
    for (v, phase), richness_vals in sorted(cells.items()):
        vk = f"V{v}"
        if vk not in matrix:
            matrix[vk] = {}
        n = len(richness_vals)
        matrix[vk][phase] = {
            "mean_richness": round(sum(richness_vals) / max(n, 1), 2),
            "n_responses": n,
        }

    return matrix


def identify_blind_spots(heatmap: dict, questionnaires: dict) -> list:
    """Find (version × dimension) cells with surfacing_rate < 20%."""
    blind_spots = []
    for vk, dims in heatmap.items():
        v = int(vk.replace("V", ""))
        q_data = questionnaires.get(v, {})
        questions = q_data.get("questions", [])

        for dim, data in dims.items():
            if data["surfacing_rate"] < 20.0:
                # Find questions targeting this dimension
                targeting = []
                for q in questions:
                    targets = q.get("target_latent_dimensions", [])
                    if dim in targets:
                        targeting.append(q.get("question_id", ""))

                dim_info = LATENT_DIMENSIONS.get(dim, {})
                strategies = dim_info.get("surfacing_strategies", [])

                blind_spots.append({
                    "version": v,
                    "dimension": dim,
                    "surfacing_rate": data["surfacing_rate"],
                    "questions_targeting": targeting,
                    "diagnosis": f"Only {data['count']}/{data['total']} transcripts surfaced '{dim}'. "
                                 f"{len(targeting)} questions target this dimension.",
                    "recommendation": f"Add probe: {strategies[0]}" if strategies else "Add targeted probe",
                })

    return sorted(blind_spots, key=lambda x: x["surfacing_rate"])


def build_question_rankings(scores: list) -> dict:
    """Rank questions by mean richness and dimension surfacing."""
    by_question = defaultdict(lambda: {"richness": [], "dims_surfaced": set(), "probe_count": 0})

    for sc in scores:
        qid = sc.get("question_id", "")
        if not qid:
            continue
        by_question[qid]["richness"].append(sc.get("composite_richness", 0))
        for d in sc.get("latent_dimensions_surfaced", []):
            by_question[qid]["dims_surfaced"].add(d)

    rankings = []
    for qid, data in by_question.items():
        n = len(data["richness"])
        mean_r = round(sum(data["richness"]) / max(n, 1), 2)
        rankings.append({
            "question_id": qid,
            "mean_richness": mean_r,
            "n_responses": n,
            "distinct_dimensions_surfaced": len(data["dims_surfaced"]),
            "dimensions": sorted(data["dims_surfaced"]),
        })

    rankings.sort(key=lambda x: (-x["mean_richness"], -x["distinct_dimensions_surfaced"]))

    # Split by version prefix
    by_version = defaultdict(list)
    for r in rankings:
        v = r["question_id"].split("_")[0] if "_" in r["question_id"] else "?"
        by_version[v].append(r)

    result = {}
    for v, qs in sorted(by_version.items()):
        result[v] = {
            "top_5": qs[:5],
            "bottom_5": qs[-5:] if len(qs) > 5 else qs,
            "total_questions": len(qs),
        }

    return result


def export_heatmap_md(heatmap: dict, output_path: Path):
    """Export dimension heatmap as markdown table."""
    with open(output_path, "w") as f:
        f.write("# Dimension Surfacing Heatmap (Version × Latent Dimension)\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write("Cells: surfacing rate (%). Green >60%, Yellow 20-60%, Red <20%\n\n")

        # Header
        versions = sorted(heatmap.keys())
        f.write(f"| {'Dimension':<30s} |")
        for v in versions:
            f.write(f" {v:>6s} |")
        f.write("\n")
        f.write(f"|{'-'*31}|")
        for _ in versions:
            f.write(f"{'-'*8}|")
        f.write("\n")

        for dim in ALL_DIMS:
            label = dim.replace("_", " ").title()[:30]
            f.write(f"| {label:<30s} |")
            for v in versions:
                rate = heatmap.get(v, {}).get(dim, {}).get("surfacing_rate", 0)
                icon = "🟢" if rate > 60 else "🟡" if rate >= 20 else "🔴"
                f.write(f" {rate:5.1f}% |")
            f.write("\n")

    log.info(f"  Heatmap → {output_path}")


def export_rankings_md(rankings: dict, output_path: Path):
    """Export question rankings as markdown."""
    with open(output_path, "w") as f:
        f.write("# Question Effectiveness Rankings\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        for v, data in sorted(rankings.items()):
            f.write(f"## {v} ({data['total_questions']} questions)\n\n")
            f.write("### Top 5 (highest richness + most dimensions)\n\n")
            f.write("| Rank | Question ID | Mean Richness | Dims Surfaced |\n")
            f.write("|------|-------------|---------------|---------------|\n")
            for i, q in enumerate(data["top_5"]):
                f.write(f"| {i+1} | {q['question_id']} | {q['mean_richness']:.2f} | {q['distinct_dimensions_surfaced']} |\n")

            f.write("\n### Bottom 5 (lowest richness + fewest dimensions)\n\n")
            f.write("| Rank | Question ID | Mean Richness | Dims Surfaced |\n")
            f.write("|------|-------------|---------------|---------------|\n")
            for i, q in enumerate(data["bottom_5"]):
                f.write(f"| {i+1} | {q['question_id']} | {q['mean_richness']:.2f} | {q['distinct_dimensions_surfaced']} |\n")
            f.write("\n")

    log.info(f"  Rankings → {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Coverage Analyser")
    parser.add_argument("--scores", type=str, required=True)
    parser.add_argument("--summaries", type=str, required=True)
    parser.add_argument("--questionnaires", type=str, required=True)
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    scores = load_jsonl(args.scores)
    summaries = load_jsonl(args.summaries)
    log.info(f"Loaded {len(scores)} scores, {len(summaries)} summaries")

    with open(args.plan) as f:
        plan = json.load(f)

    questionnaires = {}
    q_dir = Path(args.questionnaires)
    for v in range(1, 6):
        qf = q_dir / f"Q_V{v}.json"
        if qf.exists():
            with open(qf) as f:
                questionnaires[v] = json.load(f)

    # Analysis 1: Dimension heatmap
    heatmap = build_dimension_heatmap(summaries)
    with open(out / "dimension_heatmap.json", "w") as f:
        json.dump(heatmap, f, indent=2)
    export_heatmap_md(heatmap, out / "dimension_heatmap.md")

    # Analysis 2: Phase coverage
    phase_cov = build_phase_coverage(scores, summaries, plan)
    with open(out / "phase_coverage.json", "w") as f:
        json.dump(phase_cov, f, indent=2)

    # Analysis 3: Blind spots
    blind_spots = identify_blind_spots(heatmap, questionnaires)
    with open(out / "blind_spots.json", "w") as f:
        json.dump(blind_spots, f, indent=2)
    log.info(f"  Blind spots: {len(blind_spots)}")

    # Analysis 4: Question rankings
    rankings = build_question_rankings(scores)
    with open(out / "question_rankings.json", "w") as f:
        json.dump(rankings, f, indent=2)
    export_rankings_md(rankings, out / "question_rankings.md")

    # Console summary
    log.info(f"\n{'='*60}")
    log.info("COVERAGE ANALYSIS SUMMARY")
    log.info(f"{'='*60}")
    for vk in sorted(heatmap.keys()):
        strengths = sum(1 for d in heatmap[vk].values() if d["surfacing_rate"] > 60)
        spots = sum(1 for d in heatmap[vk].values() if d["surfacing_rate"] < 20)
        log.info(f"  {vk}: {strengths} strengths (>60%), {spots} blind spots (<20%)")
    log.info(f"  Total blind spots: {len(blind_spots)}")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()

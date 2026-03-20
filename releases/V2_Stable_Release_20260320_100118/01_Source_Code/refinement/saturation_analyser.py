"""
Saturation Analyser — demonstrates thematic saturation (stopping criterion).
No LLM calls — pure computation on existing scored data.

Usage:
    python -m src.refinement.saturation_analyser \
        --scores data/evaluation/quality_scores.jsonl \
        --refinement-scores data/evaluation/refinement/quality_scores.jsonl \
        --service-maps data/evaluation/service_maps.jsonl \
        --refinement-maps data/evaluation/refinement/service_maps.jsonl \
        --plan data/config/administration_plan.json \
        --refinement-plan data/refinement/refinement_plan.json \
        --output data/evaluation/saturation/
"""
import json, argparse, logging
from pathlib import Path
from collections import defaultdict

from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

CONSECUTIVE_K = 3  # saturation = K consecutive transcripts with 0 new themes


def load_jsonl(path: str) -> list:
    records = []
    p = Path(path)
    if not p.exists():
        return records
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def extract_themes_from_scores(scores: list, session_id: str) -> set:
    """Extract unique thematic elements from quality scores for a session."""
    themes = set()
    session_scores = [s for s in scores if s.get("session_id") == session_id]
    for s in session_scores:
        for dim in s.get("latent_dimensions_surfaced", []):
            themes.add(f"latent:{dim}")
        for kbv in s.get("kbv_dimensions_present", []):
            themes.add(f"kbv:{kbv}")
        for area in s.get("thematic_areas_covered", []):
            themes.add(f"theme:{area}")
    return themes


def extract_themes_from_service_maps(maps: list, session_id: str) -> set:
    """Extract unique thematic elements from service maps for a session."""
    themes = set()
    session_maps = [m for m in maps if m.get("session_id") == session_id]
    for m in session_maps:
        for gap in m.get("gaps", []):
            cat = gap.get("category", gap.get("service_category", ""))
            if cat:
                themes.add(f"gap:{cat}")
        for inno in m.get("innovations", m.get("innovation_opportunities", [])):
            cat = inno.get("category", inno.get("service_category", ""))
            if cat:
                themes.add(f"innovation:{cat}")
    return themes


def analyse_saturation(scores: list, service_maps: list, session_ids: list,
                       refinement_scores: list = None, refinement_maps: list = None,
                       refinement_session_ids: list = None) -> dict:
    """Track cumulative theme emergence across transcripts."""
    cumulative = set()
    marginal_yields = []

    # Original transcripts
    for i, sid in enumerate(session_ids):
        themes = extract_themes_from_scores(scores, sid)
        themes |= extract_themes_from_service_maps(service_maps, sid)
        new_themes = themes - cumulative
        cumulative |= new_themes
        marginal_yields.append({
            "transcript_idx": i + 1,
            "session_id": sid,
            "new_themes": len(new_themes),
            "cumulative": len(cumulative),
            "source": "original",
        })

    # Determine saturation point
    saturation_point = None
    for i in range(len(marginal_yields)):
        if i + CONSECUTIVE_K <= len(marginal_yields):
            window = marginal_yields[i:i + CONSECUTIVE_K]
            if all(w["new_themes"] == 0 for w in window):
                saturation_point = marginal_yields[i]["transcript_idx"]
                break

    pre_refinement_total = len(cumulative)

    # Refinement transcripts
    post_refinement_new = 0
    if refinement_scores and refinement_session_ids:
        for i, sid in enumerate(refinement_session_ids):
            themes = extract_themes_from_scores(refinement_scores, sid)
            if refinement_maps:
                themes |= extract_themes_from_service_maps(refinement_maps, sid)
            new_themes = themes - cumulative
            cumulative |= new_themes
            post_refinement_new += len(new_themes)
            marginal_yields.append({
                "transcript_idx": len(session_ids) + i + 1,
                "session_id": sid,
                "new_themes": len(new_themes),
                "cumulative": len(cumulative),
                "source": "refinement",
            })

    # Per-category saturation
    categories = {"latent_dimensions": set(), "service_gaps": set(), "innovation_opportunities": set(), "kbv_dimensions": set(), "thematic_areas": set()}
    cat_saturation = {}
    for cat_name in categories:
        prefix_map = {"latent_dimensions": "latent:", "service_gaps": "gap:", "innovation_opportunities": "innovation:", "kbv_dimensions": "kbv:", "thematic_areas": "theme:"}
        prefix = prefix_map[cat_name]
        cat_themes = {t for t in cumulative if t.startswith(prefix)}
        cat_saturation[cat_name] = {
            "total_unique": len(cat_themes),
            "saturation_at": None,
        }
        # Find saturation point for this category
        cat_cumulative = set()
        for my in marginal_yields:
            sid = my["session_id"]
            src = my["source"]
            if src == "original":
                all_themes = extract_themes_from_scores(scores, sid) | extract_themes_from_service_maps(service_maps, sid)
            else:
                all_themes = set()
                if refinement_scores:
                    all_themes = extract_themes_from_scores(refinement_scores, sid)
                if refinement_maps:
                    all_themes |= extract_themes_from_service_maps(refinement_maps, sid)
            cat_new = {t for t in all_themes if t.startswith(prefix)} - cat_cumulative
            cat_cumulative |= cat_new
            if not cat_new and cat_saturation[cat_name]["saturation_at"] is None:
                # Check consecutive
                pass  # Simplified: mark first zero

    return {
        "total_transcripts": len(marginal_yields),
        "total_unique_themes": len(cumulative),
        "saturation_point": saturation_point,
        "saturation_reached": saturation_point is not None,
        "marginal_yields": marginal_yields,
        "post_refinement_new_themes": post_refinement_new,
        "pre_refinement_total": pre_refinement_total,
        "theme_categories": cat_saturation,
    }


def generate_report(analysis: dict, version: int) -> str:
    """Generate markdown saturation report."""
    lines = [
        f"# Saturation Analysis Report — V{version}",
        "",
        f"Total transcripts analysed: {analysis['total_transcripts']}",
        f"Total unique themes identified: {analysis['total_unique_themes']}",
        "",
    ]

    if analysis["saturation_reached"]:
        lines.append(f"**Saturation reached at transcript {analysis['saturation_point']}** "
                     f"({CONSECUTIVE_K} consecutive transcripts with zero new themes)")
    else:
        lines.append("**Saturation NOT reached** — new themes were still emerging at the end of the corpus.")
        # Find the last transcript that added themes
        last_new = None
        for my in reversed(analysis["marginal_yields"]):
            if my["new_themes"] > 0:
                last_new = my
                break
        if last_new:
            lines.append(f"Last new theme emerged at transcript {last_new['transcript_idx']} ({last_new['session_id']})")

    lines.extend(["", "## Theme Categories", ""])
    lines.append("| Category | Unique Themes |")
    lines.append("|----------|---------------|")
    for cat, info in analysis["theme_categories"].items():
        lines.append(f"| {cat} | {info['total_unique']} |")

    if analysis["post_refinement_new_themes"] > 0:
        lines.extend([
            "", "## Post-Refinement Findings", "",
            f"The refinement round introduced **{analysis['post_refinement_new_themes']}** new themes",
            f"not observed in the original {analysis['pre_refinement_total']} themes.",
            "This suggests the refined instrument accessed previously untapped dimensions.",
        ])
    elif analysis.get("post_refinement_new_themes") == 0 and analysis.get("pre_refinement_total"):
        lines.extend([
            "", "## Post-Refinement Findings", "",
            "The refinement round introduced **zero new themes**.",
            "This confirms thematic saturation — the original instrument had already",
            "captured the full thematic space for this population.",
        ])

    lines.extend(["", "## Marginal Yield Trajectory", ""])
    lines.append("| Transcript | Session | New Themes | Cumulative | Source |")
    lines.append("|------------|---------|------------|------------|--------|")
    for my in analysis["marginal_yields"][:20]:
        lines.append(f"| {my['transcript_idx']} | {my['session_id']} | {my['new_themes']} | {my['cumulative']} | {my['source']} |")
    if len(analysis["marginal_yields"]) > 20:
        lines.append(f"| ... | ... | ... | ... | ... |")
        for my in analysis["marginal_yields"][-5:]:
            lines.append(f"| {my['transcript_idx']} | {my['session_id']} | {my['new_themes']} | {my['cumulative']} | {my['source']} |")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Saturation Analyser")
    parser.add_argument("--scores", type=str, required=True)
    parser.add_argument("--refinement-scores", type=str, default="")
    parser.add_argument("--service-maps", type=str, required=True)
    parser.add_argument("--refinement-maps", type=str, default="")
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--refinement-plan", type=str, default="")
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    run = TimestampedRun(args.output)
    run.record_read(args.scores)
    run.record_read(args.service_maps)
    run.record_read(args.plan)

    scores = load_jsonl(args.scores)
    service_maps = load_jsonl(args.service_maps)

    with open(args.plan) as f:
        admin_plan = json.load(f)

    # Determine winner version from refinement plan
    version = None
    if args.refinement_plan and Path(args.refinement_plan).exists():
        run.record_read(args.refinement_plan)
        with open(args.refinement_plan) as f:
            ref_plan = json.load(f)
        version = ref_plan.get("winner", {}).get("version")

    if version is None:
        # Fallback: use most common version in scores
        from collections import Counter
        vcounts = Counter()
        summaries = load_jsonl(str(Path(args.scores).parent / "transcript_summaries.jsonl"))
        for s in summaries:
            vcounts[s.get("questionnaire_version")] += 1
        version = vcounts.most_common(1)[0][0] if vcounts else 1

    # Get session IDs for this version, ordered
    summaries = load_jsonl(str(Path(args.scores).parent / "transcript_summaries.jsonl"))
    version_sessions = sorted(
        [s["session_id"] for s in summaries if s.get("questionnaire_version") == version],
        key=lambda x: int(x.replace("S_", "").replace("S_R", "1000"))
    )
    log.info(f"Analysing saturation for V{version} ({len(version_sessions)} original sessions)")

    # Load refinement data if available
    refinement_scores = load_jsonl(args.refinement_scores) if args.refinement_scores else []
    refinement_maps = load_jsonl(args.refinement_maps) if args.refinement_maps else []
    refinement_session_ids = sorted({s["session_id"] for s in refinement_scores}) if refinement_scores else []

    if refinement_scores:
        run.record_read(args.refinement_scores)
        log.info(f"Including {len(refinement_session_ids)} refinement sessions")
    if refinement_maps:
        run.record_read(args.refinement_maps)

    analysis = analyse_saturation(
        scores, service_maps, version_sessions,
        refinement_scores, refinement_maps, refinement_session_ids,
    )
    analysis["run_timestamp"] = run.timestamp
    analysis["version"] = version

    # Write analysis
    analysis_path = run.output_path("saturation_analysis.json")
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    run.stable_pointer("saturation_analysis.json", analysis_path)

    # Write curve data
    curve_data = [{"x": my["transcript_idx"], "y": my["cumulative"]} for my in analysis["marginal_yields"]]
    curve_path = run.output_path("saturation_curve_data.json")
    with open(curve_path, "w") as f:
        json.dump(curve_data, f, indent=2)
    run.stable_pointer("saturation_curve_data.json", curve_path)

    # Write report
    report = generate_report(analysis, version)
    report_path = run.output_path("saturation_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    run.stable_pointer("saturation_report.md", report_path)

    run.write_manifest("saturation_analyser", config={"version": version})

    log.info(f"Unique themes: {analysis['total_unique_themes']}")
    log.info(f"Saturation reached: {analysis['saturation_reached']}")
    if analysis["saturation_reached"]:
        log.info(f"Saturation point: transcript {analysis['saturation_point']}")
    if refinement_scores:
        log.info(f"Post-refinement new themes: {analysis['post_refinement_new_themes']}")
    log.info(f"Report → {report_path}")


if __name__ == "__main__":
    main()

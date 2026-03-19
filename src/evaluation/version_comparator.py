"""
Version Comparator — statistical comparison across 5 questionnaire versions.
No LLM calls — pure computation on evaluation outputs.

Usage:
    python -m src.evaluation.version_comparator \
        --scores data/evaluation/transcript_summaries.jsonl \
        --coverage data/evaluation/dimension_heatmap.json \
        --gaps data/evaluation/service_aggregate.json \
        --plan data/config/administration_plan.json \
        --output data/evaluation/
"""
import json, argparse, logging, math
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

# BIBD group structure
GROUP_PAIRS = {
    "A": (1, 2), "B": (1, 3), "C": (2, 4), "D": (3, 5), "E": (4, 5),
}


def load_jsonl(path: str) -> list:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def mean(vals):
    return sum(vals) / max(len(vals), 1)


def std(vals):
    if len(vals) < 2:
        return 0
    m = mean(vals)
    return math.sqrt(sum((x - m) ** 2 for x in vals) / (len(vals) - 1))


def ci_95(vals):
    n = len(vals)
    if n < 2:
        return (0, 0)
    m = mean(vals)
    se = std(vals) / math.sqrt(n)
    return (round(m - 1.96 * se, 3), round(m + 1.96 * se, 3))


def cohens_d(vals1, vals2):
    n1, n2 = len(vals1), len(vals2)
    if n1 < 2 or n2 < 2:
        return 0
    m1, m2 = mean(vals1), mean(vals2)
    s1, s2 = std(vals1), std(vals2)
    pooled = math.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
    if pooled == 0:
        return 0
    return round((m1 - m2) / pooled, 3)


def kruskal_wallis_h(groups):
    """Compute Kruskal-Wallis H statistic (simplified)."""
    all_vals = []
    for g in groups:
        for v in g:
            all_vals.append(v)
    n = len(all_vals)
    if n < 2:
        return 0, 1.0

    # Rank all values
    sorted_vals = sorted(range(n), key=lambda i: all_vals[i])
    ranks = [0] * n
    for rank, idx in enumerate(sorted_vals):
        ranks[idx] = rank + 1

    # Split ranks back into groups
    idx = 0
    group_ranks = []
    for g in groups:
        gr = ranks[idx:idx + len(g)]
        group_ranks.append(gr)
        idx += len(g)

    # H statistic
    k = len(groups)
    h = (12 / (n * (n + 1))) * sum(
        len(gr) * (mean(gr) - (n + 1) / 2) ** 2
        for gr in group_ranks
    )

    # Approximate p-value using chi-square with k-1 df
    # Very rough approximation
    df = k - 1
    p = max(0.001, 1 - _chi2_cdf(h, df)) if h > 0 else 1.0

    return round(h, 3), round(p, 4)


def _chi2_cdf(x, df):
    """Very rough chi-square CDF approximation."""
    if x <= 0:
        return 0
    # Wilson-Hilferty approximation
    z = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def wilcoxon_signed_rank(diffs):
    """Simplified Wilcoxon signed-rank test."""
    diffs = [d for d in diffs if d != 0]
    n = len(diffs)
    if n < 5:
        return 0, 1.0

    abs_diffs = [(abs(d), d) for d in diffs]
    abs_diffs.sort(key=lambda x: x[0])

    w_plus = sum(i + 1 for i, (_, d) in enumerate(abs_diffs) if d > 0)
    w_minus = sum(i + 1 for i, (_, d) in enumerate(abs_diffs) if d < 0)
    w = min(w_plus, w_minus)

    # Normal approximation for n >= 10
    mu = n * (n + 1) / 4
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    if sigma == 0:
        return w, 1.0
    z = (w - mu) / sigma
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return round(z, 3), round(p, 4)


def quality_comparison(summaries: list) -> dict:
    """Analysis 1: Quality score comparison across versions."""
    by_version = defaultdict(list)
    for s in summaries:
        by_version[s.get("questionnaire_version", 0)].append(s)

    dims = ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]
    comparison = {}

    for v in sorted(by_version.keys()):
        vk = f"V{v}"
        transcripts = by_version[v]
        richness_vals = [t.get("mean_composite_richness", 0) for t in transcripts]
        surfacing_vals = [t.get("surfacing_rate", 0) for t in transcripts]

        dim_vals = {}
        for d in dims:
            vals = [t.get("mean_scores", {}).get(d, 0) for t in transcripts]
            dim_vals[d] = {
                "mean": round(mean(vals), 2),
                "std": round(std(vals), 2),
                "ci_95": ci_95(vals),
            }

        comparison[vk] = {
            "n": len(transcripts),
            "composite_richness": {
                "mean": round(mean(richness_vals), 2),
                "std": round(std(richness_vals), 2),
                "ci_95": ci_95(richness_vals),
            },
            "surfacing_rate": {
                "mean": round(mean(surfacing_vals), 3),
                "std": round(std(surfacing_vals), 3),
            },
            "dimensions": dim_vals,
        }

    # Kruskal-Wallis across versions
    groups = [
        [t.get("mean_composite_richness", 0) for t in by_version[v]]
        for v in sorted(by_version.keys())
    ]
    h_stat, p_val = kruskal_wallis_h(groups)

    # Pairwise effect sizes
    versions = sorted(by_version.keys())
    pairwise = {}
    for i, v1 in enumerate(versions):
        for v2 in versions[i + 1:]:
            vals1 = [t.get("mean_composite_richness", 0) for t in by_version[v1]]
            vals2 = [t.get("mean_composite_richness", 0) for t in by_version[v2]]
            d = cohens_d(vals1, vals2)
            pairwise[f"V{v1}_vs_V{v2}"] = {"cohens_d": d, "interpretation": "small" if abs(d) < 0.5 else "medium" if abs(d) < 0.8 else "large"}

    return {
        "version_stats": comparison,
        "kruskal_wallis": {"H": h_stat, "p": p_val, "significant": p_val < 0.05},
        "pairwise_effect_sizes": pairwise,
    }


def within_subject_comparison(summaries: list, plan: list) -> dict:
    """Analysis 2: Within-subject comparison using BIBD structure."""
    # Map persona_id → session summaries
    by_persona = defaultdict(list)
    for s in summaries:
        by_persona[s.get("persona_id", "")].append(s)

    # Map session → group
    session_group = {}
    for p in plan:
        session_group[p["session_id"]] = p.get("group", "")

    results = {}
    for group, (v1, v2) in GROUP_PAIRS.items():
        diffs = []
        for pid, sessions in by_persona.items():
            s_v1 = [s for s in sessions if s.get("questionnaire_version") == v1]
            s_v2 = [s for s in sessions if s.get("questionnaire_version") == v2]
            if s_v1 and s_v2:
                r1 = s_v1[0].get("mean_composite_richness", 0)
                r2 = s_v2[0].get("mean_composite_richness", 0)
                diffs.append(r1 - r2)

        if diffs:
            z, p = wilcoxon_signed_rank(diffs)
            results[f"Group_{group}_V{v1}_vs_V{v2}"] = {
                "n_pairs": len(diffs),
                "mean_diff": round(mean(diffs), 3),
                "std_diff": round(std(diffs), 3),
                "wilcoxon_z": z,
                "p_value": p,
                "significant": p < 0.05,
                "favours": f"V{v1}" if mean(diffs) > 0 else f"V{v2}",
            }

    return results


def dimension_coverage_comparison(heatmap: dict) -> dict:
    """Analysis 3: Dimension coverage comparison."""
    result = {}
    for vk, dims in sorted(heatmap.items()):
        strengths = sum(1 for d in dims.values() if d.get("surfacing_rate", 0) > 60)
        blind_spots = sum(1 for d in dims.values() if d.get("surfacing_rate", 0) < 20)
        mean_rate = round(mean([d.get("surfacing_rate", 0) for d in dims.values()]), 1)
        result[vk] = {
            "strengths": strengths,
            "blind_spots": blind_spots,
            "mean_surfacing_rate": mean_rate,
        }
    return result


def gap_yield_comparison(aggregate: dict) -> dict:
    """Analysis 4: Service gap yield comparison."""
    return aggregate.get("version_comparison", {})


def interaction_effects(summaries: list) -> dict:
    """Analysis 5: Version × stage and version × risk interactions."""
    # Version × stage
    cells_stage = defaultdict(list)
    cells_risk = defaultdict(list)
    for s in summaries:
        v = s.get("questionnaire_version", 0)
        stage = s.get("persona_journey_stage", "unknown")
        risk = s.get("persona_risk_level", "unknown")
        r = s.get("mean_composite_richness", 0)
        cells_stage[(v, stage)].append(r)
        cells_risk[(v, risk)].append(r)

    stage_effects = {}
    for (v, stage), vals in sorted(cells_stage.items()):
        key = f"V{v}_{stage}"
        stage_effects[key] = {"mean": round(mean(vals), 2), "n": len(vals)}

    risk_effects = {}
    for (v, risk), vals in sorted(cells_risk.items()):
        key = f"V{v}_{risk}"
        risk_effects[key] = {"mean": round(mean(vals), 2), "n": len(vals)}

    return {"version_x_stage": stage_effects, "version_x_risk": risk_effects}


def version_ranking(quality: dict, dim_coverage: dict, gap_yield: dict) -> dict:
    """Compute weighted composite ranking."""
    rankings = {}
    for vk in sorted(quality.get("version_stats", {}).keys()):
        q = quality["version_stats"][vk]
        dc = dim_coverage.get(vk, {})
        gy = gap_yield.get(vk, {})

        quality_score = q.get("composite_richness", {}).get("mean", 0)
        coverage_score = dc.get("mean_surfacing_rate", 0) / 100
        innovation_score = (gy.get("total_gaps", 0) + gy.get("total_innovations", 0)) / max(q.get("n", 1), 1)
        # Breadth: coverage of journey phases (rough proxy)
        breadth_score = (12 - dc.get("blind_spots", 0)) / 12

        composite = (
            quality_score * 0.40 +
            coverage_score * 5 * 0.25 +
            min(innovation_score, 5) * 0.20 +
            breadth_score * 5 * 0.15
        )

        rankings[vk] = {
            "quality_score": round(quality_score, 2),
            "coverage_score": round(coverage_score, 3),
            "innovation_score": round(innovation_score, 2),
            "breadth_score": round(breadth_score, 2),
            "composite": round(composite, 3),
        }

    # Rank
    ranked = sorted(rankings.items(), key=lambda x: -x[1]["composite"])
    for i, (vk, data) in enumerate(ranked):
        data["rank"] = i + 1

    return dict(ranked)


def export_comparison_md(quality: dict, within: dict, ranking: dict, output_path: Path):
    """Export comparison results as markdown."""
    with open(output_path, "w") as f:
        f.write("# Version Quality Comparison\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        # Table 1: Quality scores
        f.write("## Quality Scores by Version\n\n")
        f.write("| Version | N | Richness (mean) | SD | 95% CI | Surfacing Rate |\n")
        f.write("|---------|---|-----------------|-----|--------|----------------|\n")
        for vk, data in sorted(quality.get("version_stats", {}).items()):
            r = data["composite_richness"]
            sr = data["surfacing_rate"]
            f.write(f"| {vk} | {data['n']} | {r['mean']:.2f} | {r['std']:.2f} | "
                    f"({r['ci_95'][0]:.2f}, {r['ci_95'][1]:.2f}) | {sr['mean']:.1%} |\n")

        kw = quality.get("kruskal_wallis", {})
        f.write(f"\nKruskal-Wallis H = {kw.get('H', 0):.3f}, p = {kw.get('p', 1):.4f}")
        f.write(f" {'(significant)' if kw.get('significant') else '(not significant)'}\n\n")

        # Within-subject
        f.write("## Within-Subject Comparison (BIBD)\n\n")
        f.write("| Group | Comparison | N pairs | Mean diff | Wilcoxon Z | p-value | Favours |\n")
        f.write("|-------|------------|---------|-----------|------------|---------|--------|\n")
        for key, data in sorted(within.items()):
            parts = key.split("_")
            group = parts[1]
            comp = "_".join(parts[2:])
            sig = " *" if data.get("significant") else ""
            f.write(f"| {group} | {comp} | {data['n_pairs']} | {data['mean_diff']:.3f} | "
                    f"{data['wilcoxon_z']:.3f} | {data['p_value']:.4f}{sig} | {data['favours']} |\n")

        # Ranking
        f.write("\n## Version Ranking\n\n")
        f.write("| Rank | Version | Quality (40%) | Coverage (25%) | Innovation (20%) | Breadth (15%) | Composite |\n")
        f.write("|------|---------|---------------|----------------|------------------|---------------|----------|\n")
        for vk, data in sorted(ranking.items(), key=lambda x: x[1]["rank"]):
            f.write(f"| {data['rank']} | {vk} | {data['quality_score']:.2f} | "
                    f"{data['coverage_score']:.3f} | {data['innovation_score']:.2f} | "
                    f"{data['breadth_score']:.2f} | {data['composite']:.3f} |\n")

    log.info(f"  Comparison → {output_path}")


def export_ranking_md(ranking: dict, output_path: Path):
    """Export version ranking as markdown."""
    with open(output_path, "w") as f:
        f.write("# Version Ranking\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        ranked = sorted(ranking.items(), key=lambda x: x[1]["rank"])
        best = ranked[0]

        f.write(f"**Recommended version: {best[0]}** (composite score: {best[1]['composite']:.3f})\n\n")

        for vk, data in ranked:
            f.write(f"## #{data['rank']}: {vk}\n")
            f.write(f"- Quality: {data['quality_score']:.2f}/5\n")
            f.write(f"- Coverage: {data['coverage_score']:.1%}\n")
            f.write(f"- Innovation yield: {data['innovation_score']:.2f}\n")
            f.write(f"- Breadth: {data['breadth_score']:.0%}\n")
            f.write(f"- **Composite: {data['composite']:.3f}**\n\n")

    log.info(f"  Ranking → {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Version Comparator")
    parser.add_argument("--scores", type=str, required=True)
    parser.add_argument("--coverage", type=str, required=True)
    parser.add_argument("--gaps", type=str, required=True)
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    summaries = load_jsonl(args.scores)
    with open(args.coverage) as f:
        heatmap = json.load(f)
    with open(args.gaps) as f:
        aggregate = json.load(f)
    with open(args.plan) as f:
        plan = json.load(f)

    log.info(f"Loaded {len(summaries)} summaries")

    # Analysis 1
    quality = quality_comparison(summaries)
    with open(out / "version_quality_comparison.json", "w") as f:
        json.dump(quality, f, indent=2)

    # Analysis 2
    within = within_subject_comparison(summaries, plan)
    with open(out / "within_subject_comparison.json", "w") as f:
        json.dump(within, f, indent=2)

    # Analysis 3
    dim_cov = dimension_coverage_comparison(heatmap)
    with open(out / "dimension_coverage_comparison.json", "w") as f:
        json.dump(dim_cov, f, indent=2)

    # Analysis 4
    gap_y = gap_yield_comparison(aggregate)
    with open(out / "gap_yield_comparison.json", "w") as f:
        json.dump(gap_y, f, indent=2)

    # Analysis 5
    interactions = interaction_effects(summaries)
    with open(out / "interaction_effects.json", "w") as f:
        json.dump(interactions, f, indent=2)

    # Ranking
    ranking = version_ranking(quality, dim_cov, gap_y)
    with open(out / "version_ranking.json", "w") as f:
        json.dump(ranking, f, indent=2)

    # Markdown exports
    export_comparison_md(quality, within, ranking, out / "version_quality_comparison.md")
    export_ranking_md(ranking, out / "version_ranking.md")

    # Interaction effects markdown
    with open(out / "interaction_effects.md", "w") as f:
        f.write("# Interaction Effects\n\n")
        f.write("## Version x Journey Stage\n\n")
        f.write("| Cell | Mean Richness | N |\n|------|---------------|---|\n")
        for key, data in sorted(interactions["version_x_stage"].items()):
            f.write(f"| {key} | {data['mean']:.2f} | {data['n']} |\n")
        f.write("\n## Version x Risk Level\n\n")
        f.write("| Cell | Mean Richness | N |\n|------|---------------|---|\n")
        for key, data in sorted(interactions["version_x_risk"].items()):
            f.write(f"| {key} | {data['mean']:.2f} | {data['n']} |\n")

    # Console
    log.info(f"\n{'='*60}")
    log.info("VERSION COMPARISON SUMMARY")
    log.info(f"{'='*60}")
    for vk, data in sorted(ranking.items(), key=lambda x: x[1]["rank"]):
        log.info(f"  #{data['rank']} {vk}: composite={data['composite']:.3f} "
                 f"(quality={data['quality_score']:.2f}, coverage={data['coverage_score']:.3f})")
    kw = quality.get("kruskal_wallis", {})
    log.info(f"  Kruskal-Wallis H={kw.get('H', 0):.3f}, p={kw.get('p', 1):.4f}")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()

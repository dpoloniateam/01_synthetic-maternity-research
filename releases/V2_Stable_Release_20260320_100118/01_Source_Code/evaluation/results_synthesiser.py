"""
Results Synthesiser — paper-ready outputs from all evaluation modules.
No LLM calls — pure aggregation and formatting.

Produces:
  - Executive summary (markdown)
  - Paper tables (LaTeX-ready and markdown)
  - Figure data JSONs (for plotting)
  - Results narrative draft (markdown)

Usage:
    python -m src.evaluation.results_synthesiser \
        --eval-dir data/evaluation/ \
        --plan data/config/administration_plan.json \
        --output data/evaluation/synthesis/
"""
import json, argparse, logging, math
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)


def load_jsonl(path: Path) -> list:
    records = []
    if not path.exists():
        return records
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


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


# ─── Load all evaluation outputs ────────────────────────────────────────────

def load_all(eval_dir: Path) -> dict:
    """Load all evaluation artefacts into a single dict."""
    data = {}
    data["scoring_summary"] = load_json(eval_dir / "scoring_summary.json")
    data["summaries"] = load_jsonl(eval_dir / "transcript_summaries.jsonl")
    data["scores"] = load_jsonl(eval_dir / "quality_scores.jsonl")
    data["dimension_heatmap"] = load_json(eval_dir / "dimension_heatmap.json")
    data["phase_coverage"] = load_json(eval_dir / "phase_coverage.json")
    data["blind_spots"] = load_json(eval_dir / "blind_spots.json") if (eval_dir / "blind_spots.json").exists() else []
    data["question_rankings"] = load_json(eval_dir / "question_rankings.json")
    data["service_aggregate"] = load_json(eval_dir / "service_aggregate.json")
    data["gap_heatmap"] = load_json(eval_dir / "gap_heatmap.json")
    data["version_quality"] = load_json(eval_dir / "version_quality_comparison.json")
    data["within_subject"] = load_json(eval_dir / "within_subject_comparison.json")
    data["version_ranking"] = load_json(eval_dir / "version_ranking.json")
    data["interaction_effects"] = load_json(eval_dir / "interaction_effects.json")
    data["inter_rater"] = load_json(eval_dir / "inter_rater_agreement.json")
    return data


# ─── Executive Summary ──────────────────────────────────────────────────────

def build_executive_summary(data: dict, plan: list) -> str:
    """Generate executive summary markdown."""
    ss = data["scoring_summary"]
    summaries = data["summaries"]
    vq = data["version_quality"]
    ranking = data["version_ranking"]
    ir = data["inter_rater"]
    sa = data["service_aggregate"]

    n_transcripts = ss.get("total_transcripts", len(summaries))
    n_responses = ss.get("total_responses_scored", 0)
    mean_richness = ss.get("mean_composite_richness", 0)
    mean_surf = ss.get("mean_surfacing_rate", 0)

    # Best version
    best_v = None
    best_score = -1
    for vk, rd in ranking.items():
        if rd.get("composite", 0) > best_score:
            best_score = rd["composite"]
            best_v = vk

    # Kruskal-Wallis
    kw = vq.get("kruskal_wallis", {})

    # ICC
    comp_icc = ir.get("composite_richness", {}).get("icc", "N/A")
    comp_interp = ir.get("composite_richness", {}).get("interpretation", "N/A")

    # Gaps & innovations
    total_gaps = sa.get("total_transcripts", 0)  # used as proxy
    gap_cats = sa.get("gap_severity_distribution", {})
    inn_cats = sa.get("innovation_categories", {})
    total_innovations = sum(inn_cats.values()) if inn_cats else 0
    total_gap_count = sum(
        sum(sev.values()) for sev in gap_cats.values()
    ) if gap_cats else 0

    lines = [
        "# Executive Summary: Synthetic Maternity Care Interview Study",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Study Design",
        "",
        f"- **Design:** Balanced Incomplete Block Design (BIBD) with 5 questionnaire versions",
        f"- **Participants:** {len(set(s.get('persona_id','') for s in summaries))} composite synthetic personas",
        f"- **Sessions:** {n_transcripts} interviews across 5 BIBD groups",
        f"- **Administration:** Each persona answered 2 of 5 versions (within-subject comparison)",
        "",
        "## Key Findings",
        "",
        "### 1. Response Quality",
        "",
        f"- **Mean composite richness:** {mean_richness:.2f}/5.0",
        f"- **Mean latent dimension surfacing rate:** {mean_surf:.1%}",
        f"- **Total responses scored:** {n_responses}",
    ]

    # Per-dimension means
    global_means = ss.get("mean_scores_global", {})
    if global_means:
        lines.append("")
        lines.append("| Dimension | Mean Score |")
        lines.append("|-----------|-----------|")
        for dim, val in sorted(global_means.items()):
            lines.append(f"| {dim.replace('_',' ').title()} | {val:.2f}/5 |")

    lines.extend([
        "",
        "### 2. Version Comparison",
        "",
        f"- **Kruskal-Wallis H:** {kw.get('H', 'N/A')}, p = {kw.get('p', 'N/A')}",
        f"- **Significant difference:** {'Yes' if kw.get('significant') else 'No'}",
    ])

    if best_v:
        lines.append(f"- **Top-ranked version:** {best_v} (composite = {best_score:.3f})")

    # Version ranking table
    if ranking:
        lines.extend(["", "| Rank | Version | Quality | Coverage | Innovation | Composite |",
                       "|------|---------|---------|----------|------------|-----------|"])
        for vk, rd in sorted(ranking.items(), key=lambda x: x[1].get("rank", 99)):
            lines.append(f"| {rd.get('rank','-')} | {vk} | {rd.get('quality_score',0):.2f} | "
                         f"{rd.get('coverage_score',0):.3f} | {rd.get('innovation_score',0):.2f} | "
                         f"{rd.get('composite',0):.3f} |")

    lines.extend([
        "",
        "### 3. Inter-Rater Reliability",
        "",
        f"- **Composite ICC(2,1):** {comp_icc} ({comp_interp})",
    ])

    # Per-dim ICC
    dims_with_issues = []
    for dim in ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]:
        d = ir.get(dim, {})
        icc_val = d.get("icc", "N/A")
        if isinstance(icc_val, (int, float)) and icc_val < 0.60:
            dims_with_issues.append(dim)
    if dims_with_issues:
        lines.append(f"- **Dimensions below good agreement:** {', '.join(dims_with_issues)}")
    else:
        lines.append("- All dimensions show adequate inter-rater agreement (ICC >= 0.60)")

    lines.extend([
        "",
        "### 4. Service Mapping",
        "",
        f"- **Service gaps identified:** {total_gap_count}",
        f"- **Innovation opportunities:** {total_innovations}",
    ])

    # Top innovation categories
    if inn_cats:
        top_3 = sorted(inn_cats.items(), key=lambda x: -x[1])[:3]
        lines.append("- **Top innovation areas:** " + ", ".join(
            f"{cat.replace('_',' ').title()} ({n})" for cat, n in top_3))

    # Blind spots
    blind = data.get("blind_spots", [])
    if isinstance(blind, list) and blind:
        lines.extend([
            "",
            "### 5. Coverage Gaps",
            "",
            f"- **Total blind spots (surfacing < 20%):** {len(blind)}",
        ])
        worst = blind[:3]
        for b in worst:
            lines.append(f"  - V{b.get('version','?')}/{b.get('dimension','?')}: "
                         f"{b.get('surfacing_rate',0):.1f}%")

    lines.extend([
        "",
        "## Methodological Notes",
        "",
        "- All transcripts were generated using synthetic personas created from Synthea EHR data + HuggingFace FinePersonas",
        "- Quality scoring used LLM-as-judge methodology across 5 dimensions",
        "- Inter-rater reliability verified with 3 independent LLM providers",
        "- BIBD design ensures balanced version comparison with within-subject controls",
        "",
        "---",
        f"*Report generated by results_synthesiser.py on {datetime.now().strftime('%Y-%m-%d')}*",
    ])

    return "\n".join(lines)


# ─── Paper Tables ────────────────────────────────────────────────────────────

def build_paper_tables(data: dict) -> dict:
    """Generate paper-ready tables as both markdown and LaTeX."""
    tables = {}

    # Table 1: Quality Scores by Version
    vq = data.get("version_quality", {})
    vs = vq.get("version_stats", {})
    if vs:
        md = ["| Version | N | Richness M(SD) | 95% CI | Surfacing Rate |",
              "|---------|---|----------------|--------|----------------|"]
        latex = [
            r"\begin{table}[h]",
            r"\caption{Quality scores by questionnaire version}",
            r"\begin{tabular}{lcccc}",
            r"\hline",
            r"Version & N & Richness M(SD) & 95\% CI & Surfacing Rate \\",
            r"\hline",
        ]
        for vk, d in sorted(vs.items()):
            r = d.get("composite_richness", {})
            sr = d.get("surfacing_rate", {})
            md.append(f"| {vk} | {d['n']} | {r.get('mean',0):.2f} ({r.get('std',0):.2f}) | "
                      f"({r.get('ci_95',(0,0))[0]:.2f}, {r.get('ci_95',(0,0))[1]:.2f}) | "
                      f"{sr.get('mean',0):.1%} |")
            latex.append(f"{vk} & {d['n']} & {r.get('mean',0):.2f} ({r.get('std',0):.2f}) & "
                         f"({r.get('ci_95',(0,0))[0]:.2f}, {r.get('ci_95',(0,0))[1]:.2f}) & "
                         f"{sr.get('mean',0):.1%} \\\\")
        latex.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
        tables["table1_quality_by_version"] = {"markdown": "\n".join(md), "latex": "\n".join(latex)}

    # Table 2: Pairwise Effect Sizes
    pairwise = vq.get("pairwise_effect_sizes", {})
    if pairwise:
        md = ["| Comparison | Cohen's d | Interpretation |",
              "|------------|-----------|----------------|"]
        for pair, d in sorted(pairwise.items()):
            md.append(f"| {pair.replace('_', ' ')} | {d.get('cohens_d',0):.3f} | {d.get('interpretation','?')} |")
        tables["table2_pairwise_effects"] = {"markdown": "\n".join(md)}

    # Table 3: Within-Subject Comparison (BIBD)
    within = data.get("within_subject", {})
    if within:
        md = ["| Group | Comparison | N | Mean Diff | Wilcoxon Z | p | Favours |",
              "|-------|------------|---|-----------|------------|---|---------|"]
        for key, d in sorted(within.items()):
            sig = "*" if d.get("significant") else ""
            md.append(f"| {key.split('_')[1]} | {'_'.join(key.split('_')[2:])} | "
                      f"{d['n_pairs']} | {d['mean_diff']:.3f} | {d['wilcoxon_z']:.3f} | "
                      f"{d['p_value']:.4f}{sig} | {d['favours']} |")
        tables["table3_within_subject"] = {"markdown": "\n".join(md)}

    # Table 4: Inter-Rater Reliability
    ir = data.get("inter_rater", {})
    if ir:
        md = ["| Dimension | ICC(2,1) | Interpretation | Krippendorff alpha |",
              "|-----------|----------|----------------|-------------------|"]
        for dim in ["emotional_depth", "specificity", "latent_surfacing",
                     "narrative_quality", "clinical_grounding", "composite_richness"]:
            d = ir.get(dim, {})
            md.append(f"| {dim.replace('_',' ').title()} | {d.get('icc','N/A')} | "
                      f"{d.get('interpretation','N/A')} | {d.get('krippendorff_alpha','N/A')} |")
        tables["table4_inter_rater"] = {"markdown": "\n".join(md)}

    # Table 5: Dimension Surfacing Heatmap
    hm = data.get("dimension_heatmap", {})
    if hm:
        versions = sorted(hm.keys())
        header = "| Dimension |" + "|".join(f" {v} " for v in versions) + "|"
        sep = "|-----------|" + "|".join("------" for _ in versions) + "|"
        md = [header, sep]
        all_dims = sorted(set(d for v in hm.values() for d in v.keys()))
        for dim in all_dims:
            row = f"| {dim.replace('_',' ').title()[:25]} |"
            for v in versions:
                rate = hm.get(v, {}).get(dim, {}).get("surfacing_rate", 0)
                row += f" {rate:5.1f}% |"
            md.append(row)
        tables["table5_dimension_heatmap"] = {"markdown": "\n".join(md)}

    return tables


# ─── Figure Data ─────────────────────────────────────────────────────────────

def build_figure_data(data: dict) -> dict:
    """Generate JSON datasets for plotting."""
    figures = {}

    # Figure 1: Box plot data — richness by version
    summaries = data.get("summaries", [])
    by_version = defaultdict(list)
    for s in summaries:
        v = s.get("questionnaire_version", 0)
        by_version[v].append(s.get("mean_composite_richness", 0))

    fig1 = {}
    for v in sorted(by_version.keys()):
        vals = sorted(by_version[v])
        n = len(vals)
        fig1[f"V{v}"] = {
            "values": vals,
            "n": n,
            "min": vals[0] if vals else 0,
            "q1": vals[n // 4] if n >= 4 else (vals[0] if vals else 0),
            "median": vals[n // 2] if vals else 0,
            "q3": vals[3 * n // 4] if n >= 4 else (vals[-1] if vals else 0),
            "max": vals[-1] if vals else 0,
            "mean": round(mean(vals), 3),
        }
    figures["fig1_richness_boxplot"] = fig1

    # Figure 2: Radar chart — dimension scores by version
    vq = data.get("version_quality", {}).get("version_stats", {})
    fig2 = {}
    dims = ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]
    for vk, vdata in sorted(vq.items()):
        fig2[vk] = {dim: vdata.get("dimensions", {}).get(dim, {}).get("mean", 0) for dim in dims}
    figures["fig2_dimension_radar"] = fig2

    # Figure 3: Heatmap — surfacing rate (version × dimension)
    figures["fig3_surfacing_heatmap"] = data.get("dimension_heatmap", {})

    # Figure 4: Gap severity distribution
    gap_sev = data.get("service_aggregate", {}).get("gap_severity_distribution", {})
    figures["fig4_gap_severity"] = gap_sev

    # Figure 5: Innovation categories bar chart
    inn_cats = data.get("service_aggregate", {}).get("innovation_categories", {})
    figures["fig5_innovation_categories"] = inn_cats

    # Figure 6: Interaction effects — version x stage
    ie = data.get("interaction_effects", {}).get("version_x_stage", {})
    figures["fig6_version_x_stage"] = ie

    # Figure 7: Interaction effects — version x risk
    ir = data.get("interaction_effects", {}).get("version_x_risk", {})
    figures["fig7_version_x_risk"] = ir

    # Figure 8: Phase coverage heatmap
    figures["fig8_phase_coverage"] = data.get("phase_coverage", {})

    return figures


# ─── Results Narrative ───────────────────────────────────────────────────────

def build_results_narrative(data: dict) -> str:
    """Generate a results section draft in academic style."""
    ss = data.get("scoring_summary", {})
    vq = data.get("version_quality", {})
    ranking = data.get("version_ranking", {})
    within = data.get("within_subject", {})
    ir = data.get("inter_rater", {})
    sa = data.get("service_aggregate", {})
    blind = data.get("blind_spots", [])
    summaries = data.get("summaries", [])

    n = ss.get("total_transcripts", len(summaries))
    n_resp = ss.get("total_responses_scored", 0)
    mean_r = ss.get("mean_composite_richness", 0)
    mean_surf = ss.get("mean_surfacing_rate", 0)
    global_means = ss.get("mean_scores_global", {})

    lines = [
        "# Results",
        "",
        "## 3.1 Descriptive Statistics",
        "",
        f"A total of {n} synthetic interview transcripts were generated and scored, "
        f"yielding {n_resp} question-response pairs for quality evaluation. "
        f"The overall mean composite richness score was {mean_r:.2f} (SD = {std([s.get('mean_composite_richness',0) for s in summaries]):.2f}) "
        f"on a 0-5 scale. The mean latent dimension surfacing rate across all "
        f"transcripts was {mean_surf:.1%}.",
        "",
    ]

    # Dimension breakdown
    if global_means:
        dim_text = []
        for dim in ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]:
            v = global_means.get(dim, 0)
            dim_text.append(f"{dim.replace('_',' ')} (M = {v:.2f})")
        lines.append("Across the five quality dimensions, mean scores were: " + ", ".join(dim_text) + ".")
        lines.append("")

    # Version comparison
    kw = vq.get("kruskal_wallis", {})
    lines.extend([
        "## 3.2 Cross-Version Comparison",
        "",
    ])

    vs = vq.get("version_stats", {})
    if vs:
        parts = []
        for vk, d in sorted(vs.items()):
            r = d.get("composite_richness", {})
            parts.append(f"{vk}: M = {r.get('mean',0):.2f}, SD = {r.get('std',0):.2f}, "
                         f"95% CI [{r.get('ci_95',(0,0))[0]:.2f}, {r.get('ci_95',(0,0))[1]:.2f}]")
        lines.append("Quality scores by version: " + "; ".join(parts) + ".")
        lines.append("")

    if kw:
        sig_text = "significant" if kw.get("significant") else "not statistically significant"
        lines.append(f"A Kruskal-Wallis test revealed a {sig_text} difference across versions "
                     f"(H = {kw.get('H',0):.3f}, p = {kw.get('p',1):.4f}).")
        lines.append("")

    # Pairwise
    pairwise = vq.get("pairwise_effect_sizes", {})
    if pairwise:
        large_effects = [(k, v) for k, v in pairwise.items() if v.get("interpretation") == "large"]
        medium_effects = [(k, v) for k, v in pairwise.items() if v.get("interpretation") == "medium"]
        if large_effects:
            lines.append("Large effect sizes were observed for: " +
                         ", ".join(f"{k.replace('_',' ')} (d = {v['cohens_d']:.3f})" for k, v in large_effects) + ".")
        if medium_effects:
            lines.append("Medium effect sizes were observed for: " +
                         ", ".join(f"{k.replace('_',' ')} (d = {v['cohens_d']:.3f})" for k, v in medium_effects) + ".")
        if not large_effects and not medium_effects:
            lines.append("All pairwise comparisons yielded small effect sizes (|d| < 0.5), "
                         "suggesting minimal practical differences between versions.")
        lines.append("")

    # Within-subject
    if within:
        lines.extend([
            "## 3.3 Within-Subject Analysis (BIBD)",
            "",
            "The balanced incomplete block design enabled within-subject comparisons "
            "for each BIBD group pair. ",
        ])
        sig_pairs = [(k, v) for k, v in within.items() if v.get("significant")]
        if sig_pairs:
            lines.append(f"{len(sig_pairs)} of {len(within)} within-subject comparisons "
                         "reached statistical significance (p < .05):")
            for k, v in sig_pairs:
                lines.append(f"  - {k}: mean diff = {v['mean_diff']:.3f}, "
                             f"Z = {v['wilcoxon_z']:.3f}, p = {v['p_value']:.4f}, "
                             f"favouring {v['favours']}")
        else:
            lines.append("No within-subject comparisons reached statistical significance, "
                         "suggesting consistent performance across version pairs.")
        lines.append("")

    # Ranking
    if ranking:
        ranked = sorted(ranking.items(), key=lambda x: x[1].get("rank", 99))
        best = ranked[0]
        lines.extend([
            "## 3.4 Version Ranking",
            "",
            f"Using a weighted composite (quality 40%, coverage 25%, innovation 20%, breadth 15%), "
            f"{best[0]} ranked first with a composite score of {best[1].get('composite',0):.3f}. "
            f"The full ranking was: " +
            ", ".join(f"{vk} ({rd.get('composite',0):.3f})" for vk, rd in ranked) + ".",
            "",
        ])

    # Inter-rater reliability
    if ir:
        comp_data = ir.get("composite_richness", {})
        lines.extend([
            "## 3.5 Inter-Rater Reliability",
            "",
            f"Inter-rater reliability was assessed using {comp_data.get('n_subjects', 30)} "
            f"transcripts scored independently by three LLM providers. "
            f"The composite richness ICC(2,1) was {comp_data.get('icc','N/A')} "
            f"({comp_data.get('interpretation','N/A')} agreement).",
            "",
        ])

        dim_results = []
        for dim in ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]:
            d = ir.get(dim, {})
            dim_results.append(f"{dim.replace('_',' ')} (ICC = {d.get('icc','N/A')})")
        lines.append("Per-dimension ICCs: " + ", ".join(dim_results) + ".")
        lines.append("")

    # Service mapping
    inn_cats = sa.get("innovation_categories", {})
    gap_sev = sa.get("gap_severity_distribution", {})
    if inn_cats or gap_sev:
        total_inn = sum(inn_cats.values()) if inn_cats else 0
        total_gaps = sum(sum(s.values()) for s in gap_sev.values()) if gap_sev else 0
        lines.extend([
            "## 3.6 Service Mapping",
            "",
            f"Service mapping analysis identified {total_gaps} service gaps and "
            f"{total_inn} innovation opportunities across {sa.get('total_transcripts', n)} transcripts.",
            "",
        ])
        if inn_cats:
            top_cats = sorted(inn_cats.items(), key=lambda x: -x[1])[:5]
            lines.append("The most frequently identified innovation areas were: " +
                         ", ".join(f"{cat.replace('_',' ')} (n={count})" for cat, count in top_cats) + ".")
            lines.append("")

    # Blind spots
    if isinstance(blind, list) and blind:
        lines.extend([
            "## 3.7 Coverage Gaps",
            "",
            f"Coverage analysis identified {len(blind)} blind spots (dimension-version cells "
            f"with surfacing rates below 20%). ",
        ])
        if len(blind) > 0:
            worst = blind[0]
            lines.append(f"The most severe gap was {worst.get('dimension','')} in "
                         f"V{worst.get('version','')}, with a surfacing rate of "
                         f"{worst.get('surfacing_rate',0):.1f}%.")
        lines.append("")

    lines.extend([
        "---",
        f"*Draft generated by results_synthesiser.py on {datetime.now().strftime('%Y-%m-%d')}*",
    ])

    return "\n".join(lines)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Results Synthesiser")
    parser.add_argument("--eval-dir", type=str, required=True)
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    eval_dir = Path(args.eval_dir)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    with open(args.plan) as f:
        plan = json.load(f)

    log.info("Loading evaluation artefacts...")
    data = load_all(eval_dir)
    log.info(f"  Summaries: {len(data['summaries'])}")
    log.info(f"  Scores: {len(data['scores'])}")

    # 1. Executive summary
    exec_summary = build_executive_summary(data, plan)
    with open(out / "executive_summary.md", "w") as f:
        f.write(exec_summary)
    log.info(f"  Executive summary -> {out / 'executive_summary.md'}")

    # 2. Paper tables
    tables = build_paper_tables(data)
    with open(out / "paper_tables.json", "w") as f:
        json.dump(tables, f, indent=2, ensure_ascii=False)

    # Also export as markdown
    with open(out / "paper_tables.md", "w") as f:
        f.write("# Paper-Ready Tables\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        for name, content in sorted(tables.items()):
            f.write(f"## {name.replace('_', ' ').title()}\n\n")
            f.write(content.get("markdown", "") + "\n\n")
            if "latex" in content:
                f.write("### LaTeX\n\n```latex\n" + content["latex"] + "\n```\n\n")
    log.info(f"  Paper tables -> {out / 'paper_tables.md'}")

    # 3. Figure data
    figures = build_figure_data(data)
    with open(out / "figure_data.json", "w") as f:
        json.dump(figures, f, indent=2, ensure_ascii=False)
    log.info(f"  Figure data -> {out / 'figure_data.json'} ({len(figures)} figures)")

    # 4. Results narrative
    narrative = build_results_narrative(data)
    with open(out / "results_narrative.md", "w") as f:
        f.write(narrative)
    log.info(f"  Results narrative -> {out / 'results_narrative.md'}")

    # Console
    log.info(f"\n{'='*60}")
    log.info("SYNTHESIS COMPLETE")
    log.info(f"{'='*60}")
    log.info(f"  Output directory: {out}")
    log.info(f"  Files generated:")
    log.info(f"    - executive_summary.md")
    log.info(f"    - paper_tables.json / paper_tables.md")
    log.info(f"    - figure_data.json")
    log.info(f"    - results_narrative.md")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()

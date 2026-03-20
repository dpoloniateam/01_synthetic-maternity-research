"""
Table generator for publication-ready manuscript tables.

Reads Sprint 5/6 evaluation data and produces Markdown, CSV, and LaTeX
tables. No LLM calls -- pure data reading and formatting.

Usage:
    python -m src.manuscript.table_generator \
        --evaluation data/evaluation/ \
        --refinement data/refinement/ \
        --output docs/manuscript/tables/
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from src.refinement.timestamped_run import TimestampedRun

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TABLE_TITLES = {
    1: "Version Quality Comparison",
    2: "Within-Subject Paired Comparison",
    3: "Latent Dimension Surfacing Heatmap",
    4: "Inter-Rater Reliability",
    5: "Refinement Impact -- Original V4 vs Refined V4_R1",
    6: "Robustness Testing Results",
    7: "Saturation Metrics",
    8: "Pairwise Effect Sizes",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_json(path: str) -> dict:
    """Load a JSON file and return its contents."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _md_row(cells: list[str]) -> str:
    """Format a list of cell values as a Markdown table row."""
    return "| " + " | ".join(str(c) for c in cells) + " |"


def _md_separator(n_cols: int) -> str:
    """Create a Markdown table separator row."""
    return "|" + "|".join(["---"] * n_cols) + "|"


def _csv_text(headers: list[str], rows: list[list[str]]) -> str:
    """Render headers + rows as CSV text."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return buf.getvalue()


def _latex_escape(text: str) -> str:
    """Escape special LaTeX characters in a string."""
    text = str(text)
    for ch in ("&", "%", "$", "#", "_", "{", "}"):
        text = text.replace(ch, f"\\{ch}")
    return text


def _latex_table(caption: str, headers: list[str], rows: list[list[str]],
                 label: str = "") -> str:
    """Build a basic LaTeX tabular environment."""
    col_spec = "l" + "c" * (len(headers) - 1)
    lines = [
        "\\begin{table}[htbp]",
        f"\\caption{{{_latex_escape(caption)}}}",
    ]
    if label:
        lines.append(f"\\label{{{label}}}")
    lines += [
        "\\centering",
        f"\\begin{{tabular}}{{{col_spec}}}",
        "\\hline",
        " & ".join(_latex_escape(h) for h in headers) + " \\\\",
        "\\hline",
    ]
    for row in rows:
        lines.append(" & ".join(_latex_escape(c) for c in row) + " \\\\")
    lines += [
        "\\hline",
        "\\end{tabular}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def _parse_md_table(md_text: str) -> tuple[list[str], list[list[str]]]:
    """Parse a Markdown table string into (headers, rows).

    Handles tables produced by the synthesis pipeline where each row
    is pipe-delimited.
    """
    lines = [l.strip() for l in md_text.strip().split("\n") if l.strip()]
    # First line is header
    header_cells = [c.strip() for c in lines[0].split("|") if c.strip()]
    data_rows: list[list[str]] = []
    for line in lines[1:]:
        # Skip separator lines like |---|---|
        if re.match(r"^\|[\s\-|]+\|$", line):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if cells:
            data_rows.append(cells)
    return header_cells, data_rows


# ---------------------------------------------------------------------------
# Table builders
# ---------------------------------------------------------------------------


def build_table_1(paper_tables: dict) -> tuple[str, str, str]:
    """Table 1: Version Quality Comparison (from paper_tables table1)."""
    src = paper_tables["table1_quality_by_version"]
    headers, rows = _parse_md_table(src["markdown"])
    md_lines = [
        "## Table 1: Version Quality Comparison",
        "",
        _md_row(headers),
        _md_separator(len(headers)),
    ]
    for row in rows:
        md_lines.append(_md_row(row))
    latex = _latex_table(
        "Quality scores by questionnaire version", headers, rows,
        label="tab:quality_by_version",
    )
    md_lines += ["", "```latex", latex, "```"]
    md = "\n".join(md_lines)
    csv_out = _csv_text(headers, rows)
    return md, csv_out, latex


def build_table_2(paper_tables: dict) -> tuple[str, str, str]:
    """Table 2: Within-Subject Paired Comparison (from paper_tables table3)."""
    src = paper_tables["table3_within_subject"]
    headers, rows = _parse_md_table(src["markdown"])
    md_lines = [
        "## Table 2: Within-Subject Paired Comparison",
        "",
        _md_row(headers),
        _md_separator(len(headers)),
    ]
    for row in rows:
        md_lines.append(_md_row(row))
    latex = _latex_table(
        "Within-subject paired comparison (Wilcoxon signed-rank)",
        headers, rows, label="tab:within_subject",
    )
    md_lines += ["", "```latex", latex, "```"]
    md = "\n".join(md_lines)
    csv_out = _csv_text(headers, rows)
    return md, csv_out, latex


def build_table_3(paper_tables: dict) -> tuple[str, str, str]:
    """Table 3: Latent Dimension Surfacing Heatmap (from paper_tables table5)."""
    src = paper_tables["table5_dimension_heatmap"]
    headers, rows = _parse_md_table(src["markdown"])
    md_lines = [
        "## Table 3: Latent Dimension Surfacing Heatmap",
        "",
        _md_row(headers),
        _md_separator(len(headers)),
    ]
    for row in rows:
        md_lines.append(_md_row(row))
    latex = _latex_table(
        "Latent dimension surfacing rates by version (\\%)",
        headers, rows, label="tab:dimension_heatmap",
    )
    md_lines += ["", "```latex", latex, "```"]
    md = "\n".join(md_lines)
    csv_out = _csv_text(headers, rows)
    return md, csv_out, latex


def build_table_4(paper_tables: dict) -> tuple[str, str, str]:
    """Table 4: Inter-Rater Reliability (from paper_tables table4)."""
    src = paper_tables["table4_inter_rater"]
    headers, rows = _parse_md_table(src["markdown"])
    md_lines = [
        "## Table 4: Inter-Rater Reliability",
        "",
        _md_row(headers),
        _md_separator(len(headers)),
    ]
    for row in rows:
        md_lines.append(_md_row(row))
    latex = _latex_table(
        "Inter-rater reliability across quality dimensions",
        headers, rows, label="tab:inter_rater",
    )
    md_lines += ["", "```latex", latex, "```"]
    md = "\n".join(md_lines)
    csv_out = _csv_text(headers, rows)
    return md, csv_out, latex


def build_table_5(
    paper_tables: dict,
    figure_data: dict,
    scoring_summary: dict,
) -> tuple[str, str, str]:
    """Table 5: Refinement Impact -- Original V4 vs Refined V4_R1.

    Compares original V4 scores (from figure_data radar) with refined
    scores (from refinement scoring_summary).
    """
    original_dims = figure_data.get("fig2_dimension_radar", {}).get("V4", {})
    refined_dims = scoring_summary.get("mean_scores_global", {})

    # Original V4 composite from paper_tables table1
    headers_t1, rows_t1 = _parse_md_table(
        paper_tables["table1_quality_by_version"]["markdown"]
    )
    original_richness = "N/A"
    original_surfacing = "N/A"
    for row in rows_t1:
        if row[0].strip() == "V4":
            # Headers: Version(0) | N(1) | Richness M(SD)(2) | 95% CI(3) | Surfacing Rate(4)
            original_richness = row[2]
            original_surfacing = row[4] if len(row) > 4 else "N/A"
            break

    refined_richness = scoring_summary.get("mean_composite_richness", "N/A")
    refined_surfacing_raw = scoring_summary.get("mean_surfacing_rate", "N/A")
    if isinstance(refined_surfacing_raw, (int, float)):
        refined_surfacing = f"{refined_surfacing_raw * 100:.1f}%"
    else:
        refined_surfacing = str(refined_surfacing_raw)

    # Dimension-level comparison
    dim_order = [
        "emotional_depth", "specificity", "latent_surfacing",
        "narrative_quality", "clinical_grounding",
    ]
    dim_labels = {
        "emotional_depth": "Emotional Depth",
        "specificity": "Specificity",
        "latent_surfacing": "Latent Surfacing",
        "narrative_quality": "Narrative Quality",
        "clinical_grounding": "Clinical Grounding",
    }

    headers = ["Metric", "Original V4", "Refined V4_R1", "Delta"]
    rows: list[list[str]] = []

    for dim_key in dim_order:
        label = dim_labels[dim_key]
        orig = original_dims.get(dim_key)
        ref = refined_dims.get(dim_key)
        if orig is not None and ref is not None:
            delta = ref - orig
            sign = "+" if delta >= 0 else ""
            rows.append([label, f"{orig:.2f}", f"{ref:.2f}", f"{sign}{delta:.2f}"])
        else:
            o_str = f"{orig:.2f}" if orig is not None else "N/A"
            r_str = f"{ref:.2f}" if ref is not None else "N/A"
            rows.append([label, o_str, r_str, "N/A"])

    # Composite row
    if isinstance(refined_richness, (int, float)):
        refined_r_str = f"{refined_richness:.2f}"
    else:
        refined_r_str = str(refined_richness)
    rows.append(["**Composite Richness**", original_richness, refined_r_str, ""])
    rows.append(["**Surfacing Rate**", original_surfacing, refined_surfacing, ""])

    # Compute delta for composite if possible
    try:
        # Parse original richness mean from "M (SD)" format
        orig_m = float(re.match(r"([\d.]+)", original_richness).group(1))
        ref_m = float(refined_richness) if isinstance(refined_richness, (int, float)) else float(refined_r_str)
        delta_c = ref_m - orig_m
        sign_c = "+" if delta_c >= 0 else ""
        rows[-2][-1] = f"{sign_c}{delta_c:.2f}"
    except (AttributeError, ValueError, TypeError):
        pass

    # Compute delta for surfacing rate
    try:
        orig_s = float(original_surfacing.replace("%", ""))
        ref_s = float(refined_surfacing.replace("%", ""))
        delta_s = ref_s - orig_s
        sign_s = "+" if delta_s >= 0 else ""
        rows[-1][-1] = f"{sign_s}{delta_s:.1f}pp"
    except (ValueError, TypeError):
        pass

    md_lines = [
        "## Table 5: Refinement Impact -- Original V4 vs Refined V4_R1",
        "",
        _md_row(headers),
        _md_separator(len(headers)),
    ]
    for row in rows:
        md_lines.append(_md_row(row))
    latex = _latex_table(
        "Refinement impact: Original V4 vs Refined V4\\_R1",
        headers, rows, label="tab:refinement_impact",
    )
    md_lines += ["", "```latex", latex, "```"]
    md = "\n".join(md_lines)
    csv_out = _csv_text(headers, rows)
    return md, csv_out, latex


def build_table_6(robustness: dict) -> tuple[str, str, str]:
    """Table 6: Robustness Testing Results (from adversarial robustness_report)."""
    profiles = robustness.get("profiles", [])
    summary = robustness.get("summary", {})

    headers = [
        "Profile Type", "Persona", "Mean Richness",
        "Pop. Mean", "Ratio", "Threshold", "Passed",
    ]
    rows: list[list[str]] = []
    for p in profiles:
        rows.append([
            p.get("profile_type", ""),
            p.get("persona_name", ""),
            f"{p.get('mean_richness', 0):.2f}",
            f"{p.get('population_mean', 0):.2f}",
            f"{p.get('ratio_to_population', 0):.2f}",
            f"{p.get('threshold', 0):.2f}",
            "Yes" if p.get("passed") else "No",
        ])

    # Summary row
    rows.append([
        "**Overall**", "",
        f"{summary.get('adversarial_mean_richness', 0):.2f}",
        f"{summary.get('population_mean_richness', 0):.2f}",
        "",
        "",
        f"{summary.get('n_passed', 0)}/{summary.get('n_profiles', 0)}",
    ])

    md_lines = [
        "## Table 6: Robustness Testing Results",
        "",
        _md_row(headers),
        _md_separator(len(headers)),
    ]
    for row in rows:
        md_lines.append(_md_row(row))
    latex = _latex_table(
        "Adversarial robustness testing across vulnerable population profiles",
        headers, rows, label="tab:robustness",
    )
    md_lines += ["", "```latex", latex, "```"]
    md = "\n".join(md_lines)
    csv_out = _csv_text(headers, rows)
    return md, csv_out, latex


def build_table_7(saturation: dict) -> tuple[str, str, str]:
    """Table 7: Saturation Metrics (from saturation_analysis.json)."""
    headers = ["Metric", "Value"]
    rows: list[list[str]] = []

    rows.append(["Total Transcripts", str(saturation.get("total_transcripts", ""))])
    rows.append(["Original Transcripts", str(saturation.get("original_transcripts", ""))])
    rows.append(["Refinement Transcripts", str(saturation.get("refinement_transcripts", ""))])
    rows.append(["Total Unique Themes", str(saturation.get("total_unique_themes", ""))])
    rows.append(["Pre-Refinement Themes", str(saturation.get("pre_refinement_themes", ""))])
    rows.append(["Post-Refinement New Themes", str(saturation.get("post_refinement_new_themes", ""))])

    novelty = saturation.get("refinement_novelty_rate")
    if novelty is not None:
        rows.append(["Refinement Novelty Rate", f"{novelty:.1%}"])
    else:
        rows.append(["Refinement Novelty Rate", "N/A"])

    plateau_c = saturation.get("plateau_point_combined")
    rows.append(["Plateau Point (Combined)", str(plateau_c) if plateau_c is not None else "Not reached"])
    plateau_o = saturation.get("plateau_point_original")
    rows.append(["Plateau Point (Original)", str(plateau_o) if plateau_o is not None else "Not reached"])

    # Category saturation sub-table
    cat_sat = saturation.get("category_saturation", {})
    for cat_name, cat_data in sorted(cat_sat.items()):
        total = cat_data.get("total_unique", "")
        plat = cat_data.get("plateau_at")
        plat_str = str(plat) if plat is not None else "Not reached"
        rows.append([f"  {cat_name.title()} -- Unique Codes", str(total)])
        rows.append([f"  {cat_name.title()} -- Plateau At", plat_str])

    # Yield comparison
    yc = saturation.get("yield_comparison", {})
    if yc:
        rows.append(["Original Mean Yield", f"{yc.get('original_mean', 0):.2f}"])
        rows.append(["Refinement Mean Yield", f"{yc.get('refinement_mean', 0):.2f}"])
        rows.append(["Mann-Whitney U", f"{yc.get('mann_whitney_U', 0):.1f}"])
        p_val = yc.get("p_value")
        if p_val is not None:
            rows.append(["p-value", f"{p_val:.6f}"])
        rows.append(["Significant", str(yc.get("significant", ""))])

    md_lines = [
        "## Table 7: Saturation Metrics",
        "",
        _md_row(headers),
        _md_separator(len(headers)),
    ]
    for row in rows:
        md_lines.append(_md_row(row))
    latex = _latex_table(
        "Thematic saturation metrics", headers, rows,
        label="tab:saturation",
    )
    md_lines += ["", "```latex", latex, "```"]
    md = "\n".join(md_lines)
    csv_out = _csv_text(headers, rows)
    return md, csv_out, latex


def build_table_8(paper_tables: dict) -> tuple[str, str, str]:
    """Table 8: Pairwise Effect Sizes (from paper_tables table2)."""
    src = paper_tables["table2_pairwise_effects"]
    headers, rows = _parse_md_table(src["markdown"])
    md_lines = [
        "## Table 8: Pairwise Effect Sizes",
        "",
        _md_row(headers),
        _md_separator(len(headers)),
    ]
    for row in rows:
        md_lines.append(_md_row(row))
    latex = _latex_table(
        "Pairwise effect sizes (Cohen's d) between questionnaire versions",
        headers, rows, label="tab:pairwise_effects",
    )
    md_lines += ["", "```latex", latex, "```"]
    md = "\n".join(md_lines)
    csv_out = _csv_text(headers, rows)
    return md, csv_out, latex


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

BUILDERS = {
    1: "build_table_1",
    2: "build_table_2",
    3: "build_table_3",
    4: "build_table_4",
    5: "build_table_5",
    6: "build_table_6",
    7: "build_table_7",
    8: "build_table_8",
}


def generate_all_tables(
    evaluation_dir: str,
    refinement_dir: str,
    output_dir: str,
) -> dict[str, Any]:
    """Load data, build all 8 tables, write outputs.

    Returns a summary dict with paths written and table metadata.
    """
    run = TimestampedRun(output_dir)

    # ---- Load data sources ------------------------------------------------
    paper_tables_path = os.path.join(
        evaluation_dir, "synthesis", "paper_tables.json"
    )
    figure_data_path = os.path.join(
        evaluation_dir, "synthesis", "figure_data.json"
    )
    scoring_summary_path = os.path.join(
        evaluation_dir, "refinement", "scoring_summary.json"
    )
    robustness_path = os.path.join(
        evaluation_dir, "adversarial", "robustness_report.json"
    )
    saturation_path = os.path.join(
        evaluation_dir, "saturation", "saturation_analysis.json"
    )

    paper_tables = _load_json(paper_tables_path)
    run.record_read(paper_tables_path)

    figure_data = _load_json(figure_data_path)
    run.record_read(figure_data_path)

    scoring_summary = _load_json(scoring_summary_path)
    run.record_read(scoring_summary_path)

    robustness = _load_json(robustness_path)
    run.record_read(robustness_path)

    saturation = _load_json(saturation_path)
    run.record_read(saturation_path)

    # Also record refinement_plan as an input (used for context)
    refinement_plan_path = os.path.join(refinement_dir, "refinement_plan.json")
    if os.path.exists(refinement_plan_path):
        run.record_read(refinement_plan_path)

    # ---- Build each table -------------------------------------------------
    all_md_parts: list[str] = []
    results: dict[int, dict] = {}

    for table_num in sorted(BUILDERS.keys()):
        if table_num == 5:
            md, csv_out, latex = build_table_5(
                paper_tables, figure_data, scoring_summary,
            )
        elif table_num == 6:
            md, csv_out, latex = build_table_6(robustness)
        elif table_num == 7:
            md, csv_out, latex = build_table_7(saturation)
        else:
            # Tables 1-4 and 8 take only paper_tables
            builder_fn = globals()[BUILDERS[table_num]]
            md, csv_out, latex = builder_fn(paper_tables)

        # Write individual Markdown file
        md_filename = f"table_{table_num}.md"
        md_path = run.output_path(md_filename)
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, "w", encoding="utf-8") as fh:
            fh.write(md + "\n")
        run.stable_pointer(md_filename, md_path)

        # Write individual CSV file
        csv_filename = f"table_{table_num}.csv"
        csv_path = run.output_path(csv_filename)
        with open(csv_path, "w", encoding="utf-8") as fh:
            fh.write(csv_out)
        run.stable_pointer(csv_filename, csv_path)

        all_md_parts.append(md)
        results[table_num] = {
            "title": TABLE_TITLES[table_num],
            "md_path": md_path,
            "csv_path": csv_path,
        }

    # ---- Write combined Markdown ------------------------------------------
    combined_md = (
        "# Publication-Ready Tables\n\n"
        f"Generated: {run.timestamp}\n\n"
        + "\n\n---\n\n".join(all_md_parts)
        + "\n"
    )
    combined_filename = "all_tables.md"
    combined_path = run.output_path(combined_filename)
    with open(combined_path, "w", encoding="utf-8") as fh:
        fh.write(combined_md)
    run.stable_pointer(combined_filename, combined_path)

    # ---- Manifest ---------------------------------------------------------
    run.write_manifest(
        module_name="src.manuscript.table_generator",
        config={
            "evaluation_dir": evaluation_dir,
            "refinement_dir": refinement_dir,
            "output_dir": output_dir,
            "tables_generated": list(BUILDERS.keys()),
        },
        cost=0.0,
    )

    summary = {
        "timestamp": run.timestamp,
        "tables": results,
        "combined_md": combined_path,
        "output_dir": output_dir,
        "n_tables": len(BUILDERS),
    }
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate publication-ready tables from evaluation data.",
    )
    parser.add_argument(
        "--evaluation",
        required=True,
        help="Path to the evaluation data directory (e.g. data/evaluation/).",
    )
    parser.add_argument(
        "--refinement",
        required=True,
        help="Path to the refinement data directory (e.g. data/refinement/).",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for generated tables (e.g. docs/manuscript/tables/).",
    )
    args = parser.parse_args()

    summary = generate_all_tables(
        evaluation_dir=args.evaluation,
        refinement_dir=args.refinement,
        output_dir=args.output,
    )

    print(f"Generated {summary['n_tables']} tables (timestamp: {summary['timestamp']})")
    print(f"Combined file: {summary['combined_md']}")
    for num, info in sorted(summary["tables"].items()):
        print(f"  Table {num}: {info['title']}")
        print(f"    MD:  {info['md_path']}")
        print(f"    CSV: {info['csv_path']}")


if __name__ == "__main__":
    main()

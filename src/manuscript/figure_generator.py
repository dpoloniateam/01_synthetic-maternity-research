"""
Manuscript figure generator for synthetic maternity research project.

Reads evaluation data and produces publication-ready matplotlib figures
as PNG (300 DPI) plus companion JSON data files for reproducibility.

No LLM calls -- pure data visualisation.

Usage:
    python -m src.manuscript.figure_generator \
        --evaluation data/evaluation/ \
        --refinement data/refinement/ \
        --output docs/manuscript/figures/
"""

# Agg backend must be set before any pyplot import
import matplotlib
matplotlib.use("Agg")

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# ---------------------------------------------------------------------------
# Project import
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.refinement.timestamped_run import TimestampedRun

# ---------------------------------------------------------------------------
# Academic style configuration
# ---------------------------------------------------------------------------

def _apply_academic_style() -> None:
    """Configure matplotlib for clean academic figures."""
    plt.rcParams.update({
        # Font
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif", "serif"],
        "font.size": 10,
        # Axes
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        # Ticks
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        # Grid -- minimal
        "axes.grid": False,
        # Legend
        "legend.frameon": False,
        "legend.fontsize": 9,
        # Figure
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
    })


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

PALETTE = {
    "original": "#2c7bb6",
    "refinement": "#d7191c",
    "versions": ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e"],
    "population_mean": "#333333",
}


# ---------------------------------------------------------------------------
# Helper: save figure + data JSON
# ---------------------------------------------------------------------------

def _save_figure(
    fig: plt.Figure,
    fig_number: int,
    data: dict,
    run: TimestampedRun,
) -> Tuple[str, str]:
    """Save PNG (300 DPI) and companion JSON; create stable pointers."""
    base_png = f"fig_{fig_number}.png"
    base_json = f"fig_{fig_number}_data.json"

    ts_png = run.output_path(base_png)
    ts_json = run.output_path(base_json)

    fig.tight_layout()
    fig.savefig(ts_png, dpi=300, bbox_inches="tight")
    plt.close(fig)

    with open(ts_json, "w") as fh:
        json.dump(data, fh, indent=2, default=str)

    run.stable_pointer(base_png, ts_png)
    run.stable_pointer(base_json, ts_json)

    return ts_png, ts_json


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def _load_json(path: str) -> Any:
    with open(path) as fh:
        return json.load(fh)


def _load_jsonl(path: str) -> List[dict]:
    records = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ---------------------------------------------------------------------------
# Figure 1: Version Quality Box Plots
# ---------------------------------------------------------------------------

def figure_1_quality_boxplots(
    evaluation_dir: str,
    run: TimestampedRun,
) -> Tuple[str, str]:
    """
    Box plots of composite richness grouped by questionnaire version.

    Primary source: transcript_summaries.jsonl (grouped by questionnaire_version).
    Fallback: figure_data.json -> fig1_richness_boxplot.
    """
    summaries_path = os.path.join(evaluation_dir, "transcript_summaries.jsonl")
    run.record_read(summaries_path)

    # Try to load from transcript_summaries.jsonl
    version_data: Dict[str, List[float]] = {}
    if os.path.exists(summaries_path):
        records = _load_jsonl(summaries_path)
        for rec in records:
            v = f"V{rec['questionnaire_version']}"
            version_data.setdefault(v, []).append(rec["mean_composite_richness"])
    else:
        # Fallback to precomputed figure_data.json
        fd_path = os.path.join(evaluation_dir, "synthesis", "figure_data.json")
        run.record_read(fd_path)
        fd = _load_json(fd_path)
        for v, info in fd["fig1_richness_boxplot"].items():
            version_data[v] = info["values"]

    versions = sorted(version_data.keys())
    data_arrays = [version_data[v] for v in versions]

    # -- Plot --
    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(
        data_arrays,
        tick_labels=versions,
        patch_artist=True,
        widths=0.5,
        showfliers=True,
        flierprops={"marker": "o", "markersize": 3, "alpha": 0.5},
        medianprops={"color": "black", "linewidth": 1.5},
    )
    for patch, colour in zip(bp["boxes"], PALETTE["versions"]):
        patch.set_facecolor(colour)
        patch.set_alpha(0.7)

    ax.set_xlabel("Questionnaire Version")
    ax.set_ylabel("Composite Richness Score")
    ax.set_title("Figure 1. Composite Richness by Questionnaire Version")

    # Build JSON data
    json_data = {}
    for v, vals in zip(versions, data_arrays):
        arr = np.array(vals)
        json_data[v] = {
            "n": len(vals),
            "mean": round(float(np.mean(arr)), 3),
            "median": round(float(np.median(arr)), 3),
            "q1": round(float(np.percentile(arr, 25)), 3),
            "q3": round(float(np.percentile(arr, 75)), 3),
            "min": round(float(np.min(arr)), 3),
            "max": round(float(np.max(arr)), 3),
            "values": [round(float(x), 3) for x in sorted(vals)],
        }

    return _save_figure(fig, 1, json_data, run)


# ---------------------------------------------------------------------------
# Figure 2: Latent Dimension Coverage Heatmap
# ---------------------------------------------------------------------------

def figure_2_dimension_heatmap(
    evaluation_dir: str,
    run: TimestampedRun,
) -> Tuple[str, str]:
    """
    5x12 heatmap of latent-dimension surfacing rates per version.

    Primary source: paper_tables.json -> table5_dimension_heatmap (markdown).
    Fallback: figure_data.json -> fig3_surfacing_heatmap.
    """
    pt_path = os.path.join(evaluation_dir, "synthesis", "paper_tables.json")
    fd_path = os.path.join(evaluation_dir, "synthesis", "figure_data.json")
    run.record_read(pt_path)

    # Try paper_tables.json first (parse markdown table)
    versions: List[str] = []
    dimensions: List[str] = []
    rates: List[List[float]] = []  # rows = dimensions, cols = versions

    if os.path.exists(pt_path):
        pt = _load_json(pt_path)
        md = pt["table5_dimension_heatmap"]["markdown"]
        lines = [l.strip() for l in md.strip().split("\n") if l.strip()]
        # First line is the header
        header = [c.strip() for c in lines[0].split("|") if c.strip()]
        versions = header[1:]  # skip "Dimension"
        # Skip separator line (lines[1])
        for row_line in lines[2:]:
            cells = [c.strip() for c in row_line.split("|") if c.strip()]
            if len(cells) < 2:
                continue
            dim_name = cells[0]
            dimensions.append(dim_name)
            row_vals = []
            for cell in cells[1:]:
                val = float(cell.replace("%", "").strip())
                row_vals.append(val)
            rates.append(row_vals)
    else:
        # Fallback to figure_data.json
        run.record_read(fd_path)
        fd = _load_json(fd_path)
        hm = fd["fig3_surfacing_heatmap"]
        versions = sorted(hm.keys())
        dimensions = sorted(hm[versions[0]].keys())
        for dim in dimensions:
            row = [hm[v][dim]["surfacing_rate"] for v in versions]
            rates.append(row)

    rate_array = np.array(rates)

    # -- Custom green-yellow-red colormap --
    cmap = LinearSegmentedColormap.from_list(
        "coverage",
        [(0.85, 0.15, 0.15), (1.0, 0.85, 0.2), (0.2, 0.7, 0.3)],
        N=256,
    )

    # -- Plot --
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(rate_array, cmap=cmap, aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(range(len(versions)))
    ax.set_xticklabels(versions)
    ax.set_yticks(range(len(dimensions)))
    # Clean up dimension labels for display
    dim_labels = [d.replace("_", " ").title() for d in dimensions]
    ax.set_yticklabels(dim_labels, fontsize=8)

    # Annotate cells with percentage values
    for i in range(len(dimensions)):
        for j in range(len(versions)):
            val = rate_array[i, j]
            text_color = "white" if val < 20 or val > 80 else "black"
            ax.text(
                j, i, f"{val:.0f}%",
                ha="center", va="center",
                fontsize=7, color=text_color, fontweight="bold",
            )

    cbar = fig.colorbar(im, ax=ax, shrink=0.8, label="Surfacing Rate (%)")
    ax.set_title("Figure 2. Latent Dimension Coverage Heatmap")
    ax.set_xlabel("Questionnaire Version")

    json_data = {
        "versions": versions,
        "dimensions": dimensions,
        "rates": rates,
    }
    return _save_figure(fig, 2, json_data, run)


# ---------------------------------------------------------------------------
# Figure 3: Saturation Curve
# ---------------------------------------------------------------------------

def figure_3_saturation_curve(
    evaluation_dir: str,
    run: TimestampedRun,
) -> Tuple[str, str]:
    """
    Cumulative themes vs transcript number with fitted power curve.

    Source: data/evaluation/saturation/saturation_curve_data.json
    """
    sc_path = os.path.join(evaluation_dir, "saturation", "saturation_curve_data.json")
    run.record_read(sc_path)
    data = _load_json(sc_path)

    xs = np.array([p["x"] for p in data], dtype=float)
    ys = np.array([p["y"] for p in data], dtype=float)
    sources = [p["source"] for p in data]

    # Split into original vs refinement
    orig_mask = np.array([s == "original" for s in sources])
    ref_mask = np.array([s == "refinement" for s in sources])

    # Fit power curve y = a * x^b using log-log linear regression
    log_x = np.log(xs)
    log_y = np.log(np.maximum(ys, 1))  # avoid log(0)
    coeffs = np.polyfit(log_x, log_y, 1)
    b_fit = coeffs[0]
    a_fit = np.exp(coeffs[1])
    x_smooth = np.linspace(1, xs.max(), 200)
    y_fit = a_fit * x_smooth ** b_fit

    # -- Plot --
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.scatter(
        xs[orig_mask], ys[orig_mask],
        c=PALETTE["original"], s=20, alpha=0.7,
        label="Original sessions", zorder=3,
    )
    ax.scatter(
        xs[ref_mask], ys[ref_mask],
        c=PALETTE["refinement"], s=20, alpha=0.7,
        label="Refinement sessions", zorder=3,
    )
    ax.plot(
        x_smooth, y_fit,
        color="#999999", linewidth=1.5, linestyle="--",
        label=f"Power fit: y = {a_fit:.1f} x^{{{b_fit:.2f}}}",
        zorder=2,
    )

    # Mark transition point
    if np.any(ref_mask):
        trans_x = xs[ref_mask][0]
        ax.axvline(
            trans_x, color="#aaaaaa", linewidth=0.8, linestyle=":",
            label=f"Refinement start (n={int(trans_x)})",
        )

    ax.set_xlabel("Transcript Number")
    ax.set_ylabel("Cumulative Unique Themes")
    ax.set_title("Figure 3. Thematic Saturation Curve")
    ax.legend(loc="lower right", fontsize=8)

    json_data = {
        "points": data,
        "power_fit": {"a": round(a_fit, 4), "b": round(b_fit, 4)},
    }
    return _save_figure(fig, 3, json_data, run)


# ---------------------------------------------------------------------------
# Figure 4: Robustness Comparison Bar Chart
# ---------------------------------------------------------------------------

def figure_4_robustness_bars(
    evaluation_dir: str,
    run: TimestampedRun,
) -> Tuple[str, str]:
    """
    Grouped bar chart: 5 quality dimensions for each adversarial profile,
    with horizontal population mean line.

    Source: data/evaluation/adversarial/robustness_report.json
    """
    rr_path = os.path.join(evaluation_dir, "adversarial", "robustness_report.json")
    run.record_read(rr_path)
    report = _load_json(rr_path)

    profiles = report["profiles"]
    dimensions = ["emotional_depth", "specificity", "latent_surfacing",
                   "narrative_quality", "clinical_grounding"]
    dim_labels = [d.replace("_", " ").title() for d in dimensions]

    profile_labels = [p["profile_type"].replace("_", " ").title() for p in profiles]
    n_profiles = len(profiles)
    n_dims = len(dimensions)

    # Extract population means (same across profiles, use first)
    pop_means = [
        profiles[0]["dimension_comparison"][d]["population"]
        for d in dimensions
    ]

    # Extract adversarial scores
    adv_scores = []
    for p in profiles:
        scores = [p["dimension_scores"][d] for d in dimensions]
        adv_scores.append(scores)

    # -- Plot --
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(n_dims)
    total_width = 0.75
    bar_width = total_width / n_profiles

    colours = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]
    for i, (scores, label) in enumerate(zip(adv_scores, profile_labels)):
        offset = (i - n_profiles / 2 + 0.5) * bar_width
        ax.bar(
            x + offset, scores, bar_width,
            label=label, color=colours[i % len(colours)], alpha=0.8,
        )

    # Population mean horizontal lines
    for j, pm in enumerate(pop_means):
        ax.hlines(
            pm, j - total_width / 2, j + total_width / 2,
            colors=PALETTE["population_mean"], linewidths=1.5, linestyles="--",
        )
    # One legend entry for population mean
    ax.hlines(
        [], 0, 0,
        colors=PALETTE["population_mean"], linewidths=1.5, linestyles="--",
        label="Population Mean",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(dim_labels, fontsize=8, rotation=15, ha="right")
    ax.set_ylabel("Score")
    ax.set_title("Figure 4. Adversarial Profile Robustness")
    ax.legend(loc="upper right", fontsize=7, ncol=2)

    json_data = {
        "dimensions": dimensions,
        "profiles": [
            {
                "profile_type": p["profile_type"],
                "dimension_scores": p["dimension_scores"],
                "mean_richness": p["mean_richness"],
            }
            for p in profiles
        ],
        "population_means": dict(zip(dimensions, pop_means)),
    }
    return _save_figure(fig, 4, json_data, run)


# ---------------------------------------------------------------------------
# Figure 5: Rolling Marginal Yield
# ---------------------------------------------------------------------------

def figure_5_rolling_yield(
    evaluation_dir: str,
    run: TimestampedRun,
) -> Tuple[str, str]:
    """
    Line plot of rolling mean new themes per transcript,
    colour-coded by original vs refinement.

    Source: data/evaluation/saturation/rolling_yield_data.json
    """
    ry_path = os.path.join(evaluation_dir, "saturation", "rolling_yield_data.json")
    run.record_read(ry_path)
    data = _load_json(ry_path)

    idxs = np.array([p["transcript_idx"] for p in data], dtype=float)
    rolling = np.array([p["rolling_mean"] for p in data], dtype=float)
    sources = [p["source"] for p in data]

    orig_mask = np.array([s == "original" for s in sources])
    ref_mask = np.array([s == "refinement" for s in sources])

    # -- Plot --
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(
        idxs[orig_mask], rolling[orig_mask],
        color=PALETTE["original"], linewidth=1.5,
        label="Original sessions",
    )
    ax.plot(
        idxs[ref_mask], rolling[ref_mask],
        color=PALETTE["refinement"], linewidth=1.5,
        label="Refinement sessions",
    )

    # Fill under curves for visual distinction
    ax.fill_between(
        idxs[orig_mask], rolling[orig_mask],
        alpha=0.1, color=PALETTE["original"],
    )
    ax.fill_between(
        idxs[ref_mask], rolling[ref_mask],
        alpha=0.1, color=PALETTE["refinement"],
    )

    # Mark transition
    if np.any(ref_mask):
        trans_x = idxs[ref_mask][0]
        ax.axvline(
            trans_x, color="#aaaaaa", linewidth=0.8, linestyle=":",
            label=f"Refinement start (n={int(trans_x)})",
        )

    ax.set_xlabel("Transcript Number")
    ax.set_ylabel("Rolling Mean New Themes")
    ax.set_title("Figure 5. Rolling Marginal Yield of New Themes")
    ax.legend(loc="upper right", fontsize=8)

    json_data = {
        "points": data,
    }
    return _save_figure(fig, 5, json_data, run)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def generate_all_figures(
    evaluation_dir: str,
    refinement_dir: str,
    output_dir: str,
) -> dict:
    """Generate all five manuscript figures and return summary."""
    _apply_academic_style()
    os.makedirs(output_dir, exist_ok=True)

    run = TimestampedRun(output_dir)
    results = {}

    generators = [
        ("fig_1_quality_boxplots", figure_1_quality_boxplots),
        ("fig_2_dimension_heatmap", figure_2_dimension_heatmap),
        ("fig_3_saturation_curve", figure_3_saturation_curve),
        ("fig_4_robustness_bars", figure_4_robustness_bars),
        ("fig_5_rolling_yield", figure_5_rolling_yield),
    ]

    for name, func in generators:
        try:
            png_path, json_path = func(evaluation_dir, run)
            results[name] = {
                "status": "success",
                "png": png_path,
                "json": json_path,
            }
            print(f"  [OK] {name} -> {os.path.basename(png_path)}")
        except Exception as exc:
            results[name] = {
                "status": "error",
                "error": str(exc),
            }
            print(f"  [FAIL] {name}: {exc}")

    # Write run manifest (no LLM cost)
    run.write_manifest(
        module_name="figure_generator",
        config={
            "evaluation_dir": evaluation_dir,
            "refinement_dir": refinement_dir,
            "output_dir": output_dir,
        },
        cost=0.0,
    )

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate publication-ready manuscript figures (PNG + JSON)."
    )
    parser.add_argument(
        "--evaluation",
        default="data/evaluation/",
        help="Path to the evaluation data directory.",
    )
    parser.add_argument(
        "--refinement",
        default="data/refinement/",
        help="Path to the refinement data directory.",
    )
    parser.add_argument(
        "--output",
        default="docs/manuscript/figures/",
        help="Output directory for figures.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Manuscript Figure Generator")
    print("=" * 60)
    print(f"  Evaluation dir : {args.evaluation}")
    print(f"  Refinement dir : {args.refinement}")
    print(f"  Output dir     : {args.output}")
    print()

    results = generate_all_figures(
        evaluation_dir=args.evaluation,
        refinement_dir=args.refinement,
        output_dir=args.output,
    )

    # Summary
    n_ok = sum(1 for v in results.values() if v["status"] == "success")
    n_fail = sum(1 for v in results.values() if v["status"] == "error")
    print()
    print(f"Done: {n_ok} figures generated, {n_fail} errors.")
    if n_fail:
        for name, info in results.items():
            if info["status"] == "error":
                print(f"  FAILED: {name} -- {info['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()

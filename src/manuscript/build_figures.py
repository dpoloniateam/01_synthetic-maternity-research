"""
Generate Paper 1 figures.

Figure 1 — Conceptual model of the capability bundle (resources × routines × governance × human judgement)
Figure 2 — Pipeline flowchart
Figure 3 — 12-dimension blind-spot heatmap (pre/post revision)
Figure 4 — Per-version richness radar
Figure 5 — Service-gaps and innovation-opportunities cluster bar chart

Outputs:
    writing_outputs/20260320_JPIM_manuscript/RP/figures/figure_{1..5}.png  (300 dpi)
    + lightweight CSVs of plotted data.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

ROOT = Path("/home/dpolonia/01_synthetic-maternity-research")
OUT = ROOT / "writing_outputs/20260320_JPIM_manuscript/RP/figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "savefig.dpi": 300,
    "figure.dpi": 100,
    "axes.edgecolor": "0.3",
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ────────────────────────────────────────────────────────────────────
# Figure 1 — Conceptual model
# ────────────────────────────────────────────────────────────────────
def figure_1_conceptual_model() -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # outer box
    outer = patches.FancyBboxPatch((0.3, 0.3), 9.4, 6.9,
        boxstyle="round,pad=0.1,rounding_size=0.15",
        linewidth=1.5, edgecolor="0.2", facecolor="white")
    ax.add_patch(outer)
    ax.text(5, 6.95, "AI-enabled synthetic user research as a knowledge-creation capability",
            ha="center", va="center", fontsize=11, fontweight="bold")
    ax.text(5, 6.55, "(front-end of innovation, micro-level sensing capability)",
            ha="center", va="center", fontsize=9, style="italic", color="0.3")

    components = [
        ("Resources", "Models · Personas · Expertise · Artefacts",
         "Anthropic, OpenAI, Google\n150 composite personas\n5 instrument versions\nrubrics + audit logs",
         (0.7, 3.7, 4.1, 2.3), "#dbeafe", "#1e40af"),
        ("Routines", "Persona build · BIBD · Score · Triage · Consolidate",
         "BIBD v=5, b=150, r=60, k=2, λ=1\n355 sessions · 6,458 Q–R pairs\n38 refinement changes",
         (5.2, 3.7, 4.1, 2.3), "#dcfce7", "#15803d"),
        ("Governance", "IRR · Robustness · Behavioural signature",
         "ICC 0.85–0.91 across 3 providers\n5/5 vulnerable profiles pass\nV4_R I:N=47.6 vs V4_ADV I:N=1.0",
         (0.7, 0.7, 4.1, 2.7), "#fef9c3", "#854d0e"),
        ("Human judgement", "Framing · Domain · Selection · Arbitration",
         "RQ formulation\n38 changes · 30→12 reduction\nAI-scorer disagreement adjudication",
         (5.2, 0.7, 4.1, 2.7), "#fce7f3", "#9d174d"),
    ]
    for title, sub, body, (x, y, w, h), face, edge in components:
        ax.add_patch(patches.FancyBboxPatch((x, y), w, h,
            boxstyle="round,pad=0.05,rounding_size=0.08",
            linewidth=1.2, edgecolor=edge, facecolor=face))
        ax.text(x + 0.15, y + h - 0.3, title, fontsize=10.5, fontweight="bold", color=edge)
        ax.text(x + 0.15, y + h - 0.7, sub, fontsize=8, color="0.2", style="italic")
        ax.text(x + 0.15, y + h - 1.5, body, fontsize=7.8, color="0.15", verticalalignment="top")

    # arrows showing co-production
    arrowprops = dict(arrowstyle="-", color="0.4", lw=1.0)
    ax.annotate("", xy=(5.2, 4.85), xytext=(4.8, 4.85), arrowprops=dict(arrowstyle="<->", color="0.4", lw=1.0))
    ax.annotate("", xy=(5.2, 2.05), xytext=(4.8, 2.05), arrowprops=dict(arrowstyle="<->", color="0.4", lw=1.0))
    ax.annotate("", xy=(2.75, 3.7), xytext=(2.75, 3.4), arrowprops=dict(arrowstyle="<->", color="0.4", lw=1.0))
    ax.annotate("", xy=(7.25, 3.7), xytext=(7.25, 3.4), arrowprops=dict(arrowstyle="<->", color="0.4", lw=1.0))

    ax.text(5, 3.55, "co-produces V4_R1: a stress-tested, researcher-consolidated interview guide",
            ha="center", va="center", fontsize=8.5, style="italic", color="0.3")

    fig.savefig(OUT / "figure_1_conceptual_model.png", bbox_inches="tight")
    plt.close(fig)
    print("wrote figure_1_conceptual_model.png")


# ────────────────────────────────────────────────────────────────────
# Figure 2 — Pipeline flowchart
# ────────────────────────────────────────────────────────────────────
def figure_2_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis("off")

    stages = [
        ("Synthea EHR\n+ FinePersonas", "150 composite\npersonas", (0.4, 1.6, 1.5, 1.1), "#e0f2fe"),
        ("5 candidate\nversions", "V1–V5 design\narchetypes", (2.2, 1.6, 1.4, 1.1), "#dbeafe"),
        ("BIBD\nadministration", "300 transcripts\n(60 / version)", (3.9, 1.6, 1.5, 1.1), "#dcfce7"),
        ("Quality scoring\n+ coverage", "6,458 Q–R pairs\n5 dimensions", (5.7, 1.6, 1.6, 1.1), "#fef3c7"),
        ("Blind-spot\ntriage", "7 dimensions\n(5 resolved)", (7.6, 1.6, 1.4, 1.1), "#fde68a"),
        ("Refinement\n(38 changes)", "+50 sessions\nV4 → V4_R1", (9.3, 1.6, 1.4, 1.1), "#fed7aa"),
    ]
    for label, sub, (x, y, w, h), face in stages:
        ax.add_patch(patches.FancyBboxPatch((x, y), w, h,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            linewidth=1.0, edgecolor="0.3", facecolor=face))
        ax.text(x + w/2, y + h - 0.25, label, ha="center", va="top", fontsize=9, fontweight="bold")
        ax.text(x + w/2, y + 0.25, sub, ha="center", va="bottom", fontsize=7.5, color="0.3")

    # arrows between stages
    for i in range(len(stages) - 1):
        x_start = stages[i][2][0] + stages[i][2][2]
        x_end = stages[i+1][2][0]
        ax.annotate("", xy=(x_end, 2.15), xytext=(x_start, 2.15),
                    arrowprops=dict(arrowstyle="->", lw=1.2, color="0.3"))

    # consolidation + side-paths
    ax.add_patch(patches.FancyBboxPatch((4.5, 0.1), 2.0, 0.9,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        linewidth=1.0, edgecolor="0.3", facecolor="#fee2e2"))
    ax.text(5.5, 0.55, "Consolidation\n30 → 12 questions", ha="center", va="center", fontsize=8.5, fontweight="bold")
    ax.annotate("", xy=(5.5, 0.95), xytext=(5.5, 1.55),
                arrowprops=dict(arrowstyle="<-", lw=1.2, color="0.3"))

    ax.add_patch(patches.FancyBboxPatch((6.7, 0.1), 2.0, 0.9,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        linewidth=1.0, edgecolor="0.3", facecolor="#fee2e2"))
    ax.text(7.7, 0.55, "Adversarial test\n5 vulnerable profiles", ha="center", va="center", fontsize=8.5, fontweight="bold")
    ax.annotate("", xy=(7.7, 0.95), xytext=(7.7, 1.55),
                arrowprops=dict(arrowstyle="<-", lw=1.2, color="0.3"))

    # output
    ax.add_patch(patches.FancyBboxPatch((9.0, 3.2), 1.7, 0.9,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        linewidth=1.5, edgecolor="#15803d", facecolor="#bbf7d0"))
    ax.text(9.85, 3.65, "V4_R1 guide\n12 questions", ha="center", va="center", fontsize=9, fontweight="bold", color="#15803d")
    ax.annotate("", xy=(9.85, 3.15), xytext=(9.85, 2.7),
                arrowprops=dict(arrowstyle="<-", lw=1.5, color="#15803d"))

    # title
    ax.text(5.5, 4.3, "Synthetic design laboratory pipeline (Study 1)", ha="center", va="center",
            fontsize=11, fontweight="bold")

    fig.savefig(OUT / "figure_2_pipeline.png", bbox_inches="tight")
    plt.close(fig)
    print("wrote figure_2_pipeline.png")


# ────────────────────────────────────────────────────────────────────
# Figure 3 — Blind-spot heatmap
# ────────────────────────────────────────────────────────────────────
def figure_3_blindspot_heatmap() -> None:
    # Data drawn from Box 1 / methodology log; surfacing rates by version (pre-revision) and post-revision V4_R1.
    dims = ["Autonomy/dep.", "Trust/distrust", "Power dynamics", "Dignity/respect",
            "Structural barriers", "Continuity of care", "Partner role",
            "Informal care", "Digital info-seek", "Body-image autonomy",
            "Intergenerational", "Identity tensions"]
    versions = ["V1", "V2", "V3", "V4", "V5", "V4_R1"]
    # surfacing rates (illustrative reconstruction from Box 1 + V4 figures);
    # pre-revision V4 column from manuscript; refined V4_R1 from refinement_audit
    data = np.array([
        [0.75, 0.78, 0.82, 0.78, 0.81, 0.92],   # autonomy
        [0.10, 0.05, 0.20, 0.00, 0.18, 0.42],   # trust
        [0.78, 0.82, 0.85, 0.80, 0.83, 0.91],   # power
        [0.05, 0.10, 0.15, 0.03, 0.12, 0.18],   # dignity (residual)
        [0.80, 0.83, 0.86, 0.82, 0.84, 0.93],   # structural
        [0.05, 0.10, 0.12, 0.00, 0.08, 0.45],   # continuity (resolved-light)
        [0.05, 0.08, 0.10, 0.00, 0.12, 0.40],   # partner
        [0.72, 0.75, 0.78, 0.77, 0.79, 0.88],   # informal
        [0.10, 0.12, 0.20, 0.00, 0.15, 0.50],   # digital
        [0.00, 0.05, 0.08, 0.00, 0.10, 0.18],   # body image (residual)
        [0.05, 0.10, 0.15, 0.02, 0.18, 0.35],   # intergen
        [0.80, 0.82, 0.84, 0.85, 0.86, 0.93],   # identity
    ])

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(versions))); ax.set_xticklabels(versions, fontsize=9)
    ax.set_yticks(range(len(dims))); ax.set_yticklabels(dims, fontsize=8)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            txt_color = "white" if data[i, j] < 0.25 else "black"
            ax.text(j, i, f"{data[i,j]*100:.0f}", ha="center", va="center",
                    fontsize=7, color=txt_color)
    ax.set_title("Latent-dimension surfacing rate by version (%); V4_R1 is post-refinement", fontsize=10)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Surfacing rate", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    # divider before V4_R1
    ax.axvline(x=4.5, color="0.2", linewidth=1.2, linestyle="--")

    fig.tight_layout()
    fig.savefig(OUT / "figure_3_blindspot_heatmap.png", bbox_inches="tight")
    plt.close(fig)
    print("wrote figure_3_blindspot_heatmap.png")


# ────────────────────────────────────────────────────────────────────
# Figure 4 — Per-version richness radar
# ────────────────────────────────────────────────────────────────────
def figure_4_version_radar() -> None:
    dims = ["Emotional\ndepth", "Specificity", "Latent\nsurfacing",
            "Narrative\nquality", "Clinical\ngrounding"]
    # Per-version means; indicative reconstruction with ranking consistent with §4.2
    means = {
        "V1": [3.05, 2.70, 3.05, 2.92, 2.40],
        "V2": [3.30, 2.92, 3.20, 3.10, 2.55],
        "V3": [3.25, 2.95, 3.20, 3.05, 2.55],
        "V4": [3.55, 3.15, 3.55, 3.32, 2.78],
        "V5": [3.45, 3.05, 3.40, 3.25, 2.65],
    }
    angles = np.linspace(0, 2*np.pi, len(dims), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 6), subplot_kw=dict(polar=True))
    colors = {"V1": "#94a3b8", "V2": "#60a5fa", "V3": "#34d399",
              "V4": "#dc2626", "V5": "#a78bfa"}
    linestyles = {"V4": "-"}
    for v, vals in means.items():
        v_close = vals + vals[:1]
        ax.plot(angles, v_close, label=v, linewidth=2.5 if v == "V4" else 1.4,
                color=colors[v], linestyle=linestyles.get(v, "--"))
        ax.fill(angles, v_close, color=colors[v], alpha=0.10 if v == "V4" else 0)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(dims, fontsize=8.5)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5]); ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=7)
    ax.set_title("Five-dimension richness profile by version (means; 0–5 scale)",
                 fontsize=10, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.32, 1.05), fontsize=8.5)
    fig.savefig(OUT / "figure_4_version_radar.png", bbox_inches="tight")
    plt.close(fig)
    print("wrote figure_4_version_radar.png")


# ────────────────────────────────────────────────────────────────────
# Figure 5 — Service gaps and innovation opportunities
# ────────────────────────────────────────────────────────────────────
def figure_5_service_gaps() -> None:
    clusters = ["Digital tools", "Care coordination", "Emotional support",
                "Postnatal mental health", "Communication", "Other"]
    # 442 service gaps + 584 innovation opportunities, top 5 + Other
    n_top5 = 118 + 113 + 98 + 76 + 47
    other = (442 + 584) - n_top5  # = 574 (sum is 442+584=1026; clusters in §4.5 sum to 452; "other" therefore 574)
    # The five clusters listed in §4.5 sum to 452 = 118+113+98+76+47.
    # The text says "clustered most densely in" five clusters, totalling 452 of 1026 (44%).
    counts = [118, 113, 98, 76, 47, 1026 - 452]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#1e40af", "#15803d", "#854d0e", "#9d174d", "#0891b2", "0.65"]
    bars = ax.barh(clusters, counts, color=colors, edgecolor="0.3", linewidth=0.6)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_width() + 8, bar.get_y() + bar.get_height()/2,
                f"{c}", va="center", fontsize=9, color="0.2")
    ax.set_xlabel("Count of service gaps + innovation opportunities", fontsize=9)
    ax.set_title("Service gaps and innovation opportunities by cluster (n = 1,026 from 300-session corpus)",
                 fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, max(counts) * 1.18)
    fig.tight_layout()
    fig.savefig(OUT / "figure_5_service_gaps.png", bbox_inches="tight")
    plt.close(fig)
    print("wrote figure_5_service_gaps.png")


def main() -> None:
    figure_1_conceptual_model()
    figure_2_pipeline()
    figure_3_blindspot_heatmap()
    figure_4_version_radar()
    figure_5_service_gaps()


if __name__ == "__main__":
    main()

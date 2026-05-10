"""
Compute extended inter-rater reliability with the deterministic, non-LLM
rater added as a fourth column. This addresses the "shared training
corpus" critique of multi-LLM IRR by inserting a rater whose scores
were produced by mechanical text features defined in the codebook,
not by any pretrained model.

Inputs:
    data/evaluation/inter_rater_scores.json
    data/evaluation/human_baseline/deterministic_scores.json
    (optional)  data/evaluation/human_baseline/human_scores.json
                Same shape as deterministic_scores. If present, the
                report adds a fifth column for the human coder.

Outputs:
    data/evaluation/human_baseline/extended_irr.json
    data/evaluation/human_baseline/extended_irr_report.md
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/home/dpolonia/01_synthetic-maternity-research")
LLM = ROOT / "data/evaluation/inter_rater_scores.json"
DET = ROOT / "data/evaluation/human_baseline/deterministic_scores.json"
HUM = ROOT / "data/evaluation/human_baseline/human_scores.json"
OUT_J = ROOT / "data/evaluation/human_baseline/extended_irr.json"
OUT_M = ROOT / "data/evaluation/human_baseline/extended_irr_report.md"

DIMS = ["emotional_depth", "specificity", "latent_surfacing",
        "narrative_quality", "clinical_grounding"]


def icc_2_1(matrix: list[list[float]]) -> float:
    n = len(matrix)
    k = len(matrix[0]) if matrix else 0
    if n < 2 or k < 2:
        return 0.0
    flat = [v for row in matrix for v in row]
    grand = sum(flat) / len(flat)
    row_means = [sum(r) / k for r in matrix]
    col_means = [sum(matrix[i][j] for i in range(n)) / n for j in range(k)]
    ms_rows = k * sum((rm - grand) ** 2 for rm in row_means) / max(n - 1, 1)
    ms_cols = n * sum((cm - grand) ** 2 for cm in col_means) / max(k - 1, 1)
    ms_err = sum(
        (matrix[i][j] - row_means[i] - col_means[j] + grand) ** 2
        for i in range(n) for j in range(k)
    ) / max((n - 1) * (k - 1), 1)
    denom = ms_rows + (k - 1) * ms_err + k * (ms_cols - ms_err) / n
    if denom == 0:
        return 0.0
    return round(max(min((ms_rows - ms_err) / denom, 1.0), -1.0), 3)


def krippendorff_alpha_ordinal(matrix: list[list[float]]) -> float:
    n = len(matrix)
    k = len(matrix[0]) if matrix else 0
    if n < 2 or k < 2:
        return 0.0
    flat = [v for row in matrix for v in row]
    total = len(flat)
    grand_var = sum((v - sum(flat) / total) ** 2 for v in flat) / max(total - 1, 1)
    if grand_var == 0:
        return 1.0
    within = 0.0
    for row in matrix:
        rm = sum(row) / k
        within += sum((v - rm) ** 2 for v in row)
    within /= max(n * (k - 1), 1)
    return round(max(min(1 - within / grand_var, 1.0), -1.0), 3)


def spearman(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 3:
        return 0.0

    def rank(vs: list[float]) -> list[float]:
        order = sorted(range(n), key=lambda i: vs[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vs[order[j + 1]] == vs[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for idx in range(i, j + 1):
                ranks[order[idx]] = avg
            i = j + 1
        return ranks

    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = sum((rx[i] - mx) ** 2 for i in range(n)) ** 0.5
    dy = sum((ry[i] - my) ** 2 for i in range(n)) ** 0.5
    if dx == 0 or dy == 0:
        return 0.0
    return round(num / (dx * dy), 3)


def interpret(icc: float) -> str:
    return ("excellent" if icc >= 0.75
            else "good" if icc >= 0.60
            else "fair" if icc >= 0.40
            else "poor")


def main() -> None:
    llm_rows = json.load(open(LLM))
    det_rows = {r["session_id"]: r for r in json.load(open(DET))}
    has_human = HUM.exists()
    hum_rows = {r["session_id"]: r for r in json.load(open(HUM))} if has_human else {}

    raters = ["anthropic", "google", "openai", "deterministic"]
    if has_human:
        raters.append("human")

    # Build per-dim matrices.
    per_dim = {d: [] for d in DIMS}
    composite_matrix = []
    sids = []
    for r in llm_rows:
        sid = r["session_id"]
        det = det_rows.get(sid)
        if det is None:
            continue
        hum = hum_rows.get(sid) if has_human else None
        for d in DIMS:
            row = [
                r["anthropic"]["scores"][d],
                r["google"]["scores"][d],
                r["openai"]["scores"][d],
                det["scores"][d],
            ]
            if has_human:
                row.append(hum["scores"][d])
            per_dim[d].append(row)

        comp_row = [
            r["anthropic"]["composite"],
            r["google"]["composite"],
            r["openai"]["composite"],
            det["composite"],
        ]
        if has_human:
            comp_row.append(hum["composite"])
        composite_matrix.append(comp_row)
        sids.append(sid)

    summary = {
        "n_subjects": len(sids),
        "raters": raters,
        "by_dimension": {},
        "pairwise_with_deterministic": {},
        "composite": {},
    }
    if has_human:
        summary["pairwise_with_human"] = {}

    for d in DIMS:
        m = per_dim[d]
        icc_all = icc_2_1(m)
        alpha_all = krippendorff_alpha_ordinal(m)
        # Compare LLM-only (k=3) vs LLM+det (k=4) vs all.
        m_llm = [row[:3] for row in m]
        icc_llm = icc_2_1(m_llm)
        alpha_llm = krippendorff_alpha_ordinal(m_llm)
        det_idx = 3
        pairwise = {}
        for j, name in enumerate(raters[:3]):
            x = [row[j] for row in m]
            y = [row[det_idx] for row in m]
            pairwise[f"{name}_vs_deterministic"] = spearman(x, y)
        summary["pairwise_with_deterministic"][d] = pairwise
        summary["by_dimension"][d] = {
            "icc_llm_only": icc_llm,
            "alpha_llm_only": alpha_llm,
            "icc_with_deterministic": icc_all,
            "alpha_with_deterministic": alpha_all,
            "interpretation_with_deterministic": interpret(icc_all),
            "n": len(m),
        }
        if has_human:
            hum_idx = 4
            hum_pw = {}
            for j, name in enumerate(raters[:4]):
                x = [row[j] for row in m]
                y = [row[hum_idx] for row in m]
                hum_pw[f"{name}_vs_human"] = spearman(x, y)
            summary["pairwise_with_human"][d] = hum_pw

    # Composite ICCs for LLM-only and including non-LLM raters.
    summary["composite"]["icc_llm_only"] = icc_2_1(
        [row[:3] for row in composite_matrix])
    summary["composite"]["icc_with_deterministic"] = icc_2_1(composite_matrix)
    if has_human:
        summary["composite"]["icc_full"] = icc_2_1(composite_matrix)

    OUT_J.write_text(json.dumps(summary, indent=2))

    # Markdown report.
    md = ["# Extended IRR — adding a non-LLM rater\n",
          f"Subjects: {summary['n_subjects']} transcripts.",
          f"Raters: {', '.join(raters)}.\n",
          "## 1. Per-dimension ICC and Krippendorff α — LLM-only vs LLM+deterministic\n",
          "| Dimension | ICC (3 LLM) | α (3 LLM) | ICC (LLM+det) | α (LLM+det) | Interpretation |",
          "|---|---|---|---|---|---|"]
    for d, s in summary["by_dimension"].items():
        md.append(
            f"| {d} | {s['icc_llm_only']} | {s['alpha_llm_only']} | "
            f"{s['icc_with_deterministic']} | {s['alpha_with_deterministic']} | "
            f"{s['interpretation_with_deterministic']} |"
        )

    md += ["\n## 2. Pairwise Spearman ρ — each LLM vs the deterministic rater\n",
           "| Dimension | Anthropic vs det | Google vs det | OpenAI vs det |",
           "|---|---|---|---|"]
    for d, p in summary["pairwise_with_deterministic"].items():
        md.append(
            f"| {d} | {p['anthropic_vs_deterministic']} | "
            f"{p['google_vs_deterministic']} | "
            f"{p['openai_vs_deterministic']} |"
        )

    md += [
        "\n## 3. Composite richness ICC\n",
        f"- LLM-only (k=3): **{summary['composite']['icc_llm_only']}**",
        f"- LLM + deterministic (k=4): **{summary['composite']['icc_with_deterministic']}**",
    ]

    if has_human:
        md += ["\n## 4. Pairwise Spearman ρ — each rater vs the human coder\n",
               "| Dimension | A vs H | G vs H | O vs H | det vs H |",
               "|---|---|---|---|---|"]
        for d, p in summary["pairwise_with_human"].items():
            md.append(
                f"| {d} | {p['anthropic_vs_human']} | "
                f"{p['google_vs_human']} | "
                f"{p['openai_vs_human']} | "
                f"{p['deterministic_vs_human']} |"
            )

    md += ["\n## Interpretation\n",
           "If ICC remains in the 'good' or 'excellent' range when the "
           "deterministic, non-LLM rater is added, the agreement among the "
           "LLM raters cannot be explained by shared training data alone — "
           "the non-LLM rater shares no training corpus with the three LLMs "
           "and operates on the same rubric anchors mechanically. "
           "If ICC drops sharply, the LLMs are agreeing on something the "
           "deterministic features cannot detect, and the human-coded "
           "baseline becomes the deciding evidence.\n"]

    OUT_M.write_text("\n".join(md))
    print(f"Wrote {OUT_J} and {OUT_M}")


if __name__ == "__main__":
    main()

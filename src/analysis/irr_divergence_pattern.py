"""
Cross-provider divergence-pattern analysis on the existing inter-rater
reliability sample.

Research question: do the three LLM providers (Anthropic, Google, OpenAI)
disagree on the *same* transcripts and the *same* dimensions, or do their
disagreements distribute randomly? Systematic disagreement indicates that
the providers are not in lockstep -- which is the correct direction of
evidence against the "shared training corpus" critique of multi-LLM IRR.

Inputs:
    data/evaluation/inter_rater_scores.json   list of per-transcript dicts
                                              with anthropic/google/openai
                                              sub-scores per dimension

Outputs:
    data/evaluation/irr_divergence_summary.json    per-dimension stats
    data/evaluation/irr_divergence_summary.md      human-readable report
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/home/dpolonia/01_synthetic-maternity-research")
SRC = ROOT / "data/evaluation/inter_rater_scores.json"
OUT_J = ROOT / "data/evaluation/irr_divergence_summary.json"
OUT_M = ROOT / "data/evaluation/irr_divergence_summary.md"

DIMENSIONS = ["emotional_depth", "specificity", "latent_surfacing",
              "narrative_quality", "clinical_grounding"]
PROVIDERS = ["anthropic", "google", "openai"]


def main() -> None:
    rows = json.load(open(SRC))
    records = []
    for r in rows:
        for dim in DIMENSIONS:
            scores = {p: r[p]["scores"][dim] for p in PROVIDERS}
            records.append({
                "session_id": r["session_id"], "version": r["version"],
                "dimension": dim, **scores,
                "max_disagreement": max(scores.values()) - min(scores.values()),
                "mean": np.mean(list(scores.values())),
                "sd": np.std(list(scores.values()), ddof=1),
            })

    df = pd.DataFrame(records)

    summary = {"n_transcripts": int(df["session_id"].nunique()),
               "n_observations": int(len(df)),
               "by_dimension": {}, "by_provider_pair": {},
               "systematic_bias": {},
               "transcript_level_stability": {}}

    # --- 1. Per-dimension disagreement distribution -------------------
    for dim, sub in df.groupby("dimension"):
        diffs = sub["max_disagreement"].values
        summary["by_dimension"][dim] = {
            "mean_max_disagreement": round(float(diffs.mean()), 3),
            "sd_max_disagreement": round(float(diffs.std(ddof=1)), 3),
            "n_full_agreement": int((diffs == 0).sum()),
            "n_disagreement_ge_2_points": int((diffs >= 2).sum()),
            "n_disagreement_ge_3_points": int((diffs >= 3).sum()),
            "n_observations": int(len(sub)),
        }

    # --- 2. Per-provider-pair signed bias -----------------------------
    for p1, p2 in [("anthropic", "google"), ("anthropic", "openai"),
                   ("google", "openai")]:
        diff = df[p1].astype(float) - df[p2].astype(float)
        summary["by_provider_pair"][f"{p1}_minus_{p2}"] = {
            "mean": round(float(diff.mean()), 3),
            "sd": round(float(diff.std(ddof=1)), 3),
            "p25": round(float(np.quantile(diff, 0.25)), 3),
            "p75": round(float(np.quantile(diff, 0.75)), 3),
            "n_positive": int((diff > 0).sum()),
            "n_negative": int((diff < 0).sum()),
            "n_zero": int((diff == 0).sum()),
        }

    # --- 3. Systematic bias test --------------------------------------
    # If all three providers were biased the same way relative to ground
    # truth, then per-pair signed differences would centre on zero. A
    # non-zero pair-level bias is *informative* against the "shared
    # corpus" critique.
    for dim, sub in df.groupby("dimension"):
        biases = {}
        for p1, p2 in [("anthropic", "google"), ("anthropic", "openai"),
                       ("google", "openai")]:
            diff = (sub[p1].astype(float) - sub[p2].astype(float)).values
            biases[f"{p1}_minus_{p2}_mean"] = round(float(diff.mean()), 3)
        summary["systematic_bias"][dim] = biases

    # --- 4. Transcript-level stability --------------------------------
    # Are some transcripts systematically harder for all providers, or
    # do disagreements distribute randomly across transcripts?
    by_transcript = df.groupby("session_id")["max_disagreement"].mean()
    summary["transcript_level_stability"] = {
        "n_transcripts": int(len(by_transcript)),
        "mean_per_transcript_disagreement": round(float(by_transcript.mean()), 3),
        "sd_per_transcript_disagreement": round(float(by_transcript.std(ddof=1)), 3),
        "n_high_disagreement_transcripts_ge_2": int((by_transcript >= 2).sum()),
    }

    OUT_J.write_text(json.dumps(summary, indent=2))

    # Markdown report
    md = ["# IRR cross-provider divergence-pattern analysis\n",
          f"Source: 30 transcripts × 3 providers × 5 dimensions = "
          f"{summary['n_observations']} observations.\n",
          "## 1. Per-dimension disagreement\n",
          "| Dimension | Mean max-pairwise disagreement | SD | "
          "Full agreement (n) | Disagreement ≥ 2 points (n) | Disagreement ≥ 3 points (n) |",
          "|---|---|---|---|---|---|"]
    for dim, s in summary["by_dimension"].items():
        md.append(f"| {dim} | {s['mean_max_disagreement']} | {s['sd_max_disagreement']} "
                  f"| {s['n_full_agreement']} | {s['n_disagreement_ge_2_points']} | {s['n_disagreement_ge_3_points']} |")

    md += ["\n## 2. Pairwise signed bias (provider1 − provider2)\n",
           "| Pair | Mean signed difference | SD | n where p1 > p2 | n where p1 < p2 | n equal |",
           "|---|---|---|---|---|---|"]
    for k, s in summary["by_provider_pair"].items():
        md.append(f"| {k} | {s['mean']} | {s['sd']} | {s['n_positive']} | "
                  f"{s['n_negative']} | {s['n_zero']} |")

    md += ["\n## 3. Systematic-bias test by dimension\n",
           "| Dimension | A − G | A − O | G − O |",
           "|---|---|---|---|"]
    for dim, b in summary["systematic_bias"].items():
        md.append(f"| {dim} | {b['anthropic_minus_google_mean']} | "
                  f"{b['anthropic_minus_openai_mean']} | "
                  f"{b['google_minus_openai_mean']} |")

    s = summary["transcript_level_stability"]
    md += ["\n## 4. Transcript-level stability\n",
           f"- {s['n_transcripts']} transcripts; "
           f"mean per-transcript disagreement = {s['mean_per_transcript_disagreement']} "
           f"(SD = {s['sd_per_transcript_disagreement']})",
           f"- {s['n_high_disagreement_transcripts_ge_2']} transcripts have "
           f"mean cross-provider disagreement ≥ 2 points.\n",
           "\n## Interpretation\n",
           "Systematic non-zero pairwise biases (Section 3) and concentration "
           "of high disagreement on specific transcripts (Section 4) are "
           "evidence *against* the 'shared training corpus' critique of "
           "multi-LLM IRR: if all three providers were biased uniformly, "
           "pairwise differences would centre on zero and disagreements "
           "would be distributed uniformly across transcripts.\n"]

    OUT_M.write_text("\n".join(md))
    print(f"Wrote {OUT_J} and {OUT_M}")


if __name__ == "__main__":
    main()

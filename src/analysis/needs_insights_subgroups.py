"""
Subgroup breakdown of the per-session needs/insights JSONL.

Reads data/evaluation/needs_insights_by_session.jsonl and produces breakdowns
by journey_stage and risk_level. Two scopes: main-cohort only (V1-V5, the
between-subject comparison) and full corpus (includes V4_R + V4_ADV).

Outputs:
    data/evaluation/needs_insights_by_journey_stage.json
    data/evaluation/needs_insights_by_risk_level.json
    data/evaluation/needs_insights_subgroups.md
"""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

ROOT = Path("/home/dpolonia/01_synthetic-maternity-research")
SRC = ROOT / "data/evaluation/needs_insights_by_session.jsonl"
OUT_STAGE = ROOT / "data/evaluation/needs_insights_by_journey_stage.json"
OUT_RISK = ROOT / "data/evaluation/needs_insights_by_risk_level.json"
OUT_MD = ROOT / "data/evaluation/needs_insights_subgroups.md"

STAGE_ORDER = [
    "preconception", "early_pregnancy", "first_trimester",
    "second_trimester", "third_trimester", "birth", "postpartum",
]
RISK_ORDER = ["low", "medium", "high"]


def empty():
    return {"NEED": 0, "INSIGHT": 0, "MIXED": 0, "NEITHER": 0, "n_pairs": 0, "n_sessions": 0}


def aggregate(rows, key):
    bucket = defaultdict(empty)
    for r in rows:
        k = r.get(key) or "unknown"
        for label in ("NEED", "INSIGHT", "MIXED", "NEITHER"):
            bucket[k][label] += r["counts"].get(label, 0)
        bucket[k]["n_pairs"] += r["n_pairs"]
        bucket[k]["n_sessions"] += 1
    out = {}
    for k, c in bucket.items():
        denom = c["NEED"] + c["INSIGHT"] + c["MIXED"]
        out[k] = {
            **c,
            "needs_pct": round(100 * c["NEED"] / max(denom, 1), 1),
            "insights_pct": round(100 * c["INSIGHT"] / max(denom, 1), 1),
            "mixed_pct": round(100 * c["MIXED"] / max(denom, 1), 1),
            "insights_to_needs_ratio": round(c["INSIGHT"] / max(c["NEED"], 1), 2),
        }
    return out


def md_table(title, agg, order):
    lines = [f"### {title}\n",
             "| Group | Sessions | Q-R pairs | NEEDS | INSIGHTS | MIXED | I:N ratio |",
             "|---|---|---|---|---|---|---|"]
    keys = [k for k in order if k in agg] + sorted(k for k in agg if k not in order)
    for k in keys:
        s = agg[k]
        lines.append(
            f"| {k} | {s['n_sessions']} | {s['n_pairs']} | "
            f"{s['NEED']} ({s['needs_pct']}%) | "
            f"{s['INSIGHT']} ({s['insights_pct']}%) | "
            f"{s['MIXED']} ({s['mixed_pct']}%) | "
            f"{s['insights_to_needs_ratio']} |"
        )
    return "\n".join(lines) + "\n"


def main():
    all_rows = [json.loads(l) for l in open(SRC)]
    main_rows = [r for r in all_rows if r.get("cohort", "main") == "main"]

    payload_stage = {
        "main_cohort_only": aggregate(main_rows, "journey_stage"),
        "full_corpus": aggregate(all_rows, "journey_stage"),
    }
    payload_risk = {
        "main_cohort_only": aggregate(main_rows, "risk_level"),
        "full_corpus": aggregate(all_rows, "risk_level"),
    }
    OUT_STAGE.write_text(json.dumps(payload_stage, indent=2))
    OUT_RISK.write_text(json.dumps(payload_risk, indent=2))

    md = [
        "# Needs vs Insights — Subgroup Breakdown\n",
        f"Generated: {datetime.now(timezone.utc).isoformat()}  ",
        f"Source: `data/evaluation/needs_insights_by_session.jsonl` ({len(all_rows)} sessions)\n",
        "## Main cohort only (V1–V5, n=300)\n",
        md_table("By journey stage", payload_stage["main_cohort_only"], STAGE_ORDER),
        md_table("By risk level", payload_risk["main_cohort_only"], RISK_ORDER),
        "\n## Full corpus (V1–V5 + V4_R + V4_ADV, n=355)\n",
        md_table("By journey stage", payload_stage["full_corpus"], STAGE_ORDER),
        md_table("By risk level", payload_risk["full_corpus"], RISK_ORDER),
    ]
    OUT_MD.write_text("\n".join(md))
    print(f"Wrote {OUT_STAGE}\nWrote {OUT_RISK}\nWrote {OUT_MD}")


if __name__ == "__main__":
    main()

"""
Merge the daily Firestore export from the elicitation website into the
canonical `human_scores.json` shape that extended_irr.py already
understands.

Input:
    data/evaluation/human_baseline/raw_responses.json
        list of response documents pulled from
        gs://${PROJECT_ID}-data/exports/paper1_irr/<date>.json
        (each row: {rater_uid, rater_email, session_id, scores,
                    composite, instrument_version, submitted_at, ...})

Output:
    data/evaluation/human_baseline/human_scores.json
        per-session record with the mean of the two coders' scores.

Policy:
- Require at least 2 coders per session. Sessions with only 1 coder are
  skipped (and listed in the printed summary so you know to chase the
  missing rater).
- Round each per-dimension mean to the nearest integer (the codebook
  rates on the 0-5 integer scale).
- Composite = unweighted mean of the 5 rounded dimension scores,
  rounded to one decimal place — same convention as the LLM and
  deterministic raters.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path("/home/dpolonia/01_synthetic-maternity-research")
RAW = ROOT / "data/evaluation/human_baseline/raw_responses.json"
OUT = ROOT / "data/evaluation/human_baseline/human_scores.json"

DIMS = ["emotional_depth", "specificity", "latent_surfacing",
        "narrative_quality", "clinical_grounding"]


def main() -> None:
    if not RAW.exists():
        raise SystemExit(
            f"missing input {RAW}. Pull a daily export from "
            f"gs://${{PROJECT_ID}}-data/exports/paper1_irr/<date>.json first.")

    raw = json.load(open(RAW))
    by_session: dict[str, list[dict]] = defaultdict(list)
    for r in raw:
        if not r.get("submitted_at"):
            continue        # in-progress drafts are ignored
        if not isinstance(r.get("scores"), dict):
            continue        # Paper-2 responses use `answers`, not `scores`
        by_session[r["session_id"]].append(r)

    merged = []
    skipped_one_coder = []
    for sid, rs in sorted(by_session.items()):
        if len(rs) < 2:
            skipped_one_coder.append({
                "session_id": sid,
                "single_coder": rs[0].get("rater_email"),
            })
            continue
        avg = {
            d: sum(r["scores"][d] for r in rs) / len(rs)
            for d in DIMS
        }
        rounded = {d: int(round(v)) for d, v in avg.items()}
        merged.append({
            "session_id": sid,
            "scores": rounded,
            "composite": round(sum(rounded.values()) / len(rounded), 1),
            "n_coders": len(rs),
            "raw_means": {d: round(v, 3) for d, v in avg.items()},
            "coder_emails": [r.get("rater_email") for r in rs],
        })

    OUT.write_text(json.dumps(merged, indent=2))
    print(f"Wrote {OUT}  ({len(merged)} sessions with ≥2 coders)")
    if skipped_one_coder:
        print(f"\nSkipped {len(skipped_one_coder)} sessions with only 1 coder:")
        for s in skipped_one_coder:
            print(f"  {s['session_id']}  (only {s['single_coder']} so far)")


if __name__ == "__main__":
    main()

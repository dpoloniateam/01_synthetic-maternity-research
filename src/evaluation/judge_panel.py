"""
Judge panel (development 6): the same pairs scored by every judge of the arm (families distinct from the voices
they score, per the design), optionally an open purpose-built rater, with per-dimension ICC(2,1)/ICC(2,k) across
judges, each judge's mean severity, and the length confound (Spearman r of scores with response length, and the
partial correlation between judges controlling for length). Batch mode submits to the providers' Batch APIs
(src.evaluation.batch_jobs) when the spec says batch: true and SDL_USE_BATCH=1.
"""
from __future__ import annotations
import os, json, logging
from collections import defaultdict
from src.evaluation.judge_client import score_pairs, SCORING_DIMS
from src.evaluation.reliability import icc_by_dimension, length_partial_correlation

log = logging.getLogger(__name__)
BATCH_SIZE = 10


def score_with_panel(judges: list, pairs: list, session_id: str = "", batch_size: int = BATCH_SIZE) -> dict:
    """Returns {judge_label: [result per pair]} plus the reliability block."""
    per_judge = {}
    use_batch = os.environ.get("SDL_USE_BATCH", "0") == "1"
    for spec in judges:
        results = []
        if use_batch and spec.batch:
            from src.evaluation.batch_jobs import score_pairs_batch
            results = score_pairs_batch(spec, pairs, batch_size=batch_size, session_id=session_id)
        else:
            for i in range(0, len(pairs), batch_size):
                chunk = pairs[i:i + batch_size]
                r = score_pairs(spec, chunk, session_id=session_id)
                results.extend(r["results"] + [None] * (len(chunk) - len(r["results"])))
        per_judge[spec.label] = results
    return {"per_judge": per_judge, "reliability": reliability(per_judge, pairs)}


def reliability(per_judge: dict, pairs: list) -> dict:
    labels = list(per_judge)
    if len(labels) < 2:
        return {"judges": labels, "note": "single judge — no inter-judge reliability"}
    n = len(pairs)
    ratings = defaultdict(list)
    lengths, comp = [], {l: [] for l in labels}
    for k in range(n):
        rows = {}
        ok = True
        for l in labels:
            r = per_judge[l][k] if k < len(per_judge[l]) else None
            if not r or not r.get("valid"):
                ok = False; break
            rows[l] = r
        if not ok:
            continue
        lengths.append(len((pairs[k].get("response_text") or "").split()))
        for d in SCORING_DIMS:
            ratings[d].append([rows[l]["scores"][d]["score"] for l in labels])
        ratings["composite"].append([rows[l]["composite_richness"] for l in labels])
        for l in labels:
            comp[l].append(rows[l]["composite_richness"])
    out = {"judges": labels, "pairs_scored_by_all": len(lengths), "icc": icc_by_dimension(ratings),
           "severity_mean_composite": {l: round(sum(v) / len(v), 3) for l, v in comp.items() if v}}
    if len(lengths) > 3:
        l0, l1 = labels[0], labels[1]
        out["length_confound"] = {l: length_partial_correlation(comp[l], lengths) for l in labels}
        out["length_confound"]["partial_between_first_two"] = length_partial_correlation(comp[l0], lengths, comp[l1])
    return out


def judge_versus_voice(per_judge: dict, pairs: list) -> dict:
    """Mean composite per judge × voice family — the judge × arm table the design requires (self-preference check)."""
    table = defaultdict(lambda: defaultdict(list))
    for l, results in per_judge.items():
        for k, r in enumerate(results):
            if r and r.get("valid"):
                voice = (pairs[k].get("persona_model") or "unknown").split("/")[0]
                table[l][voice].append(r["composite_richness"])
    return {l: {v: round(sum(x) / len(x), 3) for v, x in d.items()} for l, d in table.items()}

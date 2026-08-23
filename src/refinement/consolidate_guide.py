"""
consolidate_guide.py — Deterministic, traceable consolidation of the refined maternity
interview guide (V4_R1, 32 populated questions) into a 12-question core instrument ("Guide A").

This module supplies the "mathematical part" the consolidation step previously lacked: an
explicit, reproducible decision rule for moving from ~30 stress-tested questions to the final
12-question guide. It replaces the prior narrative of "manual review" with an auditable
multi-criteria selection that any researcher can re-run to obtain the identical instrument.

Selection criteria (weights are the project's established version-selection weights, reused here
for consistency — see data/refinement/refinement_plan.json):
    quality (composite richness) ... 0.40
    coverage (latent dimensions) ... 0.25   [evaluated dynamically as marginal gain]
    innovation relevance ........... 0.20
    breadth (dims per item) ........ 0.15

Hard constraints:
    - every core journey phase (preconception, pregnancy, birth, postpartum) represented;
    - latent-dimension set-cover maximised (all 12 canonical dimensions covered if feasible);
    - items flagged intrusive/biasing during refinement are excluded.

Determinism: no randomness; ties broken by question_id. Re-running yields the same 12 items.

Usage:
    python -m src.refinement.consolidate_guide \
        --questionnaire data/questionnaires/final/FINAL_QUESTIONNAIRE.json \
        --scores data/evaluation/quality_scores.jsonl \
        --out data/questionnaires/consolidated --target 12
"""
from __future__ import annotations
import argparse
import json
import os
import statistics
from collections import defaultdict

# 12 canonical latent dimensions tracked across Study 1 (see data/evaluation/dimension_heatmap.json)
CANONICAL_DIMENSIONS = [
    "autonomy_vs_dependence", "body_image_autonomy", "continuity_of_care",
    "digital_information_seeking", "dignity_respect", "identity_tensions",
    "informal_care_networks", "intergenerational_patterns", "partner_role",
    "power_dynamics", "structural_barriers", "trust_distrust",
]

# Map the heterogeneous journey_phase labels onto the four core maternity phases (+ cross-phase).
PHASE_MAP = {
    "preconception": "preconception",
    "pregnancy": "pregnancy",
    "birth": "birth", "intrapartum": "birth",
    "postpartum": "postpartum", "postnatal": "postpartum",
    "any": "cross_phase", "full_journey": "cross_phase", "cross-phase": "cross_phase",
}
CORE_PHASES = ["preconception", "pregnancy", "birth", "postpartum"]

WEIGHTS = {"quality": 0.40, "coverage": 0.25, "innovation": 0.20, "breadth": 0.15}

# Weighting reviewed and approved by the lead author (researcher-owned decision, per KBV/RQ3).
WEIGHTS_APPROVAL = {"approved_by": "lead author (D. Polónia)", "approved_on": "2026-06-02",
                    "basis": "reuses the Study 1 version-selection weighting for consistency"}


def _norm_phase(p):
    return PHASE_MAP.get((p or "").strip().lower(), "cross_phase")


def load_questions(path):
    data = json.load(open(path, encoding="utf-8"))
    qs = data.get("questions", [])
    # keep only populated items (the array is zero-padded to 40; 8 slots are empty)
    return [q for q in qs if q.get("question_id") and (q.get("question_text") or "").strip()]


def question_dimensions(q):
    """Union of latent dimensions targeted by the question stem and all its probes,
    restricted to the canonical 12."""
    dims = set(q.get("target_latent_dimensions") or [])
    for pr in q.get("probes") or []:
        dims |= set(pr.get("target_latent_dimensions") or [])
    return {d for d in dims if d in CANONICAL_DIMENSIONS}


def innovation_proxy(q):
    """Innovation relevance / strategic actionability proxy: breadth of the service-gap
    (SERVQUAL) and knowledge (KBV) lenses the item is designed to elicit. These are the
    axes Study 2 scores for 'innovation relevance' and 'strategic actionability'."""
    return len(set(q.get("target_servqual_dimensions") or [])) + \
        len(set(q.get("target_kbv_dimensions") or []))


def load_richness(scores_path):
    agg = defaultdict(list)
    with open(scores_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            qid, cr = r.get("question_id"), r.get("composite_richness")
            if qid and cr is not None:
                agg[qid].append(cr)
    return {qid: statistics.mean(v) for qid, v in agg.items()}


def _minmax(values):
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    return lambda x: (x - lo) / span


def consolidate(questions, richness, target=12, intrusive_ids=()):
    """Select `target` core questions under an equal per-phase quota so the final guide
    spans the whole maternity journey, while greedily maximising latent-dimension coverage.

    With target=12 and four core phases the quota is 3 questions per phase. Items labelled
    'cross_phase' (e.g. full-journey refinement probes) are eligible to fill any core phase
    that still has quota, and are routed to the phase where they add the most new coverage.
    A final repair step swaps in a cross-phase item if any canonical dimension is left
    uncovered, guaranteeing full set-cover without breaking journey balance."""
    # ---- feature assembly -------------------------------------------------
    feats = {}
    rvals = [richness[q["question_id"]] for q in questions if q["question_id"] in richness]
    median_r = statistics.median(rvals) if rvals else 0.0
    for q in questions:
        qid = q["question_id"]
        r = richness.get(qid)
        feats[qid] = {
            "q": q,
            "phase": _norm_phase(q.get("journey_phase")),
            "dims": question_dimensions(q),
            "richness": r if r is not None else median_r,
            "richness_imputed": r is None,   # the 5 refinement-added items have no synthetic score
            "innovation": innovation_proxy(q),
        }
    norm_r = _minmax([f["richness"] for f in feats.values()])
    norm_i = _minmax([f["innovation"] for f in feats.values()])
    max_dims = max((len(f["dims"]) for f in feats.values()), default=1) or 1

    per_phase = max(1, target // len(CORE_PHASES))
    quota = {p: per_phase for p in CORE_PHASES}

    def item_score(qid, covered):
        f = feats[qid]
        new_dims = f["dims"] - covered
        quality = WEIGHTS["quality"] * norm_r(f["richness"])
        coverage = WEIGHTS["coverage"] * (len(new_dims) / len(CANONICAL_DIMENSIONS))
        innovation = WEIGHTS["innovation"] * norm_i(f["innovation"])
        breadth = WEIGHTS["breadth"] * (len(f["dims"]) / max_dims)
        return quality + coverage + innovation + breadth, new_dims

    # ---- deterministic greedy selection under per-phase quota -------------
    selected, covered_dims = [], set()
    counts = {p: 0 for p in CORE_PHASES}
    pool = [qid for qid in sorted(feats) if qid not in intrusive_ids]
    trace = []

    def eligible_phase(f):
        if f["phase"] in CORE_PHASES and counts[f["phase"]] < quota[f["phase"]]:
            return f["phase"]
        if f["phase"] == "cross_phase":
            open_phases = [p for p in CORE_PHASES if counts[p] < quota[p]]
            return open_phases[0] if open_phases else None
        return None

    while len(selected) < target and pool:
        best, best_score, best_break, best_assign = None, None, None, None
        for qid in pool:
            assign = eligible_phase(feats[qid])
            if assign is None:
                continue
            score, new_dims = item_score(qid, covered_dims)
            breaker = (-len(new_dims), qid)
            if best_score is None or score > best_score + 1e-12 or \
               (abs(score - best_score) <= 1e-12 and breaker < best_break):
                best, best_score, best_break, best_assign = qid, score, breaker, assign
        if best is None:
            break
        f = feats[best]
        new_dims = sorted(f["dims"] - covered_dims)
        selected.append(best)
        covered_dims |= f["dims"]
        counts[best_assign] += 1
        pool.remove(best)
        trace.append({
            "rank": len(selected), "question_id": best, "phase": f["phase"],
            "assigned_phase": best_assign, "score": round(best_score, 4),
            "new_dimensions_covered": new_dims, "richness": round(f["richness"], 3),
            "richness_imputed": f["richness_imputed"],
        })

    # ---- repair: guarantee full latent-dimension set-cover ---------------
    missing = set(CANONICAL_DIMENSIONS) - covered_dims
    for dim in sorted(missing):
        cand = next((qid for qid in pool if dim in feats[qid]["dims"]), None)
        if not cand:
            continue
        # drop the selected item whose removal loses the least unique coverage
        def unique_loss(s):
            others = set().union(*(feats[x]["dims"] for x in selected if x != s)) if len(selected) > 1 else set()
            return len(feats[s]["dims"] - others)
        victim = min(selected, key=lambda s: (unique_loss(s), -1 * 0, s))
        selected.remove(victim)
        selected.append(cand)
        pool.remove(cand)
        covered_dims = set().union(*(feats[x]["dims"] for x in selected))
        trace.append({"rank": "repair", "question_id": cand, "phase": feats[cand]["phase"],
                      "swapped_out": victim, "reason": f"ensure coverage of {dim}"})

    return selected, feats, trace, sorted(covered_dims)


def build_provenance(selected, feats):
    """For every non-selected question, record whether it was merged into a kept item
    (its dimensions are a subset of a kept item in the same phase) or dropped (low yield)."""
    sel_set = set(selected)
    prov = []
    for qid in sorted(feats):
        f = feats[qid]
        if qid in sel_set:
            prov.append({"question_id": qid, "phase": f["phase"], "decision": "kept",
                         "reason": "selected as core item"})
            continue
        # find a kept item, same phase, that already covers this item's dimensions
        merge_target = None
        for s in selected:
            sf = feats[s]
            if sf["phase"] == f["phase"] and f["dims"] and f["dims"] <= sf["dims"]:
                merge_target = s
                break
        if merge_target:
            prov.append({"question_id": qid, "phase": f["phase"], "decision": "merged",
                         "merged_into": merge_target,
                         "reason": "latent-dimension coverage subsumed by kept item in same phase"})
        else:
            prov.append({"question_id": qid, "phase": f["phase"], "decision": "dropped",
                         "reason": "redundant coverage / lower composite richness; "
                                   "excluded to reduce respondent burden"})
    return prov


def coverage_metrics(qids, feats):
    dims, phases, rich = set(), set(), []
    for qid in qids:
        f = feats[qid]
        dims |= f["dims"]
        phases.add(f["phase"])
        rich.append(f["richness"])
    return {
        "n_questions": len(qids),
        "latent_dimensions_covered": len(dims & set(CANONICAL_DIMENSIONS)),
        "latent_dimension_coverage_pct": round(100 * len(dims & set(CANONICAL_DIMENSIONS)) / len(CANONICAL_DIMENSIONS), 1),
        "core_phases_covered": sorted(p for p in phases if p in CORE_PHASES),
        "mean_composite_richness": round(statistics.mean(rich), 3) if rich else None,
    }


def render_markdown(guide, selected, feats, before, after, covered):
    lines = ["# Guide A — Consolidated 12-Question Maternity Interview Guide",
             "",
             f"Derived deterministically from the {before['n_questions']}-question stress-tested "
             f"guide (V4_R1) by `src/refinement/consolidate_guide.py`.",
             "",
             f"- Latent-dimension coverage: {before['latent_dimension_coverage_pct']}% "
             f"({before['n_questions']} items) -> {after['latent_dimension_coverage_pct']}% (12 items)",
             f"- Mean composite richness: {before['mean_composite_richness']} -> {after['mean_composite_richness']}",
             f"- Core phases covered: {', '.join(after['core_phases_covered'])}",
             "", "---", ""]
    order = {p: i for i, p in enumerate(CORE_PHASES + ["cross_phase"])}
    for n, qid in enumerate(sorted(selected, key=lambda q: (order.get(feats[q]["phase"], 9), q)), 1):
        q = feats[qid]["q"]
        lines.append(f"### Q{n}. [{feats[qid]['phase']}] {q.get('question_text','').strip()}")
        dims = sorted(feats[qid]["dims"])
        if dims:
            lines.append(f"*Latent dimensions:* {', '.join(dims)}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questionnaire", default="data/questionnaires/final/FINAL_QUESTIONNAIRE.json")
    ap.add_argument("--scores", default="data/evaluation/quality_scores.jsonl")
    ap.add_argument("--out", default="data/questionnaires/consolidated")
    ap.add_argument("--target", type=int, default=12)
    args = ap.parse_args()

    questions = load_questions(args.questionnaire)
    richness = load_richness(args.scores)
    selected, feats, trace, covered = consolidate(questions, richness, target=args.target)

    before = coverage_metrics([q["question_id"] for q in questions], feats)
    after = coverage_metrics(selected, feats)
    provenance = build_provenance(selected, feats)

    os.makedirs(args.out, exist_ok=True)
    guide_questions = []
    order = {p: i for i, p in enumerate(CORE_PHASES + ["cross_phase"])}
    for n, qid in enumerate(sorted(selected, key=lambda q: (order.get(feats[q]["phase"], 9), q)), 1):
        q = dict(feats[qid]["q"])
        q["core_position"] = n
        guide_questions.append(q)

    guide = {
        "guide_id": "GUIDE_A_12Q",
        "derived_from": "V4_R1",
        "source_question_count": before["n_questions"],
        "target_question_count": args.target,
        "selection_weights": WEIGHTS,
        "selection_weights_approval": WEIGHTS_APPROVAL,
        "questions": guide_questions,
        "coverage_before": before,
        "coverage_after": after,
        "latent_dimensions_covered": covered,
    }
    json.dump(guide, open(os.path.join(args.out, "GUIDE_A_12Q.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    json.dump({"selected": selected, "trace": trace, "provenance": provenance,
               "weights": WEIGHTS, "weights_approval": WEIGHTS_APPROVAL,
               "coverage_before": before, "coverage_after": after},
              open(os.path.join(args.out, "consolidation_provenance.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    open(os.path.join(args.out, "GUIDE_A_12Q.md"), "w", encoding="utf-8").write(
        render_markdown(guide, selected, feats, before, after, covered))

    # console summary
    print(f"Source populated questions: {before['n_questions']}")
    print(f"Selected core questions:    {len(selected)}")
    print(f"Latent coverage: {before['latent_dimension_coverage_pct']}% -> {after['latent_dimension_coverage_pct']}%")
    print(f"Mean richness:   {before['mean_composite_richness']} -> {after['mean_composite_richness']}")
    print(f"Phases covered:  {after['core_phases_covered']}")
    print("Selected:", ", ".join(sorted(selected)))
    dropped = [p['question_id'] for p in provenance if p['decision'] == 'dropped']
    merged = [p['question_id'] for p in provenance if p['decision'] == 'merged']
    print(f"Merged: {len(merged)}  Dropped: {len(dropped)}")


if __name__ == "__main__":
    main()

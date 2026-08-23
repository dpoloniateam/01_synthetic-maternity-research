"""restated_nonempty_corpus.py — restatement of the main-phase and refinement results on the non-empty corpus.

Background (consistency report of 23 August 2026, §9.1): the 100 main-phase sessions whose persona was voiced
by gpt-5-mini returned no text (development-tier output cap of 512 tokens consumed before any text), so 1,611 of
the 6,458 scored responses are empty strings scored 0. This script recomputes, with the pipeline's own formulas
(src/evaluation/version_comparator.py, coverage_analyser.py, inter_rater.py), every figure of manuscript
Sections 4.1–4.4 that can be recomputed without new model calls, on three definitions of the corpus:

    A  design-based  — all sessions except those voiced by gpt-5-mini (the failing model)        [primary]
    B  response-based — all sessions, empty responses dropped, transcripts left with no response dropped
    C  single-model   — gemini-voiced sessions only (sensitivity)

It also merges the alias `trust_distrust_providers` into the canonical `trust_distrust` for the coverage
heatmap, marks the six canonical dimensions that no persona encodes as not measurable under the scorer design,
restates the inter-rater agreement on the non-empty inter-rater transcripts, restates the needs/insights
percentages with both denominators, and compares V4 and V4_R1 like for like. No LLM call is made.

Usage (working tree):
    python -m src.analysis.restated_nonempty_corpus --root . --out data/evaluation/restated_20260823
Usage (reproducibility package, from its root, where `src/` is an alias of `01_Source_Code/`):
    python -m src.analysis.restated_nonempty_corpus --root . --layout package --out <dir>

In the package the 50 re-administration transcripts are withheld under the embargo; their interview cost is
read from `interview_costs.json` (one record per session: identifiers, token counts and estimated cost, no text).
"""
from __future__ import annotations
import argparse, json, math, statistics, collections
from pathlib import Path
import numpy as np
from scipy import stats

CANON = ["autonomy_vs_dependence", "body_image_autonomy", "continuity_of_care", "digital_information_seeking",
         "dignity_respect", "identity_tensions", "informal_care_networks", "intergenerational_patterns",
         "partner_role", "power_dynamics", "structural_barriers", "trust_distrust"]
ALIAS = {"trust_distrust_providers": "trust_distrust"}
DIMS5 = ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]
GROUP_PAIRS = {"A": (1, 2), "B": (1, 3), "C": (2, 4), "D": (3, 5), "E": (4, 5)}
FAILING_MODEL = "gpt-5-mini"
W = {"quality": 0.40, "coverage": 0.25, "innovation": 0.20, "breadth": 0.15}


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf8") if l.strip()]


def num(v):
    """Judge outputs are numeric except one malformed value (S_220 / V5_PREG_Q01_P01, latent_surfacing = a list);
    non-numeric values are treated as missing, as the pipeline's composite (taken from the judge) already is."""
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def nmean(vals):
    vals = [v for v in vals if v is not None]
    return statistics.mean(vals) if vals else float("nan")


def sd(v):
    return statistics.stdev(v) if len(v) > 1 else 0.0


def ci95(v):
    m = statistics.mean(v); s = sd(v); h = 1.96 * s / math.sqrt(len(v)) if v else 0
    return round(m - h, 2), round(m + h, 2)


def cohens_d(a, b):
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2: return 0.0
    pooled = math.sqrt(((n1 - 1) * sd(a) ** 2 + (n2 - 1) * sd(b) ** 2) / (n1 + n2 - 2))
    return round((statistics.mean(a) - statistics.mean(b)) / pooled, 3) if pooled else 0.0


def icc21(M):
    M = np.asarray(M, float); n, k = M.shape; gm = M.mean()
    ms_r = k * ((M.mean(1) - gm) ** 2).sum() / (n - 1); ms_c = n * ((M.mean(0) - gm) ** 2).sum() / (k - 1)
    ms_e = ((M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + gm) ** 2).sum() / ((n - 1) * (k - 1))
    return round(float((ms_r - ms_e) / (ms_r + (k - 1) * ms_e + k * (ms_c - ms_e) / n)), 3)


def alpha_simplified(M):
    """The pipeline's own 'simplified Krippendorff alpha' (inter_rater.py): 1 − within-unit variance / grand variance."""
    M = np.asarray(M, float); n, k = M.shape; allv = M.ravel()
    gv = allv.var(ddof=1)
    if gv == 0: return 1.0
    wv = ((M - M.mean(1, keepdims=True)) ** 2).sum() / (n * (k - 1))
    return round(float(1 - wv / gv), 3)


def transcript_stats(sessions_by_version, label):
    out = {}
    for v in sorted(sessions_by_version):
        r = [s["richness"] for s in sessions_by_version[v]]
        sr = [s["surfacing_rate"] for s in sessions_by_version[v]]
        out[f"V{v}"] = {"n": len(r), "richness_mean": round(statistics.mean(r), 2), "richness_sd": round(sd(r), 2),
                        "ci95": ci95(r), "surfacing_rate_pct": round(100 * statistics.mean(sr), 1)}
    groups = [[s["richness"] for s in sessions_by_version[v]] for v in sorted(sessions_by_version)]
    H, p = stats.kruskal(*groups)
    pair = {}
    vs = sorted(sessions_by_version)
    for i, a in enumerate(vs):
        for b in vs[i + 1:]:
            pair[f"V{a}_vs_V{b}"] = cohens_d([s["richness"] for s in sessions_by_version[a]], [s["richness"] for s in sessions_by_version[b]])
    return {"set": label, "version_stats": out, "kruskal_wallis": {"H": round(float(H), 2), "p": round(float(p), 4)},
            "pairwise_cohens_d": pair}


def heatmap(sessions_by_version, dims, merge_alias=True):
    mat = {}
    for v in sorted(sessions_by_version):
        ss = sessions_by_version[v]; n = max(len(ss), 1); mat[f"V{v}"] = {}
        for d in dims:
            c = sum(1 for s in ss if d in s["surfaced_merged" if merge_alias else "surfaced_raw"])
            mat[f"V{v}"][d] = round(100 * c / n, 1)
    return mat


def within_subject(sessions, plan_groups):
    by_persona = collections.defaultdict(dict)
    for s in sessions: by_persona[s["persona_id"]][s["version"]] = s["richness"]
    res = {}
    for g, (v1, v2) in GROUP_PAIRS.items():
        diffs = [d[v1] - d[v2] for d in by_persona.values() if v1 in d and v2 in d]
        if len(diffs) >= 5:
            nz = [d for d in diffs if d != 0]
            W_, p = stats.wilcoxon(nz) if len(nz) >= 5 else (float("nan"), float("nan"))
            res[f"Group_{g}_V{v1}_vs_V{v2}"] = {"n_pairs": len(diffs), "mean_diff": round(statistics.mean(diffs), 3),
                                                  "wilcoxon_W": round(float(W_), 1), "p": round(float(p), 4),
                                                  "favours": f"V{v1}" if statistics.mean(diffs) > 0 else f"V{v2}"}
        else:
            res[f"Group_{g}_V{v1}_vs_V{v2}"] = {"n_pairs": len(diffs), "note": "fewer than five complete pairs"}
    return res


def ranking(vstats, hm, gaps_by_version, n_by_version):
    out = {}
    for vk, q in vstats.items():
        rates = list(hm[vk].values()); blind = sum(1 for r in rates if r < 20); cov = statistics.mean(rates) / 100
        gy = gaps_by_version[vk]; innov = (gy["gaps"] + gy["innovations"]) / max(n_by_version[vk], 1)
        breadth = (12 - blind) / 12
        comp = q["richness_mean"] * W["quality"] + cov * 5 * W["coverage"] + min(innov, 5) * W["innovation"] + breadth * 5 * W["breadth"]
        out[vk] = {"quality": q["richness_mean"], "coverage": round(cov, 3), "innovation": round(innov, 2),
                   "breadth": round(breadth, 2), "blind_spots_lt20": blind, "composite": round(comp, 3)}
    for i, (vk, d) in enumerate(sorted(out.items(), key=lambda x: -x[1]["composite"])): d["rank"] = i + 1
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="."); ap.add_argument("--out", required=True)
    ap.add_argument("--layout", choices=["worktree", "package"], default="worktree")
    a = ap.parse_args(); R = Path(a.root); O = Path(a.out); O.mkdir(parents=True, exist_ok=True)
    if a.layout == "package":
        E = R / "03_Evaluation_Results/evaluation"; PLAN = R / "06_Configuration/config/administration_plan.json"
        TR = R / "02_Data_Samples/transcripts"; TRR = R / "02_Data_Samples/transcripts/refinement"; ML = R / "03_Evaluation_Results/refinement/methodology_log.json"
    else:
        E = R / "data/evaluation"; PLAN = R / "data/config/administration_plan.json"
        TR = R / "data/transcripts"; TRR = R / "data/transcripts/refinement"; ML = R / "data/refinement/methodology_log.json"
    ts = jl(E / "transcript_summaries.jsonl"); qs = jl(E / "quality_scores.jsonl"); maps = jl(E / "service_maps.jsonl")
    rts = jl(E / "refinement/transcript_summaries.jsonl"); rqs = jl(E / "refinement/quality_scores.jsonl")
    irr = json.load(open(E / "inter_rater_scores.json", encoding="utf8"))
    nis = jl(E / "needs_insights_by_session.jsonl")
    plan = json.load(open(PLAN, encoding="utf8"))
    plan_sessions = plan["sessions"] if isinstance(plan, dict) and "sessions" in plan else plan
    sess_model = {s["session_id"]: s["persona_model"] for s in ts}
    resp_by_session = collections.defaultdict(list)
    for r in qs: resp_by_session[r["session_id"]].append(r)
    maps_by_session = {m["session_id"]: m for m in maps}

    def session_record(s, responses=None):
        raw = set(s["latent_dimensions_surfaced"]); merged = {ALIAS.get(d, d) for d in raw}
        rec = {"session_id": s["session_id"], "persona_id": s["persona_id"], "version": s["questionnaire_version"],
               "model": s["persona_model"], "stage": s["persona_journey_stage"], "risk": s["persona_risk_level"],
               "surfaced_raw": raw, "surfaced_merged": merged, "encoded": set(s["latent_dimensions_encoded"]),
               "surfacing_rate": s["surfacing_rate"], "richness": s["mean_composite_richness"],
               "dims": dict(s["mean_scores"])}
        if responses is not None:  # response-based recomputation
            rec["richness"] = statistics.mean(r["composite_richness"] for r in responses)
            rec["dims"] = {d: nmean(num(r["scores"].get(d)) for r in responses) for d in DIMS5}
        return rec

    # --- the three corpora -------------------------------------------------------------------------------------
    all_sessions = [session_record(s) for s in ts]
    setA = [x for x in all_sessions if FAILING_MODEL not in x["model"]]
    setC = [x for x in all_sessions if "gemini" in x["model"]]
    setB = []
    for s in ts:
        ne = [r for r in resp_by_session[s["session_id"]] if r.get("response_text_length", 1) > 0]
        if ne: setB.append(session_record(s, ne))
    empties = sum(1 for r in qs if r.get("response_text_length", 1) == 0)
    corpus = {"responses_total": len(qs), "responses_empty": empties, "responses_nonempty": len(qs) - empties,
              "sessions_total": len(ts), "sessions_by_model": dict(collections.Counter(s["persona_model"] for s in ts)),
              "empty_responses_by_model": dict(collections.Counter(sess_model[r["session_id"]] for r in qs if r.get("response_text_length", 1) == 0)),
              "zero_richness_sessions_by_version": dict(collections.Counter(s["questionnaire_version"] for s in ts if s["mean_composite_richness"] == 0)),
              "failing_model_sessions_by_version": dict(collections.Counter(s["questionnaire_version"] for s in ts if FAILING_MODEL in s["persona_model"])),
              "set_sizes": {"A_design_based": len(setA), "B_response_based": len(setB), "C_gemini_only": len(setC)}}
    # corpus-level descriptives (response level) for A and B
    respA = [r for r in qs if FAILING_MODEL not in sess_model[r["session_id"]]]
    respB = [r for r in qs if r.get("response_text_length", 1) > 0]
    def resp_desc(rs):
        return {"n_responses": len(rs), "mean_composite_richness": round(statistics.mean(r["composite_richness"] for r in rs), 2),
                "dimension_means": {d: round(nmean(num(r["scores"].get(d)) for r in rs), 2) for d in DIMS5}}
    corpus["published_all_responses"] = resp_desc(qs); corpus["A_design_based"] = resp_desc(respA); corpus["B_response_based"] = resp_desc(respB)
    for name, ss in (("published", all_sessions), ("A", setA), ("B", setB), ("C", setC)):
        corpus[f"surfacing_rate_9dim_{name}"] = round(100 * statistics.mean(x["surfacing_rate"] for x in ss), 1)

    # --- Table 3 restated, tests, within-subject, heatmaps, ranking -------------------------------------------------
    results = {"corpus": corpus}
    for label, ss in (("published_all_sessions", all_sessions), ("A_design_based", setA), ("B_response_based", setB), ("C_gemini_only", setC)):
        byv = collections.defaultdict(list)
        for x in ss: byv[x["version"]].append(x)
        t3 = transcript_stats(byv, label)
        hm_c = heatmap(byv, CANON, True); hm_raw = heatmap(byv, CANON, False)
        nine = sorted({d for x in ss for d in x["encoded"]})
        hm9 = {vk: {d: round(100 * sum(1 for x in byv[int(vk[1:])] if d in x["surfaced_raw"]) / max(len(byv[int(vk[1:])]), 1), 1) for d in nine} for vk in hm_c}
        gaps = {}
        for v, xs in byv.items():
            g = i = 0
            for x in xs:
                m = maps_by_session.get(x["session_id"]); 
                if m: g += len(m.get("service_gaps", [])); i += len(m.get("innovation_opportunities", []))
            gaps[f"V{v}"] = {"gaps": g, "innovations": i}
        nbv = {f"V{v}": len(xs) for v, xs in byv.items()}
        results[label] = {"table3": t3, "within_subject": within_subject(ss, GROUP_PAIRS),
                          "heatmap_canonical_alias_merged": hm_c, "heatmap_canonical_as_published_no_alias": hm_raw,
                          "heatmap_nine_encoded": hm9, "gap_yield": gaps,
                          "ranking_alias_merged": ranking(t3["version_stats"], hm_c, gaps, nbv),
                          "ranking_as_published_coding": ranking(t3["version_stats"], hm_raw, gaps, nbv),
                          "dimension_means_transcript_level": {f"V{v}": {d: round(statistics.mean(x["dims"][d] for x in xs), 2) for d in DIMS5} for v, xs in sorted(byv.items())}}
    results["canonical_dimensions_not_persona_encoded"] = sorted(set(CANON) - {ALIAS.get(d, d) for x in all_sessions for d in x["encoded"]})

    # --- refinement like for like -----------------------------------------------------------------------------------
    r1 = [{"richness": s["mean_composite_richness"], "surfacing_rate": s["surfacing_rate"], "dims": s["mean_scores"]} for s in rts]
    def cmp(v4, label):
        a = [x["richness"] for x in v4]; b = [x["richness"] for x in r1]
        U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        return {"V4_set": label, "V4_n": len(a), "V4_richness": round(statistics.mean(a), 2), "V4_surfacing_pct": round(100 * statistics.mean(x["surfacing_rate"] for x in v4), 1),
                "V4_R1_n": len(b), "V4_R1_richness": round(statistics.mean(b), 2), "V4_R1_surfacing_pct": round(100 * statistics.mean(x["surfacing_rate"] for x in r1), 1),
                "delta_richness_pct": round(100 * (statistics.mean(b) - statistics.mean(a)) / statistics.mean(a), 1),
                "mann_whitney_U": round(float(U), 1), "p": round(float(p), 4), "cohens_d": cohens_d(b, a),
                "V4_dimension_means": {d: round(statistics.mean(x["dims"][d] for x in v4), 2) for d in DIMS5},
                "V4_R1_dimension_means": {d: round(statistics.mean(x["dims"][d] for x in r1), 2) for d in DIMS5}}
    v4_all = [x for x in all_sessions if x["version"] == 4]; v4A = [x for x in setA if x["version"] == 4]; v4C = [x for x in setC if x["version"] == 4]
    v4B = [x for x in setB if x["version"] == 4]
    results["refinement_like_for_like"] = {"published_V4_all_60": cmp(v4_all, "all 60 sessions (as published)"), "A_design_based": cmp(v4A, "V4 without gpt-5-mini sessions"),
                                           "B_response_based": cmp(v4B, "V4 non-empty transcripts, empty responses dropped"), "C_gemini_only": cmp(v4C, "V4 gemini-voiced sessions (same model as V4_R1)"),
                                           "V4_R1_persona_model": dict(collections.Counter(s["persona_model"] or "(blank → code default gemini-3.1-flash-lite-preview)" for s in rts)),
                                           "V4_R1_empty_responses": sum(1 for r in rqs if r.get("response_text_length", 1) == 0),
                                           "surfacing_arithmetic": {"V4_published_pct": round(100 * statistics.mean(x["surfacing_rate"] for x in v4_all), 1),
                                                                    "V4_nonzero_sessions": sum(1 for x in v4_all if x["richness"] > 0),
                                                                    "V4_nonzero_mean_surfacing_pct": round(100 * statistics.mean(x["surfacing_rate"] for x in v4_all if x["richness"] > 0), 1)}}

    # --- inter-rater agreement restated ---------------------------------------------------------------------------
    provs = ["anthropic", "google", "openai"]
    M = np.array([[r[p]["composite"] for p in provs] for r in irr]); nonzero = M.sum(1) > 0
    irr_out = {"n_published": len(M), "icc21_published": icc21(M), "alpha_simplified_published_composite": alpha_simplified(M),
               "empty_transcripts": [r["session_id"] for r, z in zip(irr, nonzero) if not z],
               "n_nonempty": int(nonzero.sum()), "icc21_nonempty": icc21(M[nonzero]), "alpha_simplified_nonempty_composite": alpha_simplified(M[nonzero]),
               "by_dimension_nonempty": {}, "pairwise_spearman_nonempty_composite": {}}
    for d in DIMS5:
        Md = np.array([[r[p]["scores"][d] for p in provs] for r in irr])
        irr_out["by_dimension_nonempty"][d] = {"icc21_published": icc21(Md), "icc21_nonempty": icc21(Md[nonzero]), "alpha_simplified_nonempty": alpha_simplified(Md[nonzero])}
    Mn = M[nonzero]
    for i, a_ in enumerate(provs):
        for b_ in provs[i + 1:]:
            rho, p = stats.spearmanr(Mn[:, i], Mn[:, provs.index(b_)]); irr_out["pairwise_spearman_nonempty_composite"][f"{a_}_vs_{b_}"] = {"rho": round(float(rho), 3), "p": round(float(p), 4)}
    irr_out["empty_transcripts_model"] = {sid: sess_model.get(sid, "?") for sid in irr_out["empty_transcripts"]}
    results["inter_rater"] = irr_out

    # --- needs versus insights restated ---------------------------------------------------------------------------
    def ni_table(rows):
        byv = collections.defaultdict(lambda: collections.Counter()); nsess = collections.Counter()
        for r in rows:  # the per-session file labels V4, V4_R1 and V4_ADV alike as 4; split by session id
            sid = str(r["session_id"]); v = "V4_R1" if sid.startswith("S_R") else "V4_ADV" if sid.startswith("S_ADV") else f"V{r['version']}"
            byv[v].update(r["counts"]); nsess[v] += 1
        out = {}
        for v, c in byv.items():
            need, ins, mix, nei = c.get("NEED", 0), c.get("INSIGHT", 0), c.get("MIXED", 0), c.get("NEITHER", 0)
            tot = need + ins + mix + nei; cl = need + ins + mix
            out[str(v)] = {"sessions": nsess[v], "pairs_total": tot, "neither": nei, "needs_pct_of_classified": round(100 * need / cl, 1) if cl else None,
                           "insights_pct_of_classified": round(100 * ins / cl, 1) if cl else None, "mixed_pct_of_classified": round(100 * mix / cl, 1) if cl else None,
                           "needs_pct_of_all_pairs": round(100 * need / tot, 1) if tot else None, "insights_pct_of_all_pairs": round(100 * ins / tot, 1) if tot else None,
                           "insights_to_needs_ratio": round(ins / need, 1) if need else None}
        allc = collections.Counter()
        for r in rows: allc.update(r["counts"])
        need, ins, mix, nei = allc.get("NEED", 0), allc.get("INSIGHT", 0), allc.get("MIXED", 0), allc.get("NEITHER", 0); tot = need + ins + mix + nei; cl = need + ins + mix
        out["overall"] = {"sessions": len(rows), "pairs_total": tot, "neither": nei, "needs_pct_of_classified": round(100 * need / cl, 1), "insights_pct_of_classified": round(100 * ins / cl, 1),
                          "mixed_pct_of_classified": round(100 * mix / cl, 1), "needs_pct_of_all_pairs": round(100 * need / tot, 1), "insights_pct_of_all_pairs": round(100 * ins / tot, 1),
                          "mixed_pct_of_all_pairs": round(100 * mix / tot, 1), "neither_pct_of_all_pairs": round(100 * nei / tot, 1), "insights_to_needs_ratio": round(ins / need, 2)}
        return out
    main_versions = {"1", "2", "3", "4", "5", 1, 2, 3, 4, 5}
    keep = [r for r in nis if not (str(r["session_id"]).startswith("S_") and not str(r["session_id"]).startswith(("S_R", "S_ADV")) and FAILING_MODEL in sess_model.get(r["session_id"], ""))]
    results["needs_insights"] = {"published_all_sessions": ni_table(nis), "A_design_based_plus_V4R_V4ADV": ni_table(keep),
                                 "note": "percentages 'of classified' exclude pairs labelled NEITHER, as the pipeline and Table 4 do; 'of all pairs' use the Q-R pair column as denominator"}

    # --- cost restated ----------------------------------------------------------------------------------------------
    cost = {"main_phase_interviews_usd": 0.0, "refinement_interviews_usd": 0.0, "n_main": 0, "n_ref": 0, "source": {}}
    costfile = E / "interview_costs.json"
    costs = json.load(open(costfile, encoding="utf8")) if costfile.exists() else None
    def from_transcripts(folder, pattern, key_usd, key_n):
        n = 0
        for p in sorted(folder.glob(pattern)):
            d = json.load(open(p, encoding="utf8")); cost[key_usd] += (d.get("metadata") or {}).get("estimated_cost_usd", 0) or 0; n += 1
        cost[key_n] += n; return n
    if TR.exists() and from_transcripts(TR, "T_S_*.json", "main_phase_interviews_usd", "n_main"):
        cost["source"]["main"] = "transcript metadata"
    elif costs:
        for c in costs:
            if c["phase"] == "main": cost["main_phase_interviews_usd"] += c["estimated_cost_usd"]; cost["n_main"] += 1
        cost["source"]["main"] = "interview_costs.json"
    if TRR.exists() and from_transcripts(TRR, "T_S_R*.json", "refinement_interviews_usd", "n_ref"):
        cost["source"]["refinement"] = "transcript metadata"
    elif costs:
        for c in costs:
            if c["phase"] == "refinement": cost["refinement_interviews_usd"] += c["estimated_cost_usd"]; cost["n_ref"] += 1
        cost["source"]["refinement"] = "interview_costs.json (transcripts withheld under the embargo)"
    ml = json.load(open(ML, encoding="utf8"))
    cost["logged_refinement_layer_usd_methodology_log"] = ml.get("total_cost_usd"); cost["main_phase_interviews_usd"] = round(cost["main_phase_interviews_usd"], 2); cost["refinement_interviews_usd"] = round(cost["refinement_interviews_usd"], 2)
    cost["lower_bound_total_usd"] = round(cost["main_phase_interviews_usd"] + cost["refinement_interviews_usd"] + (ml.get("total_cost_usd") or 0), 2)
    cost["unlogged"] = "main-phase quality scoring, service mapping, inter-rater runs, persona narratives, questionnaire generation, needs/insights classification"
    results["cost"] = cost

    json.dump(results, open(O / "restated_results.json", "w", encoding="utf8"), indent=1, ensure_ascii=False, default=list)
    print("wrote", O / "restated_results.json")


if __name__ == "__main__":
    main()

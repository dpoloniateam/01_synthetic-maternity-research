"""Analyse a run directory: sessions, provenance, judge panel; extrapolate the full design; print a JSON summary."""
import json, sys, collections, statistics, glob
from pathlib import Path
run = Path(sys.argv[1]); out = {}
# --- sessions
T = {}
for f in sorted(run.glob("transcripts/T_*.json")):
    t = json.load(open(f, encoding="utf-8")); T[t["session_id"]] = t
sess = []
for sid, t in T.items():
    turns = t["turns"]; pt = [x for x in turns if x["role"] == "persona"]
    sess.append({"session_id": sid, "persona": t["persona_id"], "version": t["questionnaire_version"], "voice": t.get("persona_model"), "status": t["status"],
                 "turns": len(turns), "persona_turns": len(pt), "questions": t["metadata"]["questions_asked"], "probes": t["metadata"]["probes_deployed"],
                 "empty": sum(1 for x in pt if x.get("empty")), "truncated": sum(1 for x in pt if x.get("truncated")),
                 "in_tok": t["metadata"]["total_input_tokens"], "out_tok": t["metadata"]["total_output_tokens"],
                 "words_mean": round(statistics.mean(len((x.get("text") or "").split()) for x in pt), 1) if pt else 0,
                 "duration_s": t["metadata"]["duration_seconds"], "errors": t.get("errors", [])})
out["sessions"] = sess
# --- provenance
R = [json.loads(l) for l in open(run / "requests.jsonl", encoding="utf-8")]
by_stage = collections.defaultdict(lambda: {"calls": 0, "usd": 0.0, "in": 0, "out": 0, "cached": 0})
by_model = collections.defaultdict(lambda: {"calls": 0, "usd": 0.0, "in": 0, "out": 0, "cached": 0, "reasoning": 0, "latency": []})
per_session_cost = collections.Counter(); per_session_voice_calls = collections.Counter()
judge_by_model = collections.defaultdict(lambda: {"calls": 0, "usd": 0.0, "in": 0, "out": 0})
for r in R:
    s = by_stage[r["stage"]]; s["calls"] += 1; s["usd"] += r["cost_usd"]; s["in"] += r["input_tokens"]; s["out"] += r["output_tokens"]; s["cached"] += r.get("cached_tokens") or 0
    if r["stage"] != "persona":
        jm = judge_by_model[f'{r["provider"]}/{r["model"]}']; jm["calls"] += 1; jm["usd"] += r["cost_usd"]; jm["in"] += r["input_tokens"]; jm["out"] += r["output_tokens"]
        continue
    m = by_model[f'{r["provider"]}/{r["model"]}']; m["calls"] += 1; m["usd"] += r["cost_usd"]; m["in"] += r["input_tokens"]; m["out"] += r["output_tokens"]; m["cached"] += r.get("cached_tokens") or 0
    m["reasoning"] += (r.get("reasoning_tokens") or r.get("thinking_tokens") or 0); m["latency"].append(r.get("latency_s") or 0)
    if r["stage"] == "persona": per_session_cost[r["session_id"]] += r["cost_usd"]; per_session_voice_calls[r["session_id"]] += 1
for m in by_model.values():
    m["latency_median_s"] = round(statistics.median(m["latency"]), 1) if m["latency"] else None; m["latency_max_s"] = round(max(m["latency"]), 1) if m["latency"] else None; del m["latency"]
    m["usd"] = round(m["usd"], 4)
for s in by_stage.values(): s["usd"] = round(s["usd"], 4)
for v in judge_by_model.values(): v["usd"] = round(v["usd"], 4)
out["judge_by_model"] = dict(judge_by_model)
out["by_stage"] = dict(by_stage); out["by_model"] = dict(by_model); out["total_usd"] = round(sum(r["cost_usd"] for r in R), 4)
out["per_session_persona_cost"] = {k: round(v, 4) for k, v in per_session_cost.items()}
# per-voice session cost (completed sessions only, first attempt calls)
voice_cost = collections.defaultdict(list)
for s in sess:
    if s["status"] == "completed": voice_cost[s["voice"]].append(per_session_cost[s["session_id"]])
out["voice_session_cost_mean"] = {v: round(statistics.mean(c), 4) for v, c in voice_cost.items()}
# --- judge
Q = [json.loads(l) for l in open(run / "quality_scores.jsonl", encoding="utf-8")] if (run / "quality_scores.jsonl").exists() else []
out["judged_pairs"] = len(Q)
if Q:
    judges = sorted({j for q in Q for j in (q.get("panel_composites") or {})})
    comp = {j: [q["panel_composites"][j] for q in Q if q.get("panel_composites", {}).get(j) is not None] for j in judges}
    out["judge_mean_composite"] = {j: round(statistics.mean(v), 3) for j, v in comp.items() if v}
    # judge x voice
    jv = collections.defaultdict(lambda: collections.defaultdict(list))
    voice_of = {s["session_id"]: s["voice"] for s in sess}
    for q in Q:
        for j, c in (q.get("panel_composites") or {}).items():
            if c is not None: jv[j][voice_of.get(q["session_id"], "?")].append(c)
    out["judge_x_voice"] = {j: {v: round(statistics.mean(c), 2) for v, c in d.items()} for j, d in jv.items()}
    rel = [q["panel_reliability"] for q in Q if q.get("panel_reliability")]
    # pooled reliability across all pairs with both judges
    from src.evaluation.reliability import icc_by_dimension
    dims = ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]
    ratings = collections.defaultdict(list)
    for q in Q:
        P = q.get("panel") or {}
        if len(judges) >= 2 and all(P.get(j) for j in judges):
            for d in dims: ratings[d].append([P[j][d]["score"] for j in judges])
            ratings["composite"].append([q["panel_composites"][j] for j in judges])
    out["pooled_icc"] = icc_by_dimension(ratings) if ratings else {}
    surf = collections.Counter(d for q in Q for d in q.get("latent_dimensions_surfaced", []))
    out["surfaced_dimension_counts"] = dict(surf.most_common())
    out["judge_records_per_session"] = dict(collections.Counter(q["session_id"] for q in Q))
print(json.dumps(out, indent=1, ensure_ascii=False))

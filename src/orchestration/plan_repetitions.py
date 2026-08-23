"""
Administration plan v2 (development 8): the v1 plan (BIBD allocation of personas to versions) extended with the
experiment's arm, persona voices (round-robin, stratified by BIBD group so every voice meets every version), seeds
and repetitions. Session ids become S_001_a{arm}_r{rep}. The v1 plan is untouched.

    python -m src.orchestration.plan_repetitions --plan data/config/administration_plan.json --arm P \
        --repetitions 1 --limit 0 --output data/config/administration_plan_v2_P.json
"""
import json, argparse, copy
from src.config.experiment import load_experiment


def build_plan_v2(plan: list, arm_name: str, repetitions: int = None, seeds: list = None, limit: int = 0, persona_pool: str = None) -> list:
    exp = load_experiment(); arm = exp.arm(arm_name)
    reps = repetitions or exp.repetitions; seeds = seeds or exp.seeds
    voices = arm.persona_voices
    out = []
    # stratify the voice rotation within each BIBD group so that every (voice × version) cell is filled
    counters = {}
    for s in plan[: limit or None]:
        key = (s.get("group"), s.get("questionnaire_version"))
        idx = counters.get(key, 0); counters[key] = idx + 1
        voice = voices[idx % len(voices)]
        for r in range(1, reps + 1):
            seed = seeds[(r - 1) % len(seeds)]
            ns = copy.deepcopy(s)
            ns.update({"session_id": f"{s['session_id']}_a{arm_name}_r{r}", "base_session_id": s["session_id"], "arm": arm_name,
                       "repetition": r, "seed": seed, "persona_model": voice.label,
                       "persona_model_spec": {"provider": voice.provider, "model": voice.model, "max_output_tokens": voice.max_output_tokens, "region": voice.region},
                       "persona_pool": persona_pool or exp.persona_pool, "experiment_fingerprint": exp.fingerprint})
            out.append(ns)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="data/config/administration_plan.json")
    ap.add_argument("--arm", default=None); ap.add_argument("--repetitions", type=int, default=None)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--output", default=None)
    a = ap.parse_args()
    exp = load_experiment(); arm = a.arm or exp.default_arm
    plan = json.load(open(a.plan, encoding="utf-8"))
    v2 = build_plan_v2(plan, arm, a.repetitions, limit=a.limit)
    out = a.output or f"data/config/administration_plan_v2_{arm}.json"
    json.dump(v2, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(f"wrote {out}: {len(v2)} sessions | voices × versions:", dict(Counter((s['persona_model'], s['questionnaire_version']) for s in v2)))


if __name__ == "__main__":
    main()

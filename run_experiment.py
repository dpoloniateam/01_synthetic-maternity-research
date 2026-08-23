#!/usr/bin/env python3
"""
Synthetic Design Laboratory 2 — experiment entry point (development 9, 23 Aug 2026).

    python run_experiment.py --arm P --limit 30 --repetitions 3          # persona stage (sessions)
    python run_experiment.py --arm P --stage judge --transcripts <dir>    # judge panel over transcripts
    python run_experiment.py --arm P --check                              # offline checks only (no API calls)

Everything else comes from config/experiment.yaml (EXPERIMENT_CONFIG). The run directory (SDL_RUN_DIR) receives
requests.jsonl, manifest.json, the plan actually run, transcripts and scores.
"""
import os, sys, json, argparse, time
from pathlib import Path
from datetime import datetime


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.environ.get("EXPERIMENT_CONFIG", "config/experiment.yaml"))
    ap.add_argument("--arm", default=None)
    ap.add_argument("--stage", choices=["sessions", "judge", "all"], default="sessions")
    ap.add_argument("--plan", default="data/config/administration_plan.json")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--repetitions", type=int, default=None)
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--transcripts", default=None)
    ap.add_argument("--check", action="store_true", help="offline checks only")
    ap.add_argument("--halt-usd", type=float, default=None)
    a = ap.parse_args()
    os.environ["EXPERIMENT_CONFIG"] = a.config
    from src.config.experiment import load_experiment
    exp = load_experiment(a.config, force=True)
    arm = exp.arm(a.arm)
    os.environ["EXPERIMENT_ARM"] = arm.name
    run_dir = a.run_dir or os.environ.get("SDL_RUN_DIR") or str(Path(exp.output_root) / f"{exp.name}_{arm.name}_{datetime.now():%Y%m%d_%H%M%S}")
    os.environ["SDL_RUN_DIR"] = run_dir
    if a.halt_usd is not None:
        os.environ["SDL_COST_HALT_USD"] = str(a.halt_usd)
    elif "SDL_COST_HALT_USD" not in os.environ:
        os.environ["SDL_COST_HALT_USD"] = str(exp.cost_halt_usd)
    if not a.check:
        Path(run_dir).mkdir(parents=True, exist_ok=True)
    print(f"experiment {exp.name} v{exp.version} | arm {arm.name} — {arm.description}\nvoices: {[s.label for s in arm.persona_voices]}\njudges: {[s.label for s in arm.judges]}\nrun dir: {run_dir} | halt USD {os.environ['SDL_COST_HALT_USD']} | config sha256 {exp.fingerprint[:16]}")
    if a.check:
        from src.questionnaire.administration_check import compare_versions
        personas = [json.loads(l) for l in open(exp.persona_pool, encoding="utf-8") if l.strip()]
        rep = compare_versions(json.load(open("data/questionnaires/Q_V4.json")), json.load(open("data/questionnaires/refined/Q_V4_R1.json")), personas[:20])
        print("administration check (V4 vs V4_R1, 20 personas):", {k: v for k, v in rep.items() if k != "per_persona"})
        from src.questionnaire.frameworks import LATENT_DIMENSIONS
        enc = set(personas[0].get("latent_dimensions_canonical", {}))
        print("canonical dimensions encoded in pool:", len(enc & set(LATENT_DIMENSIONS)), "of", len(LATENT_DIMENSIONS))
        return 0
    from src.provenance.request_cache import get_cache
    cache = get_cache()
    if a.stage in ("sessions", "all"):
        from src.orchestration.plan_repetitions import build_plan_v2
        from src.orchestration.session_runner import run_batch
        plan = json.load(open(a.plan, encoding="utf-8"))
        v2 = build_plan_v2(plan, arm.name, a.repetitions, limit=a.limit)
        plan_path = Path(run_dir) / "plan.json"; json.dump(v2, open(plan_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        out_dir = str(Path(run_dir) / "transcripts")
        summary = run_batch(str(plan_path), out_dir, limit=0, parallel=a.parallel, force=False)
        print(json.dumps({k: summary[k] for k in ("total_planned", "total_completed", "total_failed", "total_cost_usd", "provenance_cost_usd") if k in summary}, indent=1))
    if a.stage in ("judge", "all"):
        from src.evaluation.quality_scorer import score_transcript
        t_dir = Path(a.transcripts or (Path(run_dir) / "transcripts"))
        personas = {}
        for l in open(exp.persona_pool, encoding="utf-8"):
            if l.strip():
                p = json.loads(l); personas[p["composite_id"]] = p
        questionnaires = {}
        for v in range(1, 6):
            qf = Path("data/questionnaires") / f"Q_V{v}.json"
            if qf.exists():
                questionnaires[v] = json.load(open(qf, encoding="utf-8"))
        out = Path(run_dir) / "quality_scores.jsonl"
        n = 0
        with open(out, "a", encoding="utf-8") as f:
            for tf in sorted(t_dir.glob("T_*.json")):
                t = json.load(open(tf, encoding="utf-8"))
                if t.get("status") == "failed":
                    continue
                for rec in score_transcript(t, personas.get(t.get("persona_id"), {}), questionnaires):
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n"); n += 1
        print(f"scored {n} pairs → {out}")
    m = cache.manifest()
    print(f"manifest → {Path(run_dir)/'manifest.json'} | cost USD {m['cost_total_usd']:.4f} by stage {m['cost_by_stage_usd']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

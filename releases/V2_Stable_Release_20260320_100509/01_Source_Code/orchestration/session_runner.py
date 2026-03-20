"""
Batch Session Runner — executes multiple interview sessions with
parallelism, resume support, and cost guardrails.

Usage:
    PIPELINE_ENV=dev python -m src.orchestration.session_runner \
        --plan data/config/administration_plan.json \
        --output data/transcripts/ \
        --limit 4 --parallel 1
"""
import json, argparse, logging, time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config.models import tracker, ENV
from src.orchestration.questionnaire_interview import run_questionnaire_interview

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

# Cost ceilings per environment
COST_CEILINGS = {
    "dev": 20.0,
    "test": 50.0,
    "prod": 100.0,
}


def get_completed_sessions(output_dir: str) -> set:
    """Find already-completed session IDs in the output directory."""
    completed = set()
    out = Path(output_dir)
    if out.exists():
        for f in out.glob("T_S_*.json"):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                if data.get("status") in ("completed", "partial"):
                    sid = data.get("session_id", "")
                    if sid:
                        completed.add(sid)
            except Exception:
                pass
    return completed


def run_batch(plan_file: str, output_dir: str, limit: int = 0,
              parallel: int = 1, force: bool = False) -> dict:
    """Run a batch of interview sessions.

    Args:
        plan_file: Path to administration_plan.json
        output_dir: Directory for transcript output
        limit: Max sessions to run (0=all)
        parallel: Number of parallel threads
        force: If True, re-run even if transcript exists

    Returns:
        Batch summary dict
    """
    # Load plan
    with open(plan_file) as f:
        plan = json.load(f)
    log.info(f"Loaded {len(plan)} sessions from plan")

    # Check for completed sessions
    if not force:
        completed = get_completed_sessions(output_dir)
        if completed:
            log.info(f"Found {len(completed)} completed sessions — skipping")
            plan = [s for s in plan if s["session_id"] not in completed]
            log.info(f"Remaining: {len(plan)} sessions")

    # Apply limit
    if limit > 0:
        plan = plan[:limit]
    log.info(f"Will run {len(plan)} sessions (parallel={parallel})")

    # Cost ceiling
    ceiling = COST_CEILINGS.get(ENV.value, 20.0)
    log.info(f"Cost ceiling: ${ceiling:.2f} ({ENV.value})")

    # Run sessions
    results = []
    failed = []
    start_time = time.time()

    if parallel <= 1:
        # Sequential execution
        for i, session in enumerate(plan):
            # Cost check
            cost = tracker.summary()
            if cost["total_cost_usd"] >= ceiling:
                log.warning(f"Cost ceiling reached (${cost['total_cost_usd']:.2f} >= ${ceiling:.2f})")
                break

            try:
                transcript = run_questionnaire_interview(session, output_dir)
                results.append(transcript)
                if transcript.get("status") == "failed":
                    failed.append(session["session_id"])
            except Exception as e:
                log.error(f"Session {session['session_id']} crashed: {e}")
                failed.append(session["session_id"])

            # Progress report every 10 sessions
            if (i + 1) % 10 == 0:
                cost = tracker.summary()
                elapsed = time.time() - start_time
                log.info(f"\n  Progress: {i+1}/{len(plan)} sessions, "
                         f"${cost['total_cost_usd']:.4f}, "
                         f"{elapsed:.0f}s elapsed")
    else:
        # Parallel execution
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {}
            for i, session in enumerate(plan):
                # Stagger starts
                if i > 0:
                    time.sleep(0.5)
                future = executor.submit(
                    run_questionnaire_interview, session, output_dir
                )
                futures[future] = session

            for i, future in enumerate(as_completed(futures)):
                session = futures[future]
                try:
                    transcript = future.result()
                    results.append(transcript)
                    if transcript.get("status") == "failed":
                        failed.append(session["session_id"])
                except Exception as e:
                    log.error(f"Session {session['session_id']} crashed: {e}")
                    failed.append(session["session_id"])

                # Progress report
                if (i + 1) % 10 == 0:
                    cost = tracker.summary()
                    log.info(f"\n  Progress: {i+1}/{len(plan)} done, "
                             f"${cost['total_cost_usd']:.4f}")

    # Build batch summary
    elapsed = round(time.time() - start_time, 1)
    cost = tracker.summary()

    completed_results = [r for r in results if r.get("status") != "failed"]
    total_turns = sum(r.get("metadata", {}).get("total_turns", 0) for r in completed_results)
    total_questions = sum(r.get("metadata", {}).get("questions_asked", 0) for r in completed_results)
    total_probes = sum(r.get("metadata", {}).get("probes_deployed", 0) for r in completed_results)
    n_completed = len(completed_results)

    # Version × stage distribution
    vs_dist = defaultdict(lambda: defaultdict(int))
    for r in completed_results:
        vs_dist[f"V{r.get('questionnaire_version', '?')}"][r.get("persona_journey_stage", "?")] += 1

    summary = {
        "batch_timestamp": datetime.now().isoformat(),
        "environment": ENV.value,
        "total_planned": len(plan),
        "total_attempted": len(results),
        "total_completed": n_completed,
        "total_failed": len(failed),
        "failed_sessions": failed,
        "total_turns": total_turns,
        "total_questions_asked": total_questions,
        "total_probes_deployed": total_probes,
        "avg_turns_per_session": round(total_turns / max(n_completed, 1), 1),
        "avg_questions_per_session": round(total_questions / max(n_completed, 1), 1),
        "avg_probes_per_session": round(total_probes / max(n_completed, 1), 1),
        "total_cost_usd": cost["total_cost_usd"],
        "cost_per_session": round(cost["total_cost_usd"] / max(n_completed, 1), 4),
        "cost_by_task": cost.get("by_task", {}),
        "duration_seconds": elapsed,
        "version_x_stage": {k: dict(v) for k, v in sorted(vs_dist.items())},
    }

    # Save summary
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = out / f"batch_summary_{ts}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Console report
    log.info(f"\n{'='*70}")
    log.info("BATCH SUMMARY")
    log.info(f"{'='*70}")
    log.info(f"  Sessions: {n_completed} completed, {len(failed)} failed "
             f"(of {len(plan)} planned)")
    log.info(f"  Total turns: {total_turns} "
             f"(avg {summary['avg_turns_per_session']}/session)")
    log.info(f"  Questions asked: {total_questions} "
             f"(avg {summary['avg_questions_per_session']}/session)")
    log.info(f"  Probes deployed: {total_probes} "
             f"(avg {summary['avg_probes_per_session']}/session)")
    log.info(f"  Total cost: ${cost['total_cost_usd']:.4f} "
             f"(${summary['cost_per_session']:.4f}/session)")
    log.info(f"  Duration: {elapsed:.0f}s")

    if cost.get("by_task"):
        log.info(f"\n  Cost by task:")
        for task, info in cost["by_task"].items():
            log.info(f"    {task:<25s} {info['calls']:>4d} calls  ${info['cost_usd']:.4f}")

    if failed:
        log.info(f"\n  Failed sessions: {', '.join(failed)}")

    log.info(f"\n  Summary → {summary_path}")
    log.info(f"{'='*70}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Batch Session Runner")
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--output", type=str, default="data/transcripts/")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--parallel", type=int, default=1)
    parser.add_argument("--force", action="store_true",
                        help="Re-run even if transcripts exist")
    args = parser.parse_args()

    log.info(f"Environment: {ENV.value}")
    run_batch(args.plan, args.output, args.limit, args.parallel, args.force)


if __name__ == "__main__":
    main()

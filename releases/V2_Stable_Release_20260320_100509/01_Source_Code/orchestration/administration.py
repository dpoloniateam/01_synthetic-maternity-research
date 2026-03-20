"""
Experimental Design & Administration Plan — Balanced Incomplete Block Design (BIBD).

150 personas × 2 versions each = 300 sessions.
5 groups of 30 personas, stratified by journey stage and risk level.

Usage:
    python -m src.orchestration.administration \
        --personas data/composite_personas/composites.jsonl \
        --questionnaires data/questionnaires/ \
        --output data/config/administration_plan.json
"""
import json, argparse, logging, random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from src.config.models import get_model, get_provider, ENV

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

# BIBD: 5 groups, each persona in exactly 2 versions, each version gets 60 personas
GROUP_VERSION_MAP = {
    "A": [1, 2],
    "B": [1, 3],
    "C": [2, 4],
    "D": [3, 5],
    "E": [4, 5],
}

GROUPS = list(GROUP_VERSION_MAP.keys())
GROUP_SIZE = 30


def load_personas(path: str) -> list:
    personas = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                personas.append(json.loads(line))
    return personas


def stratified_assign(personas: list) -> dict:
    """Assign 150 personas to 5 groups of 30 with balanced strata."""
    rng = random.Random(42)

    # Sort for reproducibility
    personas_sorted = sorted(personas, key=lambda p: (
        p.get("journey_stage", ""),
        p.get("risk_level", ""),
        p.get("composite_id", ""),
    ))

    # Build strata: (journey_stage, risk_level) → list of persona_ids
    strata = defaultdict(list)
    for p in personas_sorted:
        key = (p.get("journey_stage", "unknown"), p.get("risk_level", "unknown"))
        strata[key].append(p)

    # Round-robin assignment across groups within each stratum
    assignments = {g: [] for g in GROUPS}
    group_idx = 0

    for stratum_key in sorted(strata.keys()):
        members = strata[stratum_key]
        rng.shuffle(members)
        for p in members:
            # Find group with fewest members (that hasn't hit cap)
            candidates = sorted(GROUPS, key=lambda g: len(assignments[g]))
            for g in candidates:
                if len(assignments[g]) < GROUP_SIZE:
                    assignments[g].append(p)
                    break
            group_idx += 1

    return assignments


def build_plan(assignments: dict, questionnaires_dir: str) -> list:
    """Build the full administration plan from group assignments."""
    plan = []
    session_num = 0

    interviewer_model = f"{get_provider('interviewer')}/{get_model('interviewer')}"

    for group in GROUPS:
        versions = GROUP_VERSION_MAP[group]
        for persona in assignments[group]:
            pid = persona.get("composite_id", "")
            for version in versions:
                session_num += 1
                session_id = f"S_{session_num:03d}"

                # Persona model comes from their target_model field (set in Sprint 2)
                persona_model = persona.get("target_model", "google/gemini-3.1-flash-lite-preview")

                adapted_file = f"data/questionnaires/adapted/Q_V{version}_{pid.upper()}.json"

                # Estimate turns based on journey stage (stage-filtered question count)
                stage = persona.get("journey_stage", "pregnancy")
                if stage in ("preconception", "first_trimester"):
                    est_turns = 20
                elif stage in ("postpartum",):
                    est_turns = 24
                else:
                    est_turns = 22

                plan.append({
                    "session_id": session_id,
                    "group": group,
                    "persona_id": pid,
                    "persona_name": persona.get("name", "Unknown"),
                    "persona_journey_stage": stage,
                    "persona_risk_level": persona.get("risk_level", "unknown"),
                    "persona_vulnerability_flags": persona.get("vulnerability_flags", []),
                    "questionnaire_version": version,
                    "questionnaire_file": f"data/questionnaires/Q_V{version}.json",
                    "adapted_questionnaire_file": adapted_file,
                    "interviewer_model": interviewer_model,
                    "persona_model": persona_model,
                    "estimated_turns": est_turns,
                    "priority": version,
                })

    return plan


def build_summary(plan: list, assignments: dict) -> dict:
    """Build administration summary statistics."""
    summary = {
        "total_sessions": len(plan),
        "total_personas": sum(len(v) for v in assignments.values()),
        "sessions_per_version": {},
        "personas_per_group": {},
        "version_x_stage": {},
        "version_x_risk": {},
        "flags_per_group": {},
        "generated_at": datetime.now().isoformat(),
        "environment": ENV.value,
    }

    # Sessions per version
    v_counts = defaultdict(int)
    for s in plan:
        v_counts[s["questionnaire_version"]] += 1
    summary["sessions_per_version"] = dict(sorted(v_counts.items()))

    # Personas per group
    for g in GROUPS:
        summary["personas_per_group"][g] = {
            "count": len(assignments[g]),
            "versions": GROUP_VERSION_MAP[g],
        }

    # Version × stage distribution
    vs = defaultdict(lambda: defaultdict(int))
    for s in plan:
        vs[f"V{s['questionnaire_version']}"][s["persona_journey_stage"]] += 1
    summary["version_x_stage"] = {k: dict(v) for k, v in sorted(vs.items())}

    # Version × risk distribution
    vr = defaultdict(lambda: defaultdict(int))
    for s in plan:
        vr[f"V{s['questionnaire_version']}"][s["persona_risk_level"]] += 1
    summary["version_x_risk"] = {k: dict(v) for k, v in sorted(vr.items())}

    # Vulnerability flags per group
    for g in GROUPS:
        flags = defaultdict(int)
        for p in assignments[g]:
            for f in p.get("vulnerability_flags", []):
                flags[f] += 1
        summary["flags_per_group"][g] = dict(sorted(flags.items(), key=lambda x: -x[1]))

    return summary


def main():
    parser = argparse.ArgumentParser(description="Administration Plan Generator")
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--questionnaires", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    log.info(f"Environment: {ENV.value}")

    # Load personas
    personas = load_personas(args.personas)
    log.info(f"Loaded {len(personas)} personas")

    # Verify questionnaires exist
    q_dir = Path(args.questionnaires)
    for v in range(1, 6):
        qf = q_dir / f"Q_V{v}.json"
        if not qf.exists():
            log.error(f"Missing questionnaire: {qf}")
            return
    log.info(f"All 5 questionnaire versions found in {q_dir}")

    # Assign to groups
    assignments = stratified_assign(personas)
    for g in GROUPS:
        log.info(f"  Group {g}: {len(assignments[g])} personas → versions {GROUP_VERSION_MAP[g]}")

    # Build plan
    plan = build_plan(assignments, args.questionnaires)
    log.info(f"Generated {len(plan)} session definitions")

    # Export plan
    with open(out, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    log.info(f"Plan → {out}")

    # Build and export summary
    summary = build_summary(plan, assignments)
    summary_path = out.parent / "administration_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log.info(f"Summary → {summary_path}")

    # Console summary
    log.info(f"\n{'='*60}")
    log.info("ADMINISTRATION PLAN SUMMARY")
    log.info(f"{'='*60}")
    log.info(f"Total sessions: {summary['total_sessions']}")
    log.info(f"Sessions per version: {summary['sessions_per_version']}")

    log.info(f"\nVersion × Journey Stage:")
    stages = sorted(set(s["persona_journey_stage"] for s in plan))
    header = f"{'':>6}" + "".join(f"{st:>18}" for st in stages)
    log.info(header)
    for vk, dist in sorted(summary["version_x_stage"].items()):
        row = f"{vk:>6}" + "".join(f"{dist.get(st, 0):>18}" for st in stages)
        log.info(row)

    log.info(f"\nVersion × Risk Level:")
    risks = sorted(set(s["persona_risk_level"] for s in plan))
    header = f"{'':>6}" + "".join(f"{r:>10}" for r in risks)
    log.info(header)
    for vk, dist in sorted(summary["version_x_risk"].items()):
        row = f"{vk:>6}" + "".join(f"{dist.get(r, 0):>10}" for r in risks)
        log.info(row)

    log.info(f"\nFlags per group (top 3):")
    for g, flags in summary["flags_per_group"].items():
        top = list(flags.items())[:3]
        log.info(f"  {g}: {', '.join(f'{f}={c}' for f, c in top)}")

    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()

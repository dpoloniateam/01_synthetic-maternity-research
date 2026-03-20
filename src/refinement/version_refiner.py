"""
Version Refiner — applies probe fixes to produce refined questionnaire version(s)
and generates re-administration plan.

Usage:
    python -m src.refinement.version_refiner \
        --plan data/refinement/refinement_plan.json \
        --fixes data/refinement/probe_fixes.json \
        --questionnaires data/questionnaires/ \
        --personas data/composite_personas/composites.jsonl \
        --output data/refinement/
"""
import json, argparse, logging, copy, random
from pathlib import Path
from collections import defaultdict

from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)


def load_jsonl(path: str) -> list:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def refine_questionnaire(questionnaire: dict, fixes: dict, plan: dict) -> tuple:
    """Apply fixes to questionnaire, return (refined_q, audit_trail)."""
    refined = copy.deepcopy(questionnaire)
    audit = []
    questions = refined.get("questions", [])
    q_lookup = {q.get("question_id", ""): i for i, q in enumerate(questions)}
    version = fixes["version"]

    # 1. REPLACE bottom questions with action="replace"
    for bq in plan.get("bottom_questions", []):
        if bq["action"] == "replace":
            qid = bq["question_id"]
            # Find a NEW probe that targets this question's phase
            replacement_probes = [p for p in fixes.get("probes", []) if p.get("attach_to_question") == "NEW"]
            if replacement_probes and qid in q_lookup:
                idx = q_lookup[qid]
                old_text = questions[idx].get("question_text", questions[idx].get("text", ""))
                rp = replacement_probes.pop(0)
                questions[idx]["question_text"] = rp["probe_text"]
                questions[idx]["text"] = rp["probe_text"]
                questions[idx]["refined"] = True
                questions[idx]["refinement_action"] = "replaced"
                audit.append({
                    "action": "replace",
                    "question_id": qid,
                    "old_text": old_text[:100],
                    "new_text": rp["probe_text"][:100],
                    "rationale": rp.get("rationale", "Bottom question replaced"),
                })
                log.info(f"  REPLACED {qid} (richness={bq['mean_richness']:.2f})")

    # 2. ADD PROBES to existing questions targeting blind spots
    for probe in fixes.get("probes", []):
        attach_to = probe.get("attach_to_question", "")
        if attach_to and attach_to != "NEW" and attach_to in q_lookup:
            idx = q_lookup[attach_to]
            existing_probes = questions[idx].get("probes", questions[idx].get("follow_ups", []))
            if isinstance(existing_probes, list):
                new_probe = {
                    "text": probe["probe_text"],
                    "target_dimension": probe.get("target_dimension", ""),
                    "added_in_refinement": True,
                }
                existing_probes.append(new_probe)
                if "probes" in questions[idx]:
                    questions[idx]["probes"] = existing_probes
                else:
                    questions[idx]["follow_ups"] = existing_probes
                audit.append({
                    "action": "add_probe",
                    "question_id": attach_to,
                    "probe_text": probe["probe_text"][:100],
                    "target_dimension": probe.get("target_dimension", ""),
                    "rationale": probe.get("rationale", ""),
                })

    # 3. ADD NEW QUESTIONS for blind spots with no targeting questions
    new_q_probes = [p for p in fixes.get("probes", []) if p.get("attach_to_question") == "NEW"]
    # Group by journey phase
    by_phase = defaultdict(list)
    for p in new_q_probes:
        phase = p.get("target_journey_phase", "pregnancy")
        by_phase[phase].append(p)

    for phase, probes in by_phase.items():
        if not probes:
            continue
        # Create a new question from the first probe, attach rest as follow-ups
        new_qid = f"V{version}_NEW_{phase[:4].upper()}_{len(questions)+1:02d}"
        new_q = {
            "question_id": new_qid,
            "question_text": probes[0]["probe_text"],
            "text": probes[0]["probe_text"],
            "journey_phase": phase,
            "target_latent_dimensions": list({p.get("target_dimension", "") for p in probes}),
            "probes": [{"text": p["probe_text"], "target_dimension": p.get("target_dimension", ""), "added_in_refinement": True} for p in probes[1:]],
            "refined": True,
            "refinement_action": "new_question",
        }
        # Insert at appropriate position (find last question in this phase)
        insert_idx = len(questions)
        phase_lower = phase.lower()
        for i, q in enumerate(questions):
            q_phase = q.get("journey_phase", "").lower()
            if phase_lower in q_phase or q_phase in phase_lower:
                insert_idx = i + 1
        questions.insert(insert_idx, new_q)
        audit.append({
            "action": "new_question",
            "question_id": new_qid,
            "phase": phase,
            "text": probes[0]["probe_text"][:100],
            "n_probes": len(probes) - 1,
            "target_dimensions": new_q["target_latent_dimensions"],
        })
        log.info(f"  ADDED new question {new_qid} in {phase} with {len(probes)-1} probes")

    refined["questions"] = questions
    refined["refined"] = True
    refined["refinement_iteration"] = 1
    refined["refinement_changes"] = len(audit)

    return refined, audit


def generate_re_admin_plan(plan: dict, personas: list, refined_version: int, timestamp: str) -> dict:
    """Generate re-administration plan for testing refined questionnaire."""
    config = plan["re_administration_config"]
    n_sessions = config["n_sessions"]
    excluded_ids = set(config.get("excluded_persona_ids", []))

    # Filter to available personas
    available = [p for p in personas if p.get("composite_id", "") in excluded_ids]
    if len(available) < n_sessions:
        available = [p for p in personas]
        random.shuffle(available)

    # Stratify selection
    by_stage = defaultdict(list)
    by_risk = defaultdict(list)
    for p in available:
        by_stage[p.get("journey_stage", "unknown")].append(p)
        by_risk[p.get("risk_level", "unknown")].append(p)

    selected = []
    seen = set()
    # Round-robin across stages
    stage_iters = {s: iter(ps) for s, ps in by_stage.items()}
    while len(selected) < n_sessions:
        added = False
        for stage, it in stage_iters.items():
            if len(selected) >= n_sessions:
                break
            try:
                p = next(it)
                pid = p.get("composite_id", "")
                if pid not in seen:
                    seen.add(pid)
                    selected.append(p)
                    added = True
            except StopIteration:
                continue
        if not added:
            break

    # Build sessions
    sessions = []
    for i, p in enumerate(selected):
        sid = f"S_R{i+1:03d}"
        sessions.append({
            "session_id": sid,
            "persona_id": p.get("composite_id", ""),
            "questionnaire_version": refined_version,
            "journey_stage": p.get("journey_stage", ""),
            "risk_level": p.get("risk_level", ""),
        })

    re_admin_plan = {
        "plan_type": "re_administration",
        "timestamp": timestamp,
        "refined_version": refined_version,
        "n_sessions": len(sessions),
        "sessions": sessions,
    }

    return re_admin_plan


def main():
    parser = argparse.ArgumentParser(description="Version Refiner")
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--fixes", type=str, required=True)
    parser.add_argument("--questionnaires", type=str, required=True)
    parser.add_argument("--personas", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    run = TimestampedRun(args.output)
    run.record_read(args.plan)
    run.record_read(args.fixes)

    with open(args.plan) as f:
        plan = json.load(f)
    with open(args.fixes) as f:
        fixes = json.load(f)

    winner_v = plan["winner"]["version"]
    q_file = Path(args.questionnaires) / f"Q_V{winner_v}.json"
    run.record_read(str(q_file))
    with open(q_file) as f:
        questionnaire = json.load(f)

    personas = load_jsonl(args.personas)
    run.record_read(args.personas)

    log.info(f"Refining V{winner_v} (strategy: {plan['winner']['strategy']})")

    # Refine questionnaire
    refined, audit = refine_questionnaire(questionnaire, fixes, plan)
    log.info(f"  Applied {len(audit)} changes")

    # Write refined questionnaire
    refined_dir = Path(args.questionnaires) / "refined"
    refined_dir.mkdir(parents=True, exist_ok=True)

    refined_run = TimestampedRun(str(refined_dir))
    refined_path = refined_run.output_path(f"Q_V{winner_v}_R1.json")
    with open(refined_path, "w") as f:
        json.dump(refined, f, indent=2, ensure_ascii=False)
    refined_run.stable_pointer(f"Q_V{winner_v}_R1.json", refined_path)
    run.files_written.extend(refined_run.files_written)

    # Write human-readable version
    md_path = refined_run.output_path(f"Q_V{winner_v}_R1.md")
    with open(md_path, "w") as f:
        f.write(f"# Refined Questionnaire V{winner_v}_R1\n\n")
        f.write(f"Strategy: {plan['winner']['strategy']}\n")
        f.write(f"Refinement iteration: 1\n")
        f.write(f"Changes applied: {len(audit)}\n\n")
        for i, q in enumerate(refined.get("questions", [])):
            marker = " [REFINED]" if q.get("refined") else ""
            f.write(f"### Q{i+1}: {q.get('question_id', '')}{marker}\n")
            f.write(f"{q.get('question_text', q.get('text', ''))}\n")
            probes = q.get("probes", q.get("follow_ups", []))
            if probes:
                for p in probes:
                    p_text = p.get("text", p) if isinstance(p, dict) else str(p)
                    added = " [NEW]" if isinstance(p, dict) and p.get("added_in_refinement") else ""
                    f.write(f"  - {p_text}{added}\n")
            f.write("\n")
    refined_run.stable_pointer(f"Q_V{winner_v}_R1.md", md_path)

    # Write audit trail
    audit_path = run.output_path("refinement_audit_trail.json")
    with open(audit_path, "w") as f:
        json.dump({"version": winner_v, "iteration": 1, "changes": audit}, f, indent=2, ensure_ascii=False)
    run.stable_pointer("refinement_audit_trail.json", audit_path)

    # Generate re-administration plan
    re_plan = generate_re_admin_plan(plan, personas, winner_v, run.timestamp)

    config_dir = Path("data/config")
    re_plan_path = config_dir / f"re_administration_plan_{run.timestamp}.json"
    with open(re_plan_path, "w") as f:
        json.dump(re_plan, f, indent=2, ensure_ascii=False)
    run.files_written.append(str(re_plan_path))

    import shutil
    stable_re_plan = config_dir / "re_administration_plan.json"
    shutil.copy2(re_plan_path, stable_re_plan)
    run.files_written.append(str(stable_re_plan))

    run.write_manifest("version_refiner", config={"winner_v": winner_v, "changes": len(audit)})

    log.info(f"Refined questionnaire → {refined_path}")
    log.info(f"Audit trail → {audit_path}")
    log.info(f"Re-admin plan → {re_plan_path} ({re_plan['n_sessions']} sessions)")


if __name__ == "__main__":
    main()

"""
EHR-Contextual Question Adapter — personalises questionnaires per composite persona.

Adapts base questionnaire questions based on Synthea EHR data using a rule engine.
The same base questionnaire is PERSONALISED per patient profile, making synthetic
interviews more realistic and clinically grounded.

Usage:
    python -m src.questionnaire.ehr_adapter \
        --questionnaire data/questionnaires/Q_V1.json \
        --personas data/composite_personas/composites.jsonl \
        --output data/questionnaires/adapted/ --limit 5
"""
import json, argparse, logging, copy
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from src.questionnaire.frameworks import JOURNEY_PHASES

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# ADAPTATION RULES
# ═══════════════════════════════════════════════════════════════════════════════

# SNOMED codes for complication-based triggers
COMPLICATION_SNOMED = {
    "15394000":  "pre_eclampsia",
    "398254007": "pre_eclampsia",
    "11687002":  "gestational_diabetes",
    "46894009":  "gestational_diabetes",
    "17369002":  "miscarriage",
    "161744009": "miscarriage_history",
    "271903000": "miscarriage",
    "15938005":  "eclampsia",
    "34801009":  "ectopic_pregnancy",
    "16356006":  "multiple_pregnancy",
}

# Probes triggered by specific complications
COMPLICATION_PROBES = {
    "pre_eclampsia": [
        {
            "probe_text": "How did the diagnosis of pre-eclampsia change your feelings about the pregnancy?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["trust_distrust", "autonomy_vs_dependence"],
        },
        {
            "probe_text": "What was it like having more frequent monitoring after the diagnosis?",
            "probe_type": "elaboration",
            "target_latent_dimensions": ["structural_barriers", "power_dynamics"],
        },
    ],
    "gestational_diabetes": [
        {
            "probe_text": "How did managing gestational diabetes affect your daily life?",
            "probe_type": "elaboration",
            "target_latent_dimensions": ["autonomy_vs_dependence", "body_image_autonomy"],
        },
        {
            "probe_text": "What was the monitoring and diet management burden like?",
            "probe_type": "structural",
            "target_latent_dimensions": ["structural_barriers"],
        },
    ],
    "miscarriage": [
        {
            "probe_text": "Given your previous experience of pregnancy loss, how has that shaped your feelings in this pregnancy?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["trust_distrust", "identity_tensions"],
        },
        {
            "probe_text": "Did your care providers acknowledge your previous loss? How did that feel?",
            "probe_type": "contrast",
            "target_latent_dimensions": ["dignity_respect", "continuity_of_care"],
        },
    ],
    "miscarriage_history": [
        {
            "probe_text": "How did your history of pregnancy loss affect how you approached this pregnancy?",
            "probe_type": "motivation",
            "target_latent_dimensions": ["trust_distrust", "identity_tensions"],
        },
    ],
    "eclampsia": [
        {
            "probe_text": "Can you tell me about the emergency experience? How did it feel to lose that sense of control?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["power_dynamics", "autonomy_vs_dependence"],
        },
    ],
    "ectopic_pregnancy": [
        {
            "probe_text": "After your experience with ectopic pregnancy, how has fear of recurrence affected your planning?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["trust_distrust", "body_image_autonomy"],
        },
    ],
    "multiple_pregnancy": [
        {
            "probe_text": "How did learning you were carrying multiples change your expectations and care experience?",
            "probe_type": "contrast",
            "target_latent_dimensions": ["autonomy_vs_dependence", "structural_barriers"],
        },
    ],
}

# Risk-level adaptation probes
RISK_PROBES = {
    "high": [
        {
            "probe_text": "What has it been like having more frequent monitoring and specialist appointments?",
            "probe_type": "elaboration",
            "target_latent_dimensions": ["structural_barriers", "continuity_of_care"],
        },
        {
            "probe_text": "How has being labelled 'high-risk' affected your feelings about the pregnancy?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["identity_tensions", "power_dynamics"],
        },
        {
            "probe_text": "Do you feel the level of medical attention has been reassuring or anxiety-inducing?",
            "probe_type": "contrast",
            "target_latent_dimensions": ["trust_distrust", "autonomy_vs_dependence"],
        },
    ],
    "medium": [
        {
            "probe_text": "How has it felt being between 'normal' and 'high-risk'? Did the clinical pathway change for you?",
            "probe_type": "contrast",
            "target_latent_dimensions": ["structural_barriers", "power_dynamics"],
        },
    ],
    "low": [
        {
            "probe_text": "Has being told your pregnancy is 'low-risk' felt reassuring, or did you sometimes wish they took things more seriously?",
            "probe_type": "contrast",
            "target_latent_dimensions": ["trust_distrust", "dignity_respect"],
        },
    ],
}

# Vulnerability flag adaptation probes
VULNERABILITY_PROBES = {
    "single_parent": [
        {
            "probe_text": "What has it been like making pregnancy decisions without a partner?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["autonomy_vs_dependence", "partner_role"],
        },
        {
            "probe_text": "Who do you plan to have with you during labour, and how did you decide?",
            "probe_type": "motivation",
            "target_latent_dimensions": ["informal_care_networks", "partner_role"],
        },
        {
            "probe_text": "Have financial concerns affected your pregnancy choices?",
            "probe_type": "structural",
            "target_latent_dimensions": ["structural_barriers"],
        },
    ],
    "immigration": [
        {
            "probe_text": "How has navigating the healthcare system been different from what you're used to?",
            "probe_type": "contrast",
            "target_latent_dimensions": ["structural_barriers", "power_dynamics"],
        },
        {
            "probe_text": "Are there cultural expectations about pregnancy and birth that feel different here?",
            "probe_type": "elaboration",
            "target_latent_dimensions": ["intergenerational_patterns", "identity_tensions"],
        },
    ],
    "language_barrier": [
        {
            "probe_text": "Have you ever felt that language made it harder to communicate what you needed?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["power_dynamics", "dignity_respect"],
        },
        {
            "probe_text": "What has your experience with interpreters or translated materials been like?",
            "probe_type": "elaboration",
            "target_latent_dimensions": ["structural_barriers", "trust_distrust"],
        },
    ],
    "rural_isolation": [
        {
            "probe_text": "How does distance to your hospital or clinic affect your pregnancy experience?",
            "probe_type": "structural",
            "target_latent_dimensions": ["structural_barriers"],
        },
        {
            "probe_text": "Have you used telehealth? If so, what was that like compared to in-person visits?",
            "probe_type": "contrast",
            "target_latent_dimensions": ["digital_information_seeking", "continuity_of_care"],
        },
    ],
    "low_income": [
        {
            "probe_text": "Have cost or insurance concerns ever affected what care you could access?",
            "probe_type": "structural",
            "target_latent_dimensions": ["structural_barriers", "power_dynamics"],
        },
        {
            "probe_text": "Have workplace accommodations during pregnancy been an issue?",
            "probe_type": "elaboration",
            "target_latent_dimensions": ["structural_barriers", "identity_tensions"],
        },
    ],
    "mental_health": [
        {
            "probe_text": "How has your mental health journey intersected with your pregnancy care?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["continuity_of_care", "trust_distrust"],
        },
    ],
    "previous_loss": [
        {
            "probe_text": "How has your previous loss shaped the way you experience this pregnancy?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["trust_distrust", "identity_tensions"],
        },
    ],
    "previous_trauma": [
        {
            "probe_text": "Have your past experiences ever made medical appointments or examinations feel difficult?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["power_dynamics", "dignity_respect", "body_image_autonomy"],
        },
    ],
    "fear_of_childbirth": [
        {
            "probe_text": "What are your specific fears about childbirth, and have your care providers addressed them?",
            "probe_type": "emotion",
            "target_latent_dimensions": ["trust_distrust", "autonomy_vs_dependence"],
        },
    ],
    "high_risk_medical": [
        {
            "probe_text": "How has your medical risk status changed how you relate to your care team?",
            "probe_type": "motivation",
            "target_latent_dimensions": ["power_dynamics", "trust_distrust"],
        },
    ],
}

# Journey stage relevance for question filtering
STAGE_TO_PHASES = {
    "preconception":     ["preconception"],
    "first_trimester":   ["preconception", "pregnancy"],
    "second_trimester":  ["pregnancy"],
    "third_trimester":   ["pregnancy", "birth"],
    "birth":             ["birth", "postpartum"],
    "postpartum":        ["postpartum"],
}


# ═══════════════════════════════════════════════════════════════════════════════
# ADAPTATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def adapt_questionnaire(base_questions: list, persona: dict) -> dict:
    """Adapt a questionnaire for a specific composite persona.

    Returns the adapted questionnaire with:
    - Filtered questions by journey stage relevance
    - Added complication-based probes
    - Added risk-level probes
    - Added vulnerability-based probes
    - Clear tagging of base vs. EHR-adapted probes
    """
    pid = persona.get("composite_id", "unknown")
    stage = persona.get("journey_stage", "pregnancy")
    risk = persona.get("risk_level", "unknown")
    flags = persona.get("vulnerability_flags", [])
    meta = persona.get("source_patient_metadata", {})
    snomed_codes = meta.get("pregnancy_snomed_codes", [])

    relevant_phases = set(STAGE_TO_PHASES.get(stage, ["pregnancy"]))

    # Identify complications from SNOMED codes
    complications = set()
    for code in snomed_codes:
        if code in COMPLICATION_SNOMED:
            complications.add(COMPLICATION_SNOMED[code])
    if meta.get("has_miscarriage_history"):
        complications.add("miscarriage_history")

    adapted_questions = []
    added_probe_count = 0

    for base_q in base_questions:
        q_phase = base_q.get("journey_phase", "pregnancy")

        # Filter: only include questions relevant to this persona's stage
        if q_phase not in relevant_phases:
            continue

        q = copy.deepcopy(base_q)

        # Check EHR adaptation triggers
        triggers = set(q.get("ehr_adaptation_triggers", []))

        # Tag all existing probes as "base"; normalise string probes to dicts
        normalised_probes = []
        for p in q.get("probes", []):
            if isinstance(p, str):
                normalised_probes.append({"probe_text": p, "probe_type": "elaboration",
                                          "target_latent_dimensions": [], "source": "base"})
            else:
                p["source"] = "base"
                normalised_probes.append(p)
        q["probes"] = normalised_probes

        # Add complication-based probes
        for comp_key in complications:
            trigger_key = f"if_{comp_key}"
            if trigger_key in triggers or comp_key in triggers:
                for probe_template in COMPLICATION_PROBES.get(comp_key, []):
                    probe = copy.deepcopy(probe_template)
                    probe["probe_id"] = f"{q['question_id']}_EHR_{comp_key[:4].upper()}"
                    probe["source"] = "ehr_complication"
                    probe["trigger"] = comp_key
                    q["probes"].append(probe)
                    added_probe_count += 1

        # Add risk-level probes (only to relevant questions)
        if "if_high_risk" in triggers and risk in ("high", "critical"):
            for probe_template in RISK_PROBES.get("high", []):
                probe = copy.deepcopy(probe_template)
                probe["probe_id"] = f"{q['question_id']}_EHR_RISK"
                probe["source"] = "ehr_risk"
                probe["trigger"] = "high_risk"
                q["probes"].append(probe)
                added_probe_count += 1
        elif "if_medium_risk" in triggers and risk == "medium":
            for probe_template in RISK_PROBES.get("medium", []):
                probe = copy.deepcopy(probe_template)
                probe["probe_id"] = f"{q['question_id']}_EHR_RISK"
                probe["source"] = "ehr_risk"
                q["probes"].append(probe)
                added_probe_count += 1

        # Add vulnerability probes (match against persona's flags)
        for flag in flags:
            trigger_key = f"if_{flag}"
            if trigger_key in triggers:
                for probe_template in VULNERABILITY_PROBES.get(flag, []):
                    probe = copy.deepcopy(probe_template)
                    probe["probe_id"] = f"{q['question_id']}_EHR_{flag[:6].upper()}"
                    probe["source"] = "ehr_vulnerability"
                    probe["trigger"] = flag
                    q["probes"].append(probe)
                    added_probe_count += 1

        adapted_questions.append(q)

    return {
        "persona_id": pid,
        "persona_name": persona.get("name", "Unknown"),
        "journey_stage": stage,
        "risk_level": risk,
        "vulnerability_flags": flags,
        "complications": sorted(complications),
        "relevant_phases": sorted(relevant_phases),
        "base_question_count": len(base_questions),
        "adapted_question_count": len(adapted_questions),
        "filtered_out": len(base_questions) - len(adapted_questions),
        "added_probes": added_probe_count,
        "questions": adapted_questions,
        "adapted_at": datetime.now().isoformat(),
    }


def adapt_with_universal_probes(adapted: dict) -> dict:
    """Add universal probes based on persona profile regardless of triggers.

    Some probes are relevant based on the persona's profile even if the
    base question didn't include a specific trigger for them.
    """
    persona_risk = adapted.get("risk_level", "unknown")
    persona_flags = set(adapted.get("vulnerability_flags", []))
    complications = set(adapted.get("complications", []))

    # Only add to the first relevant question of each phase to avoid probe overload
    phase_enriched = set()

    for q in adapted["questions"]:
        q_phase = q.get("journey_phase", "pregnancy")
        if q_phase in phase_enriched:
            continue

        probes_to_add = []

        # Risk-level universal probes (one per phase)
        if persona_risk in ("high", "critical") and q_phase in ("pregnancy", "birth"):
            probes_to_add.extend(RISK_PROBES.get("high", [])[:1])
        elif persona_risk == "low" and q_phase == "pregnancy":
            probes_to_add.extend(RISK_PROBES.get("low", [])[:1])

        # Vulnerability universal probes (one per phase per flag, max 2)
        added = 0
        for flag in persona_flags:
            if added >= 2:
                break
            flag_probes = VULNERABILITY_PROBES.get(flag, [])
            if flag_probes:
                probes_to_add.append(flag_probes[0])
                added += 1

        for probe_template in probes_to_add:
            probe = copy.deepcopy(probe_template)
            probe["probe_id"] = f"{q['question_id']}_UNIV_{len(q['probes'])+1:02d}"
            probe["source"] = "universal_adaptation"
            q["probes"].append(probe)
            adapted["added_probes"] += 1

        if probes_to_add:
            phase_enriched.add(q_phase)

    return adapted


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def adapt_from_plan(plan_file: str, personas_file: str, output_dir: str):
    """Batch-adapt questionnaires for all sessions in an administration plan."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Load plan
    with open(plan_file) as f:
        plan = json.load(f)
    log.info(f"Loaded plan: {len(plan)} sessions")

    # Load all personas into a lookup
    persona_map = {}
    with open(personas_file) as f:
        for line in f:
            line = line.strip()
            if line:
                p = json.loads(line)
                persona_map[p.get("composite_id", "")] = p
    log.info(f"Loaded {len(persona_map)} personas")

    # Load all questionnaire versions
    q_versions = {}
    versions_needed = set(s["questionnaire_version"] for s in plan)
    for v in versions_needed:
        q_file = f"data/questionnaires/Q_V{v}.json"
        with open(q_file) as f:
            qdata = json.load(f)
        q_versions[v] = qdata.get("questions", [])
        log.info(f"  V{v}: {len(q_versions[v])} base questions")

    # Find unique (persona, version) pairs to avoid duplicate work
    seen = set()
    unique_tasks = []
    for s in plan:
        key = (s["persona_id"], s["questionnaire_version"])
        if key not in seen:
            seen.add(key)
            unique_tasks.append(s)
    log.info(f"Unique (persona, version) pairs: {len(unique_tasks)}")

    # Adapt
    total_probes_added = 0
    skipped = 0
    for i, session in enumerate(unique_tasks):
        pid = session["persona_id"]
        version = session["questionnaire_version"]
        adapted_path = out / f"Q_V{version}_{pid.upper()}.json"

        # Skip if already exists
        if adapted_path.exists():
            skipped += 1
            continue

        persona = persona_map.get(pid)
        if not persona:
            log.warning(f"  Persona {pid} not found — skipping")
            continue

        adapted = adapt_questionnaire(q_versions[version], persona)
        adapted = adapt_with_universal_probes(adapted)
        total_probes_added += adapted["added_probes"]

        with open(adapted_path, "w", encoding="utf-8") as f:
            json.dump(adapted, f, indent=2, ensure_ascii=False)

        if (i + 1) % 50 == 0:
            log.info(f"  Adapted {i+1}/{len(unique_tasks)}")

    generated = len(unique_tasks) - skipped
    log.info(f"\nBatch adaptation complete:")
    log.info(f"  Generated: {generated}")
    log.info(f"  Skipped (existing): {skipped}")
    log.info(f"  Total probes added: {total_probes_added}")


def main():
    parser = argparse.ArgumentParser(description="EHR Question Adapter")
    parser.add_argument("--questionnaire", type=str, default=None,
                        help="Path to base questionnaire JSON (e.g., Q_V1.json)")
    parser.add_argument("--personas", type=str, required=True,
                        help="Path to composites JSONL")
    parser.add_argument("--output", type=str, required=True,
                        help="Output directory for adapted questionnaires")
    parser.add_argument("--plan", type=str, default=None,
                        help="Path to administration plan JSON (batch mode)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Adapt for first N personas only (0=all)")
    args = parser.parse_args()

    # Plan-based batch mode
    if args.plan:
        adapt_from_plan(args.plan, args.personas, args.output)
        return

    if not args.questionnaire:
        parser.error("--questionnaire is required when not using --plan mode")

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    # Load base questionnaire
    with open(args.questionnaire) as f:
        qdata = json.load(f)
    base_questions = qdata.get("questions", [])
    version = qdata.get("version", "?")
    log.info(f"Loaded V{version} questionnaire: {len(base_questions)} base questions")

    # Load personas
    personas = []
    with open(args.personas) as f:
        for line in f:
            line = line.strip()
            if line:
                personas.append(json.loads(line))
    if args.limit > 0:
        personas = personas[:args.limit]
    log.info(f"Loaded {len(personas)} personas")

    # Adapt
    results = []
    total_probes_added = 0
    for i, persona in enumerate(personas):
        adapted = adapt_questionnaire(base_questions, persona)
        adapted = adapt_with_universal_probes(adapted)
        total_probes_added += adapted["added_probes"]

        # Export individual adapted questionnaire
        pid = persona.get("composite_id", f"cp{i+1:03d}")
        path = out / f"Q_V{version}_{pid.upper()}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(adapted, f, indent=2, ensure_ascii=False)

        results.append({
            "persona_id": pid,
            "name": persona.get("name", "?"),
            "stage": persona.get("journey_stage", "?"),
            "risk": persona.get("risk_level", "?"),
            "flags": len(persona.get("vulnerability_flags", [])),
            "base_qs": adapted["base_question_count"],
            "adapted_qs": adapted["adapted_question_count"],
            "filtered": adapted["filtered_out"],
            "added_probes": adapted["added_probes"],
        })

        if (i + 1) % 25 == 0:
            log.info(f"  Adapted {i+1}/{len(personas)}")

    log.info(f"\nAdaptation complete: {len(results)} personas")
    log.info(f"  Total probes added: {total_probes_added}")
    log.info(f"  Avg probes per persona: {total_probes_added / max(len(results), 1):.1f}")

    # Summary
    summary = {
        "version": version,
        "total_personas": len(results),
        "total_probes_added": total_probes_added,
        "avg_probes_per_persona": round(total_probes_added / max(len(results), 1), 1),
        "results": results,
        "generated_at": datetime.now().isoformat(),
    }
    summary_path = out / f"adaptation_summary_V{version}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log.info(f"  Summary → {summary_path}")

    # Console summary table
    log.info(f"\n{'='*80}")
    log.info(f"{'Persona':<12} {'Name':<12} {'Stage':<18} {'Risk':<8} {'Flags':>5} "
             f"{'Base':>5} {'Kept':>5} {'Probes+':>7}")
    log.info("-" * 80)
    for r in results:
        log.info(f"{r['persona_id']:<12} {r['name']:<12} {r['stage']:<18} "
                 f"{r['risk']:<8} {r['flags']:>5} {r['base_qs']:>5} "
                 f"{r['adapted_qs']:>5} {r['added_probes']:>7}")
    log.info(f"{'='*80}")


if __name__ == "__main__":
    main()

"""
Persona-Patient Matcher — pairs FinePersonas with Synthea patients via compatibility scoring.
Usage:
    python -m src.personas.matcher --finepersonas data/finepersonas/maternity_personas.jsonl \
        --synthea data/synthea_ehr/parsed/synthea_pregnancy_patients.jsonl \
        --output data/composite_personas/matches.json --target 150
"""
import os, json, re, argparse, logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

CATEGORY_PRIORITY = ["DIRECT_MATERNITY", "MATERNITY_ADJACENT", "HEALTHCARE_CONTEXT", "SERVICE_CONTEXT"]

AGE_PATTERNS = [
    re.compile(r"\b(\d{1,2})\s*[-–]\s*year\s*[-–]?\s*old\b", re.I),
    re.compile(r"\bage\s*[:\s]?\s*(\d{1,2})\b", re.I),
    re.compile(r"\b(\d{1,2})\s*years?\s*old\b", re.I),
    re.compile(r"\baged?\s+(\d{1,2})\b", re.I),
]

HIGH_RISK_KW = ["high-risk", "high risk", "complication", "pre-eclampsia", "preeclampsia",
    "eclampsia", "gestational diabetes", "placenta", "premature", "preterm",
    "multiple pregnancy", "twins", "multiples", "ivf", "cervical", "hemorrhage", "hypertension"]
MEDIUM_RISK_KW = ["moderate risk", "over 35", "advanced maternal age", "previous c-section",
    "overweight", "obesity", "anemia", "anaemia"]
LOW_RISK_KW = ["normal pregnancy", "healthy pregnancy", "low-risk", "low risk", "routine", "uncomplicated"]

CONTEXT_TAGS = {
    "mental_health": ["mental health", "depression", "anxiety", "stress", "psychological",
        "psychiatric", "therapy", "counseling", "counselling", "postpartum depression"],
    "social_vulnerability": ["poverty", "low income", "low-income", "homeless", "vulnerable",
        "marginalized", "disadvantaged", "underserved"],
    "immigration": ["immigrant", "immigration", "refugee", "migrant", "asylum",
        "language barrier", "interpreter", "cultural"],
    "young_mother": ["teen", "adolescent", "young mother", "young parent", "underage"],
    "single_parent": ["single mother", "single parent", "single mom", "sole parent", "unmarried"],
    "substance_use": ["substance", "addiction", "drug use", "alcohol", "tobacco", "smoking"],
    "domestic_violence": ["domestic violence", "abuse", "intimate partner", "gender-based violence"],
    "rural": ["rural", "remote", "isolated community", "underserved area"],
    "disability": ["disability", "disabled", "special needs"],
    "multiple_pregnancy": ["twins", "triplets", "multiples", "multiple pregnancy"],
    "loss_history": ["miscarriage", "stillbirth", "pregnancy loss", "infant loss", "neonatal death"],
    "fertility": ["fertility", "ivf", "infertility", "assisted reproduction", "in vitro"],
    "chronic_condition": ["diabetes", "hypertension", "chronic", "autoimmune", "thyroid", "epilepsy"],
    "breastfeeding": ["breastfeeding", "lactation", "nursing mother", "breast milk"],
    "postpartum": ["postpartum", "postnatal", "after birth", "recovery"],
}


def extract_age_hint(text):
    for pat in AGE_PATTERNS:
        m = pat.search(text)
        if m:
            age = int(m.group(1))
            if 14 <= age <= 55:
                return age
    return None


def extract_risk_hint(text):
    tl = text.lower()
    if any(k in tl for k in HIGH_RISK_KW): return "high"
    if any(k in tl for k in MEDIUM_RISK_KW): return "medium"
    if any(k in tl for k in LOW_RISK_KW): return "low"
    return None


def extract_context_tags(text):
    tl = text.lower()
    return [tag for tag, kws in CONTEXT_TAGS.items() if any(k in tl for k in kws)]


def get_patient_age(patient):
    bd = patient.get("demographics", {}).get("birth_date", "")
    if bd:
        try:
            return (datetime.now() - datetime.strptime(bd, "%Y-%m-%d")).days // 365
        except Exception:
            pass
    return None


def get_patient_context_tags(patient):
    tags = set()
    meta = patient.get("pregnancy_metadata", {})
    if meta.get("has_miscarriage_history"):
        tags.add("loss_history")
    for cond in patient.get("pregnancy_conditions", []):
        cat = cond.get("snomed_category")
        if cat == "mental_health":
            tags.add("mental_health")
        if cat == "social":
            d = cond.get("display", "").lower()
            if "poverty" in d or "lack" in d:
                tags.add("social_vulnerability")
            if "english" in d:
                tags.add("immigration")
    demo = patient.get("demographics", {})
    if demo.get("marital_status") == "Never Married":
        tags.add("single_parent")
    if meta.get("pregnancy_count", 0) >= 3:
        tags.add("multiple_pregnancy")
    return list(tags)


def score_compatibility(persona, patient, age_hint, risk_hint, persona_tags, patient_tags):
    """Score compatibility 0–100 between a persona and a patient."""
    score = 0.0
    meta = patient.get("pregnancy_metadata", {})

    # Age alignment (0-25)
    patient_age = get_patient_age(patient)
    if age_hint and patient_age:
        diff = abs(age_hint - patient_age)
        if diff <= 2: score += 25
        elif diff <= 5: score += 20
        elif diff <= 10: score += 12
        elif diff <= 15: score += 5
    elif not age_hint:
        score += 10

    # Risk profile (0-25)
    pr = meta.get("risk_level", "unknown")
    if risk_hint:
        if risk_hint == pr:
            score += 25
        elif risk_hint in ("high", "medium") and pr in ("high", "medium", "critical"):
            score += 15
        else:
            score += 5
    else:
        score += 10

    # Pregnancy count (0-15)
    pc = meta.get("pregnancy_count", 0)
    ptl = persona.get("persona", "").lower()
    if "first" in ptl and "time" in ptl:
        score += 15 if pc <= 1 else 8 if pc == 2 else 3
    elif any(w in ptl for w in ("experienced", "multiple", "second")):
        score += 15 if pc >= 2 else 5
    else:
        score += 8

    # Miscarriage history (0-15)
    persona_loss = "loss_history" in persona_tags
    patient_loss = meta.get("has_miscarriage_history", False)
    if persona_loss and patient_loss: score += 15
    elif not persona_loss and not patient_loss: score += 12
    elif persona_loss and not patient_loss: score += 3
    else: score += 8

    # Context overlap (0-20)
    if persona_tags and patient_tags:
        overlap = len(set(persona_tags) & set(patient_tags))
        if overlap >= 3: score += 20
        elif overlap >= 2: score += 15
        elif overlap >= 1: score += 10
    elif not persona_tags:
        score += 8

    return min(round(score), 100)


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def greedy_match(personas, patients, target=150):
    cat_order = {c: i for i, c in enumerate(CATEGORY_PRIORITY)}
    sorted_personas = sorted(personas,
        key=lambda p: (cat_order.get(p.get("relevance_category", "SERVICE_CONTEXT"), 9),
                       -p.get("scores", {}).get("total_score", 0)))

    # Pre-compute hints
    hints_list = []
    for p in sorted_personas:
        text = p.get("persona", "")
        hints_list.append({
            "age_hint": extract_age_hint(text),
            "risk_hint": extract_risk_hint(text),
            "context_tags": extract_context_tags(text),
        })

    patient_tag_cache = {}
    for pt in patients:
        pid = pt.get("synthea_patient_id", "")
        patient_tag_cache[pid] = get_patient_context_tags(pt)

    matches = []
    patient_use_count = defaultdict(int)
    assigned_pids = set()

    log.info(f"Greedy matching: {len(sorted_personas)} personas × {len(patients)} patients → target {target}")

    for pi, (persona, hints) in enumerate(zip(sorted_personas, hints_list)):
        if len(matches) >= target:
            break
        best_score, best_patient = -1, None
        for pt in patients:
            pid = pt.get("synthea_patient_id", "")
            penalty = 15 * patient_use_count[pid]
            raw = score_compatibility(persona, pt, hints["age_hint"], hints["risk_hint"],
                                      hints["context_tags"], patient_tag_cache[pid])
            adj = max(0, raw - penalty)
            if adj > best_score:
                best_score = adj
                best_patient = pt
        if best_patient:
            bpid = best_patient.get("synthea_patient_id", "")
            patient_use_count[bpid] += 1
            assigned_pids.add(bpid)
            matches.append({
                "match_id": f"match_{len(matches)+1:04d}",
                "compatibility_score": best_score,
                "persona": persona,
                "patient": best_patient,
                "hints": hints,
            })
        if (pi + 1) % 50 == 0:
            log.info(f"  Processed {pi+1} personas, {len(matches)} matched so far")

    log.info(f"Matching complete: {len(matches)} matches using {len(assigned_pids)} unique patients")
    return matches


def export_matches(matches, output_path):
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cat_dist, risk_dist = defaultdict(int), defaultdict(int)
    total_score = 0
    for m in matches:
        total_score += m["compatibility_score"]
        cat_dist[m["persona"].get("relevance_category", "UNKNOWN")] += 1
        risk_dist[m["patient"].get("pregnancy_metadata", {}).get("risk_level", "unknown")] += 1

    export = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "total_matches": len(matches),
        "category_distribution": dict(cat_dist),
        "risk_distribution": dict(risk_dist),
        "avg_compatibility_score": round(total_score / max(len(matches), 1), 1),
        "matches": matches,
    }

    with open(out, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False, default=str)
    log.info(f"Exported {len(matches)} matches to {out}")

    log.info(f"\n{'='*60}")
    log.info("MATCHING SUMMARY")
    log.info(f"  Total matches: {len(matches)}")
    log.info(f"  Avg compatibility: {export['avg_compatibility_score']}")
    log.info(f"  By category: {dict(cat_dist)}")
    log.info(f"  By risk level: {dict(risk_dist)}")
    score_buckets = {"90-100": 0, "70-89": 0, "50-69": 0, "30-49": 0, "0-29": 0}
    for m in matches:
        s = m["compatibility_score"]
        if s >= 90: score_buckets["90-100"] += 1
        elif s >= 70: score_buckets["70-89"] += 1
        elif s >= 50: score_buckets["50-69"] += 1
        elif s >= 30: score_buckets["30-49"] += 1
        else: score_buckets["0-29"] += 1
    log.info(f"  Score distribution: {score_buckets}")
    log.info(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Persona-Patient Matcher")
    parser.add_argument("--finepersonas", type=str, required=True)
    parser.add_argument("--synthea", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--target", type=int, default=150)
    args = parser.parse_args()

    personas = load_jsonl(args.finepersonas)
    patients = load_jsonl(args.synthea)
    log.info(f"Loaded {len(personas)} personas, {len(patients)} patients")

    matches = greedy_match(personas, patients, target=args.target)
    export_matches(matches, args.output)


if __name__ == "__main__":
    main()

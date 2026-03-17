"""
Synthea EHR Parser
===================
Parses FHIR R4 bundles from Synthea, extracts pregnancy-related
clinical data, and produces structured JSON patient summaries
suitable for composite persona construction.

Usage:
    python -m src.ingestion.synthea_parser --input data/synthea_ehr/fhir/
    python -m src.ingestion.synthea_parser --input data/synthea_ehr/fhir/ --pregnancy-only
"""

import os
import json
import glob
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Import SNOMED registry
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.utils.snomed_pregnancy import (
    PREGNANCY_SNOMED_CODES, classify_patient_risk,
    get_journey_stage_from_codes, get_code
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
log = logging.getLogger(__name__)


def parse_fhir_bundle(filepath: str) -> dict:
    """Parse a single FHIR R4 patient bundle into a structured summary."""
    with open(filepath, "r", encoding="utf-8") as f:
        bundle = json.load(f)
    
    entries = bundle.get("entry", [])
    
    patient_info = {}
    conditions = []
    procedures = []
    encounters = []
    observations = []
    medications = []
    immunizations = []
    careplans = []
    
    pregnancy_conditions = []
    pregnancy_procedures = []
    pregnancy_encounters = []
    
    all_snomed_codes = []
    
    for entry in entries:
        resource = entry.get("resource", {})
        rtype = resource.get("resourceType", "")
        
        # ── Patient demographics ──────────────────────────────────────────
        if rtype == "Patient":
            patient_info = _extract_patient(resource)
        
        # ── Conditions ────────────────────────────────────────────────────
        elif rtype == "Condition":
            cond = _extract_condition(resource)
            if cond:
                conditions.append(cond)
                if cond.get("is_pregnancy_related"):
                    pregnancy_conditions.append(cond)
                    all_snomed_codes.append(cond["code"])
        
        # ── Procedures ────────────────────────────────────────────────────
        elif rtype == "Procedure":
            proc = _extract_procedure(resource)
            if proc:
                procedures.append(proc)
                if proc.get("is_pregnancy_related"):
                    pregnancy_procedures.append(proc)
                    all_snomed_codes.append(proc["code"])
        
        # ── Encounters ────────────────────────────────────────────────────
        elif rtype == "Encounter":
            enc = _extract_encounter(resource)
            if enc:
                encounters.append(enc)
                if enc.get("is_pregnancy_related"):
                    pregnancy_encounters.append(enc)
        
        # ── Observations ──────────────────────────────────────────────────
        elif rtype == "Observation":
            obs = _extract_observation(resource)
            if obs:
                observations.append(obs)
        
        # ── MedicationRequest ─────────────────────────────────────────────
        elif rtype == "MedicationRequest":
            med = _extract_medication(resource)
            if med:
                medications.append(med)
        
        # ── CarePlan ──────────────────────────────────────────────────────
        elif rtype == "CarePlan":
            cp = _extract_careplan(resource)
            if cp:
                careplans.append(cp)
    
    # ── Derive pregnancy metadata ─────────────────────────────────────────
    has_pregnancy = len(pregnancy_conditions) > 0 or len(pregnancy_procedures) > 0
    risk_level = classify_patient_risk(all_snomed_codes) if all_snomed_codes else "unknown"
    journey_stage = get_journey_stage_from_codes(all_snomed_codes) if all_snomed_codes else "unknown"
    
    # Count pregnancies (each "Normal pregnancy" onset is roughly one pregnancy)
    pregnancy_count = sum(
        1 for c in pregnancy_conditions
        if c["code"] in ("72892002", "77386006")
    )
    
    # Check for complications
    complications = [
        c for c in pregnancy_conditions
        if c["code"] not in ("72892002", "77386006", "161744009", "161763005")
    ]
    
    # Check for miscarriage history
    has_miscarriage_history = any(
        c["code"] in ("271903000", "17369002", "161744009")
        or "miscarriage" in c.get("display", "").lower()
        for c in pregnancy_conditions
    )
    
    return {
        "synthea_patient_id": patient_info.get("id", "unknown"),
        "source_file": os.path.basename(filepath),
        "demographics": patient_info,
        "has_pregnancy": has_pregnancy,
        "pregnancy_metadata": {
            "pregnancy_count": pregnancy_count,
            "risk_level": risk_level,
            "journey_stage": journey_stage,
            "has_miscarriage_history": has_miscarriage_history,
            "complications": [
                {"code": c["code"], "display": c["display"]}
                for c in complications
            ],
            "pregnancy_snomed_codes": list(set(all_snomed_codes)),
        },
        "pregnancy_conditions": pregnancy_conditions,
        "pregnancy_procedures": pregnancy_procedures,
        "pregnancy_encounters": pregnancy_encounters,
        "all_conditions_count": len(conditions),
        "all_procedures_count": len(procedures),
        "all_encounters_count": len(encounters),
        "all_observations_count": len(observations),
        "all_medications_count": len(medications),
        "conditions_summary": conditions[:50],  # Cap for file size
        "medications_summary": medications[:30],
        "careplans_summary": careplans[:10],
    }


def _extract_patient(resource: dict) -> dict:
    """Extract patient demographics from a Patient resource."""
    name_parts = resource.get("name", [{}])[0]
    given = " ".join(name_parts.get("given", []))
    family = name_parts.get("family", "")
    
    address = resource.get("address", [{}])[0] if resource.get("address") else {}
    
    # Extract race and ethnicity from extensions
    race = ""
    ethnicity = ""
    for ext in resource.get("extension", []):
        url = ext.get("url", "")
        if "us-core-race" in url:
            for inner in ext.get("extension", []):
                if inner.get("url") == "text":
                    race = inner.get("valueString", "")
        elif "us-core-ethnicity" in url:
            for inner in ext.get("extension", []):
                if inner.get("url") == "text":
                    ethnicity = inner.get("valueString", "")
    
    return {
        "id": resource.get("id", ""),
        "name": f"{given} {family}".strip(),
        "given_name": given,
        "family_name": family,
        "gender": resource.get("gender", ""),
        "birth_date": resource.get("birthDate", ""),
        "race": race,
        "ethnicity": ethnicity,
        "marital_status": resource.get("maritalStatus", {}).get("text", ""),
        "city": address.get("city", ""),
        "state": address.get("state", ""),
        "country": address.get("country", "US"),
    }


def _extract_condition(resource: dict) -> dict | None:
    """Extract condition information."""
    coding = resource.get("code", {}).get("coding", [{}])[0]
    code = str(coding.get("code", ""))
    display = coding.get("display", "")
    system = coding.get("system", "")
    
    if not code:
        return None
    
    # Check if pregnancy-related (SNOMED registry or keyword match)
    is_preg = (
        code in PREGNANCY_SNOMED_CODES
        or any(kw in display.lower() for kw in [
            "pregnan", "matern", "obstetric", "prenatal", "antenatal",
            "postpartum", "gestation", "eclampsia", "miscarriage",
            "trimester", "childbirth", "labour", "labor", "delivery",
            "cesarean", "caesarean", "neonatal", "perinatal",
        ])
    )
    
    snomed_info = get_code(code)
    
    return {
        "code": code,
        "display": display,
        "system": system,
        "onset": resource.get("onsetDateTime", ""),
        "abatement": resource.get("abatementDateTime", ""),
        "clinical_status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", ""),
        "is_pregnancy_related": is_preg,
        "snomed_category": snomed_info["category"] if snomed_info else None,
        "snomed_severity": snomed_info["severity"] if snomed_info else None,
        "snomed_stage": snomed_info["stage"] if snomed_info else None,
    }


def _extract_procedure(resource: dict) -> dict | None:
    """Extract procedure information."""
    coding = resource.get("code", {}).get("coding", [{}])[0]
    code = str(coding.get("code", ""))
    display = coding.get("display", "")
    
    if not code:
        return None
    
    is_preg = (
        code in PREGNANCY_SNOMED_CODES
        or any(kw in display.lower() for kw in [
            "pregnan", "obstetric", "cesarean", "caesarean", "epidural",
            "episiotomy", "induction", "delivery", "birth", "labor",
            "labour", "forceps", "vacuum", "antenatal", "prenatal",
            "ultrasound", "amniocentesis",
        ])
    )
    
    return {
        "code": code,
        "display": display,
        "performed": resource.get("performedDateTime",
                                   resource.get("performedPeriod", {}).get("start", "")),
        "is_pregnancy_related": is_preg,
    }


def _extract_encounter(resource: dict) -> dict | None:
    """Extract encounter information."""
    coding = resource.get("type", [{}])[0].get("coding", [{}])[0] if resource.get("type") else {}
    code = str(coding.get("code", ""))
    display = coding.get("display", "")
    
    enc_class = resource.get("class", {})
    if isinstance(enc_class, dict):
        enc_class_code = enc_class.get("code", "")
    else:
        enc_class_code = ""
    
    is_preg = (
        code in PREGNANCY_SNOMED_CODES
        or any(kw in display.lower() for kw in [
            "pregnan", "obstetric", "prenatal", "antenatal", "postnatal",
            "maternity", "delivery", "birth",
        ])
    )
    
    period = resource.get("period", {})
    
    return {
        "code": code,
        "display": display,
        "class": enc_class_code,
        "start": period.get("start", ""),
        "end": period.get("end", ""),
        "is_pregnancy_related": is_preg,
    }


def _extract_observation(resource: dict) -> dict | None:
    """Extract observation (brief summary)."""
    coding = resource.get("code", {}).get("coding", [{}])[0]
    return {
        "code": str(coding.get("code", "")),
        "display": coding.get("display", ""),
        "value": _get_observation_value(resource),
        "date": resource.get("effectiveDateTime", ""),
    }


def _get_observation_value(resource: dict):
    """Extract observation value regardless of data type."""
    if "valueQuantity" in resource:
        vq = resource["valueQuantity"]
        return f"{vq.get('value', '')} {vq.get('unit', '')}"
    elif "valueCodeableConcept" in resource:
        return resource["valueCodeableConcept"].get("text",
               resource["valueCodeableConcept"].get("coding", [{}])[0].get("display", ""))
    elif "valueString" in resource:
        return resource["valueString"]
    elif "valueBoolean" in resource:
        return str(resource["valueBoolean"])
    elif "component" in resource:
        parts = []
        for comp in resource["component"]:
            name = comp.get("code", {}).get("coding", [{}])[0].get("display", "?")
            val = _get_observation_value(comp)
            parts.append(f"{name}: {val}")
        return "; ".join(parts)
    return ""


def _extract_medication(resource: dict) -> dict | None:
    """Extract medication request."""
    med = resource.get("medicationCodeableConcept", {})
    coding = med.get("coding", [{}])[0]
    return {
        "code": str(coding.get("code", "")),
        "display": coding.get("display", ""),
        "status": resource.get("status", ""),
        "authored_on": resource.get("authoredOn", ""),
    }


def _extract_careplan(resource: dict) -> dict | None:
    """Extract care plan."""
    cats = resource.get("category", [{}])
    cat_display = cats[0].get("coding", [{}])[0].get("display", "") if cats else ""
    return {
        "category": cat_display,
        "status": resource.get("status", ""),
        "period_start": resource.get("period", {}).get("start", ""),
    }


def parse_all_patients(input_dir: str, pregnancy_only: bool = False) -> list:
    """Parse all FHIR bundles in a directory."""
    fhir_files = sorted(glob.glob(os.path.join(input_dir, "*.json")))
    
    # Exclude hospital and practitioner files
    fhir_files = [
        f for f in fhir_files
        if "hospital" not in os.path.basename(f).lower()
        and "practitioner" not in os.path.basename(f).lower()
    ]
    
    log.info(f"Found {len(fhir_files)} patient FHIR bundles in {input_dir}")
    
    patients = []
    pregnancy_patients = 0
    
    for i, filepath in enumerate(fhir_files):
        try:
            summary = parse_fhir_bundle(filepath)
            
            if pregnancy_only and not summary["has_pregnancy"]:
                continue
            
            patients.append(summary)
            if summary["has_pregnancy"]:
                pregnancy_patients += 1
            
            if (i + 1) % 50 == 0:
                log.info(f"  Parsed {i+1}/{len(fhir_files)} "
                         f"(pregnancy: {pregnancy_patients})")
                         
        except Exception as e:
            log.error(f"  Error parsing {filepath}: {e}")
    
    log.info(f"\nParsing complete:")
    log.info(f"  Total parsed:      {len(patients)}")
    log.info(f"  With pregnancy:    {pregnancy_patients}")
    
    if pregnancy_patients > 0:
        # Risk level distribution
        risk_dist = {}
        for p in patients:
            if p["has_pregnancy"]:
                rl = p["pregnancy_metadata"]["risk_level"]
                risk_dist[rl] = risk_dist.get(rl, 0) + 1
        log.info(f"  Risk distribution: {risk_dist}")
        
        # Complication frequency
        comp_freq = {}
        for p in patients:
            for c in p["pregnancy_metadata"]["complications"]:
                comp_freq[c["display"]] = comp_freq.get(c["display"], 0) + 1
        if comp_freq:
            log.info(f"  Top complications:")
            for comp, count in sorted(comp_freq.items(), key=lambda x: -x[1])[:10]:
                log.info(f"    {comp}: {count}")
    
    return patients


def export_patients(patients: list, output_dir: str):
    """Export parsed patient summaries."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export all as JSONL
    jsonl_path = out / f"synthea_patients_{timestamp}.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for p in patients:
            f.write(json.dumps(p, ensure_ascii=False, default=str) + "\n")
    log.info(f"Exported {len(patients)} patients to {jsonl_path}")
    
    # Stable reference
    stable_path = out / "synthea_patients.jsonl"
    with open(stable_path, "w", encoding="utf-8") as f:
        for p in patients:
            f.write(json.dumps(p, ensure_ascii=False, default=str) + "\n")
    
    # Pregnancy-only subset
    preg_patients = [p for p in patients if p["has_pregnancy"]]
    preg_path = out / "synthea_pregnancy_patients.jsonl"
    with open(preg_path, "w", encoding="utf-8") as f:
        for p in preg_patients:
            f.write(json.dumps(p, ensure_ascii=False, default=str) + "\n")
    log.info(f"Pregnancy subset: {len(preg_patients)} patients to {preg_path}")
    
    # Summary stats
    summary = {
        "timestamp": timestamp,
        "total_patients": len(patients),
        "pregnancy_patients": len(preg_patients),
        "risk_distribution": {},
        "complication_frequency": {},
        "pregnancy_count_distribution": {},
    }
    
    for p in preg_patients:
        meta = p["pregnancy_metadata"]
        rl = meta["risk_level"]
        summary["risk_distribution"][rl] = summary["risk_distribution"].get(rl, 0) + 1
        
        pc = str(meta["pregnancy_count"])
        summary["pregnancy_count_distribution"][pc] = \
            summary["pregnancy_count_distribution"].get(pc, 0) + 1
        
        for c in meta["complications"]:
            d = c["display"]
            summary["complication_frequency"][d] = \
                summary["complication_frequency"].get(d, 0) + 1
    
    summary_path = out / f"synthea_summary_{timestamp}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    log.info(f"Summary: {summary_path}")
    return preg_patients


def main():
    parser = argparse.ArgumentParser(description="Synthea FHIR Parser")
    parser.add_argument("--input", type=str,
                        default="data/synthea_ehr/fhir/",
                        help="Directory containing FHIR JSON bundles")
    parser.add_argument("--output", type=str,
                        default="data/synthea_ehr/parsed/",
                        help="Output directory for parsed summaries")
    parser.add_argument("--pregnancy-only", action="store_true",
                        help="Only export patients with pregnancy records")
    
    args = parser.parse_args()
    
    patients = parse_all_patients(args.input, pregnancy_only=args.pregnancy_only)
    export_patients(patients, args.output)


if __name__ == "__main__":
    main()

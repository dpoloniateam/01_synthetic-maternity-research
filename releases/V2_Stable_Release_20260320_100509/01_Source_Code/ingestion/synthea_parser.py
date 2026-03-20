"""
Synthea EHR Parser - Parses FHIR R4 bundles, extracts pregnancy-related data.
"""
import os, json, glob, argparse, logging, sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.snomed_pregnancy import PREGNANCY_SNOMED_CODES, classify_patient_risk, get_journey_stage_from_codes, get_code

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

PREG_KEYWORDS = ["pregnan", "matern", "obstetric", "prenatal", "antenatal", "postpartum", "gestation", "eclampsia", "miscarriage", "trimester", "childbirth", "labour", "labor", "delivery", "cesarean", "caesarean", "neonatal", "perinatal"]
PROC_KEYWORDS = ["pregnan", "obstetric", "cesarean", "caesarean", "epidural", "episiotomy", "induction", "delivery", "birth", "labor", "labour", "forceps", "vacuum", "antenatal", "prenatal", "ultrasound", "amniocentesis"]

def _extract_patient(r):
    n = r.get("name", [{}])[0]
    given = " ".join(n.get("given", []))
    family = n.get("family", "")
    addr = r.get("address", [{}])[0] if r.get("address") else {}
    race, ethnicity = "", ""
    for ext in r.get("extension", []):
        url = ext.get("url", "")
        if "us-core-race" in url:
            for inner in ext.get("extension", []):
                if inner.get("url") == "text": race = inner.get("valueString", "")
        elif "us-core-ethnicity" in url:
            for inner in ext.get("extension", []):
                if inner.get("url") == "text": ethnicity = inner.get("valueString", "")
    return {"id": r.get("id",""), "name": f"{given} {family}".strip(), "given_name": given, "family_name": family, "gender": r.get("gender",""), "birth_date": r.get("birthDate",""), "race": race, "ethnicity": ethnicity, "marital_status": r.get("maritalStatus",{}).get("text",""), "city": addr.get("city",""), "state": addr.get("state",""), "country": addr.get("country","US")}

def _extract_condition(r):
    coding = r.get("code",{}).get("coding",[{}])[0]
    code, display = str(coding.get("code","")), coding.get("display","")
    if not code: return None
    is_preg = code in PREGNANCY_SNOMED_CODES or any(kw in display.lower() for kw in PREG_KEYWORDS)
    si = get_code(code)
    return {"code": code, "display": display, "system": coding.get("system",""), "onset": r.get("onsetDateTime",""), "abatement": r.get("abatementDateTime",""), "clinical_status": r.get("clinicalStatus",{}).get("coding",[{}])[0].get("code",""), "is_pregnancy_related": is_preg, "snomed_category": si["category"] if si else None, "snomed_severity": si["severity"] if si else None, "snomed_stage": si["stage"] if si else None}

def _extract_procedure(r):
    coding = r.get("code",{}).get("coding",[{}])[0]
    code, display = str(coding.get("code","")), coding.get("display","")
    if not code: return None
    is_preg = code in PREGNANCY_SNOMED_CODES or any(kw in display.lower() for kw in PROC_KEYWORDS)
    return {"code": code, "display": display, "performed": r.get("performedDateTime", r.get("performedPeriod",{}).get("start","")), "is_pregnancy_related": is_preg}

def _extract_encounter(r):
    coding = r.get("type",[{}])[0].get("coding",[{}])[0] if r.get("type") else {}
    code, display = str(coding.get("code","")), coding.get("display","")
    ec = r.get("class",{})
    ec_code = ec.get("code","") if isinstance(ec, dict) else ""
    is_preg = code in PREGNANCY_SNOMED_CODES or any(kw in display.lower() for kw in ["pregnan","obstetric","prenatal","antenatal","postnatal","maternity","delivery","birth"])
    period = r.get("period",{})
    return {"code": code, "display": display, "class": ec_code, "start": period.get("start",""), "end": period.get("end",""), "is_pregnancy_related": is_preg}

def _get_obs_value(r):
    if "valueQuantity" in r:
        vq = r["valueQuantity"]; return f"{vq.get('value','')} {vq.get('unit','')}"
    elif "valueCodeableConcept" in r:
        return r["valueCodeableConcept"].get("text", r["valueCodeableConcept"].get("coding",[{}])[0].get("display",""))
    elif "valueString" in r: return r["valueString"]
    elif "valueBoolean" in r: return str(r["valueBoolean"])
    elif "component" in r:
        return "; ".join(f"{c.get('code',{}).get('coding',[{}])[0].get('display','?')}: {_get_obs_value(c)}" for c in r["component"])
    return ""

def _extract_observation(r):
    coding = r.get("code",{}).get("coding",[{}])[0]
    return {"code": str(coding.get("code","")), "display": coding.get("display",""), "value": _get_obs_value(r), "date": r.get("effectiveDateTime","")}

def _extract_medication(r):
    coding = r.get("medicationCodeableConcept",{}).get("coding",[{}])[0]
    return {"code": str(coding.get("code","")), "display": coding.get("display",""), "status": r.get("status",""), "authored_on": r.get("authoredOn","")}

def _extract_careplan(r):
    cats = r.get("category",[{}])
    cd = cats[0].get("coding",[{}])[0].get("display","") if cats else ""
    return {"category": cd, "status": r.get("status",""), "period_start": r.get("period",{}).get("start","")}

def parse_fhir_bundle(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        bundle = json.load(f)
    patient_info, conditions, procedures, encounters, observations, medications, careplans = {}, [], [], [], [], [], []
    pregnancy_conditions, pregnancy_procedures, pregnancy_encounters = [], [], []
    all_snomed_codes = []
    for entry in bundle.get("entry", []):
        res = entry.get("resource", {})
        rt = res.get("resourceType", "")
        if rt == "Patient": patient_info = _extract_patient(res)
        elif rt == "Condition":
            c = _extract_condition(res)
            if c:
                conditions.append(c)
                if c.get("is_pregnancy_related"): pregnancy_conditions.append(c); all_snomed_codes.append(c["code"])
        elif rt == "Procedure":
            p = _extract_procedure(res)
            if p:
                procedures.append(p)
                if p.get("is_pregnancy_related"): pregnancy_procedures.append(p); all_snomed_codes.append(p["code"])
        elif rt == "Encounter":
            e = _extract_encounter(res)
            if e:
                encounters.append(e)
                if e.get("is_pregnancy_related"): pregnancy_encounters.append(e)
        elif rt == "Observation":
            o = _extract_observation(res)
            if o: observations.append(o)
        elif rt == "MedicationRequest":
            m = _extract_medication(res)
            if m: medications.append(m)
        elif rt == "CarePlan":
            cp = _extract_careplan(res)
            if cp: careplans.append(cp)
    has_pregnancy = len(pregnancy_conditions) > 0 or len(pregnancy_procedures) > 0
    risk_level = classify_patient_risk(all_snomed_codes) if all_snomed_codes else "unknown"
    journey_stage = get_journey_stage_from_codes(all_snomed_codes) if all_snomed_codes else "unknown"
    pregnancy_count = sum(1 for c in pregnancy_conditions if c["code"] in ("72892002","77386006"))
    complications = [c for c in pregnancy_conditions if c["code"] not in ("72892002","77386006","161744009","161763005")]
    has_miscarriage = any(c["code"] in ("271903000","17369002","161744009") or "miscarriage" in c.get("display","").lower() for c in pregnancy_conditions)
    return {
        "synthea_patient_id": patient_info.get("id","unknown"), "source_file": os.path.basename(filepath),
        "demographics": patient_info, "has_pregnancy": has_pregnancy,
        "pregnancy_metadata": {"pregnancy_count": pregnancy_count, "risk_level": risk_level, "journey_stage": journey_stage, "has_miscarriage_history": has_miscarriage, "complications": [{"code":c["code"],"display":c["display"]} for c in complications], "pregnancy_snomed_codes": list(set(all_snomed_codes))},
        "pregnancy_conditions": pregnancy_conditions, "pregnancy_procedures": pregnancy_procedures, "pregnancy_encounters": pregnancy_encounters,
        "all_conditions_count": len(conditions), "all_procedures_count": len(procedures), "all_encounters_count": len(encounters),
        "all_observations_count": len(observations), "all_medications_count": len(medications),
        "conditions_summary": conditions[:50], "medications_summary": medications[:30], "careplans_summary": careplans[:10],
    }

def parse_all_patients(input_dir, pregnancy_only=False):
    fhir_files = sorted(glob.glob(os.path.join(input_dir, "*.json")))
    fhir_files = [f for f in fhir_files if "hospital" not in os.path.basename(f).lower() and "practitioner" not in os.path.basename(f).lower()]
    log.info(f"Found {len(fhir_files)} patient FHIR bundles in {input_dir}")
    patients, preg_count = [], 0
    for i, fp in enumerate(fhir_files):
        try:
            s = parse_fhir_bundle(fp)
            if pregnancy_only and not s["has_pregnancy"]: continue
            patients.append(s)
            if s["has_pregnancy"]: preg_count += 1
            if (i+1) % 50 == 0: log.info(f"  Parsed {i+1}/{len(fhir_files)} (pregnancy: {preg_count})")
        except Exception as e:
            log.error(f"  Error parsing {fp}: {e}")
    log.info(f"\nParsing complete: Total={len(patients)}, Pregnancy={preg_count}")
    if preg_count > 0:
        rd = {}
        for p in patients:
            if p["has_pregnancy"]: rl = p["pregnancy_metadata"]["risk_level"]; rd[rl] = rd.get(rl,0)+1
        log.info(f"  Risk distribution: {rd}")
        cf = {}
        for p in patients:
            for c in p["pregnancy_metadata"]["complications"]: cf[c["display"]] = cf.get(c["display"],0)+1
        if cf:
            log.info(f"  Top complications:")
            for comp, count in sorted(cf.items(), key=lambda x:-x[1])[:10]: log.info(f"    {comp}: {count}")
    return patients

def export_patients(patients, output_dir):
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stable = out / "synthea_patients.jsonl"
    with open(stable,"w",encoding="utf-8") as f:
        for p in patients: f.write(json.dumps(p, ensure_ascii=False, default=str)+"\n")
    preg = [p for p in patients if p["has_pregnancy"]]
    pp = out / "synthea_pregnancy_patients.jsonl"
    with open(pp,"w",encoding="utf-8") as f:
        for p in preg: f.write(json.dumps(p, ensure_ascii=False, default=str)+"\n")
    log.info(f"Exported {len(patients)} total, {len(preg)} pregnancy to {out}")
    summary = {"timestamp": ts, "total_patients": len(patients), "pregnancy_patients": len(preg), "risk_distribution": {}, "complication_frequency": {}, "pregnancy_count_distribution": {}}
    for p in preg:
        m = p["pregnancy_metadata"]
        summary["risk_distribution"][m["risk_level"]] = summary["risk_distribution"].get(m["risk_level"],0)+1
        pc = str(m["pregnancy_count"]); summary["pregnancy_count_distribution"][pc] = summary["pregnancy_count_distribution"].get(pc,0)+1
        for c in m["complications"]: summary["complication_frequency"][c["display"]] = summary["complication_frequency"].get(c["display"],0)+1
    sp = out / f"synthea_summary_{ts}.json"
    with open(sp,"w",encoding="utf-8") as f: json.dump(summary, f, indent=2, ensure_ascii=False)
    log.info(f"Summary: {sp}")
    return preg

def main():
    parser = argparse.ArgumentParser(description="Synthea FHIR Parser")
    parser.add_argument("--input", type=str, default="data/synthea_ehr/fhir/")
    parser.add_argument("--output", type=str, default="data/synthea_ehr/parsed/")
    parser.add_argument("--pregnancy-only", action="store_true")
    args = parser.parse_args()
    patients = parse_all_patients(args.input, pregnancy_only=args.pregnancy_only)
    export_patients(patients, args.output)

if __name__ == "__main__":
    main()

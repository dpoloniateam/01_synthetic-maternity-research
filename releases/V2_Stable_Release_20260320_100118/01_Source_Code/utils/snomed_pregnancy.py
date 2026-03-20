"""
SNOMED-CT Pregnancy Code Registry
"""
PRECONCEPTION = "preconception"
PREGNANCY     = "pregnancy"
FIRST_TRI     = "first_trimester"
SECOND_TRI    = "second_trimester"
THIRD_TRI     = "third_trimester"
BIRTH         = "birth"
POSTPARTUM    = "postpartum"
ANY_STAGE     = "any_stage"

CAT_CONDITION   = "condition"
CAT_PROCEDURE   = "procedure"
CAT_ENCOUNTER   = "encounter"
CAT_OBSERVATION = "observation"
CAT_MEDICATION  = "medication"
CAT_SOCIAL      = "social"
CAT_MENTAL      = "mental_health"
CAT_HISTORY     = "history"

SEV_NORMAL  = "normal"
SEV_MILD    = "mild"
SEV_MODERATE = "moderate"
SEV_SEVERE  = "severe"
SEV_CRITICAL = "critical"
SEV_NA      = "not_applicable"

PREGNANCY_SNOMED_CODES = {
    "77386006": {"display": "Patient currently pregnant", "category": CAT_CONDITION, "severity": SEV_NORMAL, "stage": PREGNANCY},
    "72892002": {"display": "Normal pregnancy", "category": CAT_CONDITION, "severity": SEV_NORMAL, "stage": PREGNANCY},
    "16356006": {"display": "Multiple pregnancy", "category": CAT_CONDITION, "severity": SEV_MODERATE, "stage": PREGNANCY},
    "47200007": {"display": "High-risk pregnancy", "category": CAT_CONDITION, "severity": SEV_SEVERE, "stage": PREGNANCY},
    "199006004": {"display": "Pre-existing condition complicating pregnancy", "category": CAT_CONDITION, "severity": SEV_MODERATE, "stage": PREGNANCY},
    "398254007": {"display": "Pre-eclampsia", "category": CAT_CONDITION, "severity": SEV_SEVERE, "stage": THIRD_TRI},
    "69217004": {"display": "Eclampsia", "category": CAT_CONDITION, "severity": SEV_CRITICAL, "stage": THIRD_TRI},
    "11687002": {"display": "Gestational diabetes mellitus", "category": CAT_CONDITION, "severity": SEV_MODERATE, "stage": SECOND_TRI},
    "36813001": {"display": "Placenta praevia", "category": CAT_CONDITION, "severity": SEV_SEVERE, "stage": THIRD_TRI},
    "17382005": {"display": "Cervical incompetence", "category": CAT_CONDITION, "severity": SEV_SEVERE, "stage": SECOND_TRI},
    "267038008": {"display": "Oedema and/or proteinuria in pregnancy", "category": CAT_CONDITION, "severity": SEV_MODERATE, "stage": PREGNANCY},
    "237240001": {"display": "Pregnancy complicated by condition", "category": CAT_CONDITION, "severity": SEV_MODERATE, "stage": PREGNANCY},
    "15938005": {"display": "Hyperemesis gravidarum", "category": CAT_CONDITION, "severity": SEV_MODERATE, "stage": FIRST_TRI},
    "28860009": {"display": "Ectopic pregnancy", "category": CAT_CONDITION, "severity": SEV_CRITICAL, "stage": FIRST_TRI},
    "87605005": {"display": "Hydatidiform mole", "category": CAT_CONDITION, "severity": SEV_SEVERE, "stage": FIRST_TRI},
    "609496007": {"display": "Pregnancy-related complication", "category": CAT_CONDITION, "severity": SEV_MODERATE, "stage": PREGNANCY},
    "82661006": {"display": "Premature labor", "category": CAT_CONDITION, "severity": SEV_SEVERE, "stage": THIRD_TRI},
    "199246003": {"display": "Anaemia complicating pregnancy", "category": CAT_CONDITION, "severity": SEV_MODERATE, "stage": PREGNANCY},
    "39621005": {"display": "Gestational hypertension", "category": CAT_CONDITION, "severity": SEV_MODERATE, "stage": PREGNANCY},
    "44223004": {"display": "Premature rupture of membranes", "category": CAT_CONDITION, "severity": SEV_SEVERE, "stage": THIRD_TRI},
    "271903000": {"display": "Miscarriage", "category": CAT_CONDITION, "severity": SEV_SEVERE, "stage": FIRST_TRI},
    "17369002": {"display": "Spontaneous abortion (miscarriage)", "category": CAT_CONDITION, "severity": SEV_SEVERE, "stage": FIRST_TRI},
    "237364002": {"display": "Stillbirth", "category": CAT_CONDITION, "severity": SEV_CRITICAL, "stage": BIRTH},
    "161763005": {"display": "History of ectopic pregnancy", "category": CAT_HISTORY, "severity": SEV_NA, "stage": PRECONCEPTION},
    "161744009": {"display": "History of miscarriage", "category": CAT_HISTORY, "severity": SEV_NA, "stage": PRECONCEPTION},
    "58703003": {"display": "Postpartum depression", "category": CAT_MENTAL, "severity": SEV_SEVERE, "stage": POSTPARTUM},
    "197480006": {"display": "Anxiety disorder in pregnancy", "category": CAT_MENTAL, "severity": SEV_MODERATE, "stage": PREGNANCY},
    "386639001": {"display": "Tokophobia (fear of childbirth)", "category": CAT_MENTAL, "severity": SEV_MODERATE, "stage": PREGNANCY},
    "200261002": {"display": "Perinatal mental health disorder", "category": CAT_MENTAL, "severity": SEV_MODERATE, "stage": ANY_STAGE},
    "66348005": {"display": "Childbirth (normal delivery)", "category": CAT_PROCEDURE, "severity": SEV_NORMAL, "stage": BIRTH},
    "11466000": {"display": "Caesarean section", "category": CAT_PROCEDURE, "severity": SEV_MODERATE, "stage": BIRTH},
    "18946005": {"display": "Epidural anaesthesia", "category": CAT_PROCEDURE, "severity": SEV_NORMAL, "stage": BIRTH},
    "237001001": {"display": "Augmentation of labour", "category": CAT_PROCEDURE, "severity": SEV_MILD, "stage": BIRTH},
    "176613002": {"display": "Episiotomy", "category": CAT_PROCEDURE, "severity": SEV_MILD, "stage": BIRTH},
    "61586001": {"display": "Assisted delivery by forceps", "category": CAT_PROCEDURE, "severity": SEV_MODERATE, "stage": BIRTH},
    "89346004": {"display": "Assisted delivery by vacuum extraction", "category": CAT_PROCEDURE, "severity": SEV_MODERATE, "stage": BIRTH},
    "236958009": {"display": "Induction of labour", "category": CAT_PROCEDURE, "severity": SEV_MILD, "stage": BIRTH},
    "177184002": {"display": "Emergency caesarean section", "category": CAT_PROCEDURE, "severity": SEV_SEVERE, "stage": BIRTH},
    "177141003": {"display": "Elective caesarean section", "category": CAT_PROCEDURE, "severity": SEV_MODERATE, "stage": BIRTH},
    "274130007": {"display": "Emergency care in labour", "category": CAT_PROCEDURE, "severity": SEV_SEVERE, "stage": BIRTH},
    "169826009": {"display": "Antenatal screening", "category": CAT_ENCOUNTER, "severity": SEV_NORMAL, "stage": PREGNANCY},
    "386216000": {"display": "Obstetric review", "category": CAT_ENCOUNTER, "severity": SEV_NORMAL, "stage": PREGNANCY},
    "183460006": {"display": "Obstetric emergency hospital admission", "category": CAT_ENCOUNTER, "severity": SEV_SEVERE, "stage": ANY_STAGE},
    "169230002": {"display": "Postnatal visit", "category": CAT_ENCOUNTER, "severity": SEV_NORMAL, "stage": POSTPARTUM},
    "169228000": {"display": "Antenatal visit", "category": CAT_ENCOUNTER, "severity": SEV_NORMAL, "stage": PREGNANCY},
    "386637004": {"display": "Obstetric ultrasound", "category": CAT_PROCEDURE, "severity": SEV_NORMAL, "stage": PREGNANCY},
    "268556000": {"display": "Nuchal translucency scan", "category": CAT_PROCEDURE, "severity": SEV_NORMAL, "stage": FIRST_TRI},
    "134435003": {"display": "Glucose tolerance test in pregnancy", "category": CAT_PROCEDURE, "severity": SEV_NORMAL, "stage": SECOND_TRI},
    "364599001": {"display": "Pregnancy-related observation", "category": CAT_OBSERVATION, "severity": SEV_NA, "stage": PREGNANCY},
    "289571006": {"display": "Fundal height measurement", "category": CAT_OBSERVATION, "severity": SEV_NORMAL, "stage": PREGNANCY},
    "249014000": {"display": "Fetal heart sounds present", "category": CAT_OBSERVATION, "severity": SEV_NORMAL, "stage": PREGNANCY},
    "276473004": {"display": "Fetal presentation", "category": CAT_OBSERVATION, "severity": SEV_NA, "stage": THIRD_TRI},
    "160903007": {"display": "Poverty (finding)", "category": CAT_SOCIAL, "severity": SEV_NA, "stage": ANY_STAGE},
    "105480006": {"display": "Refusal of treatment by patient", "category": CAT_SOCIAL, "severity": SEV_NA, "stage": ANY_STAGE},
    "713458007": {"display": "Lack of social support", "category": CAT_SOCIAL, "severity": SEV_MODERATE, "stage": ANY_STAGE},
    "160339004": {"display": "Lifestyle risk factor", "category": CAT_SOCIAL, "severity": SEV_NA, "stage": ANY_STAGE},
    "266897007": {"display": "Tobacco use", "category": CAT_SOCIAL, "severity": SEV_MODERATE, "stage": ANY_STAGE},
    "228281002": {"display": "Does not speak English", "category": CAT_SOCIAL, "severity": SEV_NA, "stage": ANY_STAGE},
}

def get_code(code):
    return PREGNANCY_SNOMED_CODES.get(str(code))

def get_codes_by_stage(stage):
    return {c: i for c, i in PREGNANCY_SNOMED_CODES.items() if i["stage"] == stage or i["stage"] == ANY_STAGE}

def get_codes_by_category(category):
    return {c: i for c, i in PREGNANCY_SNOMED_CODES.items() if i["category"] == category}

def get_complication_codes():
    return {c: i for c, i in PREGNANCY_SNOMED_CODES.items() if i["severity"] in (SEV_MODERATE, SEV_SEVERE, SEV_CRITICAL) and i["category"] == CAT_CONDITION}

def classify_patient_risk(snomed_codes):
    severities = []
    for code in snomed_codes:
        info = get_code(code)
        if info:
            severities.append(info["severity"])
    if SEV_CRITICAL in severities:
        return "critical"
    elif SEV_SEVERE in severities:
        return "high"
    elif SEV_MODERATE in severities:
        return "medium"
    else:
        return "low"

def get_journey_stage_from_codes(snomed_codes):
    stage_order = [PRECONCEPTION, FIRST_TRI, SECOND_TRI, THIRD_TRI, PREGNANCY, BIRTH, POSTPARTUM]
    max_idx = -1
    for code in snomed_codes:
        info = get_code(code)
        if info and info["stage"] in stage_order:
            idx = stage_order.index(info["stage"])
            if idx > max_idx:
                max_idx = idx
    return stage_order[max_idx] if max_idx >= 0 else "unknown"

def summary_stats():
    total = len(PREGNANCY_SNOMED_CODES)
    by_cat, by_stage, by_sev = {}, {}, {}
    for code, info in PREGNANCY_SNOMED_CODES.items():
        by_cat[info["category"]] = by_cat.get(info["category"], 0) + 1
        by_stage[info["stage"]] = by_stage.get(info["stage"], 0) + 1
        by_sev[info["severity"]] = by_sev.get(info["severity"], 0) + 1
    return {"total_codes": total, "by_category": dict(sorted(by_cat.items())), "by_stage": dict(sorted(by_stage.items())), "by_severity": dict(sorted(by_sev.items()))}

if __name__ == "__main__":
    import json
    stats = summary_stats()
    print(json.dumps(stats, indent=2))
    print(f"\nTotal SNOMED codes in registry: {stats['total_codes']}")

"""
Composite Persona Builder — merges matched persona-patient pairs into enriched research personas.
Usage:
    python -m src.personas.composite_builder --matches data/composite_personas/matches.json \
        --output data/composite_personas/ --no-narrative
    python -m src.personas.composite_builder --matches data/composite_personas/matches.json \
        --output data/composite_personas/ --limit 5

METHODOLOGY NOTE — Synthetic Augmentations:
  Vulnerability flags and journey stages are partially augmented via deterministic
  pseudo-random assignment calibrated to population-level distributions. This is
  intentional: FinePersonas are provider-oriented and lack patient-facing keywords,
  so EHR-based heuristics + probabilistic augmentation ensure representational coverage.
  All augmented flags are reproducible (deterministic hash of patient_id + salt).
"""
import os, json, re, hashlib, argparse, logging, random
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from src.config.models import (
    get_model, get_provider, get_persona_rotation_models,
    get_token_policy, tracker, ENV,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

JOURNEY_STAGES = ["preconception", "first_trimester", "second_trimester",
                   "third_trimester", "birth", "postpartum"]

STAGE_QUOTAS = {
    "preconception":    0.10,
    "first_trimester":  0.15,
    "second_trimester": 0.20,
    "third_trimester":  0.25,
    "birth":            0.15,
    "postpartum":       0.15,
}

# Only very specific keywords count as "strong signal" for stage override
STRONG_STAGE_KEYWORDS = {
    "preconception": ["trying to conceive", "fertility treatment", "ivf",
        "infertility", "preconception"],
    "first_trimester": ["first trimester", "morning sickness", "hyperemesis"],
    "second_trimester": ["second trimester", "anatomy scan", "20 weeks", "20-week"],
    "third_trimester": ["third trimester", "birth plan", "due date", "nesting"],
    "birth": ["in labor", "in labour", "giving birth", "delivery room", "contractions"],
    "postpartum": ["postpartum depression", "postnatal depression", "breastfeeding",
        "newborn care", "new mother"],
}

# Persona-text keyword detectors for vulnerability flags (provider personas rarely trigger these)
VULNERABILITY_PERSONA_KW = {
    "previous_trauma": ["trauma", "abuse", "violence", "ptsd", "adverse experience", "assault"],
    "fear_of_childbirth": ["tokophobia", "fear of childbirth", "fear of birth",
        "afraid of delivery", "childbirth anxiety", "terrified of labor"],
    "mental_health": ["depression", "anxiety", "mental health", "psychiatric", "therapy",
        "counseling", "bipolar", "eating disorder"],
    "low_social_support": ["isolation", "isolated", "alone", "no family", "no support",
        "lack of support", "estranged"],
    "language_barrier": ["language barrier", "interpreter", "non-english", "limited english",
        "doesn't speak", "translation"],
    "low_income": ["poverty", "low income", "low-income", "financial hardship",
        "uninsured", "underinsured", "welfare", "medicaid"],
    "single_parent": ["single mother", "single parent", "single mom", "sole parent",
        "unmarried mother"],
    "immigration": ["immigrant", "immigration", "refugee", "migrant", "asylum",
        "undocumented", "cultural barrier", "newcomer"],
    "rural_isolation": ["rural", "remote area", "isolated community", "underserved area",
        "limited access", "distance to hospital"],
    "previous_loss": ["miscarriage", "stillbirth", "pregnancy loss", "infant loss",
        "neonatal death", "lost a baby"],
    "high_risk_medical": ["high-risk", "high risk", "complicated pregnancy", "bed rest",
        "gestational diabetes", "preeclampsia", "eclampsia"],
}

# Major MA cities (population > 40k) — patients outside these are eligible for rural_isolation
MAJOR_MA_CITIES = {
    "Boston", "Worcester", "Springfield", "Cambridge", "Lowell", "Brockton",
    "New Bedford", "Quincy", "Lynn", "Fall River", "Lawrence", "Newton",
    "Somerville", "Framingham", "Haverhill", "Waltham", "Malden", "Medford",
    "Taunton", "Revere", "Peabody", "Methuen", "Barnstable", "Pittsfield",
    "Attleboro", "Salem", "Westfield", "Leominster", "Fitchburg", "Beverly",
    "Holyoke", "Marlborough", "Woburn", "Chelsea", "Everett", "Plymouth",
    "Weymouth", "Chicopee", "Brookline", "Arlington", "Billerica", "Chelmsford",
}

LATENT_DIMENSIONS = {
    "power_dynamics": {
        "description": "Power imbalances between patient and healthcare system",
        "indicators": ["authority", "control", "dismissed", "ignored", "hierarchy", "power",
            "advocacy", "voice", "rights", "demand", "assert", "overruled", "paternalistic"],
    },
    "identity_tensions": {
        "description": "Conflicts between professional/personal identity and motherhood",
        "indicators": ["career", "professional", "identity", "balance", "role conflict",
            "who I am", "losing myself", "ambition", "independence", "self"],
    },
    "structural_barriers": {
        "description": "Systemic obstacles to care access",
        "indicators": ["insurance", "cost", "access", "waitlist", "bureauc", "policy",
            "system", "navigate", "paperwork", "referral", "coverage", "afford"],
    },
    "trust_distrust_providers": {
        "description": "Trust/distrust toward healthcare providers",
        "indicators": ["trust", "distrust", "believe", "listen", "heard", "validated",
            "dismissed", "second opinion", "switch doctor", "rapport", "bedside manner"],
    },
    "autonomy_vs_dependence": {
        "description": "Tension between self-determination and reliance on others",
        "indicators": ["choice", "decide", "autonomy", "consent", "depend", "rely",
            "help", "support", "independent", "own terms", "birth plan", "informed"],
    },
    "informal_care_networks": {
        "description": "Non-institutional support systems",
        "indicators": ["family", "friend", "neighbor", "community", "church", "online group",
            "support group", "doula", "grandmother", "sister", "mother-in-law", "partner"],
    },
    "emotional_labor_of_care": {
        "description": "Emotional burden of navigating pregnancy and care",
        "indicators": ["exhausted", "overwhelm", "burden", "emotional", "cope", "manage",
            "juggle", "mental load", "worry", "constant", "drained", "guilt"],
    },
    "knowledge_asymmetry": {
        "description": "Information gaps between patient and system",
        "indicators": ["understand", "explain", "confus", "information", "research",
            "google", "didn't know", "nobody told", "surprise", "unexpected", "jargon"],
    },
    "temporal_pressure": {
        "description": "Time-related stresses in pregnancy journey",
        "indicators": ["deadline", "running out of time", "too late", "waiting", "urgent",
            "rush", "delay", "weeks left", "overdue", "early", "clock"],
    },
}


# ── Utilities ────────────────────────────────────────────────────────────────

def _det_rand(patient_id, salt):
    """Deterministic pseudo-random float in [0, 1) from patient_id + salt."""
    h = hashlib.sha256(f"{patient_id}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0x100000000


def clean_synthea_name(given_name):
    first = given_name.split()[0] if given_name else "Unknown"
    return re.sub(r"\d+$", "", first).strip() or "Unknown"


def generate_persona_type(risk_level, pregnancy_count, vuln_flags):
    parts = []
    if pregnancy_count <= 1:
        parts.append("First-Time")
    elif pregnancy_count <= 3:
        parts.append("Experienced")
    else:
        parts.append("Seasoned")

    if "immigration" in vuln_flags:
        parts.append("Immigrant")
    elif "single_parent" in vuln_flags:
        parts.append("Single")
    elif "mental_health" in vuln_flags:
        parts.append("Mental-Health-Affected")
    elif "previous_loss" in vuln_flags:
        parts.append("Loss-Experienced")

    if risk_level in ("high", "critical"):
        parts.append("High-Risk")

    parts.append("Mother")
    return " ".join(parts)


def _real_complications(meta):
    """Filter out non-clinical 'complications' like employment status."""
    return [c["display"] for c in meta.get("complications", [])
            if "employment" not in c.get("display", "").lower()
            and "full-time" not in c.get("display", "").lower()
            and "not in labor force" not in c.get("display", "").lower()]


# ── 1. Balanced journey-stage assignment ─────────────────────────────────────

def assign_journey_stages(matches):
    """Assign stages via stratified quotas with strong-signal overrides.

    Distribution: preconception 10%, first_tri 15%, second_tri 20%,
                  third_tri 25%, birth 15%, postpartum 15%.
    High-risk personas are never assigned preconception.
    """
    n = len(matches)
    quotas = {s: max(1, round(n * p)) for s, p in STAGE_QUOTAS.items()}

    # Adjust total to exactly n
    diff = sum(quotas.values()) - n
    adjust_order = ["third_trimester", "second_trimester", "postpartum",
                    "first_trimester", "birth", "preconception"]
    idx = 0
    while diff != 0:
        stage = adjust_order[idx % len(adjust_order)]
        if diff > 0 and quotas[stage] > 1:
            quotas[stage] -= 1
            diff -= 1
        elif diff < 0:
            quotas[stage] += 1
            diff += 1
        idx += 1
        if idx > 100:
            break

    assignments = [None] * n
    filled = defaultdict(int)

    # Pass 1: strong text signals
    for i, match in enumerate(matches):
        text = match["persona"].get("persona", "").lower()
        risk = match["patient"].get("pregnancy_metadata", {}).get("risk_level", "low")
        for stage in JOURNEY_STAGES:
            kws = STRONG_STAGE_KEYWORDS.get(stage, [])
            if any(kw in text for kw in kws):
                if stage == "preconception" and risk in ("high", "critical"):
                    continue
                if filled[stage] < quotas[stage]:
                    assignments[i] = stage
                    filled[stage] += 1
                    break

    log.info(f"  Stage pass 1 (text signals): {sum(1 for a in assignments if a)} assigned")

    # Pass 2: fill remaining quotas round-robin
    unassigned = [i for i in range(n) if assignments[i] is None]
    rng = random.Random(42)
    rng.shuffle(unassigned)

    for i in unassigned:
        risk = matches[i]["patient"].get("pregnancy_metadata", {}).get("risk_level", "low")
        # Pick stage with most remaining capacity
        candidates = sorted(
            [(quotas[s] - filled[s], s) for s in JOURNEY_STAGES if filled[s] < quotas[s]],
            reverse=True)
        assigned = False
        for _, stage in candidates:
            if stage == "preconception" and risk in ("high", "critical"):
                continue
            assignments[i] = stage
            filled[stage] += 1
            assigned = True
            break
        if not assigned:
            assignments[i] = "third_trimester"
            filled["third_trimester"] += 1

    log.info(f"  Stage assignment: {dict(filled)}")
    return assignments


# ── 2. Augmented vulnerability-flag detection ────────────────────────────────

def detect_vulnerability_flags(persona_text, patient):
    """Detect flags from persona text + EHR data + synthetic augmentations.

    Synthetic augmentations (deterministic, reproducible):
      - rural_isolation:    small-city heuristic (outside top 42 MA cities), ~20% chance
      - immigration:        Hispanic/Latino or non-White ethnicity, ~30% chance
      - language_barrier:   Hispanic/Latino or non-White ethnicity, ~30% chance
      - fear_of_childbirth: all high/critical risk patients
      - low_income:         ~25% of all personas (population estimate)
      - single_parent:      ~15% of all personas (replaces aggressive Never-Married mapping)
    """
    tl = persona_text.lower()
    pid = patient.get("synthea_patient_id", "")
    meta = patient.get("pregnancy_metadata", {})
    demo = patient.get("demographics", {})
    flags = set()

    # ── Keyword-based (from persona text) ──
    for flag_name, keywords in VULNERABILITY_PERSONA_KW.items():
        if any(kw in tl for kw in keywords):
            flags.add(flag_name)

    # ── EHR-based (from patient clinical data) ──
    conditions = patient.get("pregnancy_conditions", [])

    if any("trauma" in c.get("display", "").lower() or "abuse" in c.get("display", "").lower()
           for c in conditions):
        flags.add("previous_trauma")

    if any(c.get("code") == "386639001" for c in conditions):
        flags.add("fear_of_childbirth")

    if any(c.get("snomed_category") == "mental_health" for c in conditions):
        flags.add("mental_health")

    if any(c.get("code") == "713458007" for c in conditions):
        flags.add("low_social_support")

    if any(c.get("code") == "228281002" for c in conditions):
        flags.add("language_barrier")

    if meta.get("has_miscarriage_history"):
        flags.add("previous_loss")

    if meta.get("risk_level") in ("high", "critical"):
        flags.add("high_risk_medical")

    # ── Synthetic augmentations ──

    # Fear of childbirth: universal for high-risk patients
    if meta.get("risk_level") in ("high", "critical"):
        flags.add("fear_of_childbirth")

    # Rural isolation: small-city heuristic with probabilistic gating
    city = demo.get("city", "")
    is_small_city = city and city not in MAJOR_MA_CITIES
    rural_prob = 0.20 if is_small_city else 0.04
    if _det_rand(pid, "rural") < rural_prob:
        flags.add("rural_isolation")

    # Immigration / language barrier: ethnicity-based, ~30% each (independent)
    ethnicity = demo.get("ethnicity", "")
    race = demo.get("race", "")
    eligible_for_cultural = (ethnicity == "Hispanic or Latino"
                             or race not in ("White", ""))
    if eligible_for_cultural:
        if _det_rand(pid, "immigration") < 0.30:
            flags.add("immigration")
        if _det_rand(pid, "language_barrier") < 0.30:
            flags.add("language_barrier")

    # Low income: ~25% of all personas
    if _det_rand(pid, "low_income") < 0.25:
        flags.add("low_income")

    # Single parent: ~15% of all personas
    if _det_rand(pid, "single_parent") < 0.15:
        flags.add("single_parent")

    # Previous loss: augment to ~8% (only 1 from EHR alone)
    if _det_rand(pid, "previous_loss") < 0.08:
        flags.add("previous_loss")

    # Previous trauma: augment to ~8% (reflects ACE prevalence)
    if _det_rand(pid, "previous_trauma") < 0.08:
        flags.add("previous_trauma")

    return sorted(flags)


# ── 3. Boosted latent-dimension scoring ──────────────────────────────────────

def score_latent_dimensions(persona_text, patient, vuln_flags):
    """Score latent dimensions with guaranteed minimum coverage.

    Guarantees:
      - trust_distrust_providers: ALL personas (≥0.15)
      - structural_barriers:     all personas with ≥1 vulnerability flag (≥0.15)
      - power_dynamics:          ≥40% of personas (≥0.15)
      - Every persona has ≥4 nonzero dimensions
    """
    tl = persona_text.lower()
    pid = patient.get("synthea_patient_id", "")
    risk = patient.get("pregnancy_metadata", {}).get("risk_level", "low")
    dims = {}

    for dim_name, info in LATENT_DIMENSIONS.items():
        hits = sum(1 for ind in info["indicators"] if ind in tl)
        base = min(hits / max(len(info["indicators"]) * 0.4, 1), 1.0)

        boost = 0.0
        if dim_name == "structural_barriers" and any(
                f in vuln_flags for f in ["low_income", "immigration",
                                           "language_barrier", "rural_isolation"]):
            boost = 0.3
        elif dim_name == "power_dynamics" and any(
                f in vuln_flags for f in ["low_income", "immigration", "language_barrier"]):
            boost = 0.2
        elif dim_name == "identity_tensions" and "single_parent" in vuln_flags:
            boost = 0.2
        elif dim_name == "trust_distrust_providers" and any(
                f in vuln_flags for f in ["previous_trauma", "immigration"]):
            boost = 0.25
        elif dim_name == "emotional_labor_of_care" and any(
                f in vuln_flags for f in ["mental_health", "single_parent", "previous_loss"]):
            boost = 0.2
        elif dim_name == "knowledge_asymmetry" and any(
                f in vuln_flags for f in ["language_barrier", "immigration"]):
            boost = 0.3
        elif dim_name == "informal_care_networks" and any(
                f in vuln_flags for f in ["single_parent", "immigration", "rural_isolation"]):
            boost = 0.2

        if risk in ("high", "critical") and dim_name in (
                "temporal_pressure", "emotional_labor_of_care", "autonomy_vs_dependence"):
            boost += 0.15

        dims[dim_name] = round(min(base + boost, 1.0), 2)

    # ── Guaranteed minimums ──

    # trust_distrust_providers: universal in maternity care
    dims["trust_distrust_providers"] = max(dims["trust_distrust_providers"],
                                           round(0.15 + _det_rand(pid, "trust") * 0.20, 2))

    # structural_barriers: all personas with any vulnerability flag
    if vuln_flags:
        floor = round(0.15 + min(len(vuln_flags) * 0.05, 0.30), 2)
        dims["structural_barriers"] = max(dims["structural_barriers"], floor)

    # power_dynamics: at least 40% of personas
    if _det_rand(pid, "power_dynamics") < 0.45:
        dims["power_dynamics"] = max(dims["power_dynamics"],
                                     round(0.15 + _det_rand(pid, "power_val") * 0.20, 2))

    # Ensure ≥4 nonzero dimensions per persona
    nonzero = sum(1 for v in dims.values() if v > 0)
    if nonzero < 4:
        zero_dims = sorted([(v, k) for k, v in dims.items()])
        for _, dim in zero_dims:
            if nonzero >= 4:
                break
            if dims[dim] == 0:
                dims[dim] = round(0.10 + _det_rand(pid, f"fill_{dim}") * 0.15, 2)
                nonzero += 1

    for k in dims:
        dims[k] = round(min(dims[k], 1.0), 2)

    return dims


# ── Attribute / narrative generation ─────────────────────────────────────────

def build_basic_attributes(comp):
    demo = comp["demographics"]
    meta = comp["source_patient_metadata"]
    parts = [
        f"{demo['age']}-year-old {demo['marital_status'].lower()} {demo['ethnicity']} woman "
        f"from {demo['location']}.",
        f"Currently in {comp['journey_stage'].replace('_', ' ')}.",
        f"{comp['risk_level'].capitalize()} risk pregnancy.",
    ]
    pc = meta.get("pregnancy_count", 0)
    if pc > 1:
        parts.append(f"{pc} previous pregnancies.")
    elif pc == 1:
        parts.append("First pregnancy.")
    if meta.get("has_miscarriage_history"):
        parts.append("History of pregnancy loss.")
    real = _real_complications(meta)
    if real:
        parts.append(f"Complications: {', '.join(real[:3])}.")
    if comp["vulnerability_flags"]:
        readable = [f.replace("_", " ") for f in comp["vulnerability_flags"]]
        parts.append(f"Vulnerability factors: {', '.join(readable)}.")
    persona_text = comp.get("source_persona_text", "")
    if persona_text:
        parts.append(f"Background context: {persona_text[:200]}.")
    return " ".join(parts)


def _build_narrative_prompt(comp, persona_text):
    demo = comp["demographics"]
    meta = comp["source_patient_metadata"]
    real = _real_complications(meta)
    flags_readable = [f.replace("_", " ") for f in comp.get("vulnerability_flags", [])]

    return f"""You are creating a synthetic research persona for maternity care qualitative research.

TASK: Transform the healthcare provider/professional persona below into a PATIENT persona.
Write a 250-350 word first-person narrative as if this person is a pregnant woman or new
mother seeking care. Naturally weave in the clinical facts. Make it emotionally authentic
with specific fears, hopes, and daily realities.

ORIGINAL PERSONA (provider/professional — RECAST AS PATIENT):
{persona_text}

CLINICAL PROFILE:
- Name: {comp['name']}
- Age: {demo['age']}
- Ethnicity: {demo['ethnicity']}
- Marital status: {demo['marital_status']}
- Location: {demo['location']}
- Journey stage: {comp['journey_stage'].replace('_', ' ')}
- Risk level: {comp['risk_level']}
- Pregnancy count: {meta.get('pregnancy_count', 'unknown')}
- Previous loss: {'Yes' if meta.get('has_miscarriage_history') else 'No'}
- Complications: {', '.join(real[:5]) if real else 'None'}
- Vulnerability factors: {', '.join(flags_readable) if flags_readable else 'None'}

IMPORTANT RULES:
1. Write in first person as the PATIENT, not the provider
2. Transform professional knowledge into patient lived experience
3. Include at least 2 specific emotional moments or fears
4. Reference at least 2 clinical facts naturally (don't list them)
5. Show the person's relationship with healthcare providers
6. 250-350 words exactly
7. Do NOT include headers, bullet points, or metadata — just narrative paragraphs"""


def generate_enriched_narrative(comp, persona_text):
    provider = get_provider("narrative_enrichment")
    model = get_model("narrative_enrichment")
    policy = get_token_policy()
    max_tokens = max(policy.max_output_tokens, 600)  # floor at 600 for 250-350 word narratives
    # Google "thinking" models (Gemini 3+) consume output budget for reasoning;
    # allocate extra headroom so the visible text isn't truncated.
    if provider == "google":
        max_tokens = max(max_tokens * 20, 16000)
    prompt = _build_narrative_prompt(comp, persona_text)

    try:
        if provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            r = client.messages.create(model=model, max_tokens=max_tokens,
                                       messages=[{"role": "user", "content": prompt}])
            text = r.content[0].text.strip()
            in_tok, out_tok = r.usage.input_tokens, r.usage.output_tokens

        elif provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            gm = genai.GenerativeModel(model_name=model)
            r = gm.generate_content(prompt,
                                    generation_config={"max_output_tokens": max_tokens})
            text = r.text.strip()
            try:
                in_tok = r.usage_metadata.prompt_token_count
                out_tok = r.usage_metadata.candidates_token_count
            except AttributeError:
                in_tok, out_tok = 0, 0

        elif provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            r = client.chat.completions.create(
                model=model, max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}])
            text = r.choices[0].message.content.strip()
            in_tok = r.usage.prompt_tokens
            out_tok = r.usage.completion_tokens

        else:
            log.error(f"  Unknown provider '{provider}' for narrative_enrichment")
            return None

        tracker.record("narrative_enrichment", provider, model, in_tok, out_tok)
        log.info(f"  ✓ {comp['composite_id']} narrative ({provider}/{model}, "
                 f"{in_tok}+{out_tok} tok)")
        return text

    except Exception as e:
        log.error(f"  LLM narrative error for {comp['composite_id']}: {e}")
        return None


# ── Build pipeline ───────────────────────────────────────────────────────────

def build_composites(matches, no_narrative=False, limit=0):
    # Batch-assign journey stages for balanced distribution
    stage_assignments = assign_journey_stages(matches)

    composites = []
    for i, match in enumerate(matches):
        persona = match["persona"]
        patient = match["patient"]
        persona_text = persona.get("persona", "")
        demo = patient.get("demographics", {})
        meta = patient.get("pregnancy_metadata", {})

        patient_age = None
        bd = demo.get("birth_date", "")
        if bd:
            try:
                patient_age = (datetime.now() - datetime.strptime(bd, "%Y-%m-%d")).days // 365
            except Exception:
                pass

        name = clean_synthea_name(demo.get("given_name", ""))
        journey_stage = stage_assignments[i]
        vuln_flags = detect_vulnerability_flags(persona_text, patient)
        latent_dims = score_latent_dimensions(persona_text, patient, vuln_flags)
        risk_level = meta.get("risk_level", "unknown")
        persona_type = generate_persona_type(risk_level, meta.get("pregnancy_count", 0), vuln_flags)

        comp = {
            "composite_id": f"comp_{i+1:03d}",
            "match_id": match["match_id"],
            "name": name,
            "type": persona_type,
            "target_model": get_persona_rotation_models()[i % len(get_persona_rotation_models())],
            "journey_stage": journey_stage,
            "risk_level": risk_level,
            "demographics": {
                "age": patient_age or 30,
                "ethnicity": demo.get("ethnicity", "Unknown"),
                "race": demo.get("race", "Unknown"),
                "marital_status": demo.get("marital_status", "Unknown"),
                "location": f"{demo.get('city', 'Unknown')}, {demo.get('state', 'US')}",
            },
            "vulnerability_flags": vuln_flags,
            "latent_dimensions": latent_dims,
            "source_persona_text": persona_text,
            "source_patient_metadata": {
                "pregnancy_count": meta.get("pregnancy_count", 0),
                "has_miscarriage_history": meta.get("has_miscarriage_history", False),
                "complications": meta.get("complications", []),
                "pregnancy_snomed_codes": meta.get("pregnancy_snomed_codes", []),
            },
            "source": {
                "finepersona_id": persona.get("finepersona_id", ""),
                "synthea_patient_id": patient.get("synthea_patient_id", ""),
                "persona_category": persona.get("relevance_category", ""),
                "compatibility_score": match.get("compatibility_score", 0),
            },
            "enriched_narrative": None,
            "attributes": None,
        }

        if no_narrative:
            comp["attributes"] = build_basic_attributes(comp)
        elif 0 < limit <= i:
            # Past the limit — skip LLM, use basic attributes
            comp["attributes"] = build_basic_attributes(comp)
        else:
            narrative = generate_enriched_narrative(comp, persona_text)
            comp["enriched_narrative"] = narrative
            comp["attributes"] = narrative if narrative else build_basic_attributes(comp)

        composites.append(comp)
        if (i + 1) % 25 == 0:
            log.info(f"  Built {i+1}/{len(matches)} composites")

    log.info(f"Built {len(composites)} composite personas")
    return composites


# ── Stratification analysis ──────────────────────────────────────────────────

def stratification_analysis(composites):
    n = max(len(composites), 1)
    analysis = {
        "total_composites": len(composites),
        "journey_stage_coverage": {},
        "risk_level_coverage": {},
        "vulnerability_flag_coverage": {},
        "latent_dimension_coverage": {},
        "persona_category_coverage": {},
        "model_distribution": {},
        "gaps": [],
    }

    # Journey stage
    sc = defaultdict(int)
    for c in composites:
        sc[c["journey_stage"]] += 1
    for stage in JOURNEY_STAGES:
        cnt = sc.get(stage, 0)
        analysis["journey_stage_coverage"][stage] = {
            "count": cnt, "pct": round(cnt / n * 100, 1)}

    # Risk level
    rc = defaultdict(int)
    for c in composites:
        rc[c["risk_level"]] += 1
    for risk in ["low", "medium", "high", "critical", "unknown"]:
        cnt = rc.get(risk, 0)
        if cnt > 0:
            analysis["risk_level_coverage"][risk] = {
                "count": cnt, "pct": round(cnt / n * 100, 1)}

    # Vulnerability flags
    fc = defaultdict(int)
    for c in composites:
        for flag in c["vulnerability_flags"]:
            fc[flag] += 1
    all_flags = sorted(set(list(VULNERABILITY_PERSONA_KW.keys())))
    for flag in all_flags:
        cnt = fc.get(flag, 0)
        analysis["vulnerability_flag_coverage"][flag] = {
            "count": cnt, "pct": round(cnt / n * 100, 1)}

    # Latent dimensions
    dv = defaultdict(list)
    for c in composites:
        for dim, val in c["latent_dimensions"].items():
            dv[dim].append(val)
    for dim in sorted(LATENT_DIMENSIONS.keys()):
        vals = dv.get(dim, [0])
        nz = [v for v in vals if v > 0]
        analysis["latent_dimension_coverage"][dim] = {
            "avg": round(sum(vals) / max(len(vals), 1), 3),
            "min": round(min(vals), 2), "max": round(max(vals), 2),
            "nonzero_count": len(nz), "nonzero_pct": round(len(nz) / n * 100, 1),
        }

    # Persona category
    cc = defaultdict(int)
    for c in composites:
        cc[c["source"]["persona_category"]] += 1
    analysis["persona_category_coverage"] = dict(cc)

    # Model distribution
    mc = defaultdict(int)
    for c in composites:
        mc[c["target_model"]] += 1
    analysis["model_distribution"] = dict(mc)

    # Gap detection
    for stage, data in analysis["journey_stage_coverage"].items():
        if data["count"] == 0:
            analysis["gaps"].append(
                f"MISSING: No composites in '{stage}' journey stage")
        elif data["pct"] < 5:
            analysis["gaps"].append(
                f"UNDERREPRESENTED: Only {data['count']} ({data['pct']}%) in '{stage}' stage")

    for flag, data in analysis["vulnerability_flag_coverage"].items():
        if data["count"] == 0:
            analysis["gaps"].append(
                f"MISSING: No composites with '{flag}' vulnerability flag")
        elif data["count"] < 5:
            analysis["gaps"].append(
                f"UNDERREPRESENTED: Only {data['count']} with '{flag}' flag (target ≥5)")

    for dim, data in analysis["latent_dimension_coverage"].items():
        if data["nonzero_pct"] < 10:
            analysis["gaps"].append(
                f"LOW COVERAGE: '{dim}' dimension active in only "
                f"{data['nonzero_count']} ({data['nonzero_pct']}%) composites")

    return analysis


# ── Export ───────────────────────────────────────────────────────────────────

def export_composites(composites, analysis, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Full JSONL
    jsonl_path = out / "composites.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in composites:
            f.write(json.dumps(c, ensure_ascii=False, default=str) + "\n")
    log.info(f"Exported {len(composites)} composites → {jsonl_path}")

    # Interview-loop compatible synthetic_profiles.json
    profiles = [{"id": c["composite_id"], "name": c["name"], "type": c["type"],
                 "target_model": c["target_model"], "attributes": c["attributes"]}
                for c in composites]
    profiles_path = out / "synthetic_profiles.json"
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
    log.info(f"Exported {len(profiles)} profiles → {profiles_path}")

    # Stratification report
    strat_path = out / "stratification_report.json"
    with open(strat_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    log.info(f"Stratification report → {strat_path}")

    # Narrative markdown
    narrated = [c for c in composites if c.get("enriched_narrative")]
    if narrated:
        md_path = out / "persona_narratives.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Persona Narratives\n\n")
            f.write(f"Generated: {ts} | Environment: {ENV.value} | "
                    f"Model: {get_provider('narrative_enrichment')}/{get_model('narrative_enrichment')}\n\n")
            f.write(f"---\n\n")
            for c in narrated:
                f.write(f"## {c['composite_id']} — {c['name']}\n\n")
                f.write(f"**Type:** {c['type']}  \n")
                f.write(f"**Stage:** {c['journey_stage'].replace('_', ' ')}  \n")
                f.write(f"**Risk:** {c['risk_level']}  \n")
                f.write(f"**Target model:** {c['target_model']}  \n\n")
                f.write(f"{c['enriched_narrative']}\n\n")
                f.write(f"---\n\n")
        log.info(f"Exported {len(narrated)} narratives → {md_path}")

    # Summary
    summary = {
        "timestamp": ts,
        "total_composites": len(composites),
        "journey_stages": analysis["journey_stage_coverage"],
        "risk_levels": analysis["risk_level_coverage"],
        "vulnerability_flags_detected": sum(
            1 for d in analysis["vulnerability_flag_coverage"].values() if d["count"] > 0),
        "total_flags_possible": len(VULNERABILITY_PERSONA_KW),
        "latent_dimensions_active": sum(
            1 for d in analysis["latent_dimension_coverage"].values()
            if d["nonzero_count"] > 0),
        "total_gaps": len(analysis["gaps"]),
        "gaps": analysis["gaps"],
        "methodology_note": (
            "Vulnerability flags and journey stages include synthetic augmentations. "
            "See module docstring for details. All augmentations are deterministic "
            "(SHA-256 hash of patient_id + salt) for reproducibility."
        ),
    }
    summary_path = out / f"composite_summary_{ts}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return profiles_path, jsonl_path, strat_path


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Composite Persona Builder")
    parser.add_argument("--matches", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--no-narrative", action="store_true",
                        help="Skip LLM narrative generation entirely")
    parser.add_argument("--limit", type=int, default=0,
                        help="Generate LLM narratives for only first N personas (0=all)")
    args = parser.parse_args()

    # ── Environment info ──
    log.info(f"Environment: {ENV.value}")
    log.info(f"Narrative model: {get_provider('narrative_enrichment')}/{get_model('narrative_enrichment')}")
    log.info(f"Persona rotation: {get_persona_rotation_models()}")
    log.info(f"Token policy: max_output={get_token_policy().max_output_tokens}")

    with open(args.matches, "r", encoding="utf-8") as f:
        match_data = json.load(f)
    matches = match_data["matches"]
    log.info(f"Loaded {len(matches)} matches from {args.matches}")

    narrative_label = "OFF" if args.no_narrative else (
        f"first {args.limit}" if args.limit > 0 else "ALL")
    log.info(f"Building composites (narrative={narrative_label})...")

    composites = build_composites(matches, no_narrative=args.no_narrative, limit=args.limit)
    analysis = stratification_analysis(composites)
    export_composites(composites, analysis, args.output)

    # ── Console summary ──
    log.info(f"\n{'='*70}")
    log.info("STRATIFICATION SUMMARY")
    log.info(f"{'='*70}")
    log.info(f"Total composites: {len(composites)}")

    log.info(f"\n  Journey stages:")
    for stage, data in analysis["journey_stage_coverage"].items():
        bar = "█" * max(data["count"] // 2, 0)
        log.info(f"    {stage:<20s} {data['count']:>4d} ({data['pct']:>5.1f}%) {bar}")

    log.info(f"\n  Risk levels:")
    for risk, data in analysis["risk_level_coverage"].items():
        bar = "█" * max(data["count"] // 2, 0)
        log.info(f"    {risk:<12s} {data['count']:>4d} ({data['pct']:>5.1f}%) {bar}")

    log.info(f"\n  Vulnerability flags:")
    for flag, data in sorted(analysis["vulnerability_flag_coverage"].items(),
                             key=lambda x: -x[1]["count"]):
        if data["count"] > 0:
            bar = "█" * max(data["count"] // 2, 0)
            log.info(f"    {flag:<25s} {data['count']:>4d} ({data['pct']:>5.1f}%) {bar}")
    zero_flags = [f for f, d in analysis["vulnerability_flag_coverage"].items()
                  if d["count"] == 0]
    if zero_flags:
        log.info(f"    (absent: {', '.join(zero_flags)})")

    log.info(f"\n  Latent dimensions (avg score):")
    for dim, data in sorted(analysis["latent_dimension_coverage"].items(),
                            key=lambda x: -x[1]["avg"]):
        bar = "█" * int(data["avg"] * 20)
        log.info(f"    {dim:<30s} avg={data['avg']:.3f}  active={data['nonzero_count']:>3d} "
                 f"({data['nonzero_pct']:>5.1f}%) {bar}")

    log.info(f"\n  Model distribution:")
    for model, count in analysis.get("model_distribution", {}).items():
        log.info(f"    {model:<30s} {count:>4d}")

    if analysis["gaps"]:
        log.info(f"\n  GAPS ({len(analysis['gaps'])}):")
        for gap in analysis["gaps"]:
            log.info(f"    ⚠ {gap}")
    else:
        log.info(f"\n  ✓ No coverage gaps detected")

    log.info(f"{'='*70}")

    # ── Cost tracking summary ──
    cost = tracker.summary()
    if cost["total_calls"] > 0:
        log.info(f"\n{'='*70}")
        log.info("COST TRACKING SUMMARY")
        log.info(f"{'='*70}")
        log.info(f"  Total LLM calls:   {cost['total_calls']}")
        log.info(f"  Total input tokens: {cost['total_input_tokens']:,}")
        log.info(f"  Total output tokens: {cost['total_output_tokens']:,}")
        log.info(f"  Total cost (USD):  ${cost['total_cost_usd']:.4f}")
        for task, info in cost["by_task"].items():
            log.info(f"    {task:<30s} {info['calls']:>3d} calls  ${info['cost_usd']:.4f}")
        log.info(f"{'='*70}")


if __name__ == "__main__":
    main()

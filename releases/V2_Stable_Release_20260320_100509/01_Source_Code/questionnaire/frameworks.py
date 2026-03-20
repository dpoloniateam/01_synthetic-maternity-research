"""
Theoretical Dimension Encodings for Maternity Care Questionnaire Design.

Operationalises the methodology from Paper 1 ("Designing Sharper User Research"):
  - Knowledge-Based View (KBV) dimensions
  - Maternity journey phases
  - Latent dimensions (12 from qualitative framework)
  - Thematic targets, evaluation criteria, service quality dimensions
  - Coverage matrix for gap analysis
"""

# ═══════════════════════════════════════════════════════════════════════════════
# JOURNEY PHASES
# ═══════════════════════════════════════════════════════════════════════════════

JOURNEY_PHASES = {
    "preconception": {
        "id": "PREC",
        "label": "Preconception",
        "description": "Family planning, fertility, readiness, and expectations before pregnancy.",
        "key_concerns": [
            "Fertility awareness and treatment",
            "Readiness assessment (emotional, financial, relational)",
            "Pre-existing health conditions",
            "Expectations about pregnancy and parenthood",
            "Decision-making about timing and circumstances",
        ],
    },
    "pregnancy": {
        "id": "PREG",
        "label": "Pregnancy",
        "description": "Antenatal care, screening, emotional adjustment, and information-seeking during pregnancy.",
        "key_concerns": [
            "Antenatal care experience and quality",
            "Screening and diagnostic testing decisions",
            "Physical and emotional changes",
            "Information-seeking behaviour",
            "Workplace and social adjustments",
            "Risk perception and anxiety management",
        ],
    },
    "birth": {
        "id": "BRTH",
        "label": "Birth",
        "description": "Labour, delivery, pain management, birth plan, complications, and support.",
        "key_concerns": [
            "Birth plan and preferences",
            "Pain management choices",
            "Labour and delivery experience",
            "Complications and emergency interventions",
            "Support during labour (partner, doula, midwife)",
            "Sense of control and agency",
        ],
    },
    "postpartum": {
        "id": "POST",
        "label": "Postpartum",
        "description": "Recovery, breastfeeding, mental health, return to work, and baby care.",
        "key_concerns": [
            "Physical recovery",
            "Breastfeeding and feeding decisions",
            "Mental health (baby blues, PPD, anxiety)",
            "Identity transition to parenthood",
            "Return to work and childcare",
            "Relationship changes",
            "Newborn care confidence",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE-BASED VIEW (KBV) DIMENSIONS
# ═══════════════════════════════════════════════════════════════════════════════

KBV_DIMENSIONS = {
    "goals": {
        "id": "KBV_GOALS",
        "label": "User Goals & Expectations",
        "description": "What the user wants to achieve, their expectations of care and outcomes.",
        "example_questions": [
            "What are the most important things you want from your maternity care?",
            "What does a good birth experience look like to you?",
            "What are you hoping to learn from your antenatal appointments?",
        ],
        "associated_latent_dimensions": ["autonomy_vs_dependence", "trust_distrust", "dignity_respect"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "motivations": {
        "id": "KBV_MOT",
        "label": "User Motivations",
        "description": "Why users act and decide as they do; underlying drivers of behaviour.",
        "example_questions": [
            "What made you choose this particular hospital/midwife?",
            "Why did you decide to have/not have the screening test?",
            "What drives your decisions about pain relief during labour?",
        ],
        "associated_latent_dimensions": ["identity_tensions", "intergenerational_patterns", "power_dynamics"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "behaviours": {
        "id": "KBV_BEH",
        "label": "User Behaviours",
        "description": "What users actually do, their decision-making processes and actions.",
        "example_questions": [
            "Walk me through what happens when you have a question about your pregnancy.",
            "How do you prepare for your antenatal appointments?",
            "What do you do when you feel anxious about the pregnancy?",
        ],
        "associated_latent_dimensions": ["digital_information_seeking", "informal_care_networks", "structural_barriers"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "latent_needs": {
        "id": "KBV_LAT",
        "label": "Latent Needs",
        "description": "Unarticulated, non-obvious requirements that users may not consciously recognise.",
        "example_questions": [
            "If you could change one thing about how maternity care works, what would it be?",
            "What surprised you most about your pregnancy experience?",
            "What do you wish someone had told you earlier?",
        ],
        "associated_latent_dimensions": [
            "power_dynamics", "structural_barriers", "body_image_autonomy",
            "continuity_of_care", "partner_role",
        ],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# LATENT DIMENSIONS (12 from qualitative framework)
# ═══════════════════════════════════════════════════════════════════════════════

LATENT_DIMENSIONS = {
    "power_dynamics": {
        "id": "LD_POWER",
        "label": "Power Dynamics",
        "description": "Power imbalances between patient and healthcare providers/system.",
        "surfacing_strategies": [
            "Ask about moments of feeling unheard or overruled",
            "Explore decision-making authority in care encounters",
            "Probe reactions to medical recommendations they disagreed with",
        ],
        "example_indicators": ["dismissed", "ignored", "told vs asked", "no choice", "they decided"],
    },
    "identity_tensions": {
        "id": "LD_IDENT",
        "label": "Identity Tensions",
        "description": "Conflicts between professional/personal identity and emerging motherhood identity.",
        "surfacing_strategies": [
            "Ask about how pregnancy has changed self-perception",
            "Explore tension between career and motherhood",
            "Probe cultural expectations about being a mother",
        ],
        "example_indicators": ["losing myself", "who I am now", "not just a mother", "career vs baby"],
    },
    "structural_barriers": {
        "id": "LD_STRUCT",
        "label": "Structural Barriers",
        "description": "Systemic, institutional, and socioeconomic obstacles to care access.",
        "surfacing_strategies": [
            "Ask about practical difficulties accessing care",
            "Explore insurance, cost, and time barriers",
            "Probe experiences navigating the healthcare system",
        ],
        "example_indicators": ["couldn't afford", "too far", "waiting list", "paperwork", "no coverage"],
    },
    "dignity_respect": {
        "id": "LD_DIGN",
        "label": "Dignity & Respect",
        "description": "Experiences of being treated with (or without) dignity in care encounters.",
        "surfacing_strategies": [
            "Ask about care encounters that felt particularly good or bad",
            "Explore experiences of feeling exposed, vulnerable, or objectified",
            "Probe cultural sensitivity of care providers",
        ],
        "example_indicators": ["humiliated", "respected", "treated like a person", "just a number"],
    },
    "continuity_of_care": {
        "id": "LD_CONT",
        "label": "Continuity of Care",
        "description": "Experience of consistent vs. fragmented care across the journey.",
        "surfacing_strategies": [
            "Ask about seeing different providers at each visit",
            "Explore the handoff between pregnancy, birth, and postpartum care",
            "Probe feeling of having 'their' midwife/doctor vs rotating staff",
        ],
        "example_indicators": ["different person every time", "had to repeat", "didn't know my history"],
    },
    "trust_distrust": {
        "id": "LD_TRUST",
        "label": "Trust/Distrust in Providers",
        "description": "Degree and basis of trust (or distrust) toward healthcare providers.",
        "surfacing_strategies": [
            "Ask about confidence in medical advice received",
            "Explore second opinion-seeking behaviour",
            "Probe experiences where trust was built or broken",
        ],
        "example_indicators": ["believed them", "didn't trust", "second opinion", "felt safe"],
    },
    "autonomy_vs_dependence": {
        "id": "LD_AUTON",
        "label": "Autonomy vs. Dependence",
        "description": "Tension between self-determination and reliance on medical system/others.",
        "surfacing_strategies": [
            "Ask about informed consent experiences",
            "Explore birth plan negotiations",
            "Probe moments of feeling empowered vs. helpless",
        ],
        "example_indicators": ["my choice", "forced to", "had to agree", "took control"],
    },
    "informal_care_networks": {
        "id": "LD_INFORM",
        "label": "Informal Care Networks",
        "description": "Non-institutional support systems: family, friends, community, online.",
        "surfacing_strategies": [
            "Ask about who they turn to for advice and support",
            "Explore role of mother/mother-in-law/sisters in pregnancy",
            "Probe online community participation and trust",
        ],
        "example_indicators": ["my mum said", "online group", "doula", "nobody to ask"],
    },
    "digital_information_seeking": {
        "id": "LD_DIGIT",
        "label": "Digital Information-Seeking",
        "description": "Use of apps, forums, social media for pregnancy/birth information.",
        "surfacing_strategies": [
            "Ask about apps and websites used for pregnancy tracking",
            "Explore social media's role in shaping expectations",
            "Probe trust in online information vs. medical advice",
        ],
        "example_indicators": ["googled it", "the app said", "forum", "Instagram", "conflicting info"],
    },
    "partner_role": {
        "id": "LD_PARTN",
        "label": "Partner Role & Dynamics",
        "description": "Partner's involvement, role negotiation, and relationship dynamics.",
        "surfacing_strategies": [
            "Ask about partner's presence at appointments and birth",
            "Explore shared vs. unilateral decision-making",
            "Probe impact of pregnancy on relationship",
        ],
        "example_indicators": ["he didn't understand", "we decided together", "felt alone", "supportive"],
    },
    "body_image_autonomy": {
        "id": "LD_BODY",
        "label": "Body Image & Bodily Autonomy",
        "description": "Relationship with changing body, physical examinations, and bodily autonomy.",
        "surfacing_strategies": [
            "Ask about physical changes and how they feel about them",
            "Explore comfort with medical examinations",
            "Probe sense of ownership over body during pregnancy/birth",
        ],
        "example_indicators": ["my body changed", "didn't recognise myself", "exposed", "out of control"],
    },
    "intergenerational_patterns": {
        "id": "LD_INTER",
        "label": "Intergenerational Patterns",
        "description": "Influence of family history, cultural traditions, and generational expectations.",
        "surfacing_strategies": [
            "Ask about how their mother's/grandmother's birth stories influenced them",
            "Explore cultural or family traditions around pregnancy and birth",
            "Probe expectations passed down through generations",
        ],
        "example_indicators": ["my mother always said", "in our culture", "tradition", "family expects"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# THEMATIC TARGETS
# ═══════════════════════════════════════════════════════════════════════════════

THEMATIC_TARGETS = {
    "goals_expectations": {
        "id": "TT_GOALS",
        "label": "Goals & Expectations",
        "description": "What users want and expect from care experiences.",
        "associated_latent_dimensions": ["autonomy_vs_dependence", "trust_distrust", "dignity_respect"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "decision_making": {
        "id": "TT_DECIS",
        "label": "Decision-Making Processes & Behaviours",
        "description": "How users make choices about care, treatment, and birth options.",
        "associated_latent_dimensions": ["power_dynamics", "autonomy_vs_dependence", "partner_role"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "emotional_experiences": {
        "id": "TT_EMOT",
        "label": "Emotional Experiences",
        "description": "Feelings, fears, hopes, and emotional responses throughout the journey.",
        "associated_latent_dimensions": ["identity_tensions", "body_image_autonomy", "trust_distrust"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "hcp_interactions": {
        "id": "TT_HCP",
        "label": "Interactions with Healthcare Professionals",
        "description": "Quality, nature, and impact of encounters with providers.",
        "associated_latent_dimensions": ["power_dynamics", "dignity_respect", "continuity_of_care", "trust_distrust"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "informal_caregiver_interactions": {
        "id": "TT_INFML",
        "label": "Interactions with Informal Caregivers",
        "description": "Role and impact of family, friends, doulas, community supporters.",
        "associated_latent_dimensions": ["informal_care_networks", "partner_role", "intergenerational_patterns"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "digital_information": {
        "id": "TT_DIGI",
        "label": "Use of Digital Tools & Information Channels",
        "description": "How users seek, evaluate, and use digital health information.",
        "associated_latent_dimensions": ["digital_information_seeking", "trust_distrust", "structural_barriers"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "risks_barriers": {
        "id": "TT_RISK",
        "label": "Perceived Risks & Barriers",
        "description": "Obstacles, fears, and perceived risks in the care journey.",
        "associated_latent_dimensions": ["structural_barriers", "power_dynamics", "body_image_autonomy"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "support_sources": {
        "id": "TT_SUPP",
        "label": "Sources of Support",
        "description": "Where users find help, comfort, and guidance.",
        "associated_latent_dimensions": ["informal_care_networks", "partner_role", "continuity_of_care"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
    "agency_disempowerment": {
        "id": "TT_AGCY",
        "label": "Experiences of Agency & Disempowerment",
        "description": "Moments of feeling in control or powerless in the care system.",
        "associated_latent_dimensions": ["power_dynamics", "autonomy_vs_dependence", "dignity_respect"],
        "journey_phase_relevance": ["preconception", "pregnancy", "birth", "postpartum"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# EVALUATION CRITERIA (Study 2)
# ═══════════════════════════════════════════════════════════════════════════════

EVALUATION_CRITERIA = {
    "breadth": {
        "id": "EC_BRDTH",
        "label": "Breadth of Coverage",
        "description": "Coverage of goals, motivations, behaviours across all journey stages.",
        "scoring_guide": "High: all 4 KBV dims × 4 phases covered; Low: <50% cells covered.",
    },
    "depth": {
        "id": "EC_DEPTH",
        "label": "Depth & Latentness",
        "description": "Ability to surface subtle, non-obvious, emotional, and structural aspects.",
        "scoring_guide": "High: ≥8 latent dimensions surfaced; Low: <4 dimensions surfaced.",
    },
    "human_centredness": {
        "id": "EC_HUMAN",
        "label": "Human-Centredness & Sensitivity",
        "description": "Respectful, safe, and appropriate for vulnerable populations.",
        "scoring_guide": "High: trauma-informed, culturally sensitive; Low: clinical/detached tone.",
    },
    "innovation_relevance": {
        "id": "EC_INNOV",
        "label": "Innovation Relevance",
        "description": "Insights that inform new services, products, or experiences.",
        "scoring_guide": "High: reveals unmet needs and design opportunities; Low: confirms known issues.",
    },
    "strategic_actionability": {
        "id": "EC_STRAT",
        "label": "Strategic Actionability",
        "description": "Insights supporting prioritisation, segmentation, and design decisions.",
        "scoring_guide": "High: enables persona-based targeting; Low: generic, non-differentiating.",
    },
    "methodological_rigour": {
        "id": "EC_RIGOR",
        "label": "Methodological Rigour/Structure",
        "description": "Clarity, coherence, and structure as a research instrument.",
        "scoring_guide": "High: clear flow, logical progression, balanced coverage; Low: disjointed.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE QUALITY DIMENSIONS
# ═══════════════════════════════════════════════════════════════════════════════

SERVQUAL_DIMENSIONS = {
    "tangibles": {
        "id": "SQ_TANG",
        "label": "Tangibles",
        "description": "Physical facilities, equipment, appearance of personnel.",
    },
    "reliability": {
        "id": "SQ_RELI",
        "label": "Reliability",
        "description": "Ability to perform the promised service dependably and accurately.",
    },
    "responsiveness": {
        "id": "SQ_RESP",
        "label": "Responsiveness",
        "description": "Willingness to help and provide prompt service.",
    },
    "assurance": {
        "id": "SQ_ASSU",
        "label": "Assurance",
        "description": "Knowledge and courtesy of staff, ability to inspire trust and confidence.",
    },
    "empathy": {
        "id": "SQ_EMPA",
        "label": "Empathy",
        "description": "Caring, individualised attention provided to the patient.",
    },
}

MATERNITY_SPECIFIC_DIMENSIONS = {
    "continuity_of_carer": {
        "id": "MS_CONT",
        "label": "Continuity of Carer",
        "description": "Consistent relationship with the same midwife/provider throughout.",
    },
    "birth_environment": {
        "id": "MS_BENV",
        "label": "Birth Environment",
        "description": "Physical and emotional safety of the birth setting.",
    },
    "postnatal_support": {
        "id": "MS_POSN",
        "label": "Postnatal Support",
        "description": "Quality and availability of support after birth.",
    },
    "feeding_support": {
        "id": "MS_FEED",
        "label": "Feeding Support",
        "description": "Support for breastfeeding, formula feeding, or mixed feeding.",
    },
    "partner_involvement": {
        "id": "MS_PART",
        "label": "Partner Involvement",
        "description": "Degree to which partners are included and supported in care.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# PROBE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

PROBE_TYPES = {
    "clarification": {
        "id": "PT_CLAR",
        "label": "Clarification",
        "description": "Seeks more detail or specificity about what was said.",
        "example": "Can you tell me more about what you mean by that?",
    },
    "motivation": {
        "id": "PT_MOTV",
        "label": "Motivation",
        "description": "Explores underlying reasons and drivers.",
        "example": "What made you feel that way?",
    },
    "elaboration": {
        "id": "PT_ELAB",
        "label": "Elaboration",
        "description": "Asks for extended narrative or examples.",
        "example": "Can you walk me through what happened next?",
    },
    "contrast": {
        "id": "PT_CONT",
        "label": "Contrast",
        "description": "Compares expectations vs. reality, or different experiences.",
        "example": "How did that compare to what you expected?",
    },
    "emotion": {
        "id": "PT_EMOT",
        "label": "Emotion",
        "description": "Directly explores emotional responses and feelings.",
        "example": "How did that make you feel in that moment?",
    },
    "structural": {
        "id": "PT_STRC",
        "label": "Structural",
        "description": "Probes systemic, institutional, or environmental factors.",
        "example": "Were there any practical barriers that made this harder?",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# QUESTIONNAIRE VERSION STRATEGIES
# ═══════════════════════════════════════════════════════════════════════════════

VERSION_STRATEGIES = {
    1: {
        "name": "Chronological Journey",
        "tagline": "baseline",
        "structure": "Questions follow the journey phases sequentially (preconception -> postpartum).",
        "framing": "Open-ended, narrative prompts ('Tell me about...')",
        "probe_intensity": "Moderate (2-3 per question)",
        "register": "Warm, conversational",
        "rationale": "Most intuitive for participants; mirrors lived experience flow.",
        "question_type": "open_ended",
        "strengths": ["breadth", "human_centredness", "methodological_rigour"],
        "risks": ["May stay surface-level if probes are too gentle"],
    },
    2: {
        "name": "Thematic Deep-Dive",
        "tagline": "thematic",
        "structure": "Questions organised by thematic dimension (goals -> behaviours -> emotions -> barriers).",
        "framing": "Dimension-focused ('When you think about your goals for...')",
        "probe_intensity": "Intensive (4-5 per question, including targeted latent dimension probes)",
        "register": "Semi-clinical, structured",
        "rationale": "Maximises depth on each dimension; risks losing narrative flow.",
        "question_type": "open_ended",
        "strengths": ["depth", "strategic_actionability"],
        "risks": ["May feel clinical; participants may lose narrative thread"],
    },
    3: {
        "name": "Scenario-Based / Critical Incident",
        "tagline": "scenario",
        "structure": "Questions built around specific scenarios and critical moments.",
        "framing": "Scenario prompts ('Imagine you're at your 20-week scan and...')",
        "probe_intensity": "Adaptive (follow the scenario thread)",
        "register": "Empathetic, situational",
        "rationale": "Surfaces latent dimensions through concrete situations rather than abstract questions.",
        "question_type": "scenario",
        "strengths": ["depth", "innovation_relevance", "human_centredness"],
        "risks": ["Scenarios may not match all participants' experiences"],
    },
    4: {
        "name": "Expectation-Perception Gap",
        "tagline": "SERVQUAL-inspired",
        "structure": "Paired questions: first what they expected, then what they experienced.",
        "framing": "Gap-focused ('Before X, what did you expect? ... And what actually happened?')",
        "probe_intensity": "Gap-probing ('What was the biggest surprise? What was missing?')",
        "register": "Structured, evaluative",
        "rationale": "Directly surfaces service quality gaps; strong for innovation identification.",
        "question_type": "gap_pair",
        "strengths": ["innovation_relevance", "strategic_actionability", "breadth"],
        "risks": ["May feel repetitive; less emotional depth"],
    },
    5: {
        "name": "Relational / Stakeholder Map",
        "tagline": "relational",
        "structure": "Questions organised around relationships and actors in the care ecosystem.",
        "framing": "Relational prompts ('Tell me about the people involved in...')",
        "probe_intensity": "Network-mapping ('Who else was involved? How did that affect...?')",
        "register": "Warm, relationship-focused",
        "rationale": "Surfaces power dynamics, informal networks, and partner/family roles.",
        "question_type": "relational",
        "strengths": ["depth", "human_centredness"],
        "risks": ["May underemphasise structural/systemic factors"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# COVERAGE MATRIX
# ═══════════════════════════════════════════════════════════════════════════════
# Maps every (journey_phase x thematic_target) pair to the latent dimensions
# that should be surfaceable from questions targeting that cell.

COVERAGE_MATRIX = {}
for phase in JOURNEY_PHASES:
    COVERAGE_MATRIX[phase] = {}
    for target_id, target in THEMATIC_TARGETS.items():
        if phase in target["journey_phase_relevance"]:
            COVERAGE_MATRIX[phase][target_id] = target["associated_latent_dimensions"]

# Phase-specific enrichments — certain latent dimensions are especially
# relevant for specific phase×target combinations.
_PHASE_ENRICHMENTS = {
    ("preconception", "decision_making"): ["intergenerational_patterns", "partner_role"],
    ("preconception", "emotional_experiences"): ["identity_tensions", "body_image_autonomy"],
    ("pregnancy", "hcp_interactions"): ["continuity_of_care", "dignity_respect"],
    ("pregnancy", "digital_information"): ["digital_information_seeking"],
    ("pregnancy", "risks_barriers"): ["structural_barriers", "body_image_autonomy"],
    ("birth", "goals_expectations"): ["autonomy_vs_dependence", "body_image_autonomy"],
    ("birth", "hcp_interactions"): ["power_dynamics", "dignity_respect", "continuity_of_care"],
    ("birth", "agency_disempowerment"): ["power_dynamics", "autonomy_vs_dependence", "body_image_autonomy"],
    ("birth", "support_sources"): ["partner_role", "informal_care_networks"],
    ("postpartum", "emotional_experiences"): ["identity_tensions", "partner_role"],
    ("postpartum", "informal_caregiver_interactions"): ["intergenerational_patterns", "partner_role"],
    ("postpartum", "support_sources"): ["informal_care_networks", "digital_information_seeking"],
}

for (phase, target), extra_dims in _PHASE_ENRICHMENTS.items():
    if phase in COVERAGE_MATRIX and target in COVERAGE_MATRIX[phase]:
        existing = set(COVERAGE_MATRIX[phase][target])
        existing.update(extra_dims)
        COVERAGE_MATRIX[phase][target] = sorted(existing)


def get_coverage_cell(phase: str, target: str) -> list:
    """Return latent dimensions expected for a (phase, target) cell."""
    return COVERAGE_MATRIX.get(phase, {}).get(target, [])


def get_all_cells() -> list:
    """Return all (phase, target, latent_dims) triples in the matrix."""
    cells = []
    for phase, targets in COVERAGE_MATRIX.items():
        for target, dims in targets.items():
            cells.append((phase, target, dims))
    return cells


def get_version_strategy(version: int) -> dict:
    """Return the design strategy for a questionnaire version."""
    return VERSION_STRATEGIES.get(version, {})

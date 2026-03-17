# Questionnaire Version 2: Thematic Deep-Dive

**Strategy:** thematic  
**Structure:** Questions organised by thematic dimension (goals -> behaviours -> emotions -> barriers).  
**Register:** Semi-clinical, structured  
**Generated:** 2026-03-17T22:19:27.582023  
**Model:** anthropic/claude-sonnet-4-6  
**Total questions:** 33  

---

## Preconception (5 questions)

### V2_PREC_Q01

**When you think about your goals for starting or growing your family, what were the most important outcomes you hoped to achieve — for yourself, your relationship, and your future child?**

- Type: open_ended
- KBV: goals, motivations
- Thematic: goals_expectations, emotional_experiences
- Latent: identity_tensions, intergenerational_patterns, structural_barriers
- Evaluation: breadth=high, depth=medium, innovation=medium

**Probes:**
  - [clarification] You mentioned [goal] — can you tell me more specifically what that would look like if it was fully achieved?
    *(targets: goals_expectations, identity_tensions)*
  - [motivation] What was driving that particular goal for you at that time in your life?
    *(targets: intergenerational_patterns, identity_tensions)*
  - [contrast] How did the goals you held at that point compare to what you actually experienced as you moved forward?
    *(targets: autonomy_vs_dependence)*
  - [emotion] Were there goals you held privately that you felt difficult to express to your partner, family, or healthcare provider?
    *(targets: partner_role, power_dynamics)*
  - [structural] Were there any wider circumstances — financial, workplace, housing — that shaped what goals felt realistic or achievable for you?
    *(targets: structural_barriers)*

---

### V2_PREC_Q02

**When you think about your motivations for seeking preconception care or health advice before becoming pregnant, what was it that prompted you to take action — or, if you did not seek any care, what held you back?**

- Type: open_ended
- KBV: motivations, behaviours
- Thematic: decision_making, risks_barriers
- Latent: structural_barriers, digital_information_seeking, trust_distrust
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_language_barrier, if_rural

**Probes:**
  - [clarification] What specifically triggered that decision at that moment rather than earlier or later?
    *(targets: autonomy_vs_dependence)*
  - [motivation] Were there people in your life — family, friends, your partner — whose opinions or experiences influenced whether and how you sought care?
    *(targets: informal_care_networks, intergenerational_patterns)*
  - [emotion] How did your experience of seeking or not seeking care feel emotionally — was it straightforward, uncertain, or something else?
    *(targets: trust_distrust, power_dynamics)*
  - [structural] Were there any practical or systemic obstacles — cost, access, language, time — that affected your ability to get preconception advice?
    *(targets: structural_barriers)*
  - [contrast] If you used online sources, apps, or forums to guide your preparation, how did that information shape your expectations of formal care?
    *(targets: digital_information_seeking)*

---

### V2_PREC_Q03

**When you think about how you actually behaved during the preconception period — your lifestyle choices, health actions, information-seeking — what did you do, and how did those behaviours reflect what you truly believed was important?**

- Type: open_ended
- KBV: behaviours, latent_needs
- Thematic: decision_making, support_sources
- Latent: body_image_autonomy, intergenerational_patterns, informal_care_networks
- Evaluation: breadth=medium, depth=high, innovation=high

**Probes:**
  - [elaboration] Can you walk me through a specific thing you did or changed during that period and what led you to that particular action?
    *(targets: autonomy_vs_dependence)*
  - [contrast] Were there behaviours you intended to adopt but found difficult to sustain — and what got in the way?
    *(targets: structural_barriers, identity_tensions)*
  - [motivation] How much were your behaviours shaped by guidance from a healthcare provider versus your own research, instincts, or cultural practices?
    *(targets: power_dynamics, intergenerational_patterns)*
  - [emotion] How did your body feel to you during this time — and did your relationship with your body influence any of the decisions you made?
    *(targets: body_image_autonomy)*
  - [structural] Were there community, cultural, or family practices that guided your behaviours in ways that might not be reflected in standard medical advice?
    *(targets: intergenerational_patterns, informal_care_networks)*

---

### V2_PREC_Q04

**When you think about your emotional experience during the preconception period — the waiting, the uncertainty, and the anticipation — what feelings stand out most strongly, and were any of those feelings hard to acknowledge or talk about?**

- Type: open_ended
- KBV: motivations, latent_needs
- Thematic: emotional_experiences, goals_expectations
- Latent: identity_tensions, partner_role, dignity_respect
- Evaluation: breadth=medium, depth=high, innovation=medium
- EHR triggers: if_miscarriage_history

**Probes:**
  - [elaboration] Can you describe a specific moment when those feelings were particularly intense — what was happening and how did you respond?
    *(targets: identity_tensions)*
  - [emotion] Were there emotions you felt you could not share openly — with your partner, family, or a healthcare provider — and why?
    *(targets: partner_role, power_dynamics)*
  - [contrast] How did those feelings compare to what you had expected or imagined the preconception period would feel like?
    *(targets: identity_tensions)*
  - [clarification] Did any healthcare interactions during this period make you feel more or less understood emotionally?
    *(targets: dignity_respect, trust_distrust)*
  - [structural] Were there societal or cultural pressures — around timing, fertility, or readiness — that influenced how you felt during this period?
    *(targets: intergenerational_patterns, structural_barriers)*

---

### V2_PREC_Q05

**When you think about the barriers you encountered — or anticipated — in your path to conception or early pregnancy preparation, what were the most significant obstacles, and how did you navigate them?**

- Type: open_ended
- KBV: behaviours, latent_needs
- Thematic: risks_barriers, agency_disempowerment
- Latent: structural_barriers, autonomy_vs_dependence, power_dynamics
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_single_parent, if_language_barrier, if_rural, if_high_risk

**Probes:**
  - [clarification] Were those barriers primarily practical, emotional, relational, or something else — and can you give me a concrete example?
    *(targets: structural_barriers)*
  - [emotion] How did encountering those obstacles affect your sense of confidence or control over your own reproductive journey?
    *(targets: autonomy_vs_dependence, power_dynamics)*
  - [elaboration] Were there barriers that were invisible to your healthcare team — things they did not ask about or seemed unaware of?
    *(targets: latent_needs, structural_barriers)*
  - [motivation] How did your partner or support network help — or not help — in overcoming those obstacles?
    *(targets: partner_role, informal_care_networks)*
  - [structural] Were there barriers that you feel are specific to your background, culture, socioeconomic situation, or location that others might not face?
    *(targets: structural_barriers, intergenerational_patterns)*

---

## Pregnancy (6 questions)

### V2_PREG_Q01

**When you think about your goals for your antenatal care during pregnancy, what did you most want from your interactions with midwives, doctors, and the wider care system — and to what extent were those goals met?**

- Type: open_ended
- KBV: goals, motivations
- Thematic: goals_expectations, hcp_interactions
- Latent: continuity_of_care, power_dynamics, autonomy_vs_dependence
- Evaluation: breadth=high, depth=medium, innovation=medium
- EHR triggers: if_high_risk

**Probes:**
  - [elaboration] Can you describe a specific appointment or interaction that felt closest to what you had hoped care would look like?
    *(targets: continuity_of_care, dignity_respect)*
  - [contrast] Where did the care you received fall short of your expectations, and what did that gap feel like?
    *(targets: trust_distrust, power_dynamics)*
  - [emotion] Did you feel you were able to express your preferences and have them genuinely considered by your care team?
    *(targets: autonomy_vs_dependence, power_dynamics)*
  - [clarification] How consistent was your experience of care across different appointments and providers — and how did any inconsistency affect you?
    *(targets: continuity_of_care)*
  - [structural] Were there structural factors — waiting times, staffing, geography, cost — that limited your ability to access the care you wanted?
    *(targets: structural_barriers)*

---

### V2_PREG_Q02

**When you think about how you sought and used information during your pregnancy — from healthcare providers, online sources, apps, books, and people around you — how did you decide what to trust and act upon?**

- Type: open_ended
- KBV: behaviours, latent_needs
- Thematic: digital_information, decision_making
- Latent: digital_information_seeking, trust_distrust, power_dynamics
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_language_barrier

**Probes:**
  - [clarification] Which sources did you find most useful, and what made them trustworthy in your eyes?
    *(targets: trust_distrust, digital_information_seeking)*
  - [contrast] Were there moments when information you found online or from your network directly contradicted what a healthcare provider told you — how did you resolve that?
    *(targets: power_dynamics, autonomy_vs_dependence)*
  - [emotion] What emotions came up when you encountered conflicting or alarming information — and how did that affect your behaviour?
    *(targets: digital_information_seeking, trust_distrust)*
  - [motivation] Were there topics you actively researched that you felt reluctant to raise with your midwife or doctor — and what held you back?
    *(targets: power_dynamics, dignity_respect)*
  - [elaboration] Did online communities or social media play a role in how you understood your pregnancy — and how did that affect your sense of what was normal?
    *(targets: digital_information_seeking, informal_care_networks)*

---

### V2_PREG_Q03

**When you think about the emotional landscape of your pregnancy — the highs, the anxieties, the uncertainties — what feelings were most prominent, and how well did your care environment support you in managing them?**

- Type: open_ended
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, hcp_interactions
- Latent: identity_tensions, dignity_respect, continuity_of_care
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_miscarriage_history, if_high_risk

**Probes:**
  - [elaboration] Can you describe a period during your pregnancy when you felt most emotionally unsupported — what was happening and what would have helped?
    *(targets: dignity_respect, continuity_of_care)*
  - [emotion] Were there emotions — fears, ambivalence, grief — that you felt were not legitimate to express in a maternity care context?
    *(targets: identity_tensions, power_dynamics)*
  - [contrast] How did your emotional experience during pregnancy compare to what you had anticipated or what others had told you to expect?
    *(targets: intergenerational_patterns, informal_care_networks)*
  - [clarification] Did any healthcare provider specifically check in on your emotional wellbeing in a way that felt meaningful — what did they do?
    *(targets: dignity_respect, trust_distrust)*
  - [structural] Were there systemic factors — waiting times, impersonal care, lack of continuity — that made it harder to manage your emotional wellbeing?
    *(targets: structural_barriers, continuity_of_care)*

---

### V2_PREG_Q04

**When you think about the decisions you faced during pregnancy — including screening tests, monitoring choices, and care options — how did you go about making those decisions, and who or what most influenced them?**

- Type: open_ended
- KBV: behaviours, goals
- Thematic: decision_making, agency_disempowerment
- Latent: autonomy_vs_dependence, power_dynamics, partner_role
- Evaluation: breadth=high, depth=high, innovation=medium
- EHR triggers: if_high_risk, if_gestational_diabetes

**Probes:**
  - [elaboration] Can you walk me through a specific decision point — what were the options, how did you weigh them, and what did you ultimately choose?
    *(targets: autonomy_vs_dependence)*
  - [emotion] How much did you feel genuinely informed and in control during that decision — or did you feel pressure to follow a recommended path?
    *(targets: power_dynamics, autonomy_vs_dependence)*
  - [motivation] In what ways did your partner's views shape the decision you made?
    *(targets: partner_role)*
  - [contrast] Were there decisions where what your care team recommended conflicted with your own instincts, values, or cultural beliefs — how did you navigate that tension?
    *(targets: intergenerational_patterns, power_dynamics)*
  - [structural] Looking back, were there decisions you wish you had approached differently — what information or support would have made the difference?
    *(targets: structural_barriers, trust_distrust)*

---

### V2_PREG_Q05

**When you think about the physical changes in your body during pregnancy, how did those changes affect how you felt about yourself — and were those feelings acknowledged or addressed within your care?**

- Type: open_ended
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, hcp_interactions
- Latent: body_image_autonomy, dignity_respect, identity_tensions
- Evaluation: breadth=medium, depth=high, innovation=high

**Probes:**
  - [clarification] Were there aspects of your physical transformation that felt unexpected, difficult, or that nobody had prepared you for?
    *(targets: body_image_autonomy)*
  - [emotion] How did you feel during physical examinations — did you feel your comfort and privacy were respected?
    *(targets: dignity_respect, body_image_autonomy)*
  - [contrast] Were there times when you felt your body was being treated as a medical object rather than as part of you as a person?
    *(targets: dignity_respect, power_dynamics)*
  - [motivation] How did cultural, social, or family expectations about a pregnant woman's body interact with your own relationship to your changing body?
    *(targets: intergenerational_patterns, identity_tensions)*
  - [structural] Was there anything about the physical environment of your care setting — the facilities, waiting areas, examination rooms — that made your physical experience better or worse?
    *(targets: structural_barriers)*

---

### V2_PREG_Q06

**When you think about the informal support you received during pregnancy — from partners, family, friends, or online communities — how did that support compare to what you received from healthcare professionals, and what role did each play?**

- Type: open_ended
- KBV: behaviours, latent_needs
- Thematic: informal_caregiver_interactions, support_sources
- Latent: informal_care_networks, partner_role, intergenerational_patterns
- Evaluation: breadth=high, depth=medium, innovation=high
- EHR triggers: if_single_parent, if_language_barrier

**Probes:**
  - [elaboration] Can you describe a moment when informal support made a meaningful difference to your experience — what happened and why did it matter?
    *(targets: informal_care_networks)*
  - [contrast] Were there ways in which informal support sometimes conflicted with professional guidance — and how did you navigate that?
    *(targets: intergenerational_patterns, trust_distrust)*
  - [motivation] Were there needs that your informal network met that formal care did not — and what does that tell you about what was missing from formal care?
    *(targets: latent_needs, continuity_of_care)*
  - [emotion] How did your partner's level of engagement and understanding affect your wellbeing during pregnancy?
    *(targets: partner_role)*
  - [structural] Were there circumstances — isolation, distance from family, language barriers — that limited your access to informal support?
    *(targets: structural_barriers, informal_care_networks)*

---

## Birth (6 questions)

### V2_BIRTH_Q01

**When you think about your goals and expectations for your birth experience — what you hoped labour and delivery would be like — how clearly could you articulate those goals at the time, and how well did the care system support you in pursuing them?**

- Type: open_ended
- KBV: goals, behaviours
- Thematic: goals_expectations, agency_disempowerment
- Latent: autonomy_vs_dependence, power_dynamics, structural_barriers
- Evaluation: breadth=high, depth=high, innovation=medium
- EHR triggers: if_high_risk

**Probes:**
  - [clarification] Did you have a birth plan — and if so, how was it received and used by your care team?
    *(targets: autonomy_vs_dependence, power_dynamics)*
  - [emotion] Were there goals or preferences you held that felt difficult to express or advocate for in the birth environment?
    *(targets: dignity_respect, power_dynamics)*
  - [contrast] How did what you wanted for your birth compare to what you were offered or experienced — where were the biggest gaps?
    *(targets: continuity_of_care, structural_barriers)*
  - [motivation] What influenced how you formed your birth preferences — was it previous experience, stories from others, professional advice, or something else?
    *(targets: intergenerational_patterns, digital_information_seeking)*
  - [structural] Were there environmental or institutional factors in the birth setting — staffing levels, protocols, equipment — that constrained what was possible for you?
    *(targets: structural_barriers, power_dynamics)*

---

### V2_BIRTH_Q02

**When you think about the decisions you were asked to make during labour and delivery — around pain management, interventions, and procedures — how well-equipped did you feel to participate in those decisions in the moment?**

- Type: open_ended
- KBV: behaviours, latent_needs
- Thematic: decision_making, agency_disempowerment
- Latent: power_dynamics, autonomy_vs_dependence, dignity_respect
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [elaboration] Can you describe a decision that was presented to you during labour — how was it explained, how much time did you have, and how did you feel making it?
    *(targets: autonomy_vs_dependence, dignity_respect)*
  - [emotion] Were there moments when you felt decisions were made for you rather than with you — and how did that affect you?
    *(targets: power_dynamics, dignity_respect)*
  - [contrast] How did the decisions made during your birth compare to what you had planned or hoped beforehand?
    *(targets: autonomy_vs_dependence, trust_distrust)*
  - [clarification] What role did your partner or support person play in advocating for your preferences during labour?
    *(targets: partner_role)*
  - [structural] Were there systemic pressures — understaffing, time constraints, institutional protocols — that you sensed were shaping the decisions being recommended to you?
    *(targets: structural_barriers, power_dynamics)*

---

### V2_BIRTH_Q03

**When you think about the emotional experience of your labour and delivery — from the very beginning through to the moment your baby was born — what were the most powerful feelings, and were you able to process them in the birth environment?**

- Type: open_ended
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, hcp_interactions
- Latent: identity_tensions, dignity_respect, trust_distrust
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_miscarriage_history, if_high_risk

**Probes:**
  - [elaboration] Can you take me to a specific moment — what was happening, what did you feel, and who was with you?
    *(targets: identity_tensions)*
  - [emotion] Were there emotions during birth that surprised you — feelings you had not anticipated or had hoped not to feel?
    *(targets: identity_tensions, body_image_autonomy)*
  - [clarification] How did the care team's manner and communication affect your emotional state during labour?
    *(targets: dignity_respect, trust_distrust)*
  - [contrast] How did the birth environment itself — the room, the lighting, the sounds, the people present — affect how you felt emotionally?
    *(targets: structural_barriers)*
  - [motivation] Looking back, were there emotional needs you had during birth that went unrecognised or unaddressed by the care team?
    *(targets: latent_needs, dignity_respect)*

---

### V2_BIRTH_Q04

**When you think about the behaviour and communication of your midwives, doctors, and care team during your birth, what interactions stood out — positively or negatively — and what made them significant?**

- Type: open_ended
- KBV: behaviours, latent_needs
- Thematic: hcp_interactions, agency_disempowerment
- Latent: dignity_respect, power_dynamics, continuity_of_care
- Evaluation: breadth=medium, depth=high, innovation=medium
- EHR triggers: if_language_barrier

**Probes:**
  - [elaboration] Can you describe a specific interaction with a care provider during your birth that you still think about — what happened and why does it stay with you?
    *(targets: dignity_respect, trust_distrust)*
  - [emotion] Were there moments when you felt dismissed, unheard, or disrespected by a member of the care team — what happened and how did it affect you?
    *(targets: dignity_respect, power_dynamics)*
  - [contrast] How did the care you received during birth compare to the care you had received throughout your pregnancy from the same or different providers?
    *(targets: continuity_of_care)*
  - [clarification] Did any provider take time to genuinely explain what was happening to you during labour — and how did that affect your trust and confidence?
    *(targets: trust_distrust, assurance)*
  - [structural] Were there patterns in how you were treated that you think might be related to your identity — your background, ethnicity, age, or circumstances?
    *(targets: structural_barriers, dignity_respect)*

---

### V2_BIRTH_Q05

**When you think about the physical environment of the place where you gave birth — the facilities, the equipment, the space — how did that environment affect your comfort, safety, and overall experience of birth?**

- Type: open_ended
- KBV: goals, latent_needs
- Thematic: goals_expectations, risks_barriers
- Latent: structural_barriers, dignity_respect, partner_role
- Evaluation: breadth=medium, depth=medium, innovation=medium
- EHR triggers: if_rural, if_high_risk

**Probes:**
  - [clarification] What specific aspects of the physical environment helped or hindered you during labour and delivery?
    *(targets: structural_barriers)*
  - [contrast] How did the birth environment compare to what you had envisioned or hoped for — and how did any difference affect you emotionally?
    *(targets: autonomy_vs_dependence, dignity_respect)*
  - [emotion] Did you feel the environment adequately supported the presence and involvement of your partner or support person?
    *(targets: partner_role)*
  - [motivation] Were there aspects of the birth environment that felt undignified, unsafe, or inadequate — and did you feel able to raise those concerns?
    *(targets: dignity_respect, power_dynamics)*
  - [structural] Did resource constraints — understaffing, equipment shortages, overcrowding — feel visible to you as a patient, and how did that affect your confidence in the system?
    *(targets: structural_barriers, trust_distrust)*

---

### V2_BIRTH_Q06

**When you think about any complications, unexpected events, or emergency interventions during your birth, how were these communicated to you, and how did you experience the shift from a planned to an unplanned situation?**

- Type: open_ended
- KBV: latent_needs, behaviours
- Thematic: emotional_experiences, hcp_interactions
- Latent: power_dynamics, autonomy_vs_dependence, trust_distrust
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [elaboration] Can you describe how you were informed about the complication or change in plan — what was said, by whom, and how?
    *(targets: power_dynamics, dignity_respect)*
  - [emotion] How did you feel in that moment — and what information or support would have helped you feel less frightened or more in control?
    *(targets: autonomy_vs_dependence, trust_distrust)*
  - [clarification] Were you given the opportunity to ask questions or was the pace of events such that you could not engage meaningfully in what was happening?
    *(targets: power_dynamics, autonomy_vs_dependence)*
  - [contrast] How did the complication or intervention affect your sense of your birth experience overall — and how have you made sense of it since?
    *(targets: identity_tensions)*
  - [structural] Did the system provide any follow-up or debrief after the complication — and if so, was it adequate to your needs?
    *(targets: continuity_of_care, structural_barriers)*

---

## Postpartum (8 questions)

### V2_POST_Q01

**When you think about your goals for recovery and support in the days and weeks after birth, what did you most want or need — and how well did the postnatal care you received address those needs?**

- Type: open_ended
- KBV: goals, latent_needs
- Thematic: goals_expectations, hcp_interactions
- Latent: continuity_of_care, dignity_respect, structural_barriers
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_high_risk, if_single_parent

**Probes:**
  - [contrast] What did 'good' postnatal care look like in your mind before you gave birth — and how did that compare to what you actually experienced?
    *(targets: continuity_of_care)*
  - [emotion] Were there needs you had in the early postpartum period that you felt unable or reluctant to articulate to your care providers?
    *(targets: latent_needs, power_dynamics)*
  - [clarification] How consistent was the support you received across different providers — midwives, health visitors, GPs — or did you experience fragmented care?
    *(targets: continuity_of_care, structural_barriers)*
  - [motivation] Were the postnatal checks and appointments focused on you as a person, or did they feel primarily focused on the baby?
    *(targets: dignity_respect, identity_tensions)*
  - [structural] Were there systemic gaps — limited home visits, short hospital stays, understaffed services — that left you without the support you needed?
    *(targets: structural_barriers, continuity_of_care)*

---

### V2_POST_Q02

**When you think about feeding your baby — whether through breastfeeding, formula, or a combination — what motivated your choices, and how supported did you feel in pursuing the approach you wanted?**

- Type: open_ended
- KBV: motivations, behaviours
- Thematic: decision_making, emotional_experiences
- Latent: autonomy_vs_dependence, dignity_respect, body_image_autonomy
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_single_parent

**Probes:**
  - [motivation] What drove your feeding choices — were they primarily personal, medical, cultural, or shaped by pressure from others?
    *(targets: autonomy_vs_dependence, intergenerational_patterns)*
  - [emotion] Did you feel judged or pressured — by healthcare providers, family, or social media — in relation to your feeding choices, and how did that affect you?
    *(targets: dignity_respect, power_dynamics)*
  - [clarification] Was the feeding support you received practical and effective — what worked well and what was missing?
    *(targets: trust_distrust)*
  - [contrast] How did your feeding experience compare to what you had planned or hoped for — and how did any gap affect your emotional wellbeing?
    *(targets: identity_tensions, body_image_autonomy)*
  - [structural] Were there structural factors — return to work timelines, lack of private facilities, cost of formula — that affected your feeding decisions?
    *(targets: structural_barriers)*

---

### V2_POST_Q03

**When you think about your emotional and mental health in the weeks and months after birth — the adjustment, the challenges, and the moments of wellbeing — what stands out most, and how well-supported did you feel?**

- Type: open_ended
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, support_sources
- Latent: identity_tensions, power_dynamics, continuity_of_care
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_single_parent, if_miscarriage_history, if_high_risk

**Probes:**
  - [elaboration] Can you describe a period when you felt particularly low, overwhelmed, or unlike yourself — what was happening and who or what helped?
    *(targets: identity_tensions, informal_care_networks)*
  - [emotion] Were there feelings or struggles you were reluctant to disclose to a healthcare provider — and what stopped you from speaking up?
    *(targets: power_dynamics, dignity_respect)*
  - [clarification] How well did your postnatal care proactively screen for or address your emotional and mental health — was it enough?
    *(targets: continuity_of_care, structural_barriers)*
  - [contrast] How did your experience of your own mental health compare to what you had been prepared for — by professionals, family, or your own research?
    *(targets: intergenerational_patterns, digital_information_seeking)*
  - [structural] Were there wider factors — financial pressures, relationship strain, housing, return to work — that affected your mental health in ways that formal care did not address?
    *(targets: structural_barriers, latent_needs)*

---

### V2_POST_Q04

**When you think about the shift in your identity and sense of self after becoming a parent, what tensions or changes were most significant — and how did those changes interact with your other roles, such as partner, professional, or daughter?**

- Type: open_ended
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, agency_disempowerment
- Latent: identity_tensions, intergenerational_patterns, body_image_autonomy
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_single_parent

**Probes:**
  - [elaboration] Can you describe a moment when you felt the tension between your new parental identity and another part of your identity most acutely?
    *(targets: identity_tensions)*
  - [motivation] How did the expectations of others — your partner, your family, your employer — shape how you experienced your new identity?
    *(targets: intergenerational_patterns, partner_role)*
  - [contrast] Did your return to work — or the anticipation of it — create particular tensions with your sense of yourself as a new parent?
    *(targets: identity_tensions, structural_barriers)*
  - [emotion] How did you feel about your body in the postpartum period — and how did that relate to your sense of identity and confidence?
    *(targets: body_image_autonomy, identity_tensions)*
  - [structural] Were there cultural or generational expectations about what kind of mother or parent you should be that shaped how you felt about yourself?
    *(targets: intergenerational_patterns, structural_barriers)*

---

### V2_POST_Q05

**When you think about the support you received from your partner in the postpartum period — in caring for the baby, supporting your recovery, and sharing emotional labour — how would you describe that experience, and what would have made it better?**

- Type: open_ended
- KBV: behaviours, latent_needs
- Thematic: informal_caregiver_interactions, support_sources
- Latent: partner_role, identity_tensions, structural_barriers
- Evaluation: breadth=medium, depth=high, innovation=medium
- EHR triggers: if_single_parent

**Probes:**
  - [contrast] How did the division of caregiving responsibilities compare to what you and your partner had discussed or assumed before the birth?
    *(targets: partner_role, identity_tensions)*
  - [emotion] Were there tensions or conflicts with your partner in the postpartum period that were difficult to navigate — what were they about?
    *(targets: partner_role, autonomy_vs_dependence)*
  - [clarification] How well did the healthcare system include and support your partner in the postnatal care process?
    *(targets: partner_role, continuity_of_care)*
  - [motivation] Did your partner's own emotional needs and adjustment get acknowledged by the care system, or was the focus entirely on you and the baby?
    *(targets: partner_role, latent_needs)*
  - [structural] Were there structural factors — paternity leave, workplace policies, financial pressures — that shaped how involved your partner was able to be?
    *(targets: structural_barriers, partner_role)*

---

### V2_POST_Q06

**When you think about the barriers you encountered in accessing postnatal support — whether physical, emotional, informational, or systemic — what were the most significant, and what impact did they have on your recovery and wellbeing?**

- Type: open_ended
- KBV: behaviours, latent_needs
- Thematic: risks_barriers, agency_disempowerment
- Latent: structural_barriers, autonomy_vs_dependence, power_dynamics
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_single_parent, if_language_barrier, if_rural, if_high_risk

**Probes:**
  - [elaboration] Can you describe a specific instance where you needed help but found it difficult to access — what happened and what got in the way?
    *(targets: structural_barriers)*
  - [clarification] Were there barriers that were invisible to your healthcare providers — things they did not ask about or seemed unaware of?
    *(targets: latent_needs, power_dynamics)*
  - [emotion] How did you feel when you encountered those barriers — did they lead to frustration, withdrawal, or finding alternative solutions?
    *(targets: autonomy_vs_dependence, trust_distrust)*
  - [contrast] Did the formal care system ever feel like a barrier in itself — through its processes, communication styles, or assumptions?
    *(targets: power_dynamics, dignity_respect)*
  - [structural] Were any of the barriers you faced specific to your personal circumstances — language, geography, socioeconomic situation, or family structure?
    *(targets: structural_barriers, informal_care_networks)*

---

### V2_POST_Q07

**When you think about how you used digital tools, apps, social media, or online communities after birth — to seek information, find support, or track your recovery — what role did those resources play, and what were their limits?**

- Type: open_ended
- KBV: behaviours, latent_needs
- Thematic: digital_information, support_sources
- Latent: digital_information_seeking, informal_care_networks, trust_distrust
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_language_barrier, if_rural

**Probes:**
  - [clarification] Which specific digital tools or communities did you find most valuable, and what made them useful in ways that formal care was not?
    *(targets: digital_information_seeking, informal_care_networks)*
  - [emotion] Were there times when information found online caused you anxiety or led you to question your care — how did you navigate that?
    *(targets: digital_information_seeking, trust_distrust)*
  - [contrast] How did your use of digital resources in the postpartum period compare to how you used them during pregnancy — did your needs change?
    *(targets: digital_information_seeking)*
  - [motivation] Were there things you searched for or questions you asked in online spaces that you would not or could not ask a healthcare provider — why?
    *(targets: power_dynamics, latent_needs)*
  - [structural] Did digital access — or lack of it — create inequality in the support available to you compared to others in your network?
    *(targets: structural_barriers, digital_information_seeking)*

---

### V2_POST_Q08

**When you reflect on your entire maternity journey — from preconception through to the postpartum period — what do you wish had been done differently by the care system, and what single change would have made the greatest difference to your experience?**

- Type: open_ended
- KBV: goals, latent_needs
- Thematic: goals_expectations, risks_barriers
- Latent: continuity_of_care, dignity_respect, latent_needs
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_high_risk, if_single_parent, if_language_barrier, if_rural, if_miscarriage_history

**Probes:**
  - [elaboration] Can you describe the specific moment or phase where you felt most let down by the system — what was the gap and what would have helped?
    *(targets: continuity_of_care, structural_barriers)*
  - [contrast] Was there a particular person or interaction across your whole journey that you feel epitomised what good care should look like — what made them different?
    *(targets: dignity_respect, trust_distrust)*
  - [motivation] If you imagine a friend going through the same journey, what advice or warnings would you give them to help them navigate the system?
    *(targets: power_dynamics, autonomy_vs_dependence)*
  - [emotion] Looking back, were there needs you had that you did not even recognise at the time — things you only understand in retrospect?
    *(targets: latent_needs, identity_tensions)*
  - [structural] What systemic changes — not just individual interactions — do you believe would most improve the maternity care experience for people in circumstances similar to yours?
    *(targets: structural_barriers, dignity_respect)*

---

## Other (8 questions)

### ?

****

- Type: open_ended
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Who first raised the idea of trying to conceive, and how did those early conversations unfold?
  - Were there any points of tension or negotiation about timing, and how were those resolved?
  - Did you feel your own sense of readiness was given equal weight in the final decision?
  - How did your partner's position influence the timeline you ultimately pursued?

---

### ?

****

- Type: open_ended
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Were there aspects of your physical self that you felt proud of, anxious about, or uncertain about in relation to pregnancy?
  - Did concerns about your body shape, weight, or physical condition influence any decisions you made during this period?
  - Did you feel you had control over how your body was perceived or discussed by healthcare providers or those around you?
  - Were there barriers you faced that were connected to how you felt about your body's readiness for pregnancy?

---

### ?

****

- Type: open_ended
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Were there moments where you felt a healthcare professional spoke to you in a way that felt dismissive or condescending?
  - Did you ever feel that you needed to advocate strongly for yourself to be taken seriously, and what did that involve?
  - How consistent was the care or advice you received across different appointments or providers?
  - Was there a particular professional you trusted more than others, and what made that relationship different?

---

### ?

****

- Type: open_ended
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Did older female relatives, such as your mother or grandmother, share advice or stories that influenced how you thought about getting pregnant?
  - Were there patterns of experience in your family — such as difficulties conceiving or particular birth experiences — that you were aware of and factored into your thinking?
  - How did your partner contribute to these informal conversations, and did their input align with what others were telling you?
  - Were there people in your network whose advice you actively sought out versus those who offered it unsolicited, and how did you weigh those contributions?

---

### ?

****

- Type: open_ended
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Were there specific platforms, websites, or communities you returned to regularly, and what made them feel credible or useful?
  - Did you ever come across information online that contradicted what a healthcare professional had told you, and how did you navigate that?
  - Were there any practical obstacles — such as cost of apps, language barriers, or limited data access — that made it harder to find reliable information?
  - Did you feel that the digital information available reflected your own circumstances and background, or did it feel aimed at a different kind of person?

---

### ?

****

- Type: open_ended
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Can you describe a specific situation where you felt judged, overlooked, or not treated as a capable decision-maker regarding your reproductive health?
  - How did those experiences affect your confidence in seeking care or expressing your preferences?
  - Did you change your behaviour — such as avoiding certain appointments or conversations — as a result of feeling disrespected?
  - Looking back, what would have made you feel more in control and more respected during that time?

---

### ?

****

- Type: open_ended
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Did you have reliable and private access to a smartphone or computer throughout your pregnancy, and did that change at any point?
  - Were there apps, portals, or online resources recommended to you that you found difficult to use or that did not feel accessible?
  - If English was not your first language, did you find that most digital health information was available in a language you were comfortable with?
  - Did financial constraints or data costs ever limit how much you could use digital resources to support your pregnancy?

---

### ?

****

- Type: open_ended
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Were there moments when a healthcare provider dismissed or minimised a concern you raised about your body or a symptom you were experiencing, and how did that make you feel?
  - Did you feel that decisions about your care — such as around tests, interventions, or referrals — were being made without fully including you, and how did you respond to that?
  - Were there aspects of your daily life — such as housing, work demands, finances, transport, or neighbourhood environment — that created risks or difficulties during your pregnancy that were hard to address?
  - How did your relationship with your own body change during pregnancy, and were there ways in which that felt empowering or, alternatively, out of your control?

---

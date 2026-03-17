# Questionnaire Version 4: Expectation-Perception Gap

**Strategy:** SERVQUAL-inspired  
**Structure:** Paired questions: first what they expected, then what they experienced.  
**Register:** Structured, evaluative  
**Generated:** 2026-03-17T22:26:45.220999  
**Model:** anthropic/claude-sonnet-4-6  
**Total questions:** 35  

---

## Preconception (6 questions)

### V4_PREC_Q01

**Before you started trying to conceive, what did you expect the process of getting support or guidance from healthcare professionals to look like? And thinking back now, what did that support actually look like in reality?**

- Type: gap_pair
- KBV: goals, motivations
- Thematic: goals_expectations, hcp_interactions
- Latent: autonomy_vs_dependence, trust_distrust
- Evaluation: breadth=high, depth=medium, innovation=high

**Probes:**
  - [contrast] What was the biggest surprise — positive or negative — when you first engaged with a healthcare provider about trying to conceive?
    *(targets: power_dynamics, trust_distrust)*
  - [elaboration] Was there anything you felt you needed in that early stage that no one offered or even asked about?
    *(targets: latent_needs, autonomy_vs_dependence)*
  - [emotion] How did it feel when your expectations met — or didn't meet — what actually happened?
    *(targets: dignity_respect, trust_distrust)*

---

### V4_PREC_Q02

**Before trying to conceive, what did you expect your own emotional readiness to feel like? And how did your emotional state actually compare to those expectations once the process began?**

- Type: gap_pair
- KBV: motivations, latent_needs
- Thematic: emotional_experiences, support_sources
- Latent: identity_tensions, intergenerational_patterns
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_single_parent

**Probes:**
  - [structural] What was missing from the support available to you emotionally at this stage — from professionals, your partner, or your wider network?
    *(targets: informal_care_networks, partner_role)*
  - [motivation] Were there feelings or fears you had that you didn't feel able to share with anyone at the time? What stopped you?
    *(targets: identity_tensions, power_dynamics)*
  - [elaboration] Did your family background or how your own parents approached parenthood shape what you expected of yourself at this stage?
    *(targets: intergenerational_patterns, identity_tensions)*

---

### V4_PREC_Q03

**Before conception, what did you expect to find when you looked for information online or through apps about fertility and getting pregnant? And what did you actually find — was it what you needed?**

- Type: gap_pair
- KBV: behaviours, latent_needs
- Thematic: digital_information, risks_barriers
- Latent: digital_information_seeking, structural_barriers
- Evaluation: breadth=high, depth=medium, innovation=high
- EHR triggers: if_language_barrier

**Probes:**
  - [contrast] What was the biggest gap between what digital sources told you and what your healthcare provider told you?
    *(targets: digital_information_seeking, trust_distrust)*
  - [emotion] Were there things you found online that made you more anxious or confused rather than reassured? Can you describe one?
    *(targets: digital_information_seeking, autonomy_vs_dependence)*
  - [clarification] Did you feel the information you found online reflected people with circumstances similar to yours — your background, your situation, your concerns?
    *(targets: structural_barriers, dignity_respect)*

---

### V4_PREC_Q04

**If you had a pre-existing health condition before pregnancy, what did you expect the healthcare system to do to help you prepare? And what actually happened when you sought that help?**

- Type: gap_pair
- KBV: goals, behaviours
- Thematic: risks_barriers, hcp_interactions
- Latent: power_dynamics, continuity_of_care
- Evaluation: breadth=high, depth=high, innovation=medium
- EHR triggers: if_high_risk

**Probes:**
  - [structural] Did you feel you had to advocate strongly for yourself, or did the system proactively reach out to support you?
    *(targets: power_dynamics, autonomy_vs_dependence)*
  - [elaboration] What was missing from the care you received at this stage that would have made a real difference?
    *(targets: continuity_of_care, structural_barriers)*
  - [emotion] How did it feel to navigate your health condition alongside the desire to conceive?
    *(targets: identity_tensions, dignity_respect)*

---

### V4_PREC_Q05

**Before you conceived, what did you expect your partner's involvement in the preconception process to look like? And how did their actual involvement compare to what you'd imagined?**

- Type: gap_pair
- KBV: motivations, latent_needs
- Thematic: informal_caregiver_interactions, emotional_experiences
- Latent: partner_role, identity_tensions
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_single_parent

**Probes:**
  - [motivation] Were there moments where you felt the burden of preparation fell disproportionately on you? What drove that?
    *(targets: partner_role, identity_tensions)*
  - [clarification] Did your healthcare provider include your partner meaningfully in consultations, or was it primarily directed at you?
    *(targets: partner_role, power_dynamics)*
  - [contrast] What surprised you most about how your relationship dynamic shifted during this period?
    *(targets: partner_role, intergenerational_patterns)*

---

### V4_PREC_Q06

**If you experienced a previous pregnancy loss, what did you expect the healthcare system to offer you when you decided to try again? And what support was actually available to you?**

- Type: gap_pair
- KBV: goals, latent_needs
- Thematic: emotional_experiences, support_sources
- Latent: dignity_respect, continuity_of_care
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_miscarriage_history

**Probes:**
  - [emotion] Was there a point where you felt your previous loss was not being taken seriously enough in the context of your new pregnancy attempt?
    *(targets: dignity_respect, trust_distrust)*
  - [elaboration] What was the biggest thing missing from the care or information you received at this stage?
    *(targets: continuity_of_care, structural_barriers)*
  - [structural] Where did you turn for support that the formal healthcare system wasn't providing?
    *(targets: informal_care_networks, digital_information_seeking)*

---

## Pregnancy (7 questions)

### V4_PREG_Q01

**When you first found out you were pregnant, what did you expect your first antenatal appointments to be like — the environment, the people, the information you'd receive? And what were they actually like?**

- Type: gap_pair
- KBV: goals, behaviours
- Thematic: goals_expectations, hcp_interactions
- Latent: dignity_respect, power_dynamics
- Evaluation: breadth=high, depth=medium, innovation=medium

**Probes:**
  - [contrast] What was the biggest surprise — positive or negative — about those first appointments?
    *(targets: trust_distrust, dignity_respect)*
  - [emotion] Did you feel listened to in those early appointments, or did you feel processed? What created that feeling?
    *(targets: power_dynamics, dignity_respect)*
  - [structural] Was there anything about the physical environment or the way the service was set up that made it harder or easier for you to engage?
    *(targets: structural_barriers, continuity_of_care)*

---

### V4_PREG_Q02

**Before your screening tests and scans, what did you expect the process of understanding your results to be like — how information would be given, by whom, and in what way? And what was the reality?**

- Type: gap_pair
- KBV: behaviours, latent_needs
- Thematic: decision_making, hcp_interactions
- Latent: autonomy_vs_dependence, digital_information_seeking
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [clarification] Was there a gap between the amount of information you were given and the amount you felt you needed to make sense of your results?
    *(targets: autonomy_vs_dependence, power_dynamics)*
  - [motivation] Did you turn to other sources — apps, online forums, friends — to understand what you'd been told? What drove that?
    *(targets: digital_information_seeking, trust_distrust)*
  - [emotion] Were there moments during this process where you felt your values or wishes weren't being taken into account?
    *(targets: dignity_respect, autonomy_vs_dependence)*

---

### V4_PREG_Q03

**During your pregnancy, what did you expect in terms of having a consistent midwife or care provider who knew your history and situation? And what continuity of care did you actually experience?**

- Type: gap_pair
- KBV: goals, latent_needs
- Thematic: hcp_interactions, agency_disempowerment
- Latent: continuity_of_care, trust_distrust
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_high_risk, if_rural

**Probes:**
  - [elaboration] What was the impact — practically or emotionally — of seeing different providers at different appointments?
    *(targets: continuity_of_care, trust_distrust)*
  - [emotion] Were there times you had to repeat your history or concerns because they weren't carried forward? How did that feel?
    *(targets: dignity_respect, continuity_of_care)*
  - [contrast] Did the fragmentation of care — if you experienced it — affect how much you trusted the system overall?
    *(targets: trust_distrust, power_dynamics)*

---

### V4_PREG_Q04

**During pregnancy, what did you expect in terms of how your changing body would be discussed and examined by healthcare providers? And how did those interactions actually feel?**

- Type: gap_pair
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, hcp_interactions
- Latent: body_image_autonomy, dignity_respect
- Evaluation: breadth=medium, depth=high, innovation=high

**Probes:**
  - [elaboration] Were there any examinations or conversations about your body that left you feeling uncomfortable or unprepared? What happened?
    *(targets: body_image_autonomy, dignity_respect)*
  - [emotion] Did you ever feel that your body was being discussed as a clinical object rather than something that belonged to you?
    *(targets: body_image_autonomy, power_dynamics)*
  - [contrast] What was the biggest gap between how you wanted your physical changes to be acknowledged and how they were actually addressed?
    *(targets: dignity_respect, identity_tensions)*

---

### V4_PREG_Q05

**Before pregnancy, what did you expect the experience of managing a high-risk condition like gestational diabetes or pre-eclampsia to involve? If relevant, how did the reality of managing it differ from your expectations?**

- Type: gap_pair
- KBV: behaviours, goals
- Thematic: risks_barriers, decision_making
- Latent: trust_distrust, structural_barriers
- Evaluation: breadth=medium, depth=high, innovation=medium
- EHR triggers: if_high_risk, if_gestational_diabetes

**Probes:**
  - [structural] What was missing from the support offered — information, emotional acknowledgement, practical help?
    *(targets: structural_barriers, continuity_of_care)*
  - [emotion] Did the diagnosis change how you felt about yourself and your pregnancy? In what way?
    *(targets: identity_tensions, body_image_autonomy)*
  - [motivation] How did you decide what information to trust — from your care team versus what you found yourself?
    *(targets: trust_distrust, digital_information_seeking)*

---

### V4_PREG_Q06

**During pregnancy, what did you expect in terms of being able to access care promptly when you had a concern — whether urgent or not? And how responsive was the system when you needed it?**

- Type: gap_pair
- KBV: behaviours, latent_needs
- Thematic: risks_barriers, agency_disempowerment
- Latent: structural_barriers, power_dynamics
- Evaluation: breadth=high, depth=medium, innovation=high
- EHR triggers: if_rural, if_language_barrier

**Probes:**
  - [motivation] Were there times you delayed seeking help because of how difficult it was to access care, or because you worried about being judged for contacting services?
    *(targets: structural_barriers, power_dynamics)*
  - [contrast] What was the biggest surprise when you did try to access urgent or unplanned support?
    *(targets: trust_distrust, structural_barriers)*
  - [structural] Did where you live, your working situation, or your language affect how easy it was to get the help you needed?
    *(targets: structural_barriers, informal_care_networks)*

---

### V4_PREG_Q07

**During pregnancy, what did you expect the role of your family, friends, or community to be in supporting you? And how did that informal support network actually show up — or not?**

- Type: gap_pair
- KBV: motivations, latent_needs
- Thematic: informal_caregiver_interactions, support_sources
- Latent: informal_care_networks, intergenerational_patterns
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_single_parent, if_language_barrier

**Probes:**
  - [contrast] Were there forms of support you received from family or community that you hadn't expected — or support you expected that didn't materialise?
    *(targets: informal_care_networks, intergenerational_patterns)*
  - [elaboration] Did family expectations or cultural traditions create any tension with the medical advice you were receiving?
    *(targets: intergenerational_patterns, autonomy_vs_dependence)*
  - [structural] Was there anything your informal network offered that formal healthcare services couldn't or didn't provide?
    *(targets: informal_care_networks, structural_barriers)*

---

## Birth (6 questions)

### V4_BIRTH_Q01

**Before labour, what did you expect creating and using a birth plan to be like — how it would be received by staff and how much it would guide your care? And what actually happened with your birth plan during labour?**

- Type: gap_pair
- KBV: goals, behaviours
- Thematic: decision_making, agency_disempowerment
- Latent: autonomy_vs_dependence, power_dynamics
- Evaluation: breadth=high, depth=high, innovation=high

**Probes:**
  - [emotion] Was there a moment during labour where your plan was set aside or overridden? What was that like?
    *(targets: autonomy_vs_dependence, power_dynamics)*
  - [clarification] Did you feel that staff read and respected your birth plan, or did it feel like a formality?
    *(targets: dignity_respect, trust_distrust)*
  - [contrast] What was missing from the process of preparing or using your birth plan that would have made you feel more in control?
    *(targets: autonomy_vs_dependence, continuity_of_care)*

---

### V4_BIRTH_Q02

**Before labour, what did you expect your pain management options to be — the range available, how they'd be offered, and how you'd be supported in deciding? And what was the reality of pain management during your labour?**

- Type: gap_pair
- KBV: goals, latent_needs
- Thematic: decision_making, emotional_experiences
- Latent: body_image_autonomy, dignity_respect
- Evaluation: breadth=high, depth=high, innovation=medium
- EHR triggers: if_high_risk

**Probes:**
  - [structural] Were there pain management options you wanted but weren't able to access? What got in the way?
    *(targets: structural_barriers, power_dynamics)*
  - [emotion] How did it feel when the pain experience differed from what you had expected or prepared for?
    *(targets: body_image_autonomy, identity_tensions)*
  - [clarification] Did you feel your pain was taken seriously and responded to promptly? What shaped that impression?
    *(targets: dignity_respect, trust_distrust)*

---

### V4_BIRTH_Q03

**When you arrived at the birth setting — whether hospital, birth centre, or home — what did you expect it to feel like in terms of safety, comfort, and how you'd be welcomed? And what was your actual experience of the environment when you arrived?**

- Type: gap_pair
- KBV: goals, motivations
- Thematic: emotional_experiences, goals_expectations
- Latent: trust_distrust, partner_role
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_rural

**Probes:**
  - [contrast] What was the biggest surprise about the physical environment or the immediate atmosphere when you arrived?
    *(targets: trust_distrust, structural_barriers)*
  - [elaboration] Were there aspects of the physical space that made you feel more or less safe during labour?
    *(targets: dignity_respect, body_image_autonomy)*
  - [structural] How was your partner or support person included — or not — in the environment and the care being provided?
    *(targets: partner_role, informal_care_networks)*

---

### V4_BIRTH_Q04

**If your birth involved an unexpected intervention or complication, what did you expect the process of being informed and involved in those decisions to look like? And how were those decisions actually made and communicated in the moment?**

- Type: gap_pair
- KBV: latent_needs, behaviours
- Thematic: agency_disempowerment, hcp_interactions
- Latent: autonomy_vs_dependence, dignity_respect
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [emotion] Did you feel you had genuine choice and sufficient information in those moments, or did decisions feel like they happened to you rather than with you?
    *(targets: autonomy_vs_dependence, power_dynamics)*
  - [elaboration] What was missing — in terms of explanation, tone, or timing — that would have helped you feel more respected in those moments?
    *(targets: dignity_respect, trust_distrust)*
  - [contrast] Looking back, did those decisions and the way they were handled affect your ability to trust healthcare providers afterward?
    *(targets: trust_distrust, continuity_of_care)*

---

### V4_BIRTH_Q05

**During labour, what did you expect the midwife or doctor present to provide in terms of emotional support and personal attention — not just clinical care? And what did you actually experience from the staff who were with you?**

- Type: gap_pair
- KBV: latent_needs, goals
- Thematic: hcp_interactions, emotional_experiences
- Latent: dignity_respect, continuity_of_care
- Evaluation: breadth=high, depth=high, innovation=medium

**Probes:**
  - [elaboration] Was there a specific moment when you felt truly seen and supported — or a moment when you felt very alone? Can you describe it?
    *(targets: dignity_respect, trust_distrust)*
  - [structural] Did the level of staffing or continuity of who was with you affect the quality of that emotional support?
    *(targets: continuity_of_care, structural_barriers)*
  - [emotion] How did it feel when the person providing your care changed partway through labour?
    *(targets: continuity_of_care, power_dynamics)*

---

### V4_BIRTH_Q06

**Before birth, what did you expect the immediate period after your baby was born to be like — skin-to-skin contact, who would be present, what would be done? And what actually happened in those first moments after delivery?**

- Type: gap_pair
- KBV: goals, latent_needs
- Thematic: emotional_experiences, agency_disempowerment
- Latent: identity_tensions, autonomy_vs_dependence
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [emotion] Was there anything that happened — or didn't happen — in those first moments that still stays with you? What was it?
    *(targets: dignity_respect, identity_tensions)*
  - [contrast] Did clinical priorities override your personal wishes in those moments? How was that handled?
    *(targets: autonomy_vs_dependence, power_dynamics)*
  - [clarification] Was your partner or support person included in the way you had hoped in those immediate post-birth moments?
    *(targets: partner_role, informal_care_networks)*

---

## Postpartum (8 questions)

### V4_POST_Q01

**Before giving birth, what did you expect your physical recovery to look and feel like in the weeks after? And how did the reality of your physical recovery compare to those expectations?**

- Type: gap_pair
- KBV: goals, behaviours
- Thematic: goals_expectations, support_sources
- Latent: body_image_autonomy, continuity_of_care
- Evaluation: breadth=high, depth=medium, innovation=medium

**Probes:**
  - [contrast] Was there a physical aspect of recovery that no one had prepared you for, or that surprised you significantly?
    *(targets: body_image_autonomy, structural_barriers)*
  - [structural] Did you feel that postnatal care adequately attended to your physical recovery, or did you feel discharged before you were truly ready?
    *(targets: continuity_of_care, power_dynamics)*
  - [elaboration] Where did you turn for information or support about your physical recovery when you needed it?
    *(targets: informal_care_networks, digital_information_seeking)*

---

### V4_POST_Q02

**Before your baby arrived, what did you expect feeding — breastfeeding or formula feeding — to be like in terms of ease, support, and how you'd feel about it? And what was the reality of feeding in the early weeks?**

- Type: gap_pair
- KBV: behaviours, latent_needs
- Thematic: emotional_experiences, decision_making
- Latent: identity_tensions, dignity_respect
- Evaluation: breadth=high, depth=high, innovation=high

**Probes:**
  - [clarification] Was there a gap between the kind of feeding support you were offered and the kind of support you actually needed?
    *(targets: dignity_respect, structural_barriers)*
  - [emotion] Did you feel judged — by professionals, family, or others — for your feeding choices or struggles? How did that affect you?
    *(targets: identity_tensions, power_dynamics)*
  - [motivation] Did you turn to online communities or apps for feeding support? What made those more or less helpful than formal sources?
    *(targets: digital_information_seeking, informal_care_networks)*

---

### V4_POST_Q03

**Before your baby arrived, what did you expect your emotional and mental health to be like in the postpartum period? And what was your actual emotional experience in the weeks and months after birth?**

- Type: gap_pair
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, risks_barriers
- Latent: identity_tensions, structural_barriers
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_single_parent

**Probes:**
  - [emotion] Was there a gap between what you were feeling and what you felt you were 'allowed' to feel — by professionals, family, or yourself?
    *(targets: identity_tensions, power_dynamics)*
  - [contrast] Were you ever screened or asked about your mental health postnatally? How was that handled — did it feel meaningful or routine?
    *(targets: dignity_respect, trust_distrust)*
  - [structural] Were there barriers — practical, cultural, or relational — that stopped you from seeking support when you were struggling emotionally?
    *(targets: structural_barriers, intergenerational_patterns)*

---

### V4_POST_Q04

**Before becoming a parent, what did you expect your sense of identity to feel like after your baby arrived? And how has your sense of who you are actually shifted since then?**

- Type: gap_pair
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, agency_disempowerment
- Latent: identity_tensions, intergenerational_patterns
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_single_parent

**Probes:**
  - [elaboration] Were there parts of your previous identity — professional, social, personal — that felt harder to hold onto than you expected?
    *(targets: identity_tensions, intergenerational_patterns)*
  - [contrast] Did the healthcare system — or anyone involved in your care — acknowledge this identity transition, or did it feel invisible?
    *(targets: dignity_respect, power_dynamics)*
  - [emotion] What surprised you most about who you became in those first months of parenthood?
    *(targets: identity_tensions, autonomy_vs_dependence)*

---

### V4_POST_Q05

**After birth, what did you expect the postnatal check-ups and follow-up care from your midwife or GP to provide? And what did that post-birth care actually look like in practice?**

- Type: gap_pair
- KBV: goals, latent_needs
- Thematic: hcp_interactions, support_sources
- Latent: continuity_of_care, structural_barriers
- Evaluation: breadth=high, depth=high, innovation=medium
- EHR triggers: if_rural, if_high_risk

**Probes:**
  - [clarification] Were there concerns you raised at postnatal appointments that you felt were not taken seriously or properly followed up?
    *(targets: power_dynamics, trust_distrust)*
  - [contrast] Did postnatal care feel like a continuation of a relationship with someone who knew you, or like starting over with strangers?
    *(targets: continuity_of_care, dignity_respect)*
  - [elaboration] What was missing from postnatal follow-up that would have made the most difference to you in those weeks?
    *(targets: structural_barriers, continuity_of_care)*

---

### V4_POST_Q06

**If you returned to work after your baby was born, what did you expect that transition to be like — practically and emotionally? And what did returning to work actually feel like?**

- Type: gap_pair
- KBV: behaviours, motivations
- Thematic: risks_barriers, emotional_experiences
- Latent: identity_tensions, structural_barriers
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_single_parent

**Probes:**
  - [structural] Were there practical aspects of returning to work — feeding, childcare, your own health — that were harder to manage than you expected?
    *(targets: structural_barriers, identity_tensions)*
  - [contrast] Did your employer, the healthcare system, or any formal service help you navigate that transition — or was it left entirely to you?
    *(targets: structural_barriers, autonomy_vs_dependence)*
  - [emotion] How did this transition affect your sense of yourself as a parent and as a professional?
    *(targets: identity_tensions, partner_role)*

---

### V4_POST_Q07

**After your baby arrived, what did you expect your relationship with your partner to be like in terms of sharing caregiving, managing the relationship, and supporting each other? And what has that relationship dynamic actually looked like?**

- Type: gap_pair
- KBV: latent_needs, motivations
- Thematic: informal_caregiver_interactions, emotional_experiences
- Latent: partner_role, identity_tensions
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_single_parent

**Probes:**
  - [contrast] What was the biggest surprise about how your partnership functioned after the baby arrived?
    *(targets: partner_role, identity_tensions)*
  - [structural] Were there ways the healthcare system either supported or overlooked your partner's wellbeing and role in the early postpartum period?
    *(targets: partner_role, structural_barriers)*
  - [elaboration] Did the division of caregiving responsibilities match what you had agreed or hoped for before birth? What changed?
    *(targets: partner_role, intergenerational_patterns)*

---

### V4_POST_Q08

**Looking across your entire maternity journey — from trying to conceive through to where you are now — what did you expect the overall experience of maternity care to deliver? And reflecting on the whole journey, what was the most significant gap between what you expected and what you received?**

- Type: gap_pair
- KBV: goals, latent_needs
- Thematic: goals_expectations, agency_disempowerment
- Latent: dignity_respect, structural_barriers
- Evaluation: breadth=high, depth=high, innovation=high

**Probes:**
  - [structural] If you could change one thing about how the maternity care system is designed — not just what individual providers do, but how the system itself works — what would it be?
    *(targets: structural_barriers, power_dynamics)*
  - [contrast] Was there a single moment across the whole journey where you felt most respected and cared for as a whole person? And a moment where you felt least so?
    *(targets: dignity_respect, continuity_of_care)*
  - [elaboration] What would you tell someone at the very start of this journey about what to expect and what to watch out for?
    *(targets: trust_distrust, autonomy_vs_dependence)*

---

## Other (8 questions)

### ?

****

- Type: 
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Were there moments when a doctor, partner, or family member's opinion overrode yours — even when you hadn't asked for their input?
  - Did any advice or expectation come from older relatives — a mother, mother-in-law, or grandmother — that shaped what you thought you should do?
  - When you think about who held the most influence over your reproductive decisions at that time, who comes to mind first, and how did that feel?
  - Was there anything you wanted to ask or challenge but felt you couldn't? What stopped you?

---

### ?

****

- Type: 
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Were there specific decisions — such as timing, fertility testing, or lifestyle changes — where you felt pressure to align with your partner's preferences over your own?
  - Did you ever feel your body or its readiness was being discussed as a shared project rather than something that belonged to you?
  - How did you negotiate disagreements, and whose view tended to prevail in those moments?
  - If you could go back, what boundaries would you have wanted to set more clearly?

---

### ?

****

- Type: 
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Were you given unsolicited comments about your weight, diet, or physical appearance? How did those comments land?
  - Did you feel that your body was being evaluated against a norm or ideal that was never explicitly stated?
  - Did concerns about how you might be perceived physically ever stop you from seeking care or asking questions?
  - How did those experiences affect your confidence in pursuing pregnancy or engaging with healthcare more broadly?

---

### ?

****

- Type: 
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Which informal sources — people or communities — did you turn to first, before or instead of a healthcare provider?
  - Were the perspectives you received from informal networks ever in tension with medical advice? How did you navigate that?
  - Did community or cultural expectations about fertility shape the kind of support you felt you could ask for or accept?
  - Were there forms of informal support you needed but couldn't access — and if so, what filled that gap, if anything?

---

### ?

****

- Type: 
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Were there appointments or decisions where you felt your input was genuinely sought, versus times when you felt you were simply being informed of a plan?
  - How did your partner's presence — or absence — in appointments change the dynamic of who was listened to?
  - Did your confidence in your own judgment grow or diminish over the course of your pregnancy?
  - Were there clinical decisions you agreed to but later wished you had questioned or refused?

---

### ?

****

- Type: 
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Was there a moment when your trust in a provider was broken — something they said, missed, or failed to explain?
  - Did you find yourself withholding information from your care team because you were uncertain how they would respond?
  - How did continuity of care — seeing the same midwife or doctor repeatedly — affect your trust?
  - Were there differences in how much you trusted different types of professionals — for example, consultants versus community midwives?

---

### ?

****

- Type: 
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Were there appointments, scans, or care moments where your partner's absence left you feeling isolated or unsupported?
  - Did healthcare providers direct information or explanations toward your partner instead of you — and how did that feel?
  - Were there ways your partner tried to advocate for you that were helpful, and ways that inadvertently undermined your voice?
  - How did your care team engage your partner — did they treat them as part of the care relationship or as an observer?

---

### ?

****

- Type: 
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Did you ever go online specifically because you felt you couldn't get enough information from your care provider — what were you looking for that you hadn't received?
  - Were the websites, apps, or forums you used easy to access and navigate given your circumstances — for example, your language, literacy, internet access, or disability?
  - How did you decide whether to trust a digital source? Were there signals that made you more or less confident in the information?
  - Did anything you read online cause you unnecessary worry, or lead you to question clinical advice you had been given — and how did you resolve that tension?
  - Were there parts of your experience — your identity, culture, health condition, or family structure — that were simply absent from the digital content you found?

---

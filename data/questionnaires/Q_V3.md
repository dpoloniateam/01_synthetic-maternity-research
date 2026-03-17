# Questionnaire Version 3: Scenario-Based / Critical Incident

**Strategy:** scenario  
**Structure:** Questions built around specific scenarios and critical moments.  
**Register:** Empathetic, situational  
**Generated:** 2026-03-17T22:23:16.203034  
**Model:** anthropic/claude-sonnet-4-6  
**Total questions:** 34  

---

## Preconception (6 questions)

### V3_PREC_Q01

**Imagine you've just decided with your partner — or on your own — that you'd like to start trying for a baby. Walk me through what that moment felt like and what your very first steps were.**

- Type: scenario
- KBV: goals, motivations
- Thematic: goals_expectations, emotional_experiences
- Latent: autonomy_vs_dependence, intergenerational_patterns
- Evaluation: breadth=high, depth=medium, innovation=medium

**Probes:**
  - [motivation] You mentioned taking those first steps — what made you choose that particular action rather than something else, like speaking to a doctor first or doing your own research online?
    *(targets: autonomy_vs_dependence, digital_information_seeking)*
  - [elaboration] How did the people closest to you — your partner, family, friends — respond when you shared this decision, or did you keep it private for a while? What influenced that choice?
    *(targets: informal_care_networks, partner_role)*
  - [structural] Was there anything about how your own mother or older female relatives had experienced becoming a parent that shaped how you were feeling in that moment?
    *(targets: intergenerational_patterns, identity_tensions)*

---

### V3_PREC_Q02

**Imagine you've booked a preconception appointment with your GP and you're sitting in the waiting room. What's going through your mind as you wait, and what are you hoping will happen in that consultation?**

- Type: scenario
- KBV: goals, behaviours
- Thematic: hcp_interactions, goals_expectations
- Latent: power_dynamics, structural_barriers
- Evaluation: breadth=high, depth=high, innovation=medium
- EHR triggers: if_high_risk

**Probes:**
  - [contrast] When you imagined how that appointment would go, how did you picture the GP responding to you — and how did reality compare, if you've had that experience?
    *(targets: trust_distrust, power_dynamics)*
  - [emotion] Were there things you wanted to raise in that appointment but felt unsure about bringing up? What held you back?
    *(targets: power_dynamics, dignity_respect)*
  - [structural] Did practical things like getting time off work, transport, or cost play any part in how you approached or prepared for that appointment?
    *(targets: structural_barriers)*

---

### V3_PREC_Q03

**Imagine you've been trying to conceive for several months without success. A close friend suggests you try a fertility app she found helpful. How do you react to that suggestion, and what do you do next?**

- Type: scenario
- KBV: behaviours, latent_needs
- Thematic: digital_information, support_sources
- Latent: digital_information_seeking, informal_care_networks
- Evaluation: breadth=medium, depth=high, innovation=high

**Probes:**
  - [motivation] What would make you trust or distrust the information you find in a fertility app compared to what a healthcare professional might tell you?
    *(targets: trust_distrust, digital_information_seeking)*
  - [emotion] How did tracking your cycle or fertility — whether through an app or another method — change how you felt about your body during this period?
    *(targets: body_image_autonomy, autonomy_vs_dependence)*
  - [elaboration] Were there online communities, forums, or social media groups you turned to? What did you find there that you couldn't find elsewhere?
    *(targets: informal_care_networks, digital_information_seeking)*

---

### V3_PREC_Q04

**Imagine you've just had a difficult conversation with your partner about whether you're both truly ready to have a child — financially, emotionally, practically. What does 'being ready' actually mean to you, and who or what helped you form that picture?**

- Type: scenario
- KBV: motivations, goals
- Thematic: goals_expectations, emotional_experiences
- Latent: identity_tensions, partner_role
- Evaluation: breadth=medium, depth=high, innovation=medium
- EHR triggers: if_single_parent

**Probes:**
  - [clarification] When you think about the financial side of readiness, were there specific worries — like maternity leave, childcare costs, housing — that felt most pressing? Where did those concerns come from?
    *(targets: structural_barriers, identity_tensions)*
  - [elaboration] Did you and your partner agree on what readiness looked like, or were there tensions between your different visions? How did you navigate that?
    *(targets: partner_role, identity_tensions)*
  - [structural] How much did your family's expectations — or the cultural context you grew up in — shape your sense of when it was the 'right' time?
    *(targets: intergenerational_patterns, informal_care_networks)*

---

### V3_PREC_Q05

**Imagine you've experienced a previous pregnancy loss and are now considering trying again. You're sitting with that knowledge as you think about the future. What thoughts and feelings come up, and what would you need from a healthcare team to feel supported going forward?**

- Type: scenario
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, support_sources
- Latent: trust_distrust, dignity_respect
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_miscarriage_history

**Probes:**
  - [emotion] When you imagine going back into the healthcare system after loss, what do you most fear about those interactions — and what would make them feel safer?
    *(targets: trust_distrust, dignity_respect)*
  - [contrast] Was there anything a healthcare professional said or did — either after the loss or now — that felt particularly unhelpful or helpful? What made the difference?
    *(targets: dignity_respect, continuity_of_care)*
  - [elaboration] Outside of the healthcare system, where have you found understanding or support — whether from people in your life or online communities of people who've been through similar experiences?
    *(targets: informal_care_networks, digital_information_seeking)*

---

### V3_PREC_Q06

**Imagine you have a pre-existing health condition and you're wondering how it might affect a future pregnancy. You decide to look it up before speaking to anyone medical. What do you search for, and how does what you find make you feel?**

- Type: scenario
- KBV: behaviours, latent_needs
- Thematic: digital_information, risks_barriers
- Latent: digital_information_seeking, autonomy_vs_dependence
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [motivation] What sources did you find most credible — and what made you trust or distrust them? Were there gaps that left you more anxious rather than reassured?
    *(targets: digital_information_seeking, trust_distrust)*
  - [contrast] When you eventually spoke with a healthcare professional about your condition and pregnancy, how prepared did you feel — and did they acknowledge the research you'd already done?
    *(targets: power_dynamics, autonomy_vs_dependence)*
  - [emotion] Did your condition change the way you thought about your body and its ability to carry a pregnancy? How did you hold that uncertainty day to day?
    *(targets: body_image_autonomy, identity_tensions)*

---

## Pregnancy (7 questions)

### V3_PREG_Q01

**Imagine it's the morning after you've taken a positive pregnancy test. Describe that morning — where are you, who's with you, and what's the very first thing you do after seeing that result?**

- Type: scenario
- KBV: motivations, behaviours
- Thematic: emotional_experiences, goals_expectations
- Latent: identity_tensions, informal_care_networks
- Evaluation: breadth=high, depth=medium, innovation=medium

**Probes:**
  - [motivation] When you decided who to tell first — or whether to tell anyone at all — what was behind that decision? What felt safe or risky about sharing the news?
    *(targets: informal_care_networks, identity_tensions)*
  - [emotion] What was the mix of emotions you were navigating that morning — and were any of them ones you hadn't expected to feel?
    *(targets: identity_tensions, autonomy_vs_dependence)*
  - [clarification] When you thought about contacting a midwife or GP to register the pregnancy, what did you actually know about the process, and how did you find out what to do?
    *(targets: structural_barriers, digital_information_seeking)*

---

### V3_PREG_Q02

**Imagine you're at your 20-week anomaly scan. The sonographer goes quiet for a moment and says they need to take a closer look at something. What goes through your mind in that silence, and how do you respond in the room?**

- Type: scenario
- KBV: latent_needs, behaviours
- Thematic: hcp_interactions, emotional_experiences
- Latent: power_dynamics, trust_distrust
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [emotion] In that moment, how much did you feel like you could ask questions or speak up — or did something stop you? What shaped that?
    *(targets: power_dynamics, dignity_respect)*
  - [elaboration] After leaving the scan, where did you turn for information or support while waiting for more news? How helpful were those sources?
    *(targets: digital_information_seeking, informal_care_networks)*
  - [contrast] If you think about the way information was communicated to you during that scan — or in the days after — what would you have wanted to be different?
    *(targets: trust_distrust, continuity_of_care)*

---

### V3_PREG_Q03

**Imagine you've just been offered the option of a screening test for a chromosomal condition. The midwife explains the test briefly and asks if you'd like to go ahead. How does that conversation feel, and how do you make your decision?**

- Type: scenario
- KBV: behaviours, motivations
- Thematic: decision_making, hcp_interactions
- Latent: autonomy_vs_dependence, power_dynamics
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_high_risk, if_language_barrier

**Probes:**
  - [motivation] Did you feel you had enough time and information to make that decision freely — or did you sense any pressure, either to accept or decline?
    *(targets: autonomy_vs_dependence, power_dynamics)*
  - [elaboration] Who else, if anyone, did you consult before deciding — and what did those conversations add that the clinical information didn't?
    *(targets: informal_care_networks, intergenerational_patterns)*
  - [structural] Did your own values, beliefs, or prior experiences shape how you approached this decision in a way that the midwife may not have been aware of?
    *(targets: identity_tensions, dignity_respect)*

---

### V3_PREG_Q04

**Imagine you're 28 weeks pregnant and you receive a call from a midwife you've never met before, telling you about a result from your routine blood test. This is the third different midwife you've spoken to this pregnancy. How does that feel, and what does it mean for how you receive that information?**

- Type: scenario
- KBV: latent_needs, goals
- Thematic: hcp_interactions, agency_disempowerment
- Latent: continuity_of_care, trust_distrust
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_high_risk, if_rural

**Probes:**
  - [elaboration] Can you describe what it's been like to build a picture of your care across different midwives and appointments — has anything fallen through the cracks?
    *(targets: continuity_of_care, trust_distrust)*
  - [motivation] How does it affect the way you communicate when you're speaking with someone who doesn't know your history? Do you find yourself editing what you say?
    *(targets: power_dynamics, autonomy_vs_dependence)*
  - [contrast] What would consistent care from one midwife have meant to you during this pregnancy — practically and emotionally?
    *(targets: continuity_of_care, dignity_respect)*

---

### V3_PREG_Q05

**Imagine it's 2am and you're 32 weeks pregnant. You've noticed something that worries you — reduced fetal movements. You're not sure whether to call the hospital or wait until morning. Walk me through what you're thinking and what you do.**

- Type: scenario
- KBV: behaviours, latent_needs
- Thematic: risks_barriers, agency_disempowerment
- Latent: power_dynamics, trust_distrust
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_high_risk, if_rural, if_language_barrier

**Probes:**
  - [motivation] What made it hard to decide whether to call — was it uncertainty about whether your concern was 'serious enough,' worry about being dismissed, or something else entirely?
    *(targets: power_dynamics, trust_distrust)*
  - [elaboration] If you searched online or messaged anyone during that 2am window — what were you hoping to find, and what did you actually find?
    *(targets: digital_information_seeking, informal_care_networks)*
  - [contrast] When you did make contact — with the hospital, a midwife, or anyone else — how were you received? Did it affect your willingness to call again in a future moment of concern?
    *(targets: dignity_respect, trust_distrust)*

---

### V3_PREG_Q06

**Imagine you've been diagnosed with gestational diabetes midway through your pregnancy. Your midwife hands you a leaflet and refers you to a dietitian. Standing outside the clinic, leaflet in hand, what are you feeling and what do you do next?**

- Type: scenario
- KBV: behaviours, latent_needs
- Thematic: risks_barriers, hcp_interactions
- Latent: structural_barriers, body_image_autonomy
- Evaluation: breadth=high, depth=high, innovation=medium
- EHR triggers: if_gestational_diabetes, if_language_barrier

**Probes:**
  - [clarification] What questions did you have in that moment that the leaflet didn't answer — and where did you go to find those answers?
    *(targets: digital_information_seeking, structural_barriers)*
  - [emotion] How did the diagnosis change how you felt about your body and your pregnancy — and were those feelings acknowledged by your care team?
    *(targets: body_image_autonomy, dignity_respect)*
  - [structural] Were there practical barriers — time, cost, access, language — that made managing the diagnosis harder than it needed to be?
    *(targets: structural_barriers, autonomy_vs_dependence)*

---

### V3_PREG_Q07

**Imagine you're scrolling through a pregnancy forum late at night and you come across a thread full of birth horror stories. You can't stop reading. What's drawing you in, and what do you do with those feelings afterwards?**

- Type: scenario
- KBV: motivations, latent_needs
- Thematic: digital_information, emotional_experiences
- Latent: digital_information_seeking, trust_distrust
- Evaluation: breadth=medium, depth=high, innovation=high

**Probes:**
  - [motivation] After reading stories like that, did you find yourself raising your concerns with a midwife or doctor — or did you hold onto them quietly? What made you decide either way?
    *(targets: digital_information_seeking, power_dynamics)*
  - [contrast] How do you weigh information you find online against what your care team tells you — and are there moments when they conflict?
    *(targets: trust_distrust, autonomy_vs_dependence)*
  - [elaboration] Were there fears building during your pregnancy that you feel weren't really picked up or addressed in your antenatal appointments?
    *(targets: continuity_of_care, dignity_respect)*

---

## Birth (6 questions)

### V3_BIRTH_Q01

**Imagine you've written a birth plan and you arrive at the labour ward. The midwife who receives you glances at your plan briefly, sets it aside, and moves on to routine checks. How does that moment land for you?**

- Type: scenario
- KBV: goals, latent_needs
- Thematic: agency_disempowerment, hcp_interactions
- Latent: power_dynamics, autonomy_vs_dependence
- Evaluation: breadth=high, depth=high, innovation=high

**Probes:**
  - [elaboration] What had you put into that birth plan — and what had you hoped it would communicate about you, beyond the practical preferences?
    *(targets: autonomy_vs_dependence, identity_tensions)*
  - [emotion] In that moment, did you say anything — or did you let it go? What shaped your response?
    *(targets: power_dynamics, dignity_respect)*
  - [contrast] Looking back, how much of what you'd hoped for from your birth actually happened — and for the parts that didn't, how have you made sense of that?
    *(targets: autonomy_vs_dependence, trust_distrust)*

---

### V3_BIRTH_Q02

**Imagine you're in established labour and the pain is much more intense than you'd anticipated. A midwife suggests an epidural, but you had wanted to manage without one. What happens inside you in that moment, and how do you decide?**

- Type: scenario
- KBV: behaviours, motivations
- Thematic: decision_making, emotional_experiences
- Latent: autonomy_vs_dependence, body_image_autonomy
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [motivation] In that moment of intense pain, how clear-headed did you feel in making that decision — and do you feel you had what you needed to make a genuinely free choice?
    *(targets: autonomy_vs_dependence, power_dynamics)*
  - [clarification] Was your partner or birth companion able to support you in that moment — and did the staff include them in the conversation?
    *(targets: partner_role, dignity_respect)*
  - [contrast] Afterwards, how did you feel about the choice you made — or had made for you — regarding pain relief? Has that feeling changed over time?
    *(targets: body_image_autonomy, identity_tensions)*

---

### V3_BIRTH_Q03

**Imagine your labour has stalled and the obstetric team is recommending an emergency caesarean. Things start moving very quickly. Walk me through what that experience was like from the moment they told you.**

- Type: scenario
- KBV: latent_needs, behaviours
- Thematic: agency_disempowerment, hcp_interactions
- Latent: power_dynamics, dignity_respect
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [emotion] In that rapid sequence of events, did you ever feel that things were happening to your body without your full understanding or agreement? What stands out?
    *(targets: power_dynamics, dignity_respect)*
  - [elaboration] Was there a particular person — a midwife, doctor, your partner, or anyone else — who made you feel anchored in that situation? What did they do that helped?
    *(targets: continuity_of_care, partner_role)*
  - [structural] In the hours and days after, was there any space given to process what had happened — was anyone from the clinical team available to debrief with you?
    *(targets: continuity_of_care, trust_distrust)*

---

### V3_BIRTH_Q04

**Imagine your birth companion has been asked to wait outside the room for a clinical procedure. You're left alone with staff you've only just met. Describe what that moment feels like and what you most need in those minutes.**

- Type: scenario
- KBV: latent_needs, goals
- Thematic: emotional_experiences, informal_caregiver_interactions
- Latent: partner_role, dignity_respect
- Evaluation: breadth=medium, depth=high, innovation=medium
- EHR triggers: if_single_parent

**Probes:**
  - [contrast] In moments like that — without your companion present — how did the behaviour of the clinical staff either compensate for that absence or make it feel more acute?
    *(targets: dignity_respect, partner_role)*
  - [motivation] Were there things you wish you had been able to say or ask for in those moments but couldn't? What got in the way?
    *(targets: power_dynamics, autonomy_vs_dependence)*
  - [elaboration] How did your experience of the physical environment — the room, the equipment, the sound and light — affect how safe or unsafe you felt?
    *(targets: body_image_autonomy, structural_barriers)*

---

### V3_BIRTH_Q05

**Imagine it's the immediate aftermath of birth — your baby has arrived, and the room begins to shift from the intensity of labour. Walk me through the next thirty minutes as you experienced them, or as you imagine them.**

- Type: scenario
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, hcp_interactions
- Latent: dignity_respect, identity_tensions
- Evaluation: breadth=medium, depth=high, innovation=high

**Probes:**
  - [emotion] Were there moments in those first minutes where you felt the clinical team's priorities and your own were pulling in different directions? What happened?
    *(targets: power_dynamics, autonomy_vs_dependence)*
  - [clarification] How were your preferences about skin-to-skin contact, cord clamping, or first feeding handled — and to what extent did those preferences feel respected in the moment?
    *(targets: dignity_respect, continuity_of_care)*
  - [elaboration] Looking back, is there something that happened — or didn't happen — in those first thirty minutes that you still think about? What is it, and why does it stay with you?
    *(targets: identity_tensions, trust_distrust)*

---

### V3_BIRTH_Q06

**Imagine you had a particular fear about childbirth — something that had been building throughout your pregnancy. Now picture yourself facing that specific fear during labour. What was it like, and what — if anything — helped?**

- Type: scenario
- KBV: latent_needs, motivations
- Thematic: emotional_experiences, support_sources
- Latent: trust_distrust, intergenerational_patterns
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_miscarriage_history, if_high_risk

**Probes:**
  - [motivation] Had you ever been able to share that fear openly with anyone in your care team during pregnancy? If so, how was it received — and if not, what stopped you?
    *(targets: power_dynamics, trust_distrust)*
  - [structural] Did that fear connect to anything in your personal history — previous experiences of hospitals, medical procedures, or experiences of loss?
    *(targets: intergenerational_patterns, identity_tensions)*
  - [emotion] In the moment of facing that fear, what did you most need from the people around you — and did you get it?
    *(targets: dignity_respect, informal_care_networks)*

---

## Postpartum (7 questions)

### V3_POST_Q01

**Imagine it's your first night at home with your newborn after being discharged from hospital. You're exhausted, possibly in pain, and your baby won't settle. What does that night feel like, and who — if anyone — is there with you?**

- Type: scenario
- KBV: latent_needs, goals
- Thematic: risks_barriers, support_sources
- Latent: continuity_of_care, structural_barriers
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_single_parent, if_rural

**Probes:**
  - [contrast] When you were discharged, how prepared did you feel for what was actually waiting for you at home — and what was the biggest gap between what you expected and what you found?
    *(targets: structural_barriers, continuity_of_care)*
  - [elaboration] If you needed help that night — whether practical, emotional, or clinical — how easy was it to access? What did you do?
    *(targets: informal_care_networks, digital_information_seeking)*
  - [structural] Was there anything about the physical realities of your own recovery that night that you hadn't been prepared for — things that hadn't been mentioned before discharge?
    *(targets: structural_barriers, dignity_respect)*

---

### V3_POST_Q02

**Imagine you're trying to breastfeed for the first time and it isn't going as you hoped. A midwife visits and watches you try, then offers advice. Describe what that moment feels like, physically and emotionally.**

- Type: scenario
- KBV: behaviours, latent_needs
- Thematic: hcp_interactions, agency_disempowerment
- Latent: body_image_autonomy, dignity_respect
- Evaluation: breadth=high, depth=high, innovation=high

**Probes:**
  - [emotion] How did it feel to have someone observing something so intimate and physically difficult? Did you feel supported, observed, or judged — or some mix of all three?
    *(targets: dignity_respect, body_image_autonomy)*
  - [contrast] Did the advice you received feel consistent across different midwives or healthcare contacts — or were you given conflicting information? How did that affect you?
    *(targets: continuity_of_care, trust_distrust)*
  - [structural] When or if you considered formula feeding, what kinds of reactions — from professionals, family, or social media — did you encounter, and how did those affect your choices?
    *(targets: power_dynamics, informal_care_networks)*

---

### V3_POST_Q03

**Imagine it's six weeks after birth. You're sitting in the GP surgery for your postnatal check. The appointment lasts ten minutes. What do you hope will happen in that room — and what does happen?**

- Type: scenario
- KBV: goals, latent_needs
- Thematic: hcp_interactions, emotional_experiences
- Latent: identity_tensions, continuity_of_care
- Evaluation: breadth=high, depth=high, innovation=high
- EHR triggers: if_high_risk

**Probes:**
  - [elaboration] Were there things you wanted to raise — about your mental health, your relationship, your body, or your sense of yourself — that the appointment didn't create space for?
    *(targets: power_dynamics, identity_tensions)*
  - [contrast] How did the GP's focus compare to your own priorities in that appointment — and did you leave feeling that your whole experience of the past six weeks had been acknowledged?
    *(targets: dignity_respect, continuity_of_care)*
  - [emotion] If you were feeling low, anxious, or not like yourself in those weeks, how easy was it to say that out loud in that appointment — and what made it easy or hard?
    *(targets: trust_distrust, structural_barriers)*

---

### V3_POST_Q04

**Imagine you're lying awake at 3am with your baby, and you find yourself feeling a deep sadness or flatness that you can't quite name. You pick up your phone. What do you do with it?**

- Type: scenario
- KBV: latent_needs, behaviours
- Thematic: emotional_experiences, digital_information
- Latent: digital_information_seeking, identity_tensions
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_single_parent, if_language_barrier

**Probes:**
  - [motivation] What were you looking for in those late-night searches or scrolling — reassurance, connection, information, or something else?
    *(targets: digital_information_seeking, informal_care_networks)*
  - [elaboration] Was there a point at which you recognised what you were feeling might be more than 'baby blues' — and when you did, who was the first person you told or the first place you sought help?
    *(targets: trust_distrust, structural_barriers)*
  - [structural] Were there cultural, family, or personal beliefs about how new mothers 'should' feel that made it harder to acknowledge or name what you were going through?
    *(targets: intergenerational_patterns, identity_tensions)*

---

### V3_POST_Q05

**Imagine your partner has returned to work and you're alone with your baby for the first full day. Describe that day — not just the logistics, but the emotional texture of it.**

- Type: scenario
- KBV: motivations, latent_needs
- Thematic: emotional_experiences, support_sources
- Latent: identity_tensions, partner_role
- Evaluation: breadth=medium, depth=high, innovation=medium
- EHR triggers: if_single_parent

**Probes:**
  - [contrast] How had you and your partner prepared for this transition — and were those preparations adequate? What hadn't you anticipated?
    *(targets: partner_role, structural_barriers)*
  - [emotion] What was the relationship between your identity before becoming a mother and how you experienced yourself in that day at home? Did they feel connected or very different?
    *(targets: identity_tensions, body_image_autonomy)*
  - [elaboration] Who or what held you together on that day — whether a person, a community, an app, or something else entirely?
    *(targets: informal_care_networks, digital_information_seeking)*

---

### V3_POST_Q06

**Imagine you're approaching your return to work. You're thinking about how you'll explain to your employer what the last few months have involved, and whether your job will still fit who you are now. What's that internal conversation like?**

- Type: scenario
- KBV: goals, motivations
- Thematic: goals_expectations, emotional_experiences
- Latent: identity_tensions, structural_barriers
- Evaluation: breadth=high, depth=medium, innovation=medium
- EHR triggers: if_single_parent

**Probes:**
  - [elaboration] Has becoming a parent changed how you see your professional identity — your ambitions, your sense of what matters, or how you want your days structured? In what ways?
    *(targets: identity_tensions, structural_barriers)*
  - [structural] Were there conversations you needed to have with your employer, partner, or childcare providers to make return to work possible — and what was difficult or unspoken in those conversations?
    *(targets: structural_barriers, partner_role)*
  - [contrast] How did the experience of maternity care — the quality, the continuity, the way you were treated — affect your sense of confidence and readiness for this transition?
    *(targets: continuity_of_care, autonomy_vs_dependence)*

---

### V3_POST_Q07

**Imagine you're at a new parents' group for the first time, surrounded by other people who have also recently given birth. You notice yourself comparing your experience to theirs. What comes up for you in that room?**

- Type: scenario
- KBV: behaviours, latent_needs
- Thematic: informal_caregiver_interactions, support_sources
- Latent: informal_care_networks, identity_tensions
- Evaluation: breadth=medium, depth=high, innovation=high
- EHR triggers: if_language_barrier, if_rural

**Probes:**
  - [emotion] Were there aspects of your birth or postnatal experience that felt hard to talk about in that room — things that felt 'outside the norm' of what others were sharing?
    *(targets: dignity_respect, identity_tensions)*
  - [clarification] How did the group — whether in person, online, or both — function as a source of practical information, emotional support, or something else? What was most valuable?
    *(targets: informal_care_networks, digital_information_seeking)*
  - [structural] Did the demographics or backgrounds of people in the group shape your experience of it — did you feel you fully belonged, or were there differences that created distance?
    *(targets: structural_barriers, intergenerational_patterns)*

---

## Other (8 questions)

### ?

****

- Type: scenario
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - In that moment, how much of the decision would feel truly yours versus shaped by others' expectations?
  - If your partner's preference conflicted with yours, how do you think that tension would be resolved — and who would feel most heard?
  - When you picture the way decisions like this were made in your family growing up, does that pattern feel like something you would want to repeat, resist, or change?
  - Are there any unspoken power dynamics — financial, cultural, or relational — that would make it harder to act on your own preference?

---

### ?

****

- Type: scenario
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Would those comments change how you feel about your body and its readiness or capability to carry a pregnancy?
  - How much ownership would you feel over decisions about your own body in that moment — empowered, scrutinised, or something else?
  - Would you feel comfortable pushing back on or questioning that advice, or would the clinical authority of the provider make that difficult?
  - How might that interaction influence whether you sought further preconception care at all?

---

### ?

****

- Type: scenario
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - What information or understanding would feel most lost in that handover — clinical details, or something more personal?
  - How would you go about re-establishing trust with a new provider at such a significant moment?
  - Would that disruption make you more likely to seek information or reassurance from other sources — family, friends, or online?
  - Has anything like this happened to you before in your healthcare experience, and if so, how did it affect you?

---

### ?

****

- Type: scenario
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Whose informal guidance would you genuinely value, and what would make their input feel helpful rather than overwhelming?
  - How would your partner factor into managing or filtering that input — would you tackle it together or separately?
  - Are there pieces of advice rooted in older generational experiences that you would feel you had to politely set aside?
  - How would you balance honouring those relationships while still making decisions that feel right for you and your partner?

---

### ?

****

- Type: scenario
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - Which of those barriers — cost, language, literacy, or connectivity — would feel most significant for someone in your situation?
  - Would those barriers push you towards less reliable sources, or would you find another route to the information you needed?
  - How would not having access to good information at this stage affect your confidence going into preconception conversations with a healthcare provider?
  - Do you think these kinds of access barriers affect everyone equally, or are some groups of women much more disadvantaged — and why?

---

### ?

****

- Type: scenario
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - What kind of support from your partner would have felt most meaningful in that moment — practical help, emotional validation, or just being listened to?
  - If your partner was not able to provide that support, how would it affect the way you faced the uncertainty ahead?
  - Would you feel comfortable telling your partner directly what you needed, or would that feel difficult — and why?
  - Who else in your life, or what other resource, would step in as a support source if your partner was not fully present in that way?

---

### ?

****

- Type: scenario
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - In that moment, how much agency — real influence over what happens to your body — would you feel you had?
  - Would you feel able to interrupt, ask questions, or push back in that consultation, or would the power dynamic make that feel impossible?
  - How would being sidelined in favour of your partner affect your sense of dignity and your trust in the care system going forward?
  - What would a consultation look like that genuinely centred your autonomy and treated you as the primary decision-maker about your own reproductive health?

---

### ?

****

- Type: scenario
- KBV: 
- Thematic: 
- Latent: 

**Probes:**
  - What would trust in your care team look like at a moment like that — what would they need to do or say for you to feel genuinely supported?
  - How would being spoken over or around by the midwife — even if unintentionally — affect your sense of dignity and your confidence in the system?
  - Would that experience change the goals you had set for your pregnancy care — for example, making you more guarded, more assertive, or more likely to seek a second opinion?
  - How would your partner's role in that moment feel to you — helpful and protective, or inadvertently reinforcing the dynamic that left you feeling sidelined?

---

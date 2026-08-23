# Provenance of Table A (the guide printed in Appendix A) — v03, with the rationale (decision point D9, accepted D9c)

| | |
|---|---|
| **Version** | v03 — 23 August 2026, accepted as a reconstruction by the authors; v02 — 23 August 2026, 01:41 WEST. Supersedes v01 (23 Aug 2026, 00:48 WEST), whose mapping was made against the set-cover guide only and whose rationale fields were empty |
| **Chronology established from the record** | The twelve-question guide is the research team's selection from V4_R1, made by manual review in April–May 2026: the audit note of 23 April 2026 already records the JPIM manuscript reproducing "the final V4_R1 guide (12 questions with probes)", and the annex of 9 May 2026 (§A1.1) lists the twelve stems of Table A word for word, each with its original V4 probes and the probes added in the refinement cycle. The deterministic set-cover procedure (`01_Source_Code/refinement/consolidate_guide.py`, 2 June 2026) was constructed afterwards "to supply the mathematical part the consolidation step previously lacked"; its output (`GUIDE_A_12Q.json`) coincides with the team's selection on five items and selects seven others. The manuscript's account of the consolidation as the set-cover procedure, and the ordering "set-cover first, team revision after" in the first revision of 23 August, are corrected in rev3.1 (§4.4, Table 7, §4.7) |
| **Status of the rationale** | The April–May records contain the selection but no per-item reasoning. The rationale below was reconstructed on 23 August 2026 from three sources that do exist: the criteria the manuscript states (§3.2.5: relevance, clarity, distinctiveness, overlap, redundancy, intrusiveness, broader applicability, sequencing, tone; §4.4), the refinement plan's diagnoses of 19 March 2026 (seven flagged dimensions, all five preconception items at the bottom of the richness ranking), and the items' own design targets and measured richness. **The authors reviewed it on 23 August 2026 and accept it as a reconstruction of their reasoning; it is not a contemporaneous record, and the package says so.** |

## 1. Mapping of the twelve Table A items to their V4_R1 sources

Richness is the mean composite richness of the item (stem and probes) in the non-empty V4 main-phase sessions (restated analysis, corpus A); targets are the item's design targets in `Q_V4_R1.json`; the set-cover column is the disposition in `consolidation_provenance.json`.

| Table A | Source item | Phase | Design targets | Richness, V4 non-empty | Set-cover | Relationship to the source |
|---|---|---|---|---|---|---|
| Q1 | `V4_PREC_Q03` | preconception | digital_information_seeking, structural_barriers | 4.03 (n=12) | dropped | extended — adds "and information (online or through apps)" and "Was it what you needed?" |
| Q2 | `V4_PREC_Q05` | preconception | partner_role, identity_tensions | 4.24 (n=9) | dropped | near-verbatim |
| Q3 | `V4_PREG_Q01` | pregnancy | dignity_respect, power_dynamics | 4.11 (n=41) | kept (set-cover Q4) | reworded — "what was the biggest surprise about…" |
| Q4 | `V4_PREG_Q04` | pregnancy | body_image_autonomy, dignity_respect | 4.36 (n=46) | dropped | near-verbatim |
| Q5 | `V4_PREG_Q02` | pregnancy | autonomy_vs_dependence, digital_information_seeking | 4.04 (n=43) | kept (set-cover Q5) | identical |
| Q6 | `V4_PREG_Q03` | pregnancy | continuity_of_care, trust_distrust | 4.00 (n=41) | kept (set-cover Q6) | reworded — adds "And how responsive was the system when you needed it?" |
| Q7 | `V4_BIRTH_Q01` | birth | autonomy_vs_dependence, power_dynamics | 4.19 (n=24) | merged into V4_BIRTH_Q04 | reworded — birth plan as the organising frame of labour |
| Q8 | `V4_BIRTH_Q03` | birth | trust_distrust, partner_role | 3.73 (n=27) | dropped | near-verbatim |
| Q9 | `V4_POST_Q01` | postpartum | body_image_autonomy, continuity_of_care | 4.18 (n=18) | dropped | identical |
| Q10 | `V4_POST_Q03` | postpartum | identity_tensions, structural_barriers | 4.19 (n=22) | kept (set-cover Q11) | identical |
| Q11 | `V4_POST_Q06` | postpartum | identity_tensions, structural_barriers | 4.02 (n=24) | dropped | generalised — from "If you returned to work…" to "what significantly changed in your life", with return to work and the partner relationship as probes |
| Q12 | `V4_POST_Q08` | postpartum | dignity_respect, structural_barriers | 4.27 (n=25) | kept (set-cover Q12) | reworded |

Five items are shared with the set-cover (Q3, Q5, Q6, Q10, Q12: two identical, three reworded); seven are V4_R1 items the set-cover did not select (Q1, Q2, Q4, Q7, Q8, Q9, Q11: six dropped, one merged). None of the twelve was newly written. The team's distribution across phases is 2 / 4 / 2 / 4 (preconception / pregnancy / birth / postpartum); the set-cover imposed 3 / 3 / 3 / 3.

## 2. The set-cover items the team did not select, and where their content went

| Set-cover item | Phase | Design targets | Richness, V4 non-empty | In Table A |
|---|---|---|---|---|
| `V4_PREC_Q01` | preconception | autonomy_vs_dependence, trust_distrust | 4.24 (n=9) | absorbed in Q1 (support and guidance before conception) |
| `V4_PREC_Q04` | preconception | power_dynamics, continuity_of_care | 3.96 (n=9) | not included — conditional on a pre-existing condition |
| `V4_PREC_Q06` | preconception | dignity_respect, continuity_of_care | 4.00 (n=11) | not included — conditional on a previous pregnancy loss; judged potentially intrusive as a main question |
| `V4_BIRTH_Q02` | birth | body_image_autonomy, dignity_respect | 4.05 (n=30) | pain management survives as a probe of Q7 |
| `V4_BIRTH_Q04` | birth | autonomy_vs_dependence, dignity_respect | 4.18 (n=28) | not included as a main question — conditional on an unexpected intervention; the override of the plan is a probe of Q7 |
| `V4_BIRTH_Q06` | birth | identity_tensions, autonomy_vs_dependence | 4.25 (n=28) | the immediate post-birth moments survive as a probe of Q8 |
| `V4_POST_Q02` | postpartum | identity_tensions, dignity_respect | 4.23 (n=23) | feeding survives as a probe of Q11 |

## 3. Rationale, item by item (reconstructed; to be confirmed by the authors)

The team's rule, as far as the record and the instrument texts allow it to be stated, was: one question per salient episode of the journey, applicable to every respondent, targeting at least one of the seven dimensions flagged by the diagnostics or one of the six persona-encoded dimensions, with conditional episodes (pre-existing condition, previous loss, unexpected intervention) and narrower topics (pain management, feeding, the first post-birth moments, return to work) carried as probes; overlapping items merged; probes that led or pre-loaded a valence removed; concrete matters before emotionally demanding ones. Measured richness was not the deciding criterion: where richness and coverage conflicted, coverage won — which is why the set-cover, weighting richness at 0.40, selects differently.

- **Q1 ← `V4_PREC_Q03` (extended).** The preconception episode every respondent has is seeking support, guidance and information; `PREC_Q03` (information-seeking; targets digital information seeking and structural barriers — the first a flagged dimension) was chosen over the set-cover's `PREC_Q01` (support from professionals), whose content it absorbs, and the stem was extended with "and information (online or through apps)" so that the flagged dimension is named in the question rather than left to a probe. The three refinement probes retained under Q1 carry trust (double-checking a provider) and intergenerational patterns (the picture of parenthood formed by watching someone close).
- **Q2 ← `V4_PREC_Q05` (near-verbatim).** The only preconception item addressing partner role and the family (both flagged dimensions: partner role at 0%, intergenerational patterns at 1.7%), with a probe on whether the provider included the partner. Kept although the set-cover dropped it for lower richness: without it the guide would not ask about the partner before birth at all.
- **Q3 ← `V4_PREG_Q01` (reworded).** Shared with the set-cover. The stem was turned into an open "what was the biggest surprise" frame and the probe "did you feel listened to, or did you feel processed?" was cut to "Did you feel listened to in those early appointments?", removing a pre-loaded valence (dignity and respect, power dynamics).
- **Q4 ← `V4_PREG_Q04` (near-verbatim).** Body image autonomy and dignity (both flagged, both at ≤ 3.3% in the diagnostics) in the setting where the literature locates them — examinations and conversations about the body (Hodgkinson et al., 2014; Bohren et al., 2015). The set-cover covered body image through `BIRTH_Q02` (pain management); the team kept the pregnancy-phase item, which applies to every respondent and had been strengthened with three refinement probes, and dropped the annex probe "discussed as a clinical object rather than something that belonged to you" as leading.
- **Q5 ← `V4_PREG_Q02` (identical).** Shared with the set-cover; screening results, information given by whom and how (autonomy; digital information seeking through the probe on other sources).
- **Q6 ← `V4_PREG_Q03` (reworded).** Shared with the set-cover; continuity of care and trust (both flagged). The clause "And how responsive was the system when you needed it?" and the probes on repeating one's history, on place of residence, work and language, and on what the informal network provided, extend the item to structural barriers and informal care networks.
- **Q7 ← `V4_BIRTH_Q01` (reworded; merged by the set-cover into `BIRTH_Q04`).** The birth plan is the frame every respondent can speak to about labour (autonomy versus dependence, power dynamics, dignity); the set-cover's picks `BIRTH_Q02` (pain management) and `BIRTH_Q04` (unexpected intervention) are carried as probes — "was there a moment … your plan and pain management options were set aside or overridden?" — because one is a sub-topic and the other is conditional.
- **Q8 ← `V4_BIRTH_Q03` (near-verbatim).** Arrival at the birth setting: safety, comfort and welcome — trust and distrust and partner role by design target (both flagged), dignity and respect through the probes on feeling seen and on the partner's inclusion. The lowest-richness birth item in the non-empty corpus, kept for what it targets rather than for its yield; the set-cover's `BIRTH_Q06` (the immediate post-birth moments) survives as its last probe.
- **Q9 ← `V4_POST_Q01` (identical).** Physical recovery — body image autonomy and continuity of care by design target (both flagged), with probes on postnatal follow-up, concerns not taken seriously, and seeing the same midwife or doctor (continuity, trust). Dropped by the set-cover in favour of `POST_Q02` (feeding), which the team carried as a probe of Q11.
- **Q10 ← `V4_POST_Q03` (identical).** Shared with the set-cover; postnatal emotional and mental health, with probes on screening and on practical, cultural or relational barriers to seeking support.
- **Q11 ← `V4_POST_Q06` (generalised).** `POST_Q06` asked about returning to work, a conditional episode; the team generalised it to what changed in the respondent's life, personally and professionally, and moved return to work, feeding and the partner relationship — division of caregiving, what was agreed before birth — into the probes (partner role, identity tensions, emotional labour).
- **Q12 ← `V4_POST_Q08` (reworded).** Shared with the set-cover; the whole-journey reflection on the gap between expectation and delivery, with two forward-looking probes (what to warn a friend about; what to change in the system's design), placed last.

Sequencing and the introductory section follow the manuscript (§4.4): concrete matters first within each phase, emotionally demanding ones later; Q12 closes the interview.

## 4. Probe count

The annex of 9 May carried every original V4 probe and every refinement probe under its question; Table A carries 43 probe questions (Table 6), the remainder having been removed as redundant, leading, or intrusive. Two examples of removal are given under Q3 and Q4 above.

## 5. Version history

| Version | Date | Content |
|---|---|---|
| v01 | 23 Aug 2026, 00:48 WEST | Mapping against the set-cover guide only; rationale fields empty |
| v02 | 23 August 2026, 01:41 WEST | Chronology established from the record; mapping to the V4_R1 sources; reconstructed rationale for each item and for the set-cover items not selected; to be confirmed by the authors |
| v03 | 23 Aug 2026 | Status line updated: the reconstructed rationale accepted by the authors as a reconstruction (decision point D9c) |

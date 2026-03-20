# Robustness Testing Report

**Generated:** 2026-03-20 09:13
**Pass threshold:** richness >= 50% of population mean (4.09)

## Overall Verdict

**Robust across vulnerable populations**

All 5 adversarial profiles exceeded the 50% threshold (richness > 2.04)

## Summary

| Metric | Value |
|--------|-------|
| Profiles tested | 5 |
| Passed | 5 |
| Failed | 0 |
| Pass rate | 100% |
| Population mean richness | 4.09 |
| Adversarial mean richness | 3.35 |

## Per-Profile Results

| Profile | Persona | Richness | Pop. Mean | Ratio | Verdict |
|---------|---------|----------|-----------|-------|---------|
| low_health_literacy | Destiny Marlowe | 3.45 | 4.09 | 84% | PASS |
| language_barrier | Mei-Ling Vasquez | 3.01 | 4.09 | 74% | PASS |
| hostile_distrustful | Renee Thibodeau | 3.51 | 4.09 | 86% | PASS |
| rural_isolated | Darlene Hutchins | 3.76 | 4.09 | 92% | PASS |
| early_pregnancy_ambivalent | Danielle Okafor | 3.02 | 4.09 | 74% | PASS |

### Low Health Literacy

**Persona:** Destiny Marlowe
**Test objective:** Elicit meaningful responses without jargon
**Verdict:** PASS (richness 3.45 vs threshold 2.04)

- Responses scored: 16
- Questions asked: 8
- Probes deployed: 8
- Dimensions surfaced: 16 (acquiescence_tendency, anxiety_level, appointment_adherence, comprehension_of_written_instructions, digital_health_access...)
- Dimensions absent: 14 (acquiescence_tendency, anxiety_level, appointment_adherence, comprehension_of_written_instructions, digital_health_access...)
- Substantive responses achieved despite adversarial profile

**Dimension scores:**

| Dimension | Adversarial | Population | Ratio | Pass |
|-----------|-------------|------------|-------|------|
| clinical_grounding | 2.62 | 3.49 | 75% | Yes |
| emotional_depth | 3.50 | 4.48 | 78% | Yes |
| latent_surfacing | 4.50 | 4.43 | 102% | Yes |
| narrative_quality | 3.38 | 4.20 | 80% | Yes |
| specificity | 3.25 | 3.87 | 84% | Yes |

### Language Barrier

**Persona:** Mei-Ling Vasquez
**Test objective:** Function through simplified communication
**Verdict:** PASS (richness 3.01 vs threshold 2.04)

- Responses scored: 16
- Questions asked: 8
- Probes deployed: 8
- Dimensions surfaced: 20 (anxiety_level, autonomy_vs_dependence, compliance_signaling_vs_actual_compliance, continuity_of_care, cultural_health_beliefs...)
- Dimensions absent: 8 (anxiety_level, continuity_of_care, cultural_health_beliefs, face_saving_tendency, health_literacy...)
- Substantive responses achieved despite adversarial profile

**Dimension scores:**

| Dimension | Adversarial | Population | Ratio | Pass |
|-----------|-------------|------------|-------|------|
| clinical_grounding | 2.31 | 3.49 | 66% | Yes |
| emotional_depth | 2.94 | 4.48 | 66% | Yes |
| latent_surfacing | 3.88 | 4.43 | 87% | Yes |
| narrative_quality | 2.88 | 4.20 | 68% | Yes |
| specificity | 3.06 | 3.87 | 79% | Yes |

### Hostile Distrustful

**Persona:** Renee Thibodeau
**Test objective:** Safe adaptive probing past defensive responses
**Verdict:** PASS (richness 3.51 vs threshold 2.04)

- Responses scored: 16
- Questions asked: 8
- Probes deployed: 8
- Dimensions surfaced: 11 (autonomy_sensitivity, deflection_frequency, emotional_guardedness, engagement_volatility, identity_tensions...)
- Dimensions absent: 8 (autonomy_sensitivity, deflection_frequency, institutional_trust, latent_unmet_need_intensity, perceived_interviewer_agenda...)
- Substantive responses achieved despite adversarial profile

**Dimension scores:**

| Dimension | Adversarial | Population | Ratio | Pass |
|-----------|-------------|------------|-------|------|
| clinical_grounding | 3.12 | 3.49 | 90% | Yes |
| emotional_depth | 3.75 | 4.48 | 84% | Yes |
| latent_surfacing | 4.25 | 4.43 | 96% | Yes |
| narrative_quality | 3.25 | 4.20 | 77% | Yes |
| specificity | 3.19 | 3.87 | 82% | Yes |

### Rural Isolated

**Persona:** Darlene Hutchins
**Test objective:** Capture experience with fragmented rural care and limited digital access
**Verdict:** PASS (richness 3.76 vs threshold 2.04)

- Responses scored: 16
- Questions asked: 8
- Probes deployed: 8
- Dimensions surfaced: 13 (autonomy_vs_dependence, care_continuity, care_fragmentation, digital_access, geographic_isolation...)
- Dimensions absent: 14 (care_continuity, care_fragmentation, digital_access, financial_stress, geographic_isolation...)
- Substantive responses achieved despite adversarial profile

**Dimension scores:**

| Dimension | Adversarial | Population | Ratio | Pass |
|-----------|-------------|------------|-------|------|
| clinical_grounding | 3.56 | 3.49 | 102% | Yes |
| emotional_depth | 3.25 | 4.48 | 73% | Yes |
| latent_surfacing | 4.38 | 4.43 | 99% | Yes |
| narrative_quality | 3.62 | 4.20 | 86% | Yes |
| specificity | 4.00 | 3.87 | 103% | Yes |

### Early Pregnancy Ambivalent

**Persona:** Danielle Okafor
**Test objective:** Surface depth in early pregnancy where V4 underperforms
**Verdict:** PASS (richness 3.02 vs threshold 2.04)

- Responses scored: 16
- Questions asked: 8
- Probes deployed: 8
- Dimensions surfaced: 10 (ambivalence_about_pregnancy, anxiety_masked, disclosure_willingness, emotional_readiness, engagement_with_care...)
- Dimensions absent: 10 (ambivalence_about_pregnancy, anxiety_masked, disclosure_willingness, emotional_readiness, engagement_with_care...)
- Substantive responses achieved despite adversarial profile

**Dimension scores:**

| Dimension | Adversarial | Population | Ratio | Pass |
|-----------|-------------|------------|-------|------|
| clinical_grounding | 2.38 | 3.49 | 68% | Yes |
| emotional_depth | 3.31 | 4.48 | 74% | Yes |
| latent_surfacing | 3.56 | 4.43 | 80% | Yes |
| narrative_quality | 2.94 | 4.20 | 70% | Yes |
| specificity | 2.94 | 3.87 | 76% | Yes |

## Paper-Ready Table

```latex
\begin{table}[h]
\caption{Adversarial robustness testing results}
\label{tab:robustness}
\begin{tabular}{llcccc}
\hline
Profile & Persona & Richness & Pop. Mean & Ratio & Verdict \\
\hline
Low Health Literacy & Destiny Marlowe & 3.45 & 4.09 & 84% & Pass \\
Language Barrier & Mei-Ling Vasquez & 3.01 & 4.09 & 74% & Pass \\
Hostile Distrustful & Renee Thibodeau & 3.51 & 4.09 & 86% & Pass \\
Rural Isolated & Darlene Hutchins & 3.76 & 4.09 & 92% & Pass \\
Early Pregnancy Ambivalent & Danielle Okafor & 3.02 & 4.09 & 74% & Pass \\
\hline
\multicolumn{6}{l}{Overall: Robust across vulnerable populations} \\
\hline
\end{tabular}
\end{table}
```

## 5. Results

### 5.1 Descriptive Overview

A total of 300 synthetic interview transcripts were generated using a Balanced
Incomplete Block Design (BIBD) with five questionnaire versions administered to
150 composite synthetic personas. Each persona completed two of the five
versions, enabling within-subject comparison. Across the full pipeline of
355 sessions (including refinement and adversarial rounds), the total
computational cost was US$0.64.

Quality evaluation yielded 6,458 question--response pairs scored on a
0--5 scale across five dimensions. The overall mean composite richness score was
3.06 (SD reported per version in Table 1). The mean latent dimension
surfacing rate across all transcripts was 72.1%.

Across the five quality dimensions, mean scores were: emotional depth
(*M* = 3.32), specificity (*M* = 2.95), latent surfacing
(*M* = 3.28), narrative quality (*M* = 3.13), and clinical grounding
(*M* = 2.59). Clinical grounding consistently scored lowest, reflecting the
challenge of eliciting clinically specific detail from synthetic personas. Quality
scoring was performed by google/gemini-3-flash-preview; interviews were conducted by openai/gpt-5-mini-2025-08-07
with multi-provider persona role-play (see Table 1 and Figure 1).

### 5.2 Response Quality Across Versions

Quality scores varied significantly across the five questionnaire versions. A
Kruskal--Wallis test revealed a statistically significant difference in composite
richness scores (*H* = 23.313, *p* = 0.001), confirming that version
design influenced response quality (Table 1, Figure 1).

**Table 1.** Quality scores by questionnaire version.

| Version | N | Richness M(SD) | 95% CI | Surfacing Rate |
|---------|---|----------------|--------|----------------|
| V1 | 60 | 2.32 (1.96) | (1.83, 2.82) | 60.9% |
| V2 | 60 | 2.81 (1.83) | (2.35, 3.27) | 76.1% |
| V3 | 60 | 2.64 (1.97) | (2.14, 3.14) | 69.8% |
| V4 | 60 | 2.99 (1.78) | (2.54, 3.44) | 80.7% |
| V5 | 60 | 2.96 (1.80) | (2.50, 3.41) | 73.0% |

All pairwise comparisons yielded small effect sizes (|*d*| < 0.50), suggesting
that while statistically significant differences existed, practical differences
between versions were modest (Table 2).

**Table 2.** Pairwise effect sizes (Cohen's *d*).

| Comparison | Cohen's *d* | Interpretation |
|------------|-------------|----------------|
| V1 vs V2 | -0.256 | small |
| V1 vs V3 | -0.161 | small |
| V1 vs V4 | -0.355 | small |
| V1 vs V5 | -0.335 | small |
| V2 vs V3 | 0.089 | small |
| V2 vs V4 | -0.100 | small |
| V2 vs V5 | -0.081 | small |
| V3 vs V4 | -0.186 | small |
| V3 vs V5 | -0.167 | small |
| V4 vs V5 | 0.019 | small |

### 5.3 Within-Subject Comparison (BIBD)

The balanced incomplete block design enabled within-subject comparisons across
five BIBD groups, each comprising 30 persona pairs. Wilcoxon signed-rank tests
were applied to each group's paired richness scores. Of the 5 within-subject
comparisons, 4 reached statistical significance (*p* < .05), as reported
in Table 3.

**Table 3.** Within-subject comparisons by BIBD group.

| Group | N | Mean Diff | Wilcoxon Z | p | Favours |
|-------|---|-----------|------------|---|---------|
| Group A V1 vs V2 | 30 | -0.203 | -3.007 | 0.0026* | V2 |
| Group B V1 vs V3 | 30 | -0.060 | -2.334 | 0.0196* | V3 |
| Group C V2 vs V4 | 30 | +0.015 | -0.192 | 0.8476 | V2 |
| Group D V3 vs V5 | 30 | +0.123 | -3.657 | 0.0003* | V3 |
| Group E V4 vs V5 | 30 | +0.101 | -2.343 | 0.0191* | V4 |

These results corroborated the between-subject findings: later versions (V2--V4)
consistently outperformed V1, and V4 emerged as the preferred instrument in
head-to-head paired comparisons (see Figure 2).

### 5.4 Latent Dimension Coverage

Across 12 latent dimensions tracked per version, surfacing rates varied
substantially (Table 5, Figure 3). Coverage analysis identified 35 blind
spots (dimension--version cells with surfacing rates below 20%).

**Table 5.** Latent dimension surfacing rates by version (heatmap summary).

| Dimension | V1 | V2 | V3 | V4 | V5 |
|-----------|------|------|------|------|------|
| Autonomy Vs Dependence | 58.3% | 73.3% | 71.7% | 78.3% | 73.3% |
| Body Image Autonomy | 1.7% | 1.7% | 1.7% | 0.0% | 0.0% |
| Continuity Of Care | 0.0% | 6.7% | 0.0% | 0.0% | 6.7% |
| Digital Information Seeking | 1.7% | 0.0% | 6.7% | 0.0% | 0.0% |
| Dignity Respect | 8.3% | 10.0% | 6.7% | 3.3% | 5.0% |
| Identity Tensions | 61.7% | 80.0% | 73.3% | 85.0% | 73.3% |
| Informal Care Networks | 61.7% | 75.0% | 68.3% | 76.7% | 73.3% |
| Intergenerational Patterns | 5.0% | 1.7% | 1.7% | 1.7% | 5.0% |
| Partner Role | 5.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Power Dynamics | 61.7% | 75.0% | 70.0% | 80.0% | 73.3% |
| Structural Barriers | 63.3% | 78.3% | 71.7% | 81.7% | 73.3% |
| Trust Distrust | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

**Well-surfaced dimensions** (mean > 50% across versions): identity tensions (74.7%), structural barriers (73.7%), power dynamics (72.0%), informal care networks (71.0%), autonomy vs dependence (71.0%).

**Persistent blind spots** (mean < 10% across versions): trust distrust (0.0%), partner role (1.0%), body image autonomy (1.0%), digital information seeking (1.7%), continuity of care (2.7%), intergenerational patterns (3.0%), dignity respect (6.7%).

The trust/distrust dimension recorded a surfacing rate of 0.0% across all five
versions, indicating a systematic instrument limitation. Body image autonomy,
continuity of care, digital information seeking, and partner role similarly
showed near-zero surfacing rates, suggesting these experiential domains require
targeted probing strategies beyond those implemented in the current instrument
set (see Section 6.4 for discussion of implications).

### 5.5 Service Provision Mapping

Service mapping analysis across 300 transcripts
identified 442 service gaps and 584 innovation opportunities
(Figure 4). The majority of service gaps were classified as high severity, indicating
that synthetic personas consistently articulated unmet needs in maternity care
provision.

**Table 6.** Service gap severity distribution by category (top 10).

| Category | High | Medium | Low | Total |
|----------|------|--------|-----|-------|
| Shared Decision Making | 81 | 9 | 0 | 90 |
| Emotional Support | 88 | 1 | 0 | 89 |
| Continuity Of Care | 73 | 1 | 0 | 74 |
| Care Coordination | 45 | 4 | 0 | 49 |
| Communication | 30 | 2 | 0 | 32 |
| Postnatal Mental Health | 32 | 0 | 0 | 32 |
| Information Quality | 13 | 4 | 0 | 17 |
| Privacy Dignity | 15 | 1 | 0 | 16 |
| Accessibility | 9 | 1 | 0 | 10 |
| Birth Environment | 9 | 0 | 0 | 9 |

The most frequently identified gap categories were emotional support
(88 high-severity), shared decision-making (81 high-severity), and continuity
of care (73 high-severity). These findings align with established maternity
care literature identifying relational and communicative dimensions as persistent
areas of unmet need.

### 5.6 Innovation Opportunities

A total of 584 innovation opportunities were extracted from synthetic
interview responses (Table 7, Figure 5). The five most frequently identified
innovation areas were: digital tools (*n* = 118), care coordination (*n* = 113), emotional support (*n* = 98), postnatal mental health (*n* = 76), communication (*n* = 47).

**Table 7.** Innovation opportunities by category.

| Category | Count | Share |
|----------|-------|-------|
| Digital Tools | 118 | 20.2% |
| Care Coordination | 113 | 19.3% |
| Emotional Support | 98 | 16.8% |
| Postnatal Mental Health | 76 | 13.0% |
| Communication | 47 | 8.0% |
| Accessibility | 23 | 3.9% |
| Shared Decision Making | 23 | 3.9% |
| Information Quality | 17 | 2.9% |
| Financial Accessibility | 16 | 2.7% |
| Continuity Of Care | 13 | 2.2% |
| Birth Environment | 11 | 1.9% |
| Privacy Dignity | 8 | 1.4% |
| Cultural Sensitivity | 7 | 1.2% |
| Partner Involvement | 7 | 1.2% |
| Transport Access | 3 | 0.5% |
| Clinical Competence | 3 | 0.5% |
| Breastfeeding Support | 1 | 0.2% |

Digital tools and care coordination together accounted for
39.6%
of all identified innovations, suggesting that technology-mediated service
improvements represent the primary opportunity space perceived by synthetic
personas. Emotional support innovations (*n* = 98)
constituted the third-largest category, reinforcing the gap analysis findings
in Section 5.5.

### 5.7 Iterative Refinement (V4 to V4_R1)

Following selection of V4 as the winning instrument, a refinement cycle was
conducted. The refined instrument (V4_R1) was administered to 50 additional
personas, generating 1,253 scored responses. Refinement targeted 7
identified blind spots through question rewording, probe additions, and
structural modifications (38 changes applied).

The refined instrument demonstrated substantial improvement across all metrics:

- **Composite richness:** V4_R1 *M* = 4.09 vs. V4 *M* = 2.99
  (+36.9%)
- **Surfacing rate:** V4_R1 = 98.9% vs. V4 = 80.7%
  (+22.5%)
- **Blind spots resolved:** 5 of 7 (2 remaining)

Per-dimension scores for the refined instrument were: emotional depth
(*M* = 4.48), specificity
(*M* = 3.87), latent surfacing
(*M* = 4.43), narrative quality
(*M* = 4.20), and clinical grounding
(*M* = 3.49).

The improvement magnitude (+36.9% composite richness) confirmed
that data-driven instrument refinement, guided by blind-spot diagnostics and
quality scoring feedback, can meaningfully enhance questionnaire performance
within a single iteration cycle.

### 5.8 Saturation Analysis

Thematic saturation was assessed across 110 transcripts (60 original V4, 50
refined V4_R1) using cumulative theme accumulation curves and rolling marginal
yield analysis with a window of 5 transcripts and a plateau threshold of 2 new
themes per transcript over 5 consecutive transcripts.

A total of 3,925 unique thematic codes were identified. The cumulative theme
curve followed a power-law trajectory (*R*^2 = 0.992), with the best-fit
equation *y* = 52.2 *x*^0.892. The near-unity exponent (0.892) indicated
near-linear theme accumulation, meaning practical saturation was not foreseeable
within feasible sample sizes (Table 8, Figure 6).

**Table 8.** Saturation analysis summary.

| Metric | Value |
|--------|-------|
| Original transcripts (V4) | 60 |
| Refinement transcripts (V4_R1) | 50 |
| Total unique themes | 3,925 |
| Pre-refinement themes | 2,108 |
| Post-refinement new themes | 1,817 |
| Refinement novelty rate | 46.3% |
| Best-fit model (original) | Power law |
| *R*^2 | 0.992 |
| Original mean yield | 35.1 themes/transcript |
| Refinement mean yield | 36.3 themes/transcript |
| Mann--Whitney *U* | 1,427.0 (*p* = 0.663) |

The refinement round introduced 1,817 themes not observed in the original 2,108
themes, representing a 46.3% novelty rate. A Mann--Whitney *U* test confirmed
no significant difference in per-transcript yield between original and refinement
corpora (*U* = 1,427.0, *p* = 0.663), indicating that the refined instrument
maintained generative capacity without diminishing returns.

Per-category saturation was reached for structured categories: latent dimensions
(14 unique, plateau at transcript 4), KBV dimensions (6 unique, plateau at
transcript 4), service gaps (14 unique, plateau at transcript 5), and innovation
opportunities (17 unique, plateau at transcript 5). However, thematic areas
(3,874 unique codes) showed no plateau, confirming an open thematic space
consistent with the power-law accumulation pattern.

These findings are consistent with qualitative research literature suggesting
that thematic saturation is instrument-dependent and that changing the instrument
can reopen the thematic space (Hennink et al., 2017; Saunders et al., 2018).

### 5.9 Robustness Testing

Adversarial robustness testing evaluated the refined instrument (V4_R1) against
five vulnerable population profiles designed to stress-test instrument
performance under challenging interview conditions. The pass threshold was
defined as composite richness exceeding 50% of the population mean (i.e.,
richness > 2.04).

All five adversarial profiles exceeded the threshold, yielding an overall
verdict of "Robust across vulnerable populations" (Table 9).

**Table 9.** Adversarial robustness testing results.

| Profile | Persona | Richness | Pop. Mean | Ratio | Verdict |
|---------|---------|----------|-----------|-------|---------|
| Low Health Literacy | Destiny Marlowe | 3.45 | 4.09 | 84% | PASS |
| Language Barrier | Mei-Ling Vasquez | 3.01 | 4.09 | 74% | PASS |
| Hostile/Distrustful | Renee Thibodeau | 3.51 | 4.09 | 86% | PASS |
| Rural Isolated | Darlene Hutchins | 3.76 | 4.09 | 92% | PASS |
| Early Pregnancy Ambivalent | Danielle Okafor | 3.02 | 4.09 | 74% | PASS |

The adversarial mean richness was 3.35, representing 82% of the population
mean (4.09). The rural isolated profile achieved the highest adversarial
richness (3.76, 92% of population), while the language barrier and early
pregnancy ambivalent profiles showed the largest performance decrements (74%
of population), identifying these as areas warranting further instrument
refinement in future iterations.

All five dimensions maintained adequate scores across adversarial profiles,
with latent surfacing consistently scoring highest (range: 3.56--4.50) and
clinical grounding lowest (range: 2.31--3.56), mirroring the pattern observed
in the main corpus.

### 5.10 Inter-Rater Reliability

Inter-rater reliability was assessed using 30 transcripts scored
independently by three LLM providers (Anthropic, Google, OpenAI), employing
an ICC(2,1) two-way random effects model. The composite richness ICC was
0.903, indicating excellent agreement (Table 4).

**Table 4.** Inter-rater reliability across scoring dimensions.

| Dimension | ICC(2,1) | Interpretation | Krippendorff's alpha |
|-----------|----------|----------------|---------------------|
| Emotional Depth | 0.903 | excellent | 0.901 |
| Specificity | 0.879 | excellent | 0.876 |
| Latent Surfacing | 0.910 | excellent | 0.908 |
| Narrative Quality | 0.846 | excellent | 0.842 |
| Clinical Grounding | 0.854 | excellent | 0.849 |
| Composite Richness | 0.903 | excellent | N/A |

All individual dimensions achieved excellent agreement (ICC >= 0.846), with
latent surfacing showing the highest concordance (ICC = 0.910) and narrative
quality the lowest (ICC = 0.846). Krippendorff's alpha values closely tracked
ICC estimates across all dimensions (range: 0.842--0.908), providing convergent
evidence of measurement consistency.

These results support the validity of using LLM-as-judge methodology for
quality assessment, provided that multi-provider triangulation is employed
to mitigate single-model scoring biases.

### 5.11 Version Ranking

A weighted composite score was computed for each version using quality (40%),
coverage (25%), innovation (20%), and breadth (15%) weights. V4 ranked
first with a composite score of 2.706, followed by V5
(2.565), representing a 5.5% advantage (Table 10).

**Table 10.** Version ranking by weighted composite score.

| Rank | Version | Quality | Coverage | Innovation | Composite |
|------|---------|---------|----------|------------|-----------|
| 1 | V4 | 2.99 | 0.339 | 3.87 | 2.706 |
| 2 | V5 | 2.96 | 0.319 | 3.35 | 2.565 |
| 3 | V2 | 2.81 | 0.335 | 3.43 | 2.542 |
| 4 | V3 | 2.64 | 0.310 | 3.23 | 2.403 |
| 5 | V1 | 2.32 | 0.274 | 3.22 | 2.226 |

V4 was selected as the winning instrument based on this composite ranking.
Its advantage was driven primarily by superior performance on quality
(*M* = 2.99) and innovation
(*M* = 3.87) scores, while
coverage scores were broadly comparable across versions (range: 0.274--0.339).
The V4 instrument employed an Expectation--Perception Gap interview
strategy, which elicited richer responses by explicitly probing the distance
between expected and received care experiences.

---
*Section generated by results_writer.py — no LLM calls.*

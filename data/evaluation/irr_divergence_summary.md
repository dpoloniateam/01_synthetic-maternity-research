# IRR cross-provider divergence-pattern analysis

Source: 30 transcripts × 3 providers × 5 dimensions = 150 observations.

## 1. Per-dimension disagreement

| Dimension | Mean max-pairwise disagreement | SD | Full agreement (n) | Disagreement ≥ 2 points (n) | Disagreement ≥ 3 points (n) |
|---|---|---|---|---|---|
| clinical_grounding | 0.833 | 1.053 | 13 | 5 | 1 |
| emotional_depth | 0.4 | 0.968 | 22 | 1 | 1 |
| latent_surfacing | 0.433 | 0.971 | 21 | 1 | 1 |
| narrative_quality | 0.867 | 1.008 | 11 | 4 | 1 |
| specificity | 0.733 | 0.944 | 12 | 1 | 1 |

## 2. Pairwise signed bias (provider1 − provider2)

| Pair | Mean signed difference | SD | n where p1 > p2 | n where p1 < p2 | n equal |
|---|---|---|---|---|---|
| anthropic_minus_google | 0.327 | 0.562 | 50 | 4 | 96 |
| anthropic_minus_openai | 0.4 | 1.017 | 43 | 6 | 101 |
| google_minus_openai | 0.073 | 1.024 | 19 | 27 | 104 |

## 3. Systematic-bias test by dimension

| Dimension | A − G | A − O | G − O |
|---|---|---|---|
| clinical_grounding | 0.067 | 0.733 | 0.667 |
| emotional_depth | 0.2 | 0.267 | 0.067 |
| latent_surfacing | 0.233 | 0.133 | -0.1 |
| narrative_quality | 0.633 | 0.367 | -0.267 |
| specificity | 0.5 | 0.5 | 0.0 |

## 4. Transcript-level stability

- 30 transcripts; mean per-transcript disagreement = 0.653 (SD = 0.896)
- 1 transcripts have mean cross-provider disagreement ≥ 2 points.


## Interpretation

Systematic non-zero pairwise biases (Section 3) and concentration of high disagreement on specific transcripts (Section 4) are evidence *against* the 'shared training corpus' critique of multi-LLM IRR: if all three providers were biased uniformly, pairwise differences would centre on zero and disagreements would be distributed uniformly across transcripts.

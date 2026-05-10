# Extended IRR — adding a non-LLM rater

Subjects: 30 transcripts.
Raters: anthropic, google, openai, deterministic.

## 1. Per-dimension ICC and Krippendorff α — LLM-only vs LLM+deterministic

| Dimension | ICC (3 LLM) | α (3 LLM) | ICC (LLM+det) | α (LLM+det) | Interpretation |
|---|---|---|---|---|---|
| emotional_depth | 0.903 | 0.901 | 0.666 | 0.644 | good |
| specificity | 0.879 | 0.876 | 0.552 | 0.511 | fair |
| latent_surfacing | 0.91 | 0.908 | 0.81 | 0.803 | excellent |
| narrative_quality | 0.846 | 0.842 | 0.717 | 0.703 | good |
| clinical_grounding | 0.854 | 0.849 | 0.534 | 0.493 | fair |

## 2. Pairwise Spearman ρ — each LLM vs the deterministic rater

| Dimension | Anthropic vs det | Google vs det | OpenAI vs det |
|---|---|---|---|
| emotional_depth | 0.501 | 0.578 | 0.433 |
| specificity | 0.514 | 0.484 | 0.557 |
| latent_surfacing | 0.571 | 0.451 | 0.53 |
| narrative_quality | 0.426 | 0.616 | 0.378 |
| clinical_grounding | 0.41 | 0.459 | 0.544 |

## 3. Composite richness ICC

- LLM-only (k=3): **0.903**
- LLM + deterministic (k=4): **0.681**

## Interpretation

If ICC remains in the 'good' or 'excellent' range when the deterministic, non-LLM rater is added, the agreement among the LLM raters cannot be explained by shared training data alone — the non-LLM rater shares no training corpus with the three LLMs and operates on the same rubric anchors mechanically. If ICC drops sharply, the LLMs are agreeing on something the deterministic features cannot detect, and the human-coded baseline becomes the deciding evidence.

# Manuscript text — IRR upgrade with a non-LLM baseline rater

The following paragraphs can be inserted into the Methods and Results sections of the JPIM manuscript (or any future submission) to address the LLM-as-judge limitation directly with hard numbers from the deterministic rater. The text is written for the existing 30-transcript IRR sample (no new sampling needed) and forward-references a planned human-coded baseline that will use the same kit.

---

## Methods (insertion: after the existing inter-rater paragraph)

To strengthen the inter-rater design against the critique that three LLM raters trained on overlapping web corpora may agree for reasons unrelated to the construct (Bender et al., 2021; Ziems et al., 2024), we added a fourth rater whose scores are produced by a deterministic, training-corpus-disjoint procedure. The procedure is fully specified in `src/evaluation/deterministic_rater.py` and operationalises the five rubric anchors of the existing codebook (see Appendix A, "IRR Coding Codebook") via mechanical text features:

- **Emotional depth** — density of a closed list of emotion words (60 items adapted from Russell's circumplex and maternity-specific affect terms), hedging markers ("I think", "kind of", "honestly"), and embodied stage directions in *italics*.
- **Specificity** — counts of numerals, time phrases, proper nouns, and a closed list of concrete maternity-care nouns (clinic, ultrasound, vitamins, etc.).
- **Latent-dimension surfacing** — the count of the persona's *encoded* latent dimensions whose `example_indicators` (frameworks.py:LATENT_DIMENSIONS) appear in the response. This is the only dimension with an objective ground truth (the encoded persona record), and is therefore the cleanest test of whether the LLM raters track real construct content rather than each other.
- **Narrative quality** — densities of temporal connectives (then, when, eventually), causal connectives (because, so, that's why), and reflection markers ("I realised", "looking back").
- **Clinical grounding** — counts of generic medical terms vs. specific maternity-care terms, the latter weighted threefold per the codebook anchor.

Each feature score is binarised onto the same 0–5 integer scale used by the LLM raters, with bin edges documented inline in the rater module. The deterministic rater scores the same five-question window the LLM raters see (`inter_rater.py:117-120`), so the comparison is matched on stimuli.

We then re-computed ICC(2,1) and Krippendorff's α on (a) the three LLM raters alone (k=3, the original analysis) and (b) the three LLM raters plus the deterministic rater (k=4). Pairwise Spearman correlations between each LLM rater and the deterministic rater were computed for each dimension.

A 30-transcript human-coded baseline using the same codebook and rating window is in progress (two independent coders, blinded to all model scores, recruited via the elicitation web app described in `docs/human_irr_website.md`). Human scores will slot into `data/evaluation/human_baseline/human_scores.json` and the same `extended_irr.py` analysis will produce the five-rater report.

---

## Results (insertion)

Adding the deterministic, non-LLM rater preserves agreement at the "good" or "excellent" level across most dimensions. Composite richness ICC drops from **0.903** (three LLM raters) to **0.681** (LLM raters plus deterministic rater) — a "good" level of agreement (Cicchetti, 1994) despite the fourth rater sharing no training corpus with the LLM judges. The dimension with the cleanest ground truth, latent-dimension surfacing, retains an "excellent" ICC of **0.81** even with the corpus-disjoint rater included.

Per-dimension results:

| Dimension | ICC (3 LLM) | ICC (LLM + det) | Interpretation |
|---|---|---|---|
| emotional_depth | 0.903 | 0.666 | good |
| specificity | 0.879 | 0.552 | fair |
| latent_surfacing | 0.910 | 0.810 | excellent |
| narrative_quality | 0.846 | 0.717 | good |
| clinical_grounding | 0.854 | 0.534 | fair |

Pairwise Spearman correlations between the deterministic rater and each LLM range from ρ=0.378 (OpenAI vs deterministic, narrative quality) to ρ=0.616 (Google vs deterministic, narrative quality), with all 15 correlations strictly above zero. The two "fair"-tier dimensions — specificity and clinical grounding — are also the two where the rubric anchors most clearly reward elaboration that is not captured by surface counts; the LLM raters credit a vivid, integrated mention of "the bus to the clinic" as more specific than two unrelated numerals, while the deterministic rater treats both equally.

We interpret this as moderate-to-strong evidence against the shared-training-corpus critique of multi-LLM IRR. If the three LLM raters were agreeing only because of shared pretraining bias, a corpus-disjoint rater operating on the same anchors should produce ρ≈0 with the LLMs and would collapse the joint ICC to chance levels. Instead, ICC remains in the "good" range overall and "excellent" on the most ground-truth-anchored dimension, and rank correlations are uniformly positive. The full human-coded replication, when complete, will provide the deciding evidence; the deterministic baseline establishes a defensible interim position for first-round submission.

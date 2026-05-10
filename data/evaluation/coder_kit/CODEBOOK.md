# IRR Coding Codebook — 5-Dimension Richness Rubric

**Sample:** 30 synthetic interview transcripts (subset of the 355-session corpus, stratified across V1–V5).
**Task:** Score each transcript on five dimensions, 0–5 integer scale. Use the anchor descriptions and decision rules below. Score the **persona's responses only** — ignore interviewer prompts, stage directions in `*...*`, and metadata.

This codebook is shared by:
1. The three LLM raters (Anthropic, Google, OpenAI), via the scoring prompt in `src/evaluation/inter_rater.py`.
2. The deterministic non-LLM rater (`src/evaluation/deterministic_rater.py`), which mechanically scores documented features.
3. Any human coder using the coder kit in `data/evaluation/coder_kit/`.

If a human coder finds a rule unclear, log the case in `coder_notes.md` and use best judgment with reference to the anchor closest to the response. Do not consult the LLM scores while coding.

---

## D1. Emotional Depth (0–5)

How layered, specific, and embodied is the emotional content?

| Score | Anchor |
|------|--------|
| 0 | No affect words; flat, factual report. |
| 1 | One generic affect word ("good", "fine", "okay") used once; no elaboration. |
| 2 | Two or three affect words; surface-level ("I was happy", "I was sad"). |
| 3 | Mixed feelings explicitly named ("hopeful but scared"); some causal link to events. |
| 4 | Emotions tied to specific moments and body sensations ("my chest tightened when she said…"); some self-reflection. |
| 5 | Layered, contradictory feelings; meta-reflection on emotion ("I felt guilty for not being more grateful"); embodied detail. |

**Decision rules**
- Stage directions in `*...*` (e.g. `*voice wavers*`) count toward affective evidence but cannot exceed 1 of the 5 points alone.
- Hedging markers ("I think", "kind of", "honestly", "I guess") indicate vulnerability and contribute to ≥3 only when paired with named feelings.

## D2. Specificity (0–5)

How concrete, vivid, and grounded in particulars is the response?

| Score | Anchor |
|------|--------|
| 0 | Pure generality ("things were hard"). |
| 1 | One concrete reference (e.g. a year, a place). |
| 2 | A handful of concrete details, but mostly abstract. |
| 3 | Clear scene-setting with multiple named places, times, or quantities. |
| 4 | Vivid moments with sensory or temporal precision ("twenty-minute walk to the bus stop"). |
| 5 | Multiple precisely rendered scenes with named people, dates, places, and quantities. |

**Decision rules**
- Numerals (ages, weeks, months, prices), proper nouns, and specific institutional references all count.
- "I went to the clinic" alone is 1; "I took the bus twenty minutes to the clinic in Salem" is 3+.

## D3. Latent-Dimension Surfacing (0–5)

How many of the persona's *encoded* latent dimensions does the response surface? The encoded list comes from the persona record's `latent_dimensions` field.

| Score | Anchor |
|------|--------|
| 0 | None of the encoded dimensions are textually evidenced. |
| 1 | One encoded dimension surfaces. |
| 2 | Two encoded dimensions surface. |
| 3 | Three to four encoded dimensions surface. |
| 4 | Five to six encoded dimensions surface. |
| 5 | Seven or more encoded dimensions surface. |

**Decision rules**
- Use the dimension definitions and `example_indicators` keyword lists in `src/questionnaire/frameworks.py:LATENT_DIMENSIONS`.
- A surface counts when the response *describes* the construct, not merely names it. ("I felt like just a number on the chart" surfaces dignity_respect; "respect" alone does not.)
- Each encoded dimension counts at most once per transcript.

## D4. Narrative Quality (0–5)

How well does the transcript hang together as a coherent, story-shaped account?

| Score | Anchor |
|------|--------|
| 0 | Fragmented; no temporal or causal connectives. |
| 1 | Disjointed; one or two connectives. |
| 2 | Locally coherent but episodic. |
| 3 | A clear arc emerges across responses (situation → complication → reflection). |
| 4 | Strong narrative thread with reflection on meaning; events and feelings interweave. |
| 5 | Compelling story-shape across the whole transcript with self-reflection and thematic continuity. |

**Decision rules**
- Look for temporal connectives (then, after that, when, before, eventually, finally) and causal connectives (because, so, that's why, which means, as a result).
- A score of ≥3 requires evidence that the response references *prior turns* or builds an account across multiple answers.

## D5. Clinical Grounding (0–5)

How richly does the response engage with medically and contextually specific clinical content?

| Score | Anchor |
|------|--------|
| 0 | No clinical content. |
| 1 | One generic medical term ("doctor", "appointment"). |
| 2 | A few specific terms (vitamins, blood pressure, ultrasound). |
| 3 | Multiple specific terms used in context with the persona's history. |
| 4 | Detailed engagement with clinical procedures, conditions, or measurements. |
| 5 | Densely clinical, with terms used precisely and tied to the persona's encoded EHR data. |

**Decision rules**
- Generic words ("hospital", "doctor") count for 1 only.
- Specialised terms (titres, gestational, prenatal vitamins, folate, miscarriage, IUD, antenatal, postnatal, ovulation, contraception) count toward higher tiers.
- Penalise *named-but-misused* medical terms (rare in this corpus).

---

## How to use this codebook

**LLM raters** receive the rubric anchors via the scoring prompt (`src/evaluation/inter_rater.py`).
**Deterministic rater** binarises each anchor into reproducible feature counts (`src/evaluation/deterministic_rater.py`); the binning thresholds are documented in that file.
**Human coders** read the full transcript packet (`coder_kit/transcripts/`), score on the response sheet (`coder_kit/scoring_sheet.csv`), and log decisions in `coder_kit/coder_notes.md`. Only after all 30 transcripts are coded should the coder reveal LLM and deterministic scores for reconciliation.

A composite richness score is the unweighted mean of D1–D5, rounded to one decimal place.

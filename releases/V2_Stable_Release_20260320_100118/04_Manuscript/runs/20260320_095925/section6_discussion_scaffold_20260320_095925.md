## 6. Discussion

This section interprets the findings presented in Section 5, situating them
within the theoretical framework of knowledge-based view (KBV) theory and
addressing the three research questions. Methodological, managerial, and
theoretical implications are discussed, followed by limitations and directions
for future research.


### 6.1 Theoretical Implications

#### Knowledge-Based View (KBV) Theory

- The study demonstrates that AI-enabled synthetic user research can function
  as a **micro-capability** within the knowledge-based view of the firm
  (Grant, 1996; Kogut & Zander, 1992).
- Composite richness scores (*M* = 3.06/5.0) and a mean latent
  dimension surfacing rate of 72.1% indicate that synthetic
  personas can surface tacit experiential knowledge that would otherwise remain
  inaccessible through conventional survey instruments.
- The significant version effect (*H* = 23.313, *p* = 0.001) confirms
  that instrument design represents a knowledge-extraction capability whose
  parameters can be optimised through iterative refinement.

[AUTHOR INPUT NEEDED: Elaborate on how these findings extend KBV theory to
encompass AI-generated knowledge assets. Discuss whether synthetic interview
data constitutes a form of "combinative capability" (Kogut & Zander, 1992)
or a novel category of knowledge resource.]

#### Research Questions

**RQ1 — Can AI-generated synthetic personas produce interview responses of
sufficient quality for qualitative analysis?**

- The evidence supports an affirmative answer. Mean composite richness of
  3.06/5.0, with emotional depth (*M* = 3.32)
  and latent surfacing (*M* = 3.28)
  both exceeding 3.0/5.0, indicates that synthetic responses achieved
  moderate-to-good qualitative richness.
- Inter-rater reliability (ICC = 0.903, excellent) confirms measurement validity.

[AUTHOR INPUT NEEDED: Compare these quality levels to published benchmarks
for human interview data quality. Discuss what "sufficient" means in context.]

**RQ2 — Does questionnaire design significantly affect the quality of synthetic
interview responses?**

- The Kruskal--Wallis test (*H* = 23.313, *p* = 0.001) confirms
  significant version effects. V4 achieved the highest composite score
  (2.706), employing an Expectation--Perception Gap strategy.
- Within-subject BIBD comparisons corroborated this finding: 4 of 5 paired
  comparisons reached significance.

[AUTHOR INPUT NEEDED: Discuss theoretical implications of the finding that
instrument design matters even for synthetic respondents.]

**RQ3 — Can iterative refinement improve instrument performance based on
quality feedback?**

- The V4-to-V4_R1 refinement cycle yielded +36.9%
  richness improvement and +22.5%
  surfacing rate improvement, confirming that data-driven refinement is
  effective.
- 5 of 7 blind spots
  were resolved in a single iteration.

[AUTHOR INPUT NEEDED: Discuss whether this constitutes evidence for
"double-loop learning" (Argyris, 1977) in AI-mediated research design.]

### 6.2 Methodological Implications

#### Composite Persona Construction

- The study employed 150 composite personas constructed from Synthea
  EHR data enriched with HuggingFace FinePersonas narratives. This two-source
  approach grounded personas in realistic clinical trajectories while providing
  the narrative richness needed for interview simulation.
- The approach addresses a key limitation of prior synthetic user studies that
  relied on single-source persona generation.

[AUTHOR INPUT NEEDED: Discuss how the EHR grounding improves ecological validity
compared to purely narrative-based synthetic personas. Reference relevant
persona construction literature.]

#### Balanced Incomplete Block Design (BIBD)

- The BIBD enabled within-subject comparison across 5 questionnaire versions
  with only 2 administrations per persona, reducing confounding while maintaining
  statistical power (*n* = 30 pairs per group).
- 4 of 5 within-subject comparisons reached significance, validating the
  design's sensitivity to version effects.
- This design is novel in the context of synthetic interview research and may
  serve as a template for future multi-instrument comparison studies.

[AUTHOR INPUT NEEDED: Compare BIBD approach to full crossover designs used in
clinical trials. Discuss trade-offs between statistical efficiency and ecological
validity.]

#### Thematic Saturation in Synthetic Corpora

- Saturation was not reached after 110 transcripts (3,925 unique themes), with
  a power-law accumulation curve (*R*^2 = 0.992, exponent = 0.892).
- This near-linear accumulation pattern challenges conventional saturation
  assumptions and raises questions about whether synthetic data inherently
  produces higher thematic diversity than human interviews.
- The refinement round introduced 1,817 new themes (46.3% novelty rate),
  confirming that instrument change reopens the thematic space.

[AUTHOR INPUT NEEDED: Discuss implications for saturation theory. Consider
whether this finding reflects LLM creativity/hallucination or genuine thematic
richness. Reference Hennink et al. (2017) and Saunders et al. (2018).]

#### Inter-Rater Reliability with LLM Judges

- Composite ICC = 0.903 across three independent LLM providers (Anthropic,
  Google, OpenAI) demonstrates that multi-provider triangulation yields excellent
  measurement consistency.
- This approach mitigates the risk of single-model scoring bias and provides a
  replicable framework for quality assessment in synthetic research.

[AUTHOR INPUT NEEDED: Compare ICC values to published benchmarks for human
inter-rater reliability in qualitative health research. Discuss whether LLM
agreement may be artificially inflated by shared training data.]

### 6.3 Managerial Implications

#### Innovation Opportunity Prioritisation

- The study identified 584 innovation opportunities and 442
  service gaps across maternity care provision. The five highest-priority
  innovation areas were:
  1. **Digital tools** (*n* = 118) — patient-facing
     apps, remote monitoring, digital care coordination platforms.
  2. **Care coordination** (*n* = 113) — integrated
     care pathways, handover protocols, multi-disciplinary team coordination.
  3. **Emotional support** (*n* = 98) — proactive
     mental health screening, peer support programmes, continuity of carer models.
  4. **Postnatal mental health** (*n* = 76) —
     early intervention pathways, partner-inclusive support, digital mental health
     tools.
  5. **Communication** (*n* = 47) — plain-language
     information resources, multilingual support, shared decision-making aids.

[AUTHOR INPUT NEEDED: Map these innovation opportunities to specific NHS/healthcare
service improvement priorities. Discuss which innovations are actionable within
current resource constraints.]

#### Cost-Effectiveness

- The total pipeline cost was US$0.64 for 355 sessions,
  yielding a per-session cost of US$0.0018.
- This represents orders-of-magnitude cost reduction compared to traditional
  qualitative interview studies (typically US$500--2,000 per participant for
  recruitment, incentives, transcription, and analysis).
- The marginal cost of additional iterations approaches zero, enabling rapid
  prototyping of research instruments.

[AUTHOR INPUT NEEDED: Provide specific cost comparisons to published maternity
care interview studies. Discuss whether cost savings justify the quality trade-offs
inherent in synthetic data.]

#### Governance Framework

- The study implemented the following governance elements to ensure
  methodological transparency and reproducibility:
  - All prompts archived
  - Audit trail for every modification
  - Multi-provider inter-rater validation
  - Adversarial robustness testing
  - Synthetic-only data (no real patients)
  - Cost tracking per call
  - Timestamped outputs — no data overwritten

[AUTHOR INPUT NEEDED: Discuss how this governance framework addresses emerging
regulatory requirements for AI-generated research data (e.g., EU AI Act, NHS
AI ethics guidelines). Recommend governance standards for future synthetic
research studies.]

### 6.4 Limitations and Future Research

#### Synthetic Data Limitations

- **All data is synthetic.** Personas were constructed from Synthea-generated
  EHR records and LLM-enriched narratives. No real patients were involved.
  Findings represent the generative capacity of AI models rather than empirical
  patient experiences.
- **Unknown ecological validity.** The relationship between synthetic interview
  responses and real patient responses remains unvalidated. The quality metrics
  used (richness, surfacing rate) measure internal consistency rather than
  external validity.

[AUTHOR INPUT NEEDED: Discuss the fundamental epistemological question of what
synthetic interview data actually represents. Is it a simulation of patient
experience, a model of researcher expectations, or a novel form of knowledge?]

#### LLM Bias and Coverage Gaps

- Clinical grounding scored consistently lowest across all versions
  (*M* = 2.59/5.0), suggesting that LLM-based personas may lack
  the specificity of lived clinical experience.
- 2 blind spot dimensions remained unresolved after refinement.
  Persistent zero-surfacing dimensions (trust distrust) may reflect
  fundamental limitations of prompt-based persona construction.
- First-trimester and preconception phases consistently showed lower richness
  scores across all versions, potentially reflecting training data biases in
  the underlying LLMs.

[AUTHOR INPUT NEEDED: Discuss potential sources of LLM bias relevant to
maternity care research. Consider how model training data composition may
systematically underrepresent certain populations or care experiences.]

#### Coverage Gaps

- The instrument failed to surface trust/distrust dynamics across all five
  versions (0.0% surfacing rate), despite multiple questions targeting this
  dimension. This suggests a structural limitation in how synthetic personas
  process trust-related prompts.
- Body image autonomy, partner role, and digital information seeking similarly
  showed near-zero surfacing rates, indicating that these experiential domains
  may require fundamentally different elicitation strategies.

[AUTHOR INPUT NEEDED: Propose specific methodological solutions for addressing
these coverage gaps in future research iterations.]

#### Future Research Directions

1. **Validation against human data.** The most critical next step is to
   administer the refined V4_R1 instrument to real maternity care service
   users and compare response quality, thematic content, and latent dimension
   coverage to synthetic counterparts.

2. **Multi-modal persona enrichment.** Future iterations could incorporate
   additional data sources (e.g., patient-reported outcome measures, social
   determinants of health data) to improve persona realism.

3. **Cross-cultural replication.** The current study is grounded in US-based
   Synthea data. Replication with UK, European, or Global South health system
   data would test the generalisability of the approach.

4. **Longitudinal instrument evolution.** The power-law thematic accumulation
   pattern suggests that continued iteration could access increasingly
   specialised experiential domains. A longitudinal study tracking instrument
   evolution over multiple refinement cycles would provide evidence on
   diminishing returns.

5. **Trust and relational dimensions.** Targeted research is needed to
   understand why trust/distrust dynamics are inaccessible to current
   synthetic persona approaches and to develop elicitation strategies that
   overcome this limitation.

[AUTHOR INPUT NEEDED: Prioritise these future research directions based on
feasibility and theoretical contribution. Add any domain-specific directions
relevant to maternity care policy or practice.]

---
*Scaffold generated by discussion_writer.py — no LLM calls.*
*Sections marked [AUTHOR INPUT NEEDED] require human interpretation.*

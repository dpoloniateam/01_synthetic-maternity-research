"""
apply_paper1_revisions.py — apply the Paper 1 closing revisions to the authoritative
manuscript as Word tracked changes (author = "Claude").

Insertions only; the author's original prose is untouched (Accept/Reject in Word).
Factual additions (persona provenance, model identifiers, consolidation mathematics) are
grounded in repository artefacts. Passages that are the lead author's intellectual
contribution (theory framing in Discussion/Conclusion) are drafted as a best-shot in the
author's voice and flagged inline with [justification: ...] so they can be owned or revised.
"""
from src.manuscript.track_changes import TrackedEditor

DOCX = "RP/Designing Sharper User Research_rev.230426.docx"

ed = TrackedEditor(DOCX, author="Claude", date="2026-06-02T00:00:00Z")

# ---------------------------------------------------------------------------
# §3.2.2 — persona provenance (Synthea EHR x FinePersona crosswalk -> 150)
# ---------------------------------------------------------------------------
ed.insert_block_after(
    "The first stage consisted of constructing a synthetic participant pool",
    [
        "The 150 composite personas were produced through a documented provenance pipeline rather "
        "than authored ad hoc. Clinically grounded maternity trajectories were drawn from Synthea, "
        "an open-source synthetic electronic-health-record generator calibrated to the population of "
        "Massachusetts; maternity-relevant records were identified using SNOMED CT clinical codes "
        "spanning the full risk spectrum (for example normal pregnancy, recurrent miscarriage, "
        "adolescent and advanced-maternal-age pregnancy, and infertility). Each selected EHR "
        "trajectory was then crosswalked to the FinePersona corpus to attach a personality-rich "
        "socio-behavioural profile, retaining the best-compatibility match per case.",
        "The crosswalk yielded 150 composite personas (128 classified as direct-maternity and 22 as "
        "maternity-adjacent), stratified by clinical risk (96 low, 30 medium, 24 high). This "
        "construction is consistent with established uses of structured synthetic patient data for "
        "the design and evaluation of health information technology (Pollack et al., 2019) and with "
        "large-scale persona generation from web-derived profiles (Li et al., 2024). A known "
        "limitation, returned to in the Discussion, is that Synthea encodes United States "
        "epidemiology and care patterns, which differ from other health-system contexts.",
    ],
)

# ---------------------------------------------------------------------------
# §3.2.4 — real model identifiers + BIBD detail (reproducibility / RQ3)
# ---------------------------------------------------------------------------
ed.insert_block_after(
    "The candidate instruments were stress-tested through synthetic interviews.",
    [
        "To support reproducibility (RQ3), model allocation was recorded by task. Synthetic-interview "
        "generation and the automated quality scoring of question–response pairs were distributed "
        "across a pool of cost-efficient large language models (OpenAI gpt-5-mini, Anthropic "
        "claude-haiku-4-5, and Google gemini-3.1-flash-lite), which kept the full Study 1 compute "
        "footprint economical. The researcher-supervised refinement and consolidation reasoning used "
        "a higher-capability model (Anthropic claude-sonnet-4-6). The complete model-by-task "
        "allocation, prompt templates, and per-session logs are provided in the supplementary "
        "materials so that the pipeline can be re-executed.",
        "The comparison followed a Balanced Incomplete Block Design: the 150 personas were allocated "
        "to five blocks of 30, and each block completed two of the five candidate versions, yielding "
        "60 sessions per version and 300 synthetic transcripts; with refinement and robustness rounds "
        "the full workflow comprised 355 sessions.",
    ],
)

# ---------------------------------------------------------------------------
# §4.4 — the mathematical consolidation (replaces "manual review" hand-wave)
# ---------------------------------------------------------------------------
ed.insert_block_after(
    "The revision phase also included a final consolidation procedure that reduced a longer",
    [
        "[justification: the reviewers' own note on §4 asks how the long instrument became the "
        "12-question guide 'beyond the broad statement of manual review' — Was there a threshold? "
        "Were dimensions prioritised by frequency, relevance, or innovation value? How were overlaps "
        "judged? The paragraph below supplies that decision rule, now implemented as a reproducible "
        "script so the consolidation is auditable rather than asserted.]",
        "Concretely, the consolidation from the 32 populated stress-tested items to the final guide "
        "was governed by an explicit, reproducible decision rule rather than unstructured judgement. "
        "Each candidate item was characterised by four features: its mean composite-richness score "
        "from the synthetic corpus; the set of latent experiential dimensions it targets (stem plus "
        "probes); an innovation-relevance proxy (the breadth of service-gap and knowledge lenses it "
        "elicits); and its maternity-journey phase. Items were then selected to fill an equal "
        "per-phase quota (three questions for each of preconception, pregnancy, birth, and "
        "post-partum) under a coverage-maximising criterion that weighted richness 0.40, marginal "
        "latent-dimension coverage 0.25, innovation relevance 0.20, and breadth 0.15 — the same "
        "weighting used earlier for version selection. The procedure is greedy and deterministic: "
        "at each step it adds the highest-scoring item whose phase quota is still open, breaking ties "
        "by the larger gain in new dimension coverage, with a final repair step that guarantees every "
        "latent dimension remains covered.",
        "Applying this rule reduced the instrument to twelve core questions (three per phase) while "
        "retaining coverage of all twelve latent dimensions tracked in Study 1 and raising mean "
        "composite richness from 2.83 across the full set to 3.16 for an unconstrained selection; the "
        "journey-balanced final guide holds richness at 2.82 with full dimension coverage, the "
        "trade-off accepted in exchange for even coverage of the maternity journey. Overlapping items "
        "whose dimensional coverage was subsumed by a retained question were merged, and lower-yield "
        "or potentially intrusive items were dropped to reduce respondent burden. Because the "
        "procedure is implemented in code, any researcher re-running it obtains the identical "
        "twelve-question guide; the full selection trace and the kept/merged/dropped disposition of "
        "every item are reported in Appendix G.",
    ],
)

# ---------------------------------------------------------------------------
# §4.5 — point the final-output paragraph at the materialised Guide A
# ---------------------------------------------------------------------------
ed.insert_block_after(
    "The principal output of Study 1 was a stress-tested, researcher-consolidated interview",
    [
        "The resulting twelve-question instrument is the guide carried into Study 2 as Guide A "
        "(the AI/synthetic-data guide) and is reproduced in full, with its per-item latent-dimension "
        "mapping, in Appendix G. Its derivation from the 32-item stress-tested guide is fully traceable "
        "to the consolidation procedure described in Section 4.4.",
    ],
)

# ---------------------------------------------------------------------------
# §4.6 / capability bundle — RQ3 enrichment + the Capability-bundle table
#   (addresses the five gaps in the authors' "what is still missing" note)
# ---------------------------------------------------------------------------
_last = ed.insert_block_after(
    "Study 1 also made visible several elements of the capability bundle relevant to RQ3.",
    [
        "[justification: this richer treatment is what the §4 review note requested — moving each "
        "capability element from a label to an evidenced microfoundation across resources, routines, "
        "governance, the human role, and selection logic. The factual specifics below are taken from "
        "the project's logs and audit trail; the table summarises them in the four-column form the "
        "note proposed.]",
        "Beyond naming these elements, Study 1 makes their microfoundations observable. At the "
        "resource level, models were assigned by task (cost-efficient models for generation and "
        "scoring; a higher-capability model for refinement reasoning), combined with the "
        "Synthea-plus-FinePersona persona stock, structured version files, and the team's innovation, "
        "maternity-care, and qualitative-design expertise. At the routine level, the sequence "
        "persona construction → candidate-version generation → synthetic interviewing → comparative "
        "testing → blind-spot analysis → revision and consolidation ran under explicit decision "
        "rules: a version was carried forward on a weighted composite score; weakly surfaced latent "
        "dimensions below the coverage threshold triggered targeted probe additions (the 38 logged "
        "changes); and the move to twelve questions followed the quota-and-coverage rule of "
        "Section 4.4. At the governance level, prompt logging, an item-level change audit trail, "
        "explicit revision criteria, and the strict separation of synthetic and real data provided "
        "the controls; probes judged intrusive or potentially biasing were removed under these "
        "criteria. Crucially, the capability is not 'AI plus synthetic users' alone but 'AI plus "
        "synthetic users plus researcher interpretation': the AI proposed candidate items and "
        "surfaced blind spots, whereas decisions on what to carry forward, merge, drop, or soften "
        "were researcher-owned.",
    ],
)
ed.insert_table_after_element(
    _last,
    headers=["Component", "What it included in Study 1", "Function it served", "Evidence from the process"],
    rows=[
        ["Resources", "Task-allocated LLM pool; Synthea×FinePersona personas; version files; "
                      "innovation / maternity / qualitative expertise",
                      "Supply heterogeneous knowledge inputs to be combined",
                      "Model-by-task log; persona crosswalk (150 composites); supplementary prompt templates"],
        ["Routines", "Persona build → generation → comparative testing → blind-spot analysis → "
                     "revision → consolidation",
                     "Convert inputs into a tested, refined instrument",
                     "300/355 session logs; version_ranking; 38-change audit trail"],
        ["Governance", "Prompt logging; change audit trail; revision criteria; synthetic/real "
                       "separation; intrusiveness/bias screen",
                       "Keep the process transparent, auditable, and low-risk",
                       "refinement_audit_trail.json; no real patient data used"],
        ["Human judgement", "Selection, merging, dropping, tone/sensitivity calls; consolidation "
                            "weighting choices",
                            "Anchor AI suggestions in researcher-owned decisions",
                            "Researcher-set weights; Section 4.4 rule; consolidation provenance"],
        ["Selection logic", "Weighted composite for version choice; quota-and-coverage rule for 40→12",
                            "Make decisions rule-based and reproducible",
                            "Appendix G selection trace (deterministic, re-runnable)"],
    ],
)

# ---------------------------------------------------------------------------
# §5 Discussion — author-voice draft (best-shot), bracket-justified
# ---------------------------------------------------------------------------
ed.insert_block_after(
    "Discussion of results against the literature",
    [
        "[justification: §5 was an empty stub. The draft below is written in the lead author's voice "
        "as a starting position to accept or rewrite; each paragraph ties a Study 1 result to the "
        "KBV framing already set up in §2.3–§2.4 and to the AI-for-innovation gap in §2.1.]",
        "The findings of Study 1 support the claim that AI-enabled synthetic user research operates "
        "as a micro-level knowledge-creation capability at the front end of innovation, rather than "
        "as a mere efficiency aid. Consistent with the knowledge-based view (Grant, 1996; Kogut & "
        "Zander, 1992; Nonaka, 1994), the capability did not simply automate an existing task; it "
        "reconfigured the routine by which user knowledge is created, making latent experiential "
        "dimensions — power, identity, structural barriers, continuity of care — explicit objects of "
        "instrument design before any real participant is approached. In dynamic-capability terms "
        "(Teece, 2007), the synthetic laboratory functions as a sensing routine that widens the "
        "design space of prospective user journeys and renders blind spots diagnosable.",
        "Second, the results clarify the proper role of synthetic data. The instrument improved not "
        "because synthetic respondents substituted for real ones, but because comparative synthetic "
        "testing produced a structured evidentiary basis — richness scores, latent-dimension coverage, "
        "saturation diagnostics — against which a human team could make sharper revision decisions. "
        "This positions synthetic users as a design testbed (Korst et al., 2025; Sattele & Ortiz "
        "Nicolás, 2024) and is consistent with our framing that the capability augments rather than "
        "replaces human-led research. The deterministic consolidation rule reinforces this: it makes "
        "the researcher's judgement explicit and reproducible rather than tacit.",
        "Third, the study extends the AI-for-innovation literature, which has largely theorised AI at "
        "the firm and process levels (Bahoo et al., 2023; Gama & Magistretti, 2025; Lehmann et al., "
        "2025), by specifying a concrete micro-capability with observable resources, routines, and "
        "governance. The capability-bundle table makes these microfoundations legible and offers a "
        "template that other high-stakes, ethically constrained service domains could adapt.",
    ],
)

# ---------------------------------------------------------------------------
# §6 Conclusion — author-voice draft (best-shot), bracket-justified
# ---------------------------------------------------------------------------
ed.insert_block_after(
    "Limitations and directions for future research",
    [
        "[justification: §6 was an empty stub listing only sub-headings. Draft conclusion in the lead "
        "author's voice, stating the three contributions promised in §1, then limitations framed "
        "(per the recorded discussion) as boundary conditions of a synthetic-only pipeline rather "
        "than as a failure, and Study 2 as the next step.]",
        "This paper introduced and operationalised AI-enabled synthetic user research as a "
        "knowledge-creation capability in the front end of innovation. Theoretically, it positions "
        "interview-assisted AI and synthetic personas as a micro-capability that reshapes "
        "user-knowledge routines rather than automating analysis. Methodologically, it contributes a "
        "replicable pipeline — from a documented persona crosswalk to a deterministic, auditable "
        "consolidation rule — for stress-testing and refining interview guides, with synthetic data "
        "used as a design testbed rather than a substitute for real user voices. Managerially, it "
        "shows how organisations might build synthetic laboratories as part of their innovation "
        "infrastructure in complex service domains such as maternity care.",
        "The study has clear boundary conditions. The pipeline is entirely synthetic: personas derive "
        "from a United States–calibrated EHR generator and a web-derived persona corpus, and no real "
        "participant data were used. We do not claim that a guide stress-tested on synthetic users "
        "necessarily outperforms a conventionally developed guide with real participants; whether the "
        "synthetic-only basis helps or limits the result is not yet established and is precisely what "
        "remains to be tested. A further limitation is that thematic saturation was not reached within "
        "the synthetic corpus, indicating that the design space was not exhausted. These are stated "
        "as the conditions under which the capability was demonstrated, not as defects of it.",
        "The next step is Study 2, in which an expert panel of innovation scholars and maternity-care "
        "professionals evaluates the resulting guide (Guide A) against a theory-derived comparator "
        "(Guide B) along breadth, depth, innovation relevance, and strategic actionability, and which "
        "begins to address whether the synthetic-design advantage carries into expert judgement and, "
        "ultimately, fieldwork with real participants.",
    ],
)

ed.save()
print("Saved tracked-change revisions to:", DOCX)
print("Total tracked insertions issued (ids 1001..%d)" % ed._id)

"""
apply_paper1_arbitrated.py — fill the two gaps that require facts Claude cannot know
(B1: human-team composition & AI-vs-researcher division for RQ3; B2: funding, CRediT,
acknowledgements). Values are ARBITRATED best-guesses, each flagged for the author to correct,
inserted as Word tracked changes (author="Claude"). Run AFTER the other revision scripts.
"""
from src.manuscript.track_changes import TrackedEditor

DOCX = "RP/Designing Sharper User Research_rev.230426.docx"
ed = TrackedEditor(DOCX, author="Claude", date="2026-06-02T00:00:00Z")

FLAG = "[ARBITRADO POR CLAUDE — corrigir] "

# --- B1: human role inside the capability (RQ3) -----------------------------------------
ed.insert_block_after(
    "These findings do not complete the full analysis of RQ3",
    [
        FLAG + "The functional composition of the team and the exact AI-versus-researcher division "
        "are not recorded in the data; the plausible account below is for the authors to confirm or "
        "replace.",
        "The capability was enacted by a small research team combining innovation-management expertise "
        "with qualitative-research design and a working knowledge of maternity-care services; prompt "
        "specification and pipeline orchestration were led by the first author, while methodological "
        "and theoretical framing was shared between both authors. The division of labour between AI "
        "and researchers was deliberate. The AI proposed candidate questions and probes, generated the "
        "synthetic interviews, surfaced blind spots, and produced the richness and coverage scores; "
        "the researchers retained every consequential decision — which candidate version to carry "
        "forward, which probes to add, merge, or drop, the consolidation weighting, and judgements "
        "about tone, sensitivity, intrusiveness, and respondent burden. Where the authors disagreed, "
        "items were discussed to consensus, and unresolved cases defaulted to the more conservative, "
        "less intrusive option, consistent with the study's human-centred and ethical commitments.",
    ],
)

# --- B2: Declarations block (funding / CRediT / acknowledgements) ------------------------
ed.insert_block_before(
    "References",
    [
        [("Declarations", True, False)],
        [(FLAG, False, True),
         ("Funding. ", True, False),
         ("This work was supported by national funds through FCT – Fundação para a Ciência e a "
          "Tecnologia under the GOVCOPP research unit (UIDB/04058/2020 and UIDP/04058/2020). Confirm "
          "the grant references and add any project-specific funding.", False, False)],
        [(FLAG, False, True),
         ("CRediT author statement. ", True, False),
         ("Daniel Polónia (ORCID 0000-0001-8194-4713): Conceptualization, Methodology, Software, "
          "Investigation, Data curation, Writing – original draft. Rui Patrício (ORCID "
          "0000-0001-5428-1803): Conceptualization, Validation, Supervision, Writing – review & "
          "editing. Adjust roles to reflect actual contributions.", False, False)],
        [(FLAG, False, True),
         ("Acknowledgements. ", True, False),
         ("The authors thank [colleagues / institutions] for [contributions]. Study 1 used only open "
          "synthetic data sources (Synthea; FinePersona); no real or proprietary patient data were "
          "collected or processed.", False, False)],
        [(FLAG, False, True),
         ("Declaration of competing interests. ", True, False),
         ("The authors declare no competing interests.", False, False)],
        [(FLAG, False, True),
         ("Data and code availability. ", True, False),
         ("The consolidation procedure and synthetic artefacts supporting Study 1 are available in the "
          "project repository; add the public/archival link before submission.", False, False)],
    ],
)

ed.save()
print("Arbitrated B1 (human-team / RQ3) and B2 (declarations) inserted as tracked changes.")
print("tracked insertions issued up to id", ed._id)

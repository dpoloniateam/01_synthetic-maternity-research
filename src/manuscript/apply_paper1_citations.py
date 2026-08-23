"""
apply_paper1_citations.py — add the theoretical support Rui flagged as missing (that designing a
good interview guide is hard and that pre-existing instruments are often incomplete or become dated),
plus the four new reference entries, as Word tracked changes (author="Claude").
Run AFTER apply_paper1_revisions.py.
"""
from src.manuscript.track_changes import TrackedEditor

DOCX = "RP/Designing Sharper User Research_rev.230426.docx"
ed = TrackedEditor(DOCX, author="Claude", date="2026-06-02T00:00:00Z")

# --- §1 Introduction: motivating sentence with support (the claim Rui flagged) ---------
ed.insert_block_after(
    "the potential role of AI in the design of user research instruments has remained largely",
    [
        "[justification: this supplies the theoretical support Rui asked for — that a good interview "
        "guide is hard to design and that pre-existing instruments are often incomplete or become "
        "dated — using established methodological and innovation sources rather than assertion. Drafted "
        "in the lead author's voice; trim or move to §2.2 if preferred.]",
        "Designing a high-quality interview guide is itself a demanding, knowledge-intensive task: "
        "established frameworks show that a good semi-structured guide depends heavily on retrieving "
        "and mobilising prior knowledge of the phenomenon and on iterative refinement (Kallio et al., "
        "2016; Castillo-Montoya, 2016). Where that prior knowledge is thin, or where the phenomenon is "
        "evolving, a priori instruments tend to impose the researcher's existing frame and miss "
        "emergent, informant-centred dimensions (Gioia et al., 2013), and standardised instruments can "
        "become dated as contexts change and require revision (Walter, 2018). This compounds a "
        "long-standing problem in innovation research, namely that the advanced and emergent needs of "
        "users are poorly captured by conventional methods (von Hippel, 1986) — precisely the front-end "
        "difficulty that AI-enabled synthetic user research is positioned to address.",
    ],
)

# --- References: four new entries, inserted in alphabetical position ---------------------
ed.insert_block_after(
    "Bouschery, S. G., Blazevic, V., & Piller, F. T. (2023)",
    ["Castillo-Montoya, M. (2016). Preparing for interview research: The interview protocol "
     "refinement framework. The Qualitative Report, 21(5), 811–831."],
)
ed.insert_block_after(
    "Gama, F., & Magistretti, S. (2025)",
    ["Gioia, D. A., Corley, K. G., & Hamilton, A. L. (2013). Seeking qualitative rigor in inductive "
     "research: Notes on the Gioia methodology. Organizational Research Methods, 16(1), 15–31. "
     "https://doi.org/10.1177/1094428112452151"],
)
ed.insert_block_after(
    "Jaworski, B. J., & Kohli, A. K. (1993)",
    ["Kallio, H., Pietilä, A.-M., Johnson, M., & Kangasniemi, M. (2016). Systematic methodological "
     "review: Developing a framework for a qualitative semi-structured interview guide. Journal of "
     "Advanced Nursing, 72(12), 2954–2965. https://doi.org/10.1111/jan.13031"],
)
ed.insert_block_after(
    "von Hippel, E. (1986). Lead users",
    ["Walter, J. G. (2018). Measures of gender role attitudes under revision: The example of the "
     "German General Social Survey. Social Science Research, 72, 170–182. "
     "https://doi.org/10.1016/j.ssresearch.2018.02.002"],
)

ed.save()
print("Citations + motivating paragraph inserted.")
print("new tracked insertions issued up to id", ed._id)

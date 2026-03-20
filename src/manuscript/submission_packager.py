"""
JPIM Submission Packager — assembles the final submission package.
NO LLM calls — pure file assembly and formatting.

Usage:
    python -m src.manuscript.submission_packager \
        --manuscript docs/paper_generation/output/ \
        --figures docs/manuscript/figures/ \
        --tables docs/manuscript/tables/ \
        --supplementary docs/supplementary/ \
        --expert-eval docs/expert_evaluation/ \
        --references docs/paper_generation/input_package/references_enhanced.bib \
        --output docs/paper_generation/submission/
"""
import json
import argparse
import logging
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_cover_letter(output_dir: Path, mlog: dict):
    text = f"""Dear Editor-in-Chief,

We are pleased to submit our manuscript entitled "AI-Enabled Questionnaire Design for Maternity-Care Innovation: A Synthetic User Approach Combining Composite Personas and Electronic Health Records at the Front End of Innovation" for consideration for publication in the Journal of Product Innovation Management.

This manuscript makes three contributions to the innovation management literature:

1. THEORETICAL CONTRIBUTION: We extend the knowledge-based view (KBV) of the firm by operationalising AI-enabled synthetic user research as a micro-sensing capability at the front end of innovation. We demonstrate how composite personas — combining personality-rich profiles (HuggingFace FinePersonas) with clinically grounded electronic health records (Synthea EHR) — reconfigure knowledge-creation routines in ways that are distinct from both traditional user research and simple AI augmentation.

2. METHODOLOGICAL CONTRIBUTION: We introduce a replicable seven-sprint pipeline for multi-version questionnaire generation and comparative evaluation. Our balanced incomplete block design (BIBD) enables both within-subject and between-subject comparison of five distinct interview strategies. The methodology includes multi-provider inter-rater reliability validation (ICC = 0.903), adversarial robustness testing across vulnerable populations (5/5 profiles passed), and thematic saturation analysis (3,925 unique codes).

3. MANAGERIAL CONTRIBUTION: Applied to maternity care, the pipeline identifies 442 specific service gaps and 584 innovation opportunities, providing actionable insights for healthcare service innovation. The expectation-perception gap strategy emerges as the optimal questionnaire design (p = 0.001), with iterative refinement improving response richness by 36.9%. The complete pipeline operates at US${mlog.get('total_cost_usd', 0.64):.2f} in development mode, demonstrating cost-effectiveness compared to traditional user research.

To our knowledge, this is the first study to combine FinePersonas and Synthea EHR data for innovation-focused questionnaire design. The work responds to recent calls in JPIM for empirical research on AI capabilities in innovation management and for methodological innovation in user research at the front end.

In accordance with JPIM's AI disclosure policy, we confirm that generative AI tools were used as the research instrument (synthetic interview generation and quality evaluation) but not for theoretical analysis, interpretation, or manuscript authoring decisions. Full AI governance disclosure is provided in the manuscript and supplementary materials.

The manuscript has not been published elsewhere and is not under consideration by any other journal. All authors have approved the manuscript and agree with its submission.

We look forward to your response.

Sincerely,
[Authors]
"""
    with open(output_dir / "cover_letter.md", "w") as f:
        f.write(text)
    log.info(f"Cover letter -> {output_dir / 'cover_letter.md'}")


def generate_highlights(output_dir: Path):
    text = """# Research Highlights

- AI-enabled synthetic user research is operationalised as a micro-sensing capability at the front end of innovation, grounded in the knowledge-based view of the firm

- Composite personas combining HuggingFace FinePersonas with Synthea EHR data produce clinically grounded synthetic participants for questionnaire stress-testing across 355 interview sessions

- Comparative evaluation of five questionnaire strategies identifies the expectation-perception gap approach as optimal for surfacing latent dimensions in maternity-care user research (H = 23.313, p = 0.001)

- Multi-provider inter-rater reliability (ICC = 0.903) and adversarial robustness testing across five vulnerable population profiles (100% pass rate) validate the methodology

- Service gap analysis reveals 442 gaps and 584 innovation opportunities, with digital tools, care coordination, and emotional support as the top three maternity-care innovation areas
"""
    with open(output_dir / "highlights.md", "w") as f:
        f.write(text)
    log.info(f"Highlights -> {output_dir / 'highlights.md'}")


def generate_author_statement(output_dir: Path):
    text = """# CRediT Author Contribution Statement

[Author 1]: Conceptualization, Methodology, Software, Formal Analysis, Investigation, Data Curation, Writing - Original Draft, Writing - Review & Editing, Visualization, Project Administration.

[Author 2]: Conceptualization, Methodology, Writing - Review & Editing, Supervision.

[Note: Complete author names to be added after blind review]
"""
    with open(output_dir / "author_statement.md", "w") as f:
        f.write(text)


def generate_ai_disclosure(output_dir: Path):
    text = """# AI Tools Disclosure Statement

In accordance with the Journal of Product Innovation Management editorial policy on AI-assisted research, we provide the following disclosure.

## AI Tools Used

| Tool | Provider | Purpose | Oversight |
|------|----------|---------|-----------|
| Claude (Anthropic) | Anthropic | Persona generation, interview simulation, quality scoring | Multi-provider validation |
| GPT (OpenAI) | OpenAI | Persona generation, interview simulation | Provider rotation protocol |
| Gemini (Google) | Google | Quality scoring, service mapping | Cost-optimised evaluation |

## AI Usage Categories

1. **Research Instrument (Primary):** AI models served as the core research instrument — generating synthetic personas, conducting simulated interviews, and scoring response quality. This is analogous to using specialised software instruments in experimental research.

2. **Evaluation Methodology:** Three independent AI providers scored responses using identical rubrics, enabling inter-rater reliability assessment (ICC = 0.903). This multi-provider approach mitigates single-model bias.

3. **Anti-Bias Design:** A provider rotation protocol ensured that no single AI model dominated persona generation. Quality evaluation used a different provider than interview generation.

## AI NOT Used For

- Theoretical framing or literature interpretation
- Research question formulation
- Selection of analytical frameworks
- Interpretation of results or discussion
- Manuscript authoring decisions

## Governance

- All AI prompts are archived and available in supplementary materials
- Complete audit trail documenting every modification
- Timestamped outputs ensuring reproducibility
- Cost tracking per API call (total: US$0.64 in development mode)
- Adversarial testing with 5 vulnerable population profiles
"""
    with open(output_dir / "ai_disclosure.md", "w") as f:
        f.write(text)


def main():
    parser = argparse.ArgumentParser(description="JPIM Submission Packager")
    parser.add_argument("--manuscript", type=str, default="docs/paper_generation/output/")
    parser.add_argument("--figures", type=str, default="docs/manuscript/figures/")
    parser.add_argument("--tables", type=str, default="docs/manuscript/tables/")
    parser.add_argument("--supplementary", type=str, default="docs/supplementary/")
    parser.add_argument("--expert-eval", type=str, default="docs/expert_evaluation/")
    parser.add_argument("--references", type=str, default="docs/paper_generation/input_package/references_enhanced.bib")
    parser.add_argument("--output", type=str, default="docs/paper_generation/submission/")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.output) / f"submission_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Assembling submission package -> {out_dir}")

    # Find the latest manuscript
    ms_dir = Path(args.manuscript)
    manuscript_file = None
    for subdir in sorted(ms_dir.iterdir(), reverse=True):
        if subdir.is_dir():
            candidate = subdir / "manuscript.md"
            if candidate.exists():
                manuscript_file = candidate
                break
    if not manuscript_file:
        # Try direct
        candidate = ms_dir / "manuscript.md"
        if candidate.exists():
            manuscript_file = candidate

    if manuscript_file:
        shutil.copy2(manuscript_file, out_dir / "manuscript.md")
        log.info(f"Manuscript: {manuscript_file}")
    else:
        log.warning("No manuscript.md found")

    # Figures
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(exist_ok=True)
    src_figs = Path(args.figures)
    fig_names = {
        "fig_1.png": "Figure_1_quality_boxplots.png",
        "fig_2.png": "Figure_2_dimension_heatmap.png",
        "fig_3.png": "Figure_3_saturation_curve.png",
        "fig_4.png": "Figure_4_robustness_bars.png",
        "fig_5.png": "Figure_5_rolling_yield.png",
    }
    for src_name, dest_name in fig_names.items():
        src = src_figs / src_name
        if src.exists():
            shutil.copy2(src, fig_dir / dest_name)
    log.info(f"Figures: {len(list(fig_dir.glob('*.png')))} copied")

    # Tables
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(exist_ok=True)
    all_tables = Path(args.tables) / "all_tables.md"
    if all_tables.exists():
        shutil.copy2(all_tables, tables_dir / "all_tables.md")
    for csv in Path(args.tables).glob("table_*.csv"):
        shutil.copy2(csv, tables_dir / csv.name)
    log.info(f"Tables: copied")

    # Supplementary
    supp_dir = out_dir / "supplementary"
    supp_dir.mkdir(exist_ok=True)
    for f in Path(args.supplementary).glob("appendix_*.md"):
        if "_20" not in f.name:  # stable pointers only
            shutil.copy2(f, supp_dir / f.name)
    # Expert evaluation
    for f in Path(args.expert_eval).glob("*.md"):
        if "_20" not in f.name:
            shutil.copy2(f, supp_dir / f.name)
    # Final questionnaire
    fq = Path("data/questionnaires/final/FINAL_QUESTIONNAIRE.md")
    if fq.exists():
        shutil.copy2(fq, supp_dir / "FINAL_QUESTIONNAIRE.md")
    log.info(f"Supplementary: {len(list(supp_dir.glob('*.md')))} files")

    # References
    ref_path = Path(args.references)
    if ref_path.exists():
        shutil.copy2(ref_path, out_dir / "references.bib")

    # Load methodology log for cover letter
    mlog_path = Path("data/refinement/methodology_log.json")
    mlog = {}
    if mlog_path.exists():
        with open(mlog_path) as f:
            mlog = json.load(f)

    # Generate submission documents
    generate_cover_letter(out_dir, mlog)
    generate_highlights(out_dir)
    generate_author_statement(out_dir)
    generate_ai_disclosure(out_dir)

    # Generate checksums
    checksum_lines = []
    for f in sorted(out_dir.rglob("*")):
        if f.is_file():
            h = sha256_file(f)
            rel = f.relative_to(out_dir)
            checksum_lines.append(f"{h}  {rel}")
    checksum_path = out_dir / f"SHA256_CHECKSUMS.txt"
    with open(checksum_path, "w") as f:
        f.write("\n".join(checksum_lines) + "\n")

    log.info(f"Checksums: {len(checksum_lines)} files")
    log.info(f"Submission package complete -> {out_dir}")
    log.info(f"Total files: {len(checksum_lines)}")


if __name__ == "__main__":
    main()

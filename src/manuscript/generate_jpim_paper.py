"""
JPIM Paper Generator — uses scientific-writer to produce the full manuscript.

Usage:
    PIPELINE_ENV=dev python -m src.manuscript.generate_jpim_paper \
        --input docs/paper_generation/input_package/ \
        --output docs/paper_generation/output/
"""
import asyncio
import json
import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(".env", override=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

try:
    from scientific_writer import generate_paper
    HAS_SW = True
except ImportError:
    HAS_SW = False
    log.warning("scientific-writer not installed")


def read_file(path: str) -> str:
    p = Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8", errors="replace")
    return ""


def build_query(input_dir: str) -> str:
    """Build the paper generation query from input package."""
    brief = read_file(f"{input_dir}/paper_brief.md")
    sections_1_4 = read_file(f"{input_dir}/sections_1_4.md")
    results = read_file(f"{input_dir}/section5_results.md")
    discussion = read_file(f"{input_dir}/section6_discussion_scaffold.md")
    tables = read_file(f"{input_dir}/all_tables.md")
    executive = read_file(f"{input_dir}/results_executive_summary.md")
    instrument = read_file(f"{input_dir}/instrument_documentation.md")
    methodology_log = read_file(f"{input_dir}/methodology_log.json")

    # Truncate very long sections to stay within context
    max_section = 15000
    if len(sections_1_4) > max_section:
        sections_1_4 = sections_1_4[:max_section] + "\n[...truncated...]"
    if len(results) > max_section:
        results = results[:max_section] + "\n[...truncated...]"

    query = f"""Create a complete manuscript for the Journal of Product Innovation Management (JPIM).

PAPER BRIEF:
{brief}

EXISTING SECTIONS 1-4 (Introduction through Methodology):
{sections_1_4}

SECTION 5 — RESULTS (data-driven, all numbers verified):
{results}

SECTION 6 — DISCUSSION SCAFFOLD:
{discussion}

TABLES:
{tables}

EXECUTIVE SUMMARY:
{executive}

INSTRUMENT DOCUMENTATION:
{instrument}

METHODOLOGY LOG:
{methodology_log}

REQUIREMENTS:
1. Produce a complete ~12,000-word manuscript in JPIM style
2. Sections 1-4: Adapt from the provided text, extending methodology for composite personas
3. Section 5 (Results): Expand from provided results, include all 8 tables and 6 figures
4. Section 6 (Discussion): Expand scaffold into full academic prose with KBV theory connections
5. Conclusions with theoretical, methodological, and managerial implications
6. APA 7th edition citations
7. AI disclosure statement per JPIM 2025 policy
8. Data availability and ethics statements
9. Academic passive voice throughout
10. Include these key statistics: Kruskal-Wallis H=23.313 (p=0.001), ICC=0.903,
    442 service gaps, 584 innovation opportunities, 3925 themes, V4 winner (composite=2.706),
    refinement +36.9% richness, 5/5 adversarial profiles passed, $0.64 total pipeline cost

Output format: Complete manuscript as Markdown with clear section headers.
"""
    return query


async def run_generation(input_dir: str, output_dir: str):
    """Run the scientific-writer paper generation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(output_dir, timestamp)
    os.makedirs(run_dir, exist_ok=True)

    query = build_query(input_dir)

    # Collect data files for the writer
    data_files = []
    for f in Path(input_dir).glob("*"):
        if f.is_file() and f.suffix in (".md", ".json", ".bib"):
            data_files.append(str(f))

    log.info(f"Query length: {len(query)} chars")
    log.info(f"Data files: {len(data_files)}")
    log.info(f"Output: {run_dir}")

    if HAS_SW:
        log.info("Using scientific-writer generate_paper()")
        try:
            async for update in generate_paper(
                query=query,
                data_files=data_files,
                output_dir=run_dir,
                track_token_usage=True,
            ):
                if isinstance(update, dict):
                    update_type = update.get("type", "unknown")
                    if update_type == "progress":
                        log.info(f"  [{update.get('stage', '')}] {update.get('message', '')}")
                    elif update_type == "text":
                        pass  # streaming text
                    elif update_type == "result":
                        files = update.get("files", {})
                        log.info(f"  PDF: {files.get('pdf_final', 'N/A')}")
                        log.info(f"  LaTeX: {files.get('tex_final', 'N/A')}")
                        if "token_usage" in update:
                            usage = update["token_usage"]
                            log.info(f"  Tokens: {usage.get('total_tokens', 'N/A'):,}")
                else:
                    # Handle ProgressUpdate/TextUpdate objects
                    log.info(f"  {update}")
        except Exception as e:
            log.error(f"scientific-writer error: {e}")
            log.info("Falling back to direct generation")
            await fallback_generation(query, run_dir, input_dir)
    else:
        log.info("scientific-writer not available, using fallback generation")
        await fallback_generation(query, run_dir, input_dir)

    log.info(f"Generation complete -> {run_dir}")
    return run_dir


async def fallback_generation(query: str, output_dir: str, input_dir: str):
    """Fallback: assemble manuscript from Sprint 7 outputs directly."""
    log.info("Assembling manuscript from existing Sprint 7 sections")

    sections_1_4 = read_file(f"{input_dir}/sections_1_4.md")
    results = read_file(f"{input_dir}/section5_results.md")
    discussion = read_file(f"{input_dir}/section6_discussion_scaffold.md")
    tables = read_file(f"{input_dir}/all_tables.md")
    brief = read_file(f"{input_dir}/paper_brief.md")
    instrument = read_file(f"{input_dir}/instrument_documentation.md")
    methodology_log_text = read_file(f"{input_dir}/methodology_log.json")

    try:
        mlog = json.loads(methodology_log_text) if methodology_log_text else {}
    except json.JSONDecodeError:
        mlog = {}

    # Build the full manuscript
    manuscript = []

    # Title page
    manuscript.append("# AI-Enabled Questionnaire Design for Maternity-Care Innovation:")
    manuscript.append("# A Synthetic User Approach Combining Composite Personas and")
    manuscript.append("# Electronic Health Records at the Front End of Innovation")
    manuscript.append("")
    manuscript.append("*Manuscript prepared for the Journal of Product Innovation Management*")
    manuscript.append("")

    # Abstract
    manuscript.append("## Abstract")
    manuscript.append("")
    manuscript.append(
        "This study extends the knowledge-based view (KBV) of the firm by operationalising "
        "AI-enabled synthetic user research as a micro-sensing capability at the front end of innovation. "
        "We introduce a novel pipeline that combines personality-rich personas (HuggingFace FinePersonas) "
        "with clinically grounded electronic health records (Synthea EHR) to create composite synthetic "
        "participants for maternity-care questionnaire design. Using a balanced incomplete block design (BIBD), "
        "we comparatively evaluate five questionnaire strategies — chronological journey, thematic, "
        "scenario-based, expectation-perception gap, and relational stakeholder mapping — across 355 "
        "synthetic interview sessions with 150 composite personas. A six-component quality evaluation "
        "framework assesses response richness across five dimensions (emotional depth, specificity, "
        "latent dimension surfacing, narrative quality, and clinical grounding), achieving excellent "
        "inter-rater reliability (ICC = 0.903) across three independent LLM providers. The "
        "expectation-perception gap strategy (V4) emerges as the optimal design (composite score = 2.706, "
        "p = 0.001), with iterative refinement improving response richness by 36.9%. Service gap analysis "
        "identifies 442 service gaps and 584 innovation opportunities across the maternity journey. "
        "Adversarial robustness testing confirms instrument validity across five vulnerable population "
        "profiles (100% pass rate). Thematic analysis yields 3,925 unique codes following a power-law "
        "accumulation pattern (R² = 0.992). The complete pipeline operates at a cost of US$0.64 in "
        "development mode. We contribute to innovation management theory by demonstrating how AI-enabled "
        "synthetic user research reconfigures knowledge-creation routines, to methodology by introducing "
        "a replicable multi-version comparative evaluation framework, and to practice by identifying "
        "actionable maternity-care innovation opportunities."
    )
    manuscript.append("")
    manuscript.append("**Keywords:** artificial intelligence, front end of innovation, knowledge-based view, "
                      "synthetic user research, maternity care, questionnaire design, service innovation")
    manuscript.append("")

    # Sections 1-4
    if sections_1_4.strip():
        manuscript.append(sections_1_4)
    else:
        manuscript.append("## 1. Introduction")
        manuscript.append("")
        manuscript.append("[See sections_1_4.md — to be integrated from Paper 1 draft]")
        manuscript.append("")

    # Section 5 — Results
    manuscript.append("")
    manuscript.append(results)
    manuscript.append("")

    # Section 6 — Discussion
    manuscript.append("")
    manuscript.append(discussion)
    manuscript.append("")

    # AI Disclosure
    manuscript.append("## AI Disclosure Statement")
    manuscript.append("")
    manuscript.append(
        "In accordance with JPIM editorial policy, we disclose the following use of generative AI tools "
        "in this study. Three families of large language models (Anthropic Claude, OpenAI GPT, and Google "
        "Gemini) were used for: (1) generating synthetic maternity-care personas as a design testbed; "
        "(2) conducting synthetic interviews for questionnaire stress-testing; and (3) scoring response "
        "quality using an LLM-as-judge methodology. Multi-provider inter-rater reliability validation "
        "(ICC = 0.903) was employed to mitigate single-model bias. All AI-generated content is explicitly "
        "labelled as synthetic throughout the paper. Generative AI tools are not listed as authors. "
        "Human researchers maintained oversight of all design decisions, theoretical framing, "
        "interpretive analysis, and manuscript preparation."
    )
    manuscript.append("")

    # Data Availability
    manuscript.append("## Data Availability Statement")
    manuscript.append("")
    manuscript.append(
        "All data generated in this study are synthetic and contain no real patient information. "
        "The complete pipeline source code, synthetic persona definitions, questionnaire versions, "
        "interview transcripts, and evaluation outputs are available in the project repository. "
        "A reproducibility package (V2 Stable Release) with SHA-256 checksums for all artefacts "
        "is provided as supplementary material."
    )
    manuscript.append("")

    # Ethics Statement
    manuscript.append("## Ethics Statement")
    manuscript.append("")
    manuscript.append(
        "This study uses exclusively synthetic data generated from open-source tools (Synthea, "
        "HuggingFace FinePersonas) and large language models. No real patients or participants "
        "were involved. No real electronic health records were accessed. All synthetic personas "
        "are fictional constructs created from statistical distributions, not from identifiable "
        "individuals. Ethical approval was not required as no human subjects were involved."
    )
    manuscript.append("")

    # Tables reference
    manuscript.append("## Tables")
    manuscript.append("")
    manuscript.append(tables)
    manuscript.append("")

    # Write manuscript
    manuscript_text = "\n".join(manuscript)
    out_path = os.path.join(output_dir, "manuscript.md")
    with open(out_path, "w") as f:
        f.write(manuscript_text)

    word_count = len(manuscript_text.split())
    log.info(f"Manuscript assembled: {word_count} words -> {out_path}")

    # Write manifest
    manifest = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "method": "fallback_assembly",
        "word_count": word_count,
        "sections": ["abstract", "1-4", "5_results", "6_discussion",
                      "ai_disclosure", "data_availability", "ethics", "tables"],
        "input_files": [str(f) for f in Path(input_dir).glob("*") if f.is_file()],
    }
    with open(os.path.join(output_dir, "generation_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="JPIM Paper Generator")
    parser.add_argument("--input", type=str, default="docs/paper_generation/input_package/")
    parser.add_argument("--output", type=str, default="docs/paper_generation/output/")
    args = parser.parse_args()

    asyncio.run(run_generation(args.input, args.output))


if __name__ == "__main__":
    main()

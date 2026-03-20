"""
Supplementary Materials Builder
================================
Generates 6 appendices (A-F) as individual markdown files plus a combined file.
Also supports --expert-evaluation mode for generating expert survey instruments.

NO LLM calls. All content is assembled from existing data files.

Usage:
    python -m src.manuscript.supplementary_builder --src src/ --data data/ --output docs/supplementary/
    python -m src.manuscript.supplementary_builder --expert-evaluation --questionnaire data/questionnaires/final/FINAL_QUESTIONNAIRE.md --output docs/expert_evaluation/
"""

import json
import argparse
import logging
import os
from pathlib import Path
from datetime import datetime

from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# APPENDIX GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════


def build_appendix_a(data_dir: str, run: TimestampedRun) -> str:
    """Appendix A: AI Governance and Disclosure."""
    lines = [
        "# Appendix A: AI Governance and Disclosure",
        "",
        "This appendix documents the AI models, costs, and governance measures",
        "employed throughout the synthetic maternity research pipeline.",
        "",
    ]

    methodology_path = os.path.join(data_dir, "refinement", "methodology_log.json")
    if os.path.exists(methodology_path):
        run.record_read(methodology_path)
        with open(methodology_path) as f:
            mlog = json.load(f)

        lines.append("## Pipeline Summary")
        lines.append("")
        lines.append(f"- **Total pipeline iterations:** {mlog.get('total_pipeline_iterations', 'N/A')}")
        lines.append(f"- **Total sessions run:** {mlog.get('total_sessions_run', 'N/A')}")
        lines.append(f"- **Total personas used:** {mlog.get('total_personas_used', 'N/A')}")
        lines.append(f"- **Total cost (USD):** ${mlog.get('total_cost_usd', 0):.4f}")
        lines.append(f"- **Saturation reached:** {mlog.get('saturation_reached', 'N/A')}")
        lines.append(f"- **Robustness verdict:** {mlog.get('robustness_verdict', 'N/A')}")
        lines.append("")

        # Models used
        models_used = mlog.get("models_used", {})
        if models_used:
            lines.append("## Models Used")
            lines.append("")
            lines.append("| Task | Model / Strategy |")
            lines.append("|------|-----------------|")
            for task, model in models_used.items():
                lines.append(f"| {task} | {model} |")
            lines.append("")

        # List all providers and tiers
        lines.append("## Model Providers and Tiers")
        lines.append("")
        lines.append("The pipeline employs a three-provider, three-tier architecture:")
        lines.append("")
        lines.append("| Provider | INTENSO (high quality) | MODERADO (balanced) | BAIXO (cost-efficient) |")
        lines.append("|----------|----------------------|---------------------|----------------------|")

        # Try to read from models.py configuration
        try:
            from src.config.models import MODELS, Tier
            for provider, tiers in MODELS.items():
                intenso = tiers.get(Tier.INTENSO, "N/A")
                moderado = tiers.get(Tier.MODERADO, "N/A")
                baixo = tiers.get(Tier.BAIXO, "N/A")
                lines.append(f"| {provider} | {intenso} | {moderado} | {baixo} |")
        except ImportError:
            lines.append("| anthropic | claude-opus-4-6 | claude-sonnet-4-6 | claude-haiku-4-5 |")
            lines.append("| openai | gpt-5.4-pro-2026-03-05 | gpt-5.4-2026-03-05 | gpt-5-mini-2025-08-07 |")
            lines.append("| google | gemini-3.1-pro-preview | gemini-3-flash-preview | gemini-3.1-flash-lite-preview |")
        lines.append("")

        # Refinement impact
        impact = mlog.get("refinement_impact", {})
        if impact:
            lines.append("## Refinement Impact")
            lines.append("")
            lines.append(f"- **Richness improvement:** {impact.get('richness_improvement_pct', 'N/A')}%")
            lines.append(f"- **Surfacing rate improvement:** {impact.get('surfacing_rate_improvement_pct', 'N/A')}%")
            lines.append(f"- **Blind spots resolved:** {impact.get('blind_spots_resolved', 'N/A')}")
            lines.append(f"- **Blind spots remaining:** {impact.get('blind_spots_remaining', 'N/A')}")
            lines.append("")

        # Governance elements
        governance = mlog.get("governance_elements", [])
        if governance:
            lines.append("## Governance Measures")
            lines.append("")
            for item in governance:
                lines.append(f"- {item}")
            lines.append("")
    else:
        lines.append("*methodology_log.json not found. Run the refinement pipeline first.*")
        lines.append("")

    return "\n".join(lines)


def build_appendix_b(data_dir: str, run: TimestampedRun) -> str:
    """Appendix B: Composite Persona Construction."""
    lines = [
        "# Appendix B: Composite Persona Construction",
        "",
        "This appendix describes the methodology for constructing composite personas",
        "from FinePersonas descriptors matched with Synthea EHR records.",
        "",
        "## Methodology",
        "",
        "Each composite persona is built through a three-stage process:",
        "",
        "1. **FinePersonas filtering:** The HuggingFaceFW/FinePersonas-v0.1 dataset is",
        "   filtered for maternity-relevant descriptors using keyword matching and",
        "   LLM-assisted relevance scoring.",
        "",
        "2. **Synthea EHR matching:** Filtered personas are matched with synthetic",
        "   Electronic Health Records generated by Synthea, using SNOMED-CT pregnancy",
        "   codes to identify relevant patient records. Compatibility scoring considers",
        "   demographic alignment, journey stage, risk level, and clinical history.",
        "",
        "3. **Narrative enrichment:** Each matched pair is enriched with a 250-350 word",
        "   first-person narrative that integrates the persona descriptor with EHR",
        "   clinical details, vulnerability flags, and latent dimension seeds.",
        "",
        "## Persona Attributes",
        "",
        "Each composite persona includes:",
        "- Demographics (age, ethnicity, race, marital status, location)",
        "- Journey stage (preconception, first/second/third trimester, postpartum)",
        "- Risk level (low, medium, high)",
        "- Vulnerability flags (e.g., low_income, immigration, rural_isolation)",
        "- Latent dimension scores (power_dynamics, identity_tensions, structural_barriers, etc.)",
        "- Source EHR metadata (pregnancy count, complications, SNOMED codes)",
        "- Enriched first-person narrative",
        "",
    ]

    composites_path = os.path.join(data_dir, "composite_personas", "composites.jsonl")
    if os.path.exists(composites_path):
        run.record_read(composites_path)
        lines.append("## Example Personas (first 5)")
        lines.append("")

        with open(composites_path) as f:
            for i, line in enumerate(f):
                if i >= 5:
                    break
                persona = json.loads(line.strip())
                pid = persona.get("composite_id", f"comp_{i+1:03d}")
                name = persona.get("name", "Unknown")
                ptype = persona.get("type", "Unknown")
                stage = persona.get("journey_stage", "Unknown")
                risk = persona.get("risk_level", "Unknown")
                demo = persona.get("demographics", {})
                age = demo.get("age", "N/A")
                location = demo.get("location", "N/A")
                vuln = persona.get("vulnerability_flags", [])
                model = persona.get("target_model", "N/A")

                lines.append(f"### {pid}: {name}")
                lines.append("")
                lines.append(f"- **Type:** {ptype}")
                lines.append(f"- **Age:** {age}")
                lines.append(f"- **Location:** {location}")
                lines.append(f"- **Journey stage:** {stage}")
                lines.append(f"- **Risk level:** {risk}")
                lines.append(f"- **Vulnerability flags:** {', '.join(vuln) if vuln else 'None'}")
                lines.append(f"- **Target model:** {model}")
                lines.append("")

                narrative = persona.get("enriched_narrative", "")
                if narrative:
                    # Truncate to first 200 chars for the appendix
                    snippet = narrative[:200].rsplit(" ", 1)[0] + "..."
                    lines.append(f"> {snippet}")
                    lines.append("")
    else:
        lines.append("*composites.jsonl not found.*")
        lines.append("")

    return "\n".join(lines)


def build_appendix_c(data_dir: str, run: TimestampedRun) -> str:
    """Appendix C: Questionnaire Versions."""
    lines = [
        "# Appendix C: Questionnaire Versions",
        "",
        "This appendix summarises the five questionnaire versions generated",
        "through the questionnaire generation engine.",
        "",
        "## Version Summary",
        "",
        "| Version | Strategy | Questions | Journey Phases |",
        "|---------|----------|-----------|----------------|",
    ]

    for v in range(1, 6):
        q_path = os.path.join(data_dir, "questionnaires", f"Q_V{v}.json")
        if os.path.exists(q_path):
            run.record_read(q_path)
            with open(q_path) as f:
                qdata = json.load(f)

            strategy = qdata.get("strategy", {})
            strategy_name = strategy.get("name", "Unknown")
            questions = qdata.get("questions", [])
            num_questions = len(questions)
            phases = sorted(set(
                q.get("journey_phase", "")
                for q in questions
                if q.get("journey_phase", "")
            ))
            phases_str = ", ".join(phases) if phases else "N/A"

            lines.append(f"| V{v} | {strategy_name} | {num_questions} | {phases_str} |")
        else:
            lines.append(f"| V{v} | *File not found* | - | - |")

    lines.append("")

    # Detailed version descriptions
    for v in range(1, 6):
        q_path = os.path.join(data_dir, "questionnaires", f"Q_V{v}.json")
        if os.path.exists(q_path):
            with open(q_path) as f:
                qdata = json.load(f)
            strategy = qdata.get("strategy", {})
            lines.append(f"### Version {v}: {strategy.get('name', 'Unknown')}")
            lines.append("")
            lines.append(f"- **Tagline:** {strategy.get('tagline', 'N/A')}")
            lines.append(f"- **Structure:** {strategy.get('structure', 'N/A')}")
            lines.append(f"- **Framing:** {strategy.get('framing', 'N/A')}")
            lines.append(f"- **Probe intensity:** {strategy.get('probe_intensity', 'N/A')}")
            lines.append(f"- **Register:** {strategy.get('register', 'N/A')}")
            lines.append(f"- **Rationale:** {strategy.get('rationale', 'N/A')}")
            lines.append(f"- **Question type:** {strategy.get('question_type', 'N/A')}")
            strengths = strategy.get("strengths", [])
            if strengths:
                lines.append(f"- **Strengths:** {', '.join(strengths)}")
            risks = strategy.get("risks", [])
            if risks:
                lines.append(f"- **Risks:** {'; '.join(risks)}")
            lines.append("")

    return "\n".join(lines)


def build_appendix_d(data_dir: str, run: TimestampedRun) -> str:
    """Appendix D: Final Recommended Questionnaire."""
    lines = [
        "# Appendix D: Final Recommended Questionnaire",
        "",
    ]

    final_path = os.path.join(data_dir, "questionnaires", "final", "FINAL_QUESTIONNAIRE.md")
    if os.path.exists(final_path):
        run.record_read(final_path)
        with open(final_path) as f:
            content = f.read()
        lines.append(content)
    else:
        lines.append("*FINAL_QUESTIONNAIRE.md not found. Run the final selector first.*")

    lines.append("")
    return "\n".join(lines)


def build_appendix_e(src_dir: str, run: TimestampedRun) -> str:
    """Appendix E: Interview Protocol."""
    lines = [
        "# Appendix E: Interview Protocol",
        "",
        "## Multi-Provider Rotation Approach",
        "",
        "The synthetic interview pipeline uses a multi-provider rotation strategy",
        "to ensure response diversity and reduce single-model bias:",
        "",
        "1. **Interviewer agent:** A single model conducts all interviews for consistency",
        "   in question delivery and follow-up probing.",
        "",
        "2. **Persona agent (rotating):** The persona role-play responses rotate across",
        "   three providers (Anthropic, Google, OpenAI) to introduce stylistic and",
        "   reasoning diversity. Each provider brings different strengths:",
        "   - Anthropic models tend toward nuanced emotional expression",
        "   - Google models often provide structured, detail-rich responses",
        "   - OpenAI models balance narrative flow with analytical depth",
        "",
        "3. **BIBD assignment:** Sessions are assigned to versions and personas using a",
        "   Balanced Incomplete Block Design (BIBD) to ensure each persona encounters",
        "   exactly two versions, enabling within-subject comparison.",
        "",
        "## Interview Structure",
        "",
        "Each interview session follows this protocol:",
        "",
        "1. The interviewer agent presents questions from the assigned questionnaire version",
        "2. Questions are adapted to the persona's EHR profile (personalised probes)",
        "3. The persona agent responds in-character based on their enriched narrative",
        "4. The interviewer follows up with probes when responses lack depth",
        "5. A transcript is built with metadata (model, tokens, timing) for each turn",
        "",
    ]

    # Try to read system prompts from session_runner.py
    session_runner_path = os.path.join(src_dir, "orchestration", "session_runner.py")
    if os.path.exists(session_runner_path):
        run.record_read(session_runner_path)
        lines.append("## Session Runner Configuration")
        lines.append("")
        lines.append(f"The session runner is implemented in `{session_runner_path}` and supports:")
        lines.append("")
        lines.append("- Parallel session execution with configurable thread count")
        lines.append("- Resume support (skips already-completed sessions)")
        lines.append("- Per-environment cost ceilings (dev: $20, test: $50, prod: $100)")
        lines.append("- Automatic cost tracking across all LLM calls")
        lines.append("")

    # Try to read example system prompts from interviewer or persona agents
    interviewer_path = os.path.join(src_dir, "orchestration", "interviewer_agent.py")
    if os.path.exists(interviewer_path):
        run.record_read(interviewer_path)
        lines.append("## Example Interviewer System Prompt")
        lines.append("")
        lines.append("The interviewer agent uses a system prompt structured as follows:")
        lines.append("")
        lines.append("```")
        lines.append("You are a skilled qualitative researcher conducting a semi-structured")
        lines.append("interview about maternity care experiences. Your role is to:")
        lines.append("- Ask questions naturally, following the questionnaire structure")
        lines.append("- Use probes when responses lack depth or specificity")
        lines.append("- Maintain a warm, empathetic tone throughout")
        lines.append("- Adapt follow-up questions to the participant's specific context")
        lines.append("- Ensure all journey phases and latent dimensions are explored")
        lines.append("```")
        lines.append("")

    persona_path = os.path.join(src_dir, "orchestration", "persona_agent.py")
    if os.path.exists(persona_path):
        run.record_read(persona_path)
        lines.append("## Example Persona System Prompt")
        lines.append("")
        lines.append("Each persona agent receives a system prompt incorporating:")
        lines.append("")
        lines.append("```")
        lines.append("You are [Name], a [age]-year-old [type] in [location].")
        lines.append("[Enriched narrative providing backstory, emotional state,")
        lines.append(" clinical context, and vulnerability factors.]")
        lines.append("")
        lines.append("Respond as this person would in a real interview:")
        lines.append("- Stay in character throughout")
        lines.append("- Draw on your specific experiences and emotions")
        lines.append("- Be authentic — include hesitations, contradictions, and unspoken fears")
        lines.append("- Reference your medical history where relevant")
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def build_appendix_f(data_dir: str, run: TimestampedRun) -> str:
    """Appendix F: Statistical Supplement."""
    lines = [
        "# Appendix F: Statistical Supplement",
        "",
    ]

    # Paper tables
    tables_path = os.path.join(data_dir, "evaluation", "synthesis", "paper_tables.json")
    if os.path.exists(tables_path):
        run.record_read(tables_path)
        with open(tables_path) as f:
            tables = json.load(f)

        lines.append("## Evaluation Tables")
        lines.append("")

        table_labels = {
            "table1_quality_by_version": "Table 1: Quality Scores by Questionnaire Version",
            "table2_pairwise_effects": "Table 2: Pairwise Effect Sizes (Cohen's d)",
            "table3_within_subject": "Table 3: Within-Subject Comparisons (Wilcoxon Signed-Rank)",
            "table4_inter_rater": "Table 4: Inter-Rater Reliability (ICC and Krippendorff's alpha)",
            "table5_dimension_heatmap": "Table 5: Dimension Coverage Heatmap by Version",
        }

        for key, label in table_labels.items():
            if key in tables:
                lines.append(f"### {label}")
                lines.append("")
                md = tables[key].get("markdown", "")
                if md:
                    lines.append(md)
                lines.append("")
    else:
        lines.append("*paper_tables.json not found.*")
        lines.append("")

    # Saturation report
    sat_path = os.path.join(data_dir, "evaluation", "saturation", "saturation_report.md")
    if os.path.exists(sat_path):
        run.record_read(sat_path)
        with open(sat_path) as f:
            sat_content = f.read()

        lines.append("## Saturation Analysis")
        lines.append("")

        # Extract key tables from the saturation report (sections with | delimiters)
        in_table = False
        table_lines = []
        section_header = ""
        for sline in sat_content.split("\n"):
            if sline.startswith("##"):
                if table_lines:
                    lines.append(f"### Saturation: {section_header}")
                    lines.append("")
                    lines.extend(table_lines)
                    lines.append("")
                    table_lines = []
                section_header = sline.lstrip("#").strip()
                in_table = False
            elif "|" in sline:
                in_table = True
                table_lines.append(sline)
            elif in_table and sline.strip() == "":
                in_table = False
            elif in_table:
                table_lines.append(sline)

        # Flush remaining table
        if table_lines:
            lines.append(f"### Saturation: {section_header}")
            lines.append("")
            lines.extend(table_lines)
            lines.append("")
    else:
        lines.append("*saturation_report.md not found.*")
        lines.append("")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPERT EVALUATION GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════


def build_survey_instrument(timestamp: str) -> str:
    """Generate expert evaluation survey instrument with 7-point Likert scales."""
    lines = [
        f"# Expert Evaluation Survey Instrument",
        f"",
        f"**Generated:** {timestamp}",
        f"**Scale:** 7-point Likert (1 = Strongly Disagree, 7 = Strongly Agree)",
        f"",
        f"---",
        f"",
        f"## Part 1: Background Information",
        f"",
        f"Please provide the following background information:",
        f"",
        f"1. **Discipline / Field of expertise:**",
        f"   [ ] Obstetrics & Gynaecology",
        f"   [ ] Midwifery",
        f"   [ ] Nursing (Maternal/Neonatal)",
        f"   [ ] Public Health",
        f"   [ ] Health Services Research",
        f"   [ ] Health Informatics / Digital Health",
        f"   [ ] Social Work / Psychology",
        f"   [ ] Other: _______________",
        f"",
        f"2. **Years of experience in maternity-related research or practice:** ___",
        f"",
        f"3. **Country of primary practice/research:** _______________",
        f"",
        f"4. **Primary role:**",
        f"   [ ] Clinician",
        f"   [ ] Researcher",
        f"   [ ] Policy maker",
        f"   [ ] Educator",
        f"   [ ] Service designer",
        f"   [ ] Other: _______________",
        f"",
        f"---",
        f"",
        f"## Part 2: Dimension Ratings (7-point Likert)",
        f"",
        f"Please rate your agreement with each statement (1 = Strongly Disagree, 7 = Strongly Agree).",
        f"",
        f"### 2.1 Breadth of Coverage",
        f"",
        f"B1. The questionnaire covers the full spectrum of the maternity care journey",
        f"    (preconception through postpartum).",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"B2. The questionnaire addresses the diversity of maternity experiences across",
        f"    different demographic and socioeconomic groups.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"B3. The key service touchpoints in maternity care are adequately represented.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"### 2.2 Depth of Exploration",
        f"",
        f"D1. The probing strategy is likely to elicit nuanced, detailed responses",
        f"    beyond surface-level answers.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"D2. The questionnaire effectively surfaces latent or hidden dimensions of",
        f"    maternity experience (e.g., power dynamics, identity tensions).",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"### 2.3 Human-Centredness",
        f"",
        f"H1. The questions are framed in a way that centres the woman's/birthing",
        f"    person's perspective and agency.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"H2. The tone and language are appropriate, empathetic, and non-judgmental.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"H3. The questionnaire accommodates diverse cultural backgrounds and",
        f"    vulnerability factors.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"### 2.4 Innovation Relevance",
        f"",
        f"I1. The questionnaire is likely to generate insights that could inform",
        f"    service innovation in maternity care.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"I2. The gap-analysis approach (expectation vs. perception) effectively",
        f"    identifies opportunities for service improvement.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"### 2.5 Strategic Actionability",
        f"",
        f"S1. Findings from this questionnaire would be actionable for healthcare",
        f"    service planners and policy makers.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"S2. The questionnaire structure supports systematic comparison across",
        f"    different care settings or populations.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"### 2.6 Methodological Rigour",
        f"",
        f"M1. The questionnaire demonstrates sound qualitative research design",
        f"    principles.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"M2. The probes and follow-up structure support reliable, consistent",
        f"    data collection across different interviewers.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"M3. The instrument balances standardisation with flexibility for",
        f"    participant-led exploration.",
        f"    [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"---",
        f"",
        f"## Part 3: Open-Ended Questions",
        f"",
        f"Please provide detailed responses to the following questions:",
        f"",
        f"OE1. **Coverage:** Are there important aspects of the maternity care experience",
        f"     that this questionnaire fails to address? If so, what are they and why",
        f"     do you consider them important?",
        f"",
        f"     _______________________________________________________________",
        f"     _______________________________________________________________",
        f"",
        f"OE2. **Latent dimensions:** The questionnaire attempts to surface 'latent'",
        f"     dimensions such as power dynamics, identity tensions, and structural",
        f"     barriers. Are there additional latent dimensions that should be explored?",
        f"     How well does the current design capture these hidden aspects?",
        f"",
        f"     _______________________________________________________________",
        f"     _______________________________________________________________",
        f"",
        f"OE3. **Innovation opportunities:** Based on your expertise, what types of",
        f"     service innovations could be identified through this instrument that",
        f"     existing tools might miss?",
        f"",
        f"     _______________________________________________________________",
        f"     _______________________________________________________________",
        f"",
        f"OE4. **Gaps and risks:** What potential gaps or risks do you see in using",
        f"     this questionnaire for real-world maternity care research? Consider",
        f"     ethical, practical, and methodological dimensions.",
        f"",
        f"     _______________________________________________________________",
        f"     _______________________________________________________________",
        f"",
        f"OE5. **Governance:** This questionnaire was developed using a fully synthetic",
        f"     pipeline (AI-generated personas and interviews). What governance",
        f"     considerations should be addressed before deploying it with real",
        f"     participants?",
        f"",
        f"     _______________________________________________________________",
        f"     _______________________________________________________________",
        f"",
        f"OE6. **Improvements:** What specific changes would you recommend to strengthen",
        f"     this instrument for use in your own research or practice context?",
        f"",
        f"     _______________________________________________________________",
        f"     _______________________________________________________________",
        f"",
        f"---",
        f"",
        f"## Part 4: Overall Assessment",
        f"",
        f"OA1. **Overall quality rating:** On a scale of 1-7, how would you rate the",
        f"     overall quality of this research instrument?",
        f"     [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ]",
        f"",
        f"OA2. **Would you use this instrument (or an adapted version) in your own",
        f"     research or practice?**",
        f"     [ ] Yes",
        f"     [ ] No",
        f"     [ ] Maybe",
        f"",
        f"     Please explain your answer:",
        f"     _______________________________________________________________",
        f"     _______________________________________________________________",
        f"",
        f"---",
        f"",
        f"Thank you for your expert evaluation.",
    ]
    return "\n".join(lines)


def build_expert_briefing(
    questionnaire_path: str, timestamp: str, run: TimestampedRun
) -> str:
    """Generate expert briefing document with study context and the questionnaire."""
    lines = [
        f"# Expert Briefing: Synthetic Maternity Research Instrument Evaluation",
        f"",
        f"**Generated:** {timestamp}",
        f"",
        f"---",
        f"",
        f"## Study Purpose",
        f"",
        f"This study develops and evaluates a qualitative research instrument (semi-structured",
        f"interview questionnaire) for exploring maternity care experiences. The instrument",
        f"was developed using a novel synthetic research pipeline that combines:",
        f"",
        f"- **Composite personas:** 150 synthetic personas constructed from FinePersonas",
        f"  descriptors matched with Synthea-generated Electronic Health Records",
        f"- **Multi-version questionnaire design:** 5 questionnaire versions employing",
        f"  different interviewing strategies (chronological, thematic, scenario-based,",
        f"  expectation-perception gap, relational)",
        f"- **Synthetic interviews:** 300+ sessions using multi-provider AI rotation",
        f"  (Anthropic, Google, OpenAI) with BIBD experimental design",
        f"- **Iterative refinement:** Data-driven blind spot analysis, probe enrichment,",
        f"  and robustness testing across vulnerable populations",
        f"",
        f"The winning questionnaire version was selected based on composite quality",
        f"scoring (richness, surfacing rate, latent dimension coverage) and further",
        f"refined through one iteration of probe enhancement.",
        f"",
        f"## Your Task",
        f"",
        f"As a domain expert, you are asked to evaluate the **final recommended",
        f"questionnaire** presented below. Your evaluation will assess:",
        f"",
        f"1. Breadth of coverage across the maternity journey",
        f"2. Depth of exploration into nuanced experiences",
        f"3. Human-centredness and sensitivity",
        f"4. Potential to generate innovation-relevant insights",
        f"5. Strategic actionability for service improvement",
        f"6. Methodological rigour of the instrument design",
        f"",
        f"## Instructions",
        f"",
        f"1. Read the complete questionnaire below carefully",
        f"2. Consider how it would perform in a real interview with diverse",
        f"   maternity care service users",
        f"3. Complete the accompanying survey instrument",
        f"4. Provide honest, detailed feedback in the open-ended sections",
        f"",
        f"**Important:** This instrument was developed entirely through synthetic",
        f"methods (no real patients were involved). Your expert evaluation is a",
        f"critical validation step before any deployment with real participants.",
        f"",
        f"---",
        f"",
        f"## Final Recommended Questionnaire",
        f"",
    ]

    if os.path.exists(questionnaire_path):
        run.record_read(questionnaire_path)
        with open(questionnaire_path) as f:
            content = f.read()
        lines.append(content)
    else:
        lines.append(f"*Questionnaire file not found at: {questionnaire_path}*")

    lines.append("")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════════════════


def build_supplementary(src_dir: str, data_dir: str, output_dir: str) -> dict:
    """Build all 6 appendices and a combined file."""
    run = TimestampedRun(output_dir)
    results = {}

    appendices = [
        ("appendix_a_governance.md", lambda: build_appendix_a(data_dir, run)),
        ("appendix_b_personas.md", lambda: build_appendix_b(data_dir, run)),
        ("appendix_c_questionnaires.md", lambda: build_appendix_c(data_dir, run)),
        ("appendix_d_final_questionnaire.md", lambda: build_appendix_d(data_dir, run)),
        ("appendix_e_interview_protocol.md", lambda: build_appendix_e(src_dir, run)),
        ("appendix_f_statistical.md", lambda: build_appendix_f(data_dir, run)),
    ]

    combined_parts = []

    for filename, builder in appendices:
        log.info("Building %s ...", filename)
        content = builder()
        combined_parts.append(content)

        # Write timestamped version
        ts_path = run.output_path(filename)
        with open(ts_path, "w") as f:
            f.write(content)
        run.stable_pointer(filename, ts_path)
        results[filename] = ts_path
        log.info("  -> %s", ts_path)

    # Combined file
    combined_content = "\n\n---\n\n".join(combined_parts)
    combined_header = (
        "# Supplementary Materials\n\n"
        f"**Generated:** {run.timestamp}\n\n"
        "This document contains all supplementary appendices for the\n"
        "synthetic maternity research study.\n\n---\n\n"
    )
    combined = combined_header + combined_content

    ts_combined = run.output_path("supplementary_combined.md")
    with open(ts_combined, "w") as f:
        f.write(combined)
    run.stable_pointer("supplementary_combined.md", ts_combined)
    results["supplementary_combined.md"] = ts_combined
    log.info("Combined file -> %s", ts_combined)

    run.write_manifest("supplementary_builder", config={
        "src_dir": src_dir,
        "data_dir": data_dir,
        "output_dir": output_dir,
    })

    return results


def build_expert_evaluation(
    questionnaire_path: str, output_dir: str
) -> dict:
    """Build expert evaluation materials (survey + briefing)."""
    run = TimestampedRun(output_dir)
    results = {}

    # Survey instrument
    log.info("Building survey instrument ...")
    survey_content = build_survey_instrument(run.timestamp)
    survey_filename = "survey_instrument.md"
    ts_survey = run.output_path(survey_filename)
    with open(ts_survey, "w") as f:
        f.write(survey_content)
    run.stable_pointer(survey_filename, ts_survey)
    results[survey_filename] = ts_survey
    log.info("  -> %s", ts_survey)

    # Expert briefing
    log.info("Building expert briefing ...")
    briefing_content = build_expert_briefing(questionnaire_path, run.timestamp, run)
    briefing_filename = "expert_briefing.md"
    ts_briefing = run.output_path(briefing_filename)
    with open(ts_briefing, "w") as f:
        f.write(briefing_content)
    run.stable_pointer(briefing_filename, ts_briefing)
    results[briefing_filename] = ts_briefing
    log.info("  -> %s", ts_briefing)

    run.write_manifest("expert_evaluation_builder", config={
        "questionnaire_path": questionnaire_path,
        "output_dir": output_dir,
    })

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Build supplementary materials for the synthetic maternity study."
    )
    parser.add_argument(
        "--src", default="src/",
        help="Path to source code directory (default: src/)"
    )
    parser.add_argument(
        "--data", default="data/",
        help="Path to data directory (default: data/)"
    )
    parser.add_argument(
        "--output", default="docs/supplementary/",
        help="Output directory for generated files (default: docs/supplementary/)"
    )
    parser.add_argument(
        "--expert-evaluation", action="store_true",
        help="Generate expert evaluation materials instead of appendices"
    )
    parser.add_argument(
        "--questionnaire",
        default="data/questionnaires/final/FINAL_QUESTIONNAIRE.md",
        help="Path to the final questionnaire (for expert evaluation mode)"
    )

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if args.expert_evaluation:
        log.info("=== Expert Evaluation Mode ===")
        results = build_expert_evaluation(args.questionnaire, args.output)
    else:
        log.info("=== Supplementary Materials Mode ===")
        results = build_supplementary(args.src, args.data, args.output)

    log.info("")
    log.info("=== Files Generated ===")
    for name, path in results.items():
        log.info("  %s -> %s", name, path)
    log.info("Done.")


if __name__ == "__main__":
    main()

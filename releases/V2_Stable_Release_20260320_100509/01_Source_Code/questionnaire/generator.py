"""
Questionnaire Version Generator — creates structured maternity-care questionnaires
using LLM calls guided by theoretical frameworks.

Usage:
    python -m src.questionnaire.generator --versions 1 --output data/questionnaires/
    python -m src.questionnaire.generator --versions 1,2,3,4,5 --output data/questionnaires/
    python -m src.questionnaire.generator --compare --output data/questionnaires/
"""
import os, json, re, argparse, logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from src.config.models import (
    get_model, get_provider, get_token_policy, tracker, ENV,
)
from src.questionnaire.frameworks import (
    JOURNEY_PHASES, KBV_DIMENSIONS, LATENT_DIMENSIONS,
    THEMATIC_TARGETS, EVALUATION_CRITERIA, SERVQUAL_DIMENSIONS,
    MATERNITY_SPECIFIC_DIMENSIONS, PROBE_TYPES, VERSION_STRATEGIES,
    COVERAGE_MATRIX, get_all_cells, get_version_strategy,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

TASK_NAME = "questionnaire_generation"


# ── LLM call ────────────────────────────────────────────────────────────────

def _llm_call(system_prompt: str, user_prompt: str) -> str:
    """Call the configured LLM for questionnaire generation."""
    provider = get_provider(TASK_NAME)
    model = get_model(TASK_NAME)
    policy = get_token_policy()
    # Questionnaire generation produces large structured JSON (20-30 questions
    # with 3-5 probes each); needs very high output limits.
    max_tokens = 32768

    # Google thinking models consume output budget for reasoning
    if provider == "google":
        max_tokens = max(max_tokens * 4, 65000)

    try:
        if provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            # Use streaming to handle large outputs (>10 min timeout)
            text_parts = []
            in_tok, out_tok = 0, 0
            with client.messages.stream(
                model=model, max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                for event_text in stream.text_stream:
                    text_parts.append(event_text)
            msg = stream.get_final_message()
            text = "".join(text_parts).strip()
            in_tok, out_tok = msg.usage.input_tokens, msg.usage.output_tokens

        elif provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            gm = genai.GenerativeModel(model_name=model,
                                       system_instruction=system_prompt)
            r = gm.generate_content(user_prompt,
                                    generation_config={"max_output_tokens": max_tokens})
            text = r.text.strip()
            try:
                in_tok = r.usage_metadata.prompt_token_count
                out_tok = r.usage_metadata.candidates_token_count
            except AttributeError:
                in_tok, out_tok = 0, 0

        elif provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            r = client.chat.completions.create(
                model=model, max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = r.choices[0].message.content.strip()
            in_tok = r.usage.prompt_tokens
            out_tok = r.usage.completion_tokens
        else:
            raise ValueError(f"Unknown provider: {provider}")

        tracker.record(TASK_NAME, provider, model, in_tok, out_tok)
        log.info(f"  LLM call ({provider}/{model}): {in_tok}+{out_tok} tok")
        return text

    except Exception as e:
        log.error(f"  LLM error: {e}")
        raise


# ── Prompt construction ─────────────────────────────────────────────────────

def _build_system_prompt() -> str:
    return """You are an expert in qualitative maternity-care research instrument design.
You have deep expertise in Knowledge-Based View (KBV) methodology, SERVQUAL service
quality assessment, and qualitative interview guide construction.

Your task is to create a structured maternity-care questionnaire version with questions
that operationalise multiple theoretical frameworks simultaneously. Every question must:
1. Target at least one KBV dimension (goals, motivations, behaviours, latent needs)
2. Be relevant to a specific journey phase (preconception, pregnancy, birth, postpartum)
3. Include probes designed to surface specific latent dimensions
4. Be tagged with thematic targets and evaluation contribution estimates

You MUST output ONLY valid JSON. No markdown, no commentary outside the JSON.
Return a JSON object with a "questions" array containing all questions."""


def _build_version_prompt(version: int) -> str:
    strategy = get_version_strategy(version)
    if not strategy:
        raise ValueError(f"Unknown version: {version}")

    # Encode frameworks compactly
    phases_desc = "\n".join(
        f"  - {k}: {v['description']} Key concerns: {', '.join(v['key_concerns'][:4])}"
        for k, v in JOURNEY_PHASES.items()
    )
    kbv_desc = "\n".join(
        f"  - {k}: {v['description']}"
        for k, v in KBV_DIMENSIONS.items()
    )
    latent_desc = "\n".join(
        f"  - {k}: {v['description']}"
        for k, v in LATENT_DIMENSIONS.items()
    )
    targets_desc = "\n".join(
        f"  - {k}: {v['description']}"
        for k, v in THEMATIC_TARGETS.items()
    )
    servqual_desc = "\n".join(
        f"  - {k}: {v['description']}"
        for k, v in SERVQUAL_DIMENSIONS.items()
    )
    maternity_desc = "\n".join(
        f"  - {k}: {v['description']}"
        for k, v in MATERNITY_SPECIFIC_DIMENSIONS.items()
    )
    probe_desc = "\n".join(
        f"  - {k}: {v['description']}"
        for k, v in PROBE_TYPES.items()
    )
    eval_desc = "\n".join(
        f"  - {k}: {v['description']}"
        for k, v in EVALUATION_CRITERIA.items()
    )

    # SNOMED codes commonly relevant
    snomed_ref = """Common SNOMED codes for triggers:
  72892002 = Normal pregnancy, 77386006 = Pregnancy (finding),
  48194001 = Pregnancy-related condition, 15394000 = Pre-eclampsia,
  11687002 = Gestational diabetes, 17369002 = Miscarriage,
  386639001 = Tokophobia, 161744009 = History of miscarriage,
  200839001 = Antepartum hemorrhage, 69896004 = Rhesus negative"""

    return f"""Generate questionnaire VERSION {version}: "{strategy['name']}" ({strategy['tagline']}).

DESIGN STRATEGY:
  Structure: {strategy['structure']}
  Framing: {strategy['framing']}
  Probe intensity: {strategy['probe_intensity']}
  Register: {strategy['register']}
  Rationale: {strategy['rationale']}
  Primary question type: {strategy['question_type']}

THEORETICAL FRAMEWORKS TO OPERATIONALISE:

JOURNEY PHASES:
{phases_desc}

KBV DIMENSIONS:
{kbv_desc}

LATENT DIMENSIONS (must be surfaced through probes, NOT asked directly):
{latent_desc}

THEMATIC TARGETS (each question should target 1-2):
{targets_desc}

SERVQUAL DIMENSIONS:
{servqual_desc}

MATERNITY-SPECIFIC QUALITY:
{maternity_desc}

PROBE TYPES (distribute across all types, not just elaboration):
{probe_desc}

EVALUATION CRITERIA (the questionnaire will be assessed on):
{eval_desc}

{snomed_ref}

REQUIREMENTS:
- Generate 20-30 questions total
- 5-8 questions per journey phase (preconception, pregnancy, birth, postpartum)
- Each question targets 1-2 KBV dimensions and 1-2 thematic areas
- Each question has {strategy['probe_intensity']}
- Each probe targets specific latent dimensions
- Distribute probe types (clarification, motivation, elaboration, contrast, emotion, structural)
- Include ehr_adaptation_triggers where relevant (e.g., "if_high_risk", "if_miscarriage_history",
  "if_gestational_diabetes", "if_single_parent", "if_language_barrier", "if_rural")
- Include snomed_context_codes where applicable
- Rate expected_evaluation_contribution for each question (breadth, depth, innovation_relevance:
  "high", "medium", "low")

OUTPUT FORMAT: Return ONLY a JSON object with this structure:
{{
  "questions": [
    {{
      "question_id": "V{version}_PREC_Q01",
      "version": {version},
      "journey_phase": "preconception",
      "question_text": "...",
      "question_type": "{strategy['question_type']}",
      "probes": [
        {{
          "probe_id": "V{version}_PREC_Q01_P01",
          "probe_text": "...",
          "probe_type": "clarification",
          "target_latent_dimensions": ["power_dynamics"]
        }}
      ],
      "target_kbv_dimensions": ["goals"],
      "target_thematic_areas": ["goals_expectations"],
      "target_servqual_dimensions": ["empathy"],
      "target_latent_dimensions": ["autonomy_vs_dependence"],
      "expected_evaluation_contribution": {{
        "breadth": "high",
        "depth": "medium",
        "innovation_relevance": "high"
      }},
      "snomed_context_codes": [],
      "ehr_adaptation_triggers": []
    }}
  ]
}}

Generate the complete questionnaire now. Output ONLY the JSON object."""


# ── Parsing ─────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences and truncation."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try extracting from markdown code fence
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Try finding first { to last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    # Handle truncated JSON: find last complete question object and close the array
    if start != -1:
        fragment = text[start:]
        # Find the last complete "}" that could close a question object
        # by looking for "}," or "}\n" patterns followed by incomplete data
        last_complete = fragment.rfind("},")
        if last_complete == -1:
            last_complete = fragment.rfind("}\n")
        if last_complete > 0:
            repaired = fragment[:last_complete + 1] + "]}"
            try:
                result = json.loads(repaired)
                log.warning(f"  Repaired truncated JSON ({len(text)} chars → "
                            f"{len(result.get('questions', []))} questions)")
                return result
            except json.JSONDecodeError:
                pass
    raise ValueError(f"Could not parse JSON from LLM response ({len(text)} chars)")


# ── Coverage validation ─────────────────────────────────────────────────────

def validate_coverage(questions: list, version: int) -> dict:
    """Check that all coverage matrix cells have at least one question."""
    # Build map of what's covered
    covered = defaultdict(lambda: defaultdict(set))  # phase -> target -> latent_dims
    for q in questions:
        phase = q.get("journey_phase", "")
        for target in q.get("target_thematic_areas", []):
            for probe in q.get("probes", []):
                if isinstance(probe, dict):
                    for dim in probe.get("target_latent_dimensions", []):
                        covered[phase][target].add(dim)
            for dim in q.get("target_latent_dimensions", []):
                if isinstance(dim, str):
                    covered[phase][target].add(dim)

    gaps = []
    for phase, targets in COVERAGE_MATRIX.items():
        for target, expected_dims in targets.items():
            actual = covered.get(phase, {}).get(target, set())
            missing = [d for d in expected_dims if d not in actual]
            if missing:
                gaps.append({
                    "phase": phase,
                    "target": target,
                    "missing_dimensions": missing,
                    "covered_dimensions": sorted(actual),
                })

    # Phase-level checks
    phase_counts = defaultdict(int)
    for q in questions:
        phase_counts[q.get("journey_phase", "")] += 1

    phase_gaps = []
    for phase in JOURNEY_PHASES:
        count = phase_counts.get(phase, 0)
        if count < 5:
            phase_gaps.append({"phase": phase, "count": count, "minimum": 5})

    # Latent dimension coverage across all questions
    latent_coverage = defaultdict(int)
    for q in questions:
        seen = set()
        for probe in q.get("probes", []):
            if isinstance(probe, dict):
                for dim in probe.get("target_latent_dimensions", []):
                    if isinstance(dim, str):
                        seen.add(dim)
        for dim in q.get("target_latent_dimensions", []):
            if isinstance(dim, str):
                seen.add(dim)
        for dim in seen:
            latent_coverage[dim] += 1

    dim_gaps = []
    for dim in LATENT_DIMENSIONS:
        if latent_coverage.get(dim, 0) < 3:
            dim_gaps.append({"dimension": dim, "count": latent_coverage.get(dim, 0), "minimum": 3})

    return {
        "total_questions": len(questions),
        "phase_counts": dict(phase_counts),
        "matrix_gaps": gaps,
        "phase_gaps": phase_gaps,
        "dimension_gaps": dim_gaps,
        "total_gaps": len(gaps) + len(phase_gaps) + len(dim_gaps),
    }


def generate_gap_fill_questions(gaps: dict, version: int) -> list:
    """Generate additional questions to fill coverage gaps."""
    matrix_gaps = gaps.get("matrix_gaps", [])
    dim_gaps = gaps.get("dimension_gaps", [])

    if not matrix_gaps and not dim_gaps:
        return []

    gap_desc = []
    for g in matrix_gaps[:10]:
        gap_desc.append(
            f"  - Phase '{g['phase']}' × Target '{g['target']}': "
            f"missing latent dimensions: {', '.join(g['missing_dimensions'])}"
        )
    for g in dim_gaps:
        gap_desc.append(
            f"  - Latent dimension '{g['dimension']}' only covered by {g['count']} questions (need ≥3)"
        )

    strategy = get_version_strategy(version)
    prompt = f"""The questionnaire VERSION {version} ("{strategy['name']}") has coverage gaps.
Generate additional questions to fill these gaps. Follow the same design strategy:
  Register: {strategy['register']}
  Question type: {strategy['question_type']}

GAPS TO FILL:
{chr(10).join(gap_desc)}

Generate 3-8 additional questions targeting these specific gaps.
Each question must follow the exact same JSON schema as the main questionnaire.
Use question IDs like V{version}_GAP_Q01, V{version}_GAP_Q02, etc.

Return ONLY a JSON object: {{"questions": [...]}}"""

    system = _build_system_prompt()
    text = _llm_call(system, prompt)
    data = _extract_json(text)
    return data.get("questions", [])


# ── Version generation ──────────────────────────────────────────────────────

def generate_version(version: int) -> dict:
    """Generate a complete questionnaire version."""
    strategy = get_version_strategy(version)
    log.info(f"\n{'='*60}")
    log.info(f"Generating VERSION {version}: {strategy['name']}")
    log.info(f"{'='*60}")

    system = _build_system_prompt()
    user = _build_version_prompt(version)
    log.info(f"  Prompt size: ~{len(system + user)} chars")

    # Step A: Generate base questions
    log.info(f"  Step A: Generating base questions...")
    text = _llm_call(system, user)
    data = _extract_json(text)
    questions = data.get("questions", [])
    log.info(f"  Generated {len(questions)} base questions")

    # Step B: Validate coverage
    log.info(f"  Step B: Validating coverage...")
    coverage = validate_coverage(questions, version)
    log.info(f"  Phase counts: {coverage['phase_counts']}")
    log.info(f"  Coverage gaps: {coverage['total_gaps']} "
             f"(matrix={len(coverage['matrix_gaps'])}, "
             f"phase={len(coverage['phase_gaps'])}, "
             f"dimension={len(coverage['dimension_gaps'])})")

    # Fill gaps if needed
    if coverage["total_gaps"] > 0:
        log.info(f"  Generating gap-fill questions...")
        fill = generate_gap_fill_questions(coverage, version)
        if fill:
            questions.extend(fill)
            log.info(f"  Added {len(fill)} gap-fill questions (total: {len(questions)})")
            coverage = validate_coverage(questions, version)
            log.info(f"  Post-fill gaps: {coverage['total_gaps']}")

    return {
        "version": version,
        "strategy": strategy,
        "questions": questions,
        "coverage": coverage,
        "generated_at": datetime.now().isoformat(),
        "model": f"{get_provider(TASK_NAME)}/{get_model(TASK_NAME)}",
        "environment": ENV.value,
    }


# ── Export ───────────────────────────────────────────────────────────────────

def export_version_json(version_data: dict, output_dir: Path):
    """Export structured JSON."""
    v = version_data["version"]
    path = output_dir / f"Q_V{v}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(version_data, f, indent=2, ensure_ascii=False)
    log.info(f"  Exported JSON → {path}")
    return path


def export_version_md(version_data: dict, output_dir: Path):
    """Export human-readable markdown."""
    v = version_data["version"]
    strategy = version_data["strategy"]
    questions = version_data["questions"]
    path = output_dir / f"Q_V{v}.md"

    lines = [
        f"# Questionnaire Version {v}: {strategy['name']}",
        f"",
        f"**Strategy:** {strategy['tagline']}  ",
        f"**Structure:** {strategy['structure']}  ",
        f"**Register:** {strategy['register']}  ",
        f"**Generated:** {version_data['generated_at']}  ",
        f"**Model:** {version_data['model']}  ",
        f"**Total questions:** {len(questions)}  ",
        f"",
        f"---",
        f"",
    ]

    # Group by phase
    by_phase = defaultdict(list)
    for q in questions:
        by_phase[q.get("journey_phase", "other")].append(q)

    for phase_key in ["preconception", "pregnancy", "birth", "postpartum", "other"]:
        phase_qs = by_phase.get(phase_key, [])
        if not phase_qs:
            continue
        phase_info = JOURNEY_PHASES.get(phase_key, {"label": phase_key.title()})
        label = phase_info.get("label", phase_key.title()) if isinstance(phase_info, dict) else phase_key.title()
        lines.append(f"## {label} ({len(phase_qs)} questions)")
        lines.append("")

        for q in phase_qs:
            qid = q.get("question_id", "?")
            lines.append(f"### {qid}")
            lines.append(f"")
            lines.append(f"**{q.get('question_text', '')}**")
            lines.append(f"")
            lines.append(f"- Type: {q.get('question_type', '')}")
            lines.append(f"- KBV: {', '.join(q.get('target_kbv_dimensions', []))}")
            lines.append(f"- Thematic: {', '.join(q.get('target_thematic_areas', []))}")
            lines.append(f"- Latent: {', '.join(q.get('target_latent_dimensions', []))}")

            contrib = q.get("expected_evaluation_contribution", {})
            if contrib:
                lines.append(f"- Evaluation: breadth={contrib.get('breadth','?')}, "
                             f"depth={contrib.get('depth','?')}, "
                             f"innovation={contrib.get('innovation_relevance','?')}")

            triggers = q.get("ehr_adaptation_triggers", [])
            if triggers:
                lines.append(f"- EHR triggers: {', '.join(triggers)}")

            lines.append(f"")
            lines.append(f"**Probes:**")
            for p in q.get("probes", []):
                if isinstance(p, str):
                    lines.append(f"  - {p}")
                    continue
                dims = ", ".join(p.get("target_latent_dimensions", []))
                lines.append(f"  - [{p.get('probe_type', '?')}] {p.get('probe_text', '')}")
                if dims:
                    lines.append(f"    *(targets: {dims})*")
            lines.append("")
            lines.append("---")
            lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log.info(f"  Exported MD → {path}")
    return path


# ── Version comparison ──────────────────────────────────────────────────────

def generate_comparison(versions: list, output_dir: Path):
    """Generate cross-version comparison matrix."""
    log.info(f"\nGenerating version comparison for {len(versions)} versions...")

    comparison = {
        "generated_at": datetime.now().isoformat(),
        "environment": ENV.value,
        "versions_compared": [v["version"] for v in versions],
        "dimension_emphasis": {},
        "phase_balance": {},
        "evaluation_profile": {},
        "overlap_analysis": {},
    }

    # Dimension emphasis per version
    for v_data in versions:
        v = v_data["version"]
        dim_counts = defaultdict(int)
        for q in v_data["questions"]:
            for d in q.get("target_latent_dimensions", []):
                if isinstance(d, str):
                    dim_counts[d] += 1
            for p in q.get("probes", []):
                if isinstance(p, dict):
                    for d in p.get("target_latent_dimensions", []):
                        if isinstance(d, str):
                            dim_counts[d] += 1
        comparison["dimension_emphasis"][f"V{v}"] = dict(
            sorted(dim_counts.items(), key=lambda x: -x[1])
        )

    # Phase balance
    for v_data in versions:
        v = v_data["version"]
        phase_counts = defaultdict(int)
        for q in v_data["questions"]:
            phase_counts[q.get("journey_phase", "?")] += 1
        comparison["phase_balance"][f"V{v}"] = dict(phase_counts)

    # Evaluation profile from question-level ratings
    for v_data in versions:
        v = v_data["version"]
        profile = defaultdict(lambda: {"high": 0, "medium": 0, "low": 0})
        for q in v_data["questions"]:
            contrib = q.get("expected_evaluation_contribution", {})
            for criterion, rating in contrib.items():
                if rating in profile[criterion]:
                    profile[criterion][rating] += 1
        comparison["evaluation_profile"][f"V{v}"] = {
            k: dict(v) for k, v in profile.items()
        }

    # Overlap: count shared thematic_target sets between versions
    target_sets = {}
    for v_data in versions:
        v = v_data["version"]
        target_sets[v] = set()
        for q in v_data["questions"]:
            key = (q.get("journey_phase", ""),
                   tuple(sorted(q.get("target_thematic_areas", []))))
            target_sets[v].add(key)

    for i, v1 in enumerate(versions):
        for v2 in versions[i + 1:]:
            key = f"V{v1['version']}_vs_V{v2['version']}"
            s1, s2 = target_sets[v1["version"]], target_sets[v2["version"]]
            overlap = len(s1 & s2)
            union = len(s1 | s2)
            comparison["overlap_analysis"][key] = {
                "shared_cells": overlap,
                "total_cells": union,
                "overlap_pct": round(overlap / max(union, 1) * 100, 1),
            }

    # Export JSON
    json_path = output_dir / "version_comparison.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    # Export MD
    md_path = output_dir / "version_comparison.md"
    md_lines = [
        "# Questionnaire Version Comparison",
        f"",
        f"Generated: {comparison['generated_at']}",
        f"",
        "## Dimension Emphasis (question + probe counts)",
        "",
    ]
    # Table header
    all_dims = sorted(set(
        d for v in comparison["dimension_emphasis"].values() for d in v
    ))
    header = "| Dimension | " + " | ".join(f"V{v['version']}" for v in versions) + " |"
    sep = "|---|" + "|".join(["---"] * len(versions)) + "|"
    md_lines.extend([header, sep])
    for dim in all_dims:
        row = f"| {dim} | "
        row += " | ".join(
            str(comparison["dimension_emphasis"].get(f"V{v['version']}", {}).get(dim, 0))
            for v in versions
        )
        row += " |"
        md_lines.append(row)

    md_lines.extend(["", "## Phase Balance", ""])
    header = "| Phase | " + " | ".join(f"V{v['version']}" for v in versions) + " |"
    md_lines.extend([header, sep])
    for phase in JOURNEY_PHASES:
        row = f"| {phase} | "
        row += " | ".join(
            str(comparison["phase_balance"].get(f"V{v['version']}", {}).get(phase, 0))
            for v in versions
        )
        row += " |"
        md_lines.append(row)

    md_lines.extend(["", "## Overlap Analysis", ""])
    for key, data in comparison["overlap_analysis"].items():
        md_lines.append(f"- **{key}**: {data['overlap_pct']}% overlap "
                        f"({data['shared_cells']}/{data['total_cells']} cells)")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # Coverage matrix JSON
    coverage_path = output_dir / "coverage_matrix.json"
    coverage = {}
    for v_data in versions:
        v = v_data["version"]
        coverage[f"V{v}"] = v_data["coverage"]
    with open(coverage_path, "w", encoding="utf-8") as f:
        json.dump(coverage, f, indent=2, ensure_ascii=False)

    log.info(f"  Comparison → {json_path}")
    log.info(f"  Comparison MD → {md_path}")
    log.info(f"  Coverage matrix → {coverage_path}")
    return comparison


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Questionnaire Version Generator")
    parser.add_argument("--versions", type=str, default="1",
                        help="Comma-separated version numbers (e.g., '1,2,3,4,5')")
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--compare", action="store_true",
                        help="Generate comparison from existing version files")
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    log.info(f"Environment: {ENV.value}")
    log.info(f"Model: {get_provider(TASK_NAME)}/{get_model(TASK_NAME)}")
    log.info(f"Token policy: max_output={get_token_policy().max_output_tokens}")

    if args.compare:
        # Load existing versions
        versions = []
        for vf in sorted(out.glob("Q_V*.json")):
            if "comparison" not in vf.name:
                with open(vf) as f:
                    versions.append(json.load(f))
        if not versions:
            log.error("No version files found for comparison")
            return
        generate_comparison(versions, out)
    else:
        version_nums = [int(v.strip()) for v in args.versions.split(",")]
        log.info(f"Generating versions: {version_nums}")

        all_versions = []
        for vn in version_nums:
            v_data = generate_version(vn)
            export_version_json(v_data, out)
            export_version_md(v_data, out)
            all_versions.append(v_data)

            log.info(f"  V{vn} summary: {len(v_data['questions'])} questions, "
                     f"{v_data['coverage']['total_gaps']} gaps remaining")

        if len(all_versions) > 1:
            generate_comparison(all_versions, out)

    # Cost summary
    cost = tracker.summary()
    if cost["total_calls"] > 0:
        log.info(f"\n{'='*60}")
        log.info("COST TRACKING SUMMARY")
        log.info(f"{'='*60}")
        log.info(f"  Total LLM calls:    {cost['total_calls']}")
        log.info(f"  Total input tokens:  {cost['total_input_tokens']:,}")
        log.info(f"  Total output tokens: {cost['total_output_tokens']:,}")
        log.info(f"  Total cost (USD):   ${cost['total_cost_usd']:.4f}")
        for task, info in cost["by_task"].items():
            log.info(f"    {task:<30s} {info['calls']:>3d} calls  ${info['cost_usd']:.4f}")
        log.info(f"{'='*60}")


if __name__ == "__main__":
    main()

"""
Robustness Reporter — produces pass/fail robustness report from adversarial scores.

No LLM calls — pure computation on scored adversarial data.

Usage:
    python -m src.refinement.robustness_reporter \
        --adversarial-scores data/evaluation/adversarial/quality_scores.jsonl \
        --adversarial-personas data/refinement/adversarial_personas.jsonl \
        --adversarial-transcripts data/transcripts/adversarial/ \
        --population-scores data/evaluation/refinement/scoring_summary.json \
        --output data/evaluation/adversarial/
"""
import json
import argparse
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime

import numpy as np

from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

PASS_THRESHOLD = 0.50  # richness must exceed 50% of population mean


def load_jsonl(path: str) -> list:
    records = []
    p = Path(path)
    if not p.exists():
        return records
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def analyse_robustness(adversarial_scores: list, personas: dict,
                       transcripts: dict, population_mean: float,
                       population_dim_means: dict) -> dict:
    """Analyse robustness per adversarial profile."""
    # Group scores by session
    by_session = defaultdict(list)
    for s in adversarial_scores:
        by_session[s["session_id"]].append(s)

    results = []
    for sid, scores in sorted(by_session.items()):
        # Find matching persona
        persona = personas.get(sid, {})
        transcript = transcripts.get(sid, {})

        # Compute mean richness for this session
        richness_vals = [s.get("composite_richness", 0) for s in scores]
        mean_richness = float(np.mean(richness_vals)) if richness_vals else 0

        # Per-dimension scores
        dim_scores = defaultdict(list)
        for s in scores:
            sc = s.get("scores", {})
            for dim, val in sc.items():
                dim_scores[dim].append(val)
        dim_means = {dim: float(np.mean(vals)) for dim, vals in dim_scores.items()}

        # Dimensions surfaced
        dims_surfaced = set()
        dims_absent = set()
        for s in scores:
            for d in s.get("latent_dimensions_surfaced", []):
                dims_surfaced.add(d)
            for d in s.get("latent_dimensions_encoded_but_absent", []):
                dims_absent.add(d)

        # KBV dimensions
        kbv_present = set()
        for s in scores:
            for k in s.get("kbv_dimensions_present", []):
                kbv_present.add(k)

        # Pass/fail
        threshold = population_mean * PASS_THRESHOLD
        passed = mean_richness >= threshold
        ratio = mean_richness / population_mean if population_mean > 0 else 0

        # Response analysis from transcript
        n_turns = transcript.get("metadata", {}).get("total_turns", 0)
        n_questions = transcript.get("metadata", {}).get("questions_asked", 0)
        n_probes = transcript.get("metadata", {}).get("probes_deployed", 0)

        # Assess interviewer adaptation
        adaptation_notes = []
        turns = transcript.get("turns", [])
        persona_responses = [t for t in turns if t.get("role") == "persona"]
        if persona_responses:
            avg_response_len = np.mean([len(t.get("text", "")) for t in persona_responses])
            if avg_response_len < 100:
                adaptation_notes.append("Short responses suggest challenging engagement")
            if avg_response_len > 300:
                adaptation_notes.append("Substantive responses achieved despite adversarial profile")

        # Dimension-level comparison
        dim_comparison = {}
        for dim, pop_mean in population_dim_means.items():
            adv_mean = dim_means.get(dim, 0)
            dim_comparison[dim] = {
                "adversarial": round(adv_mean, 2),
                "population": round(pop_mean, 2),
                "ratio": round(adv_mean / pop_mean, 2) if pop_mean > 0 else 0,
                "pass": adv_mean >= pop_mean * PASS_THRESHOLD,
            }

        results.append({
            "session_id": sid,
            "profile_type": persona.get("profile_type", "unknown"),
            "persona_name": persona.get("name", "unknown"),
            "test_objective": persona.get("test_objective", ""),
            "mean_richness": round(mean_richness, 2),
            "population_mean": round(population_mean, 2),
            "ratio_to_population": round(ratio, 2),
            "threshold": round(threshold, 2),
            "passed": passed,
            "n_responses_scored": len(scores),
            "n_turns": n_turns,
            "n_questions": n_questions,
            "n_probes": n_probes,
            "dimensions_surfaced": sorted(dims_surfaced),
            "dimensions_absent": sorted(dims_absent),
            "kbv_dimensions_present": sorted(kbv_present),
            "dimension_scores": dim_means,
            "dimension_comparison": dim_comparison,
            "adaptation_notes": adaptation_notes,
        })

    # Overall verdict
    n_pass = sum(1 for r in results if r["passed"])
    n_total = len(results)

    if n_total == 0:
        verdict = "No adversarial profiles tested"
        verdict_detail = ""
    elif n_pass == n_total:
        verdict = "Robust across vulnerable populations"
        verdict_detail = (f"All {n_total} adversarial profiles exceeded the {PASS_THRESHOLD:.0%} "
                          f"threshold (richness > {population_mean * PASS_THRESHOLD:.2f})")
    elif n_pass >= n_total * 0.6:
        failing = [r["profile_type"] for r in results if not r["passed"]]
        verdict = "Partially robust; specific adaptations needed"
        verdict_detail = (f"{n_pass}/{n_total} profiles passed. "
                          f"Failing profiles: {', '.join(failing)}")
    else:
        verdict = "Not robust; instrument requires significant adaptation"
        verdict_detail = f"Only {n_pass}/{n_total} profiles passed the threshold"

    return {
        "profiles": results,
        "summary": {
            "n_profiles": n_total,
            "n_passed": n_pass,
            "n_failed": n_total - n_pass,
            "pass_rate": round(n_pass / n_total, 2) if n_total > 0 else 0,
            "verdict": verdict,
            "verdict_detail": verdict_detail,
            "threshold_pct": PASS_THRESHOLD,
            "population_mean_richness": round(population_mean, 2),
            "adversarial_mean_richness": round(float(np.mean([r["mean_richness"] for r in results])), 2) if results else 0,
        },
    }


def generate_report(analysis: dict) -> str:
    """Generate markdown robustness report."""
    lines = []
    summary = analysis["summary"]

    lines.append("# Robustness Testing Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Pass threshold:** richness >= {summary['threshold_pct']:.0%} of population mean "
                 f"({summary['population_mean_richness']:.2f})")
    lines.append("")

    # Verdict
    lines.append("## Overall Verdict")
    lines.append("")
    lines.append(f"**{summary['verdict']}**")
    lines.append("")
    lines.append(f"{summary['verdict_detail']}")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Profiles tested | {summary['n_profiles']} |")
    lines.append(f"| Passed | {summary['n_passed']} |")
    lines.append(f"| Failed | {summary['n_failed']} |")
    lines.append(f"| Pass rate | {summary['pass_rate']:.0%} |")
    lines.append(f"| Population mean richness | {summary['population_mean_richness']:.2f} |")
    lines.append(f"| Adversarial mean richness | {summary['adversarial_mean_richness']:.2f} |")
    lines.append("")

    # Per-profile results
    lines.append("## Per-Profile Results")
    lines.append("")
    lines.append("| Profile | Persona | Richness | Pop. Mean | Ratio | Verdict |")
    lines.append("|---------|---------|----------|-----------|-------|---------|")
    for r in analysis["profiles"]:
        verdict_icon = "PASS" if r["passed"] else "FAIL"
        lines.append(f"| {r['profile_type']} | {r['persona_name']} | "
                     f"{r['mean_richness']:.2f} | {r['population_mean']:.2f} | "
                     f"{r['ratio_to_population']:.0%} | {verdict_icon} |")
    lines.append("")

    # Detailed per-profile analysis
    for r in analysis["profiles"]:
        lines.append(f"### {r['profile_type'].replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"**Persona:** {r['persona_name']}")
        lines.append(f"**Test objective:** {r['test_objective']}")
        lines.append(f"**Verdict:** {'PASS' if r['passed'] else 'FAIL'} "
                     f"(richness {r['mean_richness']:.2f} vs threshold {r['threshold']:.2f})")
        lines.append("")

        lines.append(f"- Responses scored: {r['n_responses_scored']}")
        lines.append(f"- Questions asked: {r['n_questions']}")
        lines.append(f"- Probes deployed: {r['n_probes']}")
        lines.append(f"- Dimensions surfaced: {len(r['dimensions_surfaced'])} "
                     f"({', '.join(r['dimensions_surfaced'][:5])}{'...' if len(r['dimensions_surfaced']) > 5 else ''})")
        lines.append(f"- Dimensions absent: {len(r['dimensions_absent'])} "
                     f"({', '.join(r['dimensions_absent'][:5])}{'...' if len(r['dimensions_absent']) > 5 else ''})")
        if r["adaptation_notes"]:
            for note in r["adaptation_notes"]:
                lines.append(f"- {note}")
        lines.append("")

        # Per-dimension scores
        lines.append("**Dimension scores:**")
        lines.append("")
        lines.append("| Dimension | Adversarial | Population | Ratio | Pass |")
        lines.append("|-----------|-------------|------------|-------|------|")
        for dim, comp in sorted(r["dimension_comparison"].items()):
            p = "Yes" if comp["pass"] else "No"
            lines.append(f"| {dim} | {comp['adversarial']:.2f} | {comp['population']:.2f} | "
                         f"{comp['ratio']:.0%} | {p} |")
        lines.append("")

    # LaTeX table
    lines.append("## Paper-Ready Table")
    lines.append("")
    lines.append("```latex")
    lines.append("\\begin{table}[h]")
    lines.append("\\caption{Adversarial robustness testing results}")
    lines.append("\\label{tab:robustness}")
    lines.append("\\begin{tabular}{llcccc}")
    lines.append("\\hline")
    lines.append("Profile & Persona & Richness & Pop. Mean & Ratio & Verdict \\\\")
    lines.append("\\hline")
    for r in analysis["profiles"]:
        v = "Pass" if r["passed"] else "Fail"
        pt = r['profile_type'].replace('_', ' ').title()
        lines.append(f"{pt} & {r['persona_name']} & {r['mean_richness']:.2f} & "
                     f"{r['population_mean']:.2f} & {r['ratio_to_population']:.0%} & {v} \\\\")
    lines.append("\\hline")
    lines.append(f"\\multicolumn{{6}}{{l}}{{Overall: {summary['verdict']}}} \\\\")
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Robustness Reporter")
    parser.add_argument("--adversarial-scores", type=str, required=True)
    parser.add_argument("--adversarial-personas", type=str, required=True)
    parser.add_argument("--adversarial-transcripts", type=str, required=True)
    parser.add_argument("--population-scores", type=str, required=True,
                        help="Path to refinement scoring_summary.json or evaluation scoring_summary.json")
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    run = TimestampedRun(args.output)
    run.record_read(args.adversarial_scores)
    run.record_read(args.adversarial_personas)
    run.record_read(args.population_scores)

    # Load adversarial scores
    adv_scores = load_jsonl(args.adversarial_scores)
    log.info(f"Loaded {len(adv_scores)} adversarial score records")

    # Load adversarial personas keyed by session_id
    personas_raw = load_jsonl(args.adversarial_personas)
    # Map persona composite_id to persona, then session_id to persona
    persona_by_id = {}
    for p in personas_raw:
        persona_by_id[p.get("composite_id", "")] = p

    # Load transcripts
    transcripts = {}
    t_dir = Path(args.adversarial_transcripts)
    if t_dir.exists():
        for f in sorted(t_dir.glob("T_ADV_*.json")):
            run.record_read(str(f))
            with open(f) as fh:
                t = json.load(fh)
            transcripts[t["session_id"]] = t

    # Map session_ids to personas using transcript persona_id
    personas_by_session = {}
    for sid, t in transcripts.items():
        pid = t.get("persona_id", "")
        if pid in persona_by_id:
            personas_by_session[sid] = persona_by_id[pid]
        else:
            # Try matching by profile_type
            pt = t.get("profile_type", "")
            for p in personas_raw:
                if p.get("profile_type") == pt:
                    personas_by_session[sid] = p
                    break

    # Load population stats
    with open(args.population_scores) as f:
        pop_stats = json.load(f)

    population_mean = pop_stats.get("mean_composite_richness", 3.06)
    population_dim_means = pop_stats.get("mean_scores_global", {})

    # Run analysis
    analysis = analyse_robustness(
        adv_scores, personas_by_session, transcripts,
        population_mean, population_dim_means,
    )
    analysis["run_timestamp"] = run.timestamp

    # Write report JSON
    report_json_path = run.output_path("robustness_report.json")
    with open(report_json_path, "w") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    run.stable_pointer("robustness_report.json", report_json_path)

    # Write report MD
    report = generate_report(analysis)
    report_md_path = run.output_path("robustness_report.md")
    with open(report_md_path, "w") as f:
        f.write(report)
    run.stable_pointer("robustness_report.md", report_md_path)

    run.write_manifest("robustness_reporter", config={
        "n_profiles": analysis["summary"]["n_profiles"],
        "verdict": analysis["summary"]["verdict"],
    })

    log.info(f"Verdict: {analysis['summary']['verdict']}")
    log.info(f"Pass rate: {analysis['summary']['pass_rate']:.0%} ({analysis['summary']['n_passed']}/{analysis['summary']['n_profiles']})")
    log.info(f"Report -> {report_md_path}")


if __name__ == "__main__":
    main()

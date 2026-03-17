"""
Automated Gap Analysis Coding Framework — evaluates questionnaire responses
for dimension coverage, richness, and blind spots.

This module builds the analysis framework (Sprint 3). The actual scoring runs
in Sprint 5 after synthetic interviews are complete.

Usage (framework test with mock data):
    python -m src.questionnaire.gap_analyser --test

Usage (post-interview analysis):
    python -m src.questionnaire.gap_analyser \
        --transcripts data/interviews/ \
        --questionnaire data/questionnaires/Q_V1.json \
        --output data/analysis/
"""
import json, argparse, logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from src.questionnaire.frameworks import (
    JOURNEY_PHASES, LATENT_DIMENSIONS, THEMATIC_TARGETS,
    EVALUATION_CRITERIA, COVERAGE_MATRIX,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. DIMENSION TRACKER
# ═══════════════════════════════════════════════════════════════════════════════

# Coding categories for dimension presence in a response
DIMENSION_CODES = {
    "explicit":  3,  # Dimension explicitly mentioned/discussed
    "implicit":  2,  # Dimension indirectly referenced or implied
    "absent":    0,  # Dimension not present in response
}


class DimensionTracker:
    """Tracks which latent dimensions are surfaced across transcripts.

    For each transcript, codes each latent dimension as:
      - explicit: directly mentioned or discussed
      - implicit: indirectly referenced or implied
      - absent: not present in the response
    """

    def __init__(self):
        self.records = []  # list of per-transcript coding records

    def add_coding(self, transcript_id: str, persona_id: str,
                   version: int, codings: dict):
        """Record dimension codings for one transcript.

        Args:
            transcript_id: Unique transcript identifier
            persona_id: Composite persona ID
            version: Questionnaire version number
            codings: Dict of {dimension_name: "explicit"|"implicit"|"absent"}
        """
        record = {
            "transcript_id": transcript_id,
            "persona_id": persona_id,
            "version": version,
            "codings": {},
        }
        for dim in LATENT_DIMENSIONS:
            code = codings.get(dim, "absent")
            record["codings"][dim] = {
                "code": code,
                "score": DIMENSION_CODES.get(code, 0),
            }
        self.records.append(record)

    def surfacing_rates(self, version: int = None) -> dict:
        """Calculate surfacing rate for each dimension.

        Returns dict of {dimension: {explicit_rate, implicit_rate, absent_rate, surfacing_rate}}
        """
        records = self.records
        if version is not None:
            records = [r for r in records if r["version"] == version]
        n = max(len(records), 1)

        rates = {}
        for dim in LATENT_DIMENSIONS:
            counts = {"explicit": 0, "implicit": 0, "absent": 0}
            for r in records:
                code = r["codings"].get(dim, {}).get("code", "absent")
                counts[code] = counts.get(code, 0) + 1
            surfaced = counts["explicit"] + counts["implicit"]
            rates[dim] = {
                "explicit_rate": round(counts["explicit"] / n * 100, 1),
                "implicit_rate": round(counts["implicit"] / n * 100, 1),
                "absent_rate": round(counts["absent"] / n * 100, 1),
                "surfacing_rate": round(surfaced / n * 100, 1),
                "explicit_count": counts["explicit"],
                "implicit_count": counts["implicit"],
                "absent_count": counts["absent"],
            }
        return rates


# ═══════════════════════════════════════════════════════════════════════════════
# 2. RICHNESS SCORER
# ═══════════════════════════════════════════════════════════════════════════════

class RichnessScorer:
    """Scores question-response pairs on multiple quality dimensions.

    Scoring dimensions (0-5 each):
      - emotional_depth: emotional language, hedging, contradiction
      - specificity: concrete examples vs. generic statements
      - latent_surfacing: encoded dimensions made visible
      - narrative_quality: storytelling, temporal flow, personal detail
    """

    SCORING_DIMENSIONS = {
        "emotional_depth": {
            "description": "Presence of emotional language, hedging, contradiction, ambivalence",
            "rubric": {
                0: "No emotional content",
                1: "Single basic emotion mentioned",
                2: "Some emotional language, surface-level",
                3: "Clear emotional expression with some nuance",
                4: "Rich emotional content with hedging or contradiction",
                5: "Deep emotional complexity, ambivalence, raw vulnerability",
            },
        },
        "specificity": {
            "description": "Concrete examples, specific people/places/times vs. generic statements",
            "rubric": {
                0: "Entirely generic/abstract",
                1: "One vague reference",
                2: "Some specifics but mostly general",
                3: "Balanced — clear examples alongside general points",
                4: "Detailed, specific, with names/places/times",
                5: "Vivid, granular detail throughout",
            },
        },
        "latent_surfacing": {
            "description": "Encoded dimensions made visible (power, identity, structure)",
            "rubric": {
                0: "No latent dimensions visible",
                1: "One dimension barely hinted",
                2: "One dimension clearly present, others absent",
                3: "Two dimensions present",
                4: "Three+ dimensions, some with depth",
                5: "Multiple dimensions richly interwoven",
            },
        },
        "narrative_quality": {
            "description": "Storytelling, temporal flow, personal detail, coherence",
            "rubric": {
                0: "No narrative structure",
                1: "Brief answer, no story",
                2: "Some narrative elements but fragmented",
                3: "Clear narrative arc with personal detail",
                4: "Compelling story with temporal flow",
                5: "Rich, layered narrative with reflection",
            },
        },
    }

    def __init__(self):
        self.scores = []

    def add_score(self, question_id: str, persona_id: str, version: int,
                  scores: dict, surfaced_dimensions: list = None):
        """Record richness scores for one question-response pair.

        Args:
            question_id: Question identifier
            persona_id: Persona identifier
            version: Questionnaire version
            scores: Dict of {dimension: score (0-5)}
            surfaced_dimensions: List of latent dimensions surfaced in response
        """
        record = {
            "question_id": question_id,
            "persona_id": persona_id,
            "version": version,
            "scores": {},
            "total": 0,
            "surfaced_dimensions": surfaced_dimensions or [],
        }
        for dim in self.SCORING_DIMENSIONS:
            s = min(max(scores.get(dim, 0), 0), 5)
            record["scores"][dim] = s
            record["total"] += s
        self.scores.append(record)

    def top_questions(self, n: int = 5, version: int = None) -> list:
        """Return top N questions by total richness score."""
        records = self.scores
        if version is not None:
            records = [r for r in records if r["version"] == version]
        return sorted(records, key=lambda r: -r["total"])[:n]

    def bottom_questions(self, n: int = 5, version: int = None) -> list:
        """Return bottom N questions by total richness score."""
        records = self.scores
        if version is not None:
            records = [r for r in records if r["version"] == version]
        return sorted(records, key=lambda r: r["total"])[:n]

    def question_averages(self, version: int = None) -> dict:
        """Average richness scores per question across personas."""
        records = self.scores
        if version is not None:
            records = [r for r in records if r["version"] == version]

        by_q = defaultdict(list)
        for r in records:
            by_q[r["question_id"]].append(r)

        avgs = {}
        for qid, recs in by_q.items():
            n = len(recs)
            avgs[qid] = {
                dim: round(sum(r["scores"][dim] for r in recs) / n, 2)
                for dim in self.SCORING_DIMENSIONS
            }
            avgs[qid]["total"] = round(sum(r["total"] for r in recs) / n, 2)
            avgs[qid]["n_responses"] = n
        return avgs


# ═══════════════════════════════════════════════════════════════════════════════
# 3. COVERAGE HEATMAP GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class CoverageHeatmap:
    """Produces a matrix of (version × journey_phase × latent_dimension) → surfacing_rate.

    Identifies cells with <20% surfacing rate as 'blind spots'.
    """

    def __init__(self):
        self.entries = []  # (version, phase, dimension, surfaced: bool)

    def add_entry(self, version: int, phase: str, dimension: str, surfaced: bool):
        self.entries.append({
            "version": version,
            "phase": phase,
            "dimension": dimension,
            "surfaced": surfaced,
        })

    def generate_matrix(self) -> dict:
        """Generate the coverage matrix with surfacing rates."""
        # Group by (version, phase, dimension)
        cells = defaultdict(lambda: {"surfaced": 0, "total": 0})
        for e in self.entries:
            key = (e["version"], e["phase"], e["dimension"])
            cells[key]["total"] += 1
            if e["surfaced"]:
                cells[key]["surfaced"] += 1

        matrix = {}
        blind_spots = []
        for (version, phase, dim), counts in cells.items():
            v_key = f"V{version}"
            if v_key not in matrix:
                matrix[v_key] = {}
            if phase not in matrix[v_key]:
                matrix[v_key][phase] = {}

            rate = round(counts["surfaced"] / max(counts["total"], 1) * 100, 1)
            matrix[v_key][phase][dim] = {
                "surfacing_rate": rate,
                "surfaced": counts["surfaced"],
                "total": counts["total"],
            }

            if rate < 20.0:
                blind_spots.append({
                    "version": version,
                    "phase": phase,
                    "dimension": dim,
                    "rate": rate,
                })

        return {
            "matrix": matrix,
            "blind_spots": sorted(blind_spots, key=lambda x: x["rate"]),
            "total_cells": len(cells),
            "blind_spot_count": len(blind_spots),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GAP REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class GapReportGenerator:
    """Produces a comprehensive gap analysis report per version."""

    def __init__(self, dimension_tracker: DimensionTracker,
                 richness_scorer: RichnessScorer,
                 coverage_heatmap: CoverageHeatmap):
        self.dt = dimension_tracker
        self.rs = richness_scorer
        self.ch = coverage_heatmap

    def generate_report(self, version: int) -> dict:
        """Generate gap report for a specific questionnaire version."""
        rates = self.dt.surfacing_rates(version)
        heatmap = self.ch.generate_matrix()

        # Strengths: dimensions surfaced >60%
        strengths = [
            {"dimension": dim, "surfacing_rate": data["surfacing_rate"]}
            for dim, data in rates.items()
            if data["surfacing_rate"] > 60
        ]
        strengths.sort(key=lambda x: -x["surfacing_rate"])

        # Blind spots: dimensions surfaced <20%
        blind_spots = [
            {"dimension": dim, "surfacing_rate": data["surfacing_rate"]}
            for dim, data in rates.items()
            if data["surfacing_rate"] < 20
        ]
        blind_spots.sort(key=lambda x: x["surfacing_rate"])

        # Best and worst questions
        best = self.rs.top_questions(5, version)
        worst = self.rs.bottom_questions(5, version)

        # Recommended refinements
        refinements = []
        for spot in blind_spots:
            dim = spot["dimension"]
            dim_info = LATENT_DIMENSIONS.get(dim, {})
            strategies = dim_info.get("surfacing_strategies", [])
            refinements.append({
                "dimension": dim,
                "current_rate": spot["surfacing_rate"],
                "recommendation": f"Add probes targeting '{dim}' using strategies: "
                                  f"{'; '.join(strategies[:2])}",
                "priority": "high" if spot["surfacing_rate"] < 10 else "medium",
            })

        return {
            "version": version,
            "generated_at": datetime.now().isoformat(),
            "dimension_surfacing_rates": rates,
            "strengths": strengths,
            "blind_spots": blind_spots,
            "best_questions": [
                {"question_id": q["question_id"], "total_score": q["total"],
                 "scores": q["scores"]}
                for q in best
            ],
            "worst_questions": [
                {"question_id": q["question_id"], "total_score": q["total"],
                 "scores": q["scores"]}
                for q in worst
            ],
            "refinements": refinements,
            "heatmap_blind_spots": [
                bs for bs in heatmap.get("blind_spots", [])
                if bs["version"] == version
            ],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# LLM-BASED CODING (to be called in Sprint 5)
# ═══════════════════════════════════════════════════════════════════════════════

def build_coding_prompt(question_text: str, response_text: str,
                        target_dimensions: list) -> str:
    """Build prompt for LLM-based dimension coding of a response.

    Uses task 'coverage_analysis' model from config.
    """
    dim_descriptions = "\n".join(
        f"  - {dim}: {LATENT_DIMENSIONS[dim]['description']}"
        for dim in target_dimensions if dim in LATENT_DIMENSIONS
    )

    return f"""You are coding a qualitative interview response for latent dimension presence.

QUESTION ASKED:
{question_text}

RESPONSE:
{response_text}

DIMENSIONS TO CODE (rate each as "explicit", "implicit", or "absent"):
{dim_descriptions}

Also score the response on these quality dimensions (0-5 each):
- emotional_depth: Presence of emotional language, hedging, contradiction
- specificity: Concrete examples vs. generic statements
- latent_surfacing: How many encoded dimensions are made visible
- narrative_quality: Storytelling, temporal flow, personal detail

Return ONLY a JSON object:
{{
  "dimension_codings": {{
    "dimension_name": "explicit|implicit|absent",
    ...
  }},
  "richness_scores": {{
    "emotional_depth": 0-5,
    "specificity": 0-5,
    "latent_surfacing": 0-5,
    "narrative_quality": 0-5
  }},
  "surfaced_dimensions": ["list", "of", "surfaced", "dimension", "names"]
}}"""


def build_richness_prompt(question_text: str, response_text: str) -> str:
    """Build prompt for richness scoring only (no dimension coding)."""
    return f"""Score this interview response on quality dimensions (0-5 each).

QUESTION: {question_text}
RESPONSE: {response_text}

Scoring rubric:
- emotional_depth (0-5): 0=no emotion, 5=deep complexity/ambivalence
- specificity (0-5): 0=entirely generic, 5=vivid granular detail
- latent_surfacing (0-5): 0=no latent dimensions, 5=multiple richly interwoven
- narrative_quality (0-5): 0=no narrative, 5=rich layered narrative

Return ONLY a JSON object:
{{
  "emotional_depth": 0-5,
  "specificity": 0-5,
  "latent_surfacing": 0-5,
  "narrative_quality": 0-5
}}"""


# ═══════════════════════════════════════════════════════════════════════════════
# FRAMEWORK TEST
# ═══════════════════════════════════════════════════════════════════════════════

def run_framework_test():
    """Test the gap analysis framework with mock data."""
    log.info("Running gap analysis framework test with mock data...")

    dt = DimensionTracker()
    rs = RichnessScorer()
    ch = CoverageHeatmap()

    # Mock: 3 transcripts, 2 versions
    mock_transcripts = [
        {"id": "T001", "persona": "comp_001", "version": 1,
         "codings": {"power_dynamics": "explicit", "trust_distrust": "implicit",
                     "identity_tensions": "absent", "structural_barriers": "explicit",
                     "dignity_respect": "implicit", "continuity_of_care": "absent",
                     "autonomy_vs_dependence": "explicit", "informal_care_networks": "absent",
                     "digital_information_seeking": "implicit", "partner_role": "absent",
                     "body_image_autonomy": "absent", "intergenerational_patterns": "absent"}},
        {"id": "T002", "persona": "comp_002", "version": 1,
         "codings": {"power_dynamics": "implicit", "trust_distrust": "explicit",
                     "identity_tensions": "explicit", "structural_barriers": "implicit",
                     "dignity_respect": "absent", "continuity_of_care": "implicit",
                     "autonomy_vs_dependence": "absent", "informal_care_networks": "explicit",
                     "digital_information_seeking": "absent", "partner_role": "explicit",
                     "body_image_autonomy": "implicit", "intergenerational_patterns": "absent"}},
        {"id": "T003", "persona": "comp_003", "version": 1,
         "codings": {"power_dynamics": "absent", "trust_distrust": "explicit",
                     "identity_tensions": "absent", "structural_barriers": "absent",
                     "dignity_respect": "explicit", "continuity_of_care": "absent",
                     "autonomy_vs_dependence": "implicit", "informal_care_networks": "absent",
                     "digital_information_seeking": "explicit", "partner_role": "absent",
                     "body_image_autonomy": "absent", "intergenerational_patterns": "explicit"}},
    ]

    for t in mock_transcripts:
        dt.add_coding(t["id"], t["persona"], t["version"], t["codings"])

    # Mock richness scores
    mock_scores = [
        {"qid": "V1_PREC_Q01", "persona": "comp_001", "version": 1,
         "scores": {"emotional_depth": 4, "specificity": 3, "latent_surfacing": 3, "narrative_quality": 4},
         "dims": ["power_dynamics", "trust_distrust"]},
        {"qid": "V1_PREG_Q01", "persona": "comp_001", "version": 1,
         "scores": {"emotional_depth": 2, "specificity": 1, "latent_surfacing": 1, "narrative_quality": 2},
         "dims": ["structural_barriers"]},
        {"qid": "V1_PREC_Q01", "persona": "comp_002", "version": 1,
         "scores": {"emotional_depth": 5, "specificity": 4, "latent_surfacing": 4, "narrative_quality": 5},
         "dims": ["identity_tensions", "partner_role", "trust_distrust"]},
    ]

    for s in mock_scores:
        rs.add_score(s["qid"], s["persona"], s["version"], s["scores"], s["dims"])

    # Mock heatmap entries
    for t in mock_transcripts:
        for dim, code in t["codings"].items():
            ch.add_entry(t["version"], "pregnancy", dim, code != "absent")

    # Generate report
    report_gen = GapReportGenerator(dt, rs, ch)
    report = report_gen.generate_report(version=1)

    # Print results
    log.info(f"\n{'='*60}")
    log.info("GAP ANALYSIS FRAMEWORK TEST — VERSION 1")
    log.info(f"{'='*60}")

    log.info(f"\nDimension surfacing rates:")
    rates = report["dimension_surfacing_rates"]
    for dim, data in sorted(rates.items(), key=lambda x: -x[1]["surfacing_rate"]):
        bar = "█" * int(data["surfacing_rate"] / 5)
        status = "✓" if data["surfacing_rate"] >= 60 else "⚠" if data["surfacing_rate"] >= 20 else "✗"
        log.info(f"  {status} {dim:<30s} {data['surfacing_rate']:>5.1f}% "
                 f"(E:{data['explicit_count']} I:{data['implicit_count']} A:{data['absent_count']}) {bar}")

    log.info(f"\nStrengths (>60% surfacing):")
    for s in report["strengths"]:
        log.info(f"  + {s['dimension']}: {s['surfacing_rate']}%")
    if not report["strengths"]:
        log.info("  (none)")

    log.info(f"\nBlind spots (<20% surfacing):")
    for s in report["blind_spots"]:
        log.info(f"  - {s['dimension']}: {s['surfacing_rate']}%")
    if not report["blind_spots"]:
        log.info("  (none)")

    log.info(f"\nBest questions:")
    for q in report["best_questions"]:
        log.info(f"  {q['question_id']}: total={q['total_score']}")

    log.info(f"\nWorst questions:")
    for q in report["worst_questions"]:
        log.info(f"  {q['question_id']}: total={q['total_score']}")

    log.info(f"\nRefinement recommendations:")
    for r in report["refinements"]:
        log.info(f"  [{r['priority'].upper()}] {r['dimension']} ({r['current_rate']}%): "
                 f"{r['recommendation']}")

    log.info(f"\n{'='*60}")
    log.info("Framework test complete — all components functional")
    log.info(f"{'='*60}")

    return report


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Gap Analysis Coding Framework")
    parser.add_argument("--test", action="store_true",
                        help="Run framework test with mock data")
    parser.add_argument("--transcripts", type=str,
                        help="Path to interview transcripts directory")
    parser.add_argument("--questionnaire", type=str,
                        help="Path to questionnaire JSON")
    parser.add_argument("--output", type=str,
                        help="Output directory for analysis")
    args = parser.parse_args()

    if args.test:
        run_framework_test()
    else:
        log.info("Gap analysis scoring requires interview transcripts (Sprint 5).")
        log.info("Use --test to verify the framework with mock data.")


if __name__ == "__main__":
    main()

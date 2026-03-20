"""
Diagnostic — reads Sprint 5 evaluation outputs and produces a refinement plan.
No LLM calls. Every downstream module reads from this plan.

Usage:
    python -m src.refinement.diagnostic \
        --evaluation data/evaluation/ \
        --questionnaires data/questionnaires/ \
        --plan data/config/administration_plan.json \
        --output data/refinement/
"""
import json, argparse, logging
from pathlib import Path
from collections import defaultdict

from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def load_jsonl(path: Path) -> list:
    records = []
    if not path.exists():
        return records
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


class RefinementDiagnostic:
    def __init__(self, evaluation_dir: str, questionnaires_dir: str, plan_file: str):
        self.eval_dir = Path(evaluation_dir)
        self.q_dir = Path(questionnaires_dir)
        self.plan_file = Path(plan_file)

    def run_diagnostic(self, run: TimestampedRun) -> dict:
        # Load Sprint 5 outputs
        ranking = load_json(self.eval_dir / "version_ranking.json")
        blind_spots = json.loads((self.eval_dir / "blind_spots.json").read_text()) if (self.eval_dir / "blind_spots.json").exists() else []
        question_rankings = load_json(self.eval_dir / "question_rankings.json")
        heatmap = load_json(self.eval_dir / "dimension_heatmap.json")
        inter_rater = load_json(self.eval_dir / "inter_rater_agreement.json")
        service_agg = load_json(self.eval_dir / "service_aggregate.json")
        summaries = load_jsonl(self.eval_dir / "transcript_summaries.jsonl")
        interactions = load_json(self.eval_dir / "interaction_effects.json")
        admin_plan = load_json(self.plan_file)

        run.record_read(str(self.eval_dir / "version_ranking.json"))
        run.record_read(str(self.eval_dir / "blind_spots.json"))
        run.record_read(str(self.eval_dir / "question_rankings.json"))
        run.record_read(str(self.eval_dir / "dimension_heatmap.json"))
        run.record_read(str(self.eval_dir / "inter_rater_agreement.json"))
        run.record_read(str(self.eval_dir / "service_aggregate.json"))
        run.record_read(str(self.eval_dir / "transcript_summaries.jsonl"))
        run.record_read(str(self.eval_dir / "interaction_effects.json"))
        run.record_read(str(self.plan_file))

        # 1. WINNER SELECTION
        sorted_versions = sorted(ranking.items(), key=lambda x: x[1].get("composite", 0), reverse=True)
        winner_key, winner_data = sorted_versions[0]
        runner_up_key, runner_up_data = sorted_versions[1]

        winner_version = int(winner_key.replace("V", ""))
        runner_up_version = int(runner_up_key.replace("V", ""))

        # Load questionnaire strategy
        q_file = self.q_dir / f"Q_V{winner_version}.json"
        q_data = load_json(q_file)
        strategy_info = q_data.get("strategy", {})
        strategy_name = strategy_info.get("name", "unknown") if isinstance(strategy_info, dict) else str(strategy_info)

        ru_q_file = self.q_dir / f"Q_V{runner_up_version}.json"
        ru_q_data = load_json(ru_q_file)
        ru_strategy = ru_q_data.get("strategy", {})
        ru_strategy_name = ru_strategy.get("name", "unknown") if isinstance(ru_strategy, dict) else str(ru_strategy)

        # 2. RUNNER-UP DECISION
        gap_pct = (winner_data["composite"] - runner_up_data["composite"]) / winner_data["composite"] * 100
        refine_runner_up = gap_pct < 10

        # 3. BLIND SPOT CLASSIFICATION for winner
        winner_spots = [s for s in blind_spots if s["version"] == winner_version]
        classified_spots = []
        for s in winner_spots:
            rate = s["surfacing_rate"]
            # Normalize: if stored as percentage (>1), convert
            if rate > 1:
                rate = rate / 100.0
            severity = "critical" if rate < 0.10 else "moderate"
            # Determine diagnosis
            n_targeting = len(s.get("questions_targeting", []))
            if n_targeting == 0:
                diagnosis = "no_questions_target"
            elif rate == 0:
                diagnosis = "probes_ineffective"
            else:
                diagnosis = "dimension_too_latent"
            classified_spots.append({
                "dimension": s["dimension"],
                "surfacing_rate": rate,
                "severity": severity,
                "questions_targeting": s.get("questions_targeting", []),
                "diagnosis": diagnosis,
            })

        # At-risk dimensions (20-40%) from heatmap
        v_heatmap = heatmap.get(f"V{winner_version}", {})
        at_risk = []
        for dim, info in v_heatmap.items():
            rate_pct = info["surfacing_rate"] if isinstance(info, dict) else info
            rate = rate_pct / 100.0 if rate_pct > 1 else rate_pct
            if 0.20 <= rate <= 0.40:
                at_risk.append({"dimension": dim, "surfacing_rate": rate})

        # 4. BOTTOM / TOP QUESTIONS for winner
        v_key = f"V{winner_version}"
        v_rankings = question_rankings.get(v_key, {})
        bottom_qs = []
        for q in v_rankings.get("bottom_5", []):
            richness = q.get("mean_richness", 0)
            if richness < 1.0:
                action = "replace"
            elif richness < 1.5:
                action = "augment"
            else:
                action = "keep"
            bottom_qs.append({
                "question_id": q["question_id"],
                "mean_richness": richness,
                "action": action,
            })
        top_qs = []
        for q in v_rankings.get("top_5", []):
            top_qs.append({
                "question_id": q["question_id"],
                "mean_richness": q.get("mean_richness", 0),
                "why_effective": f"High richness ({q.get('mean_richness', 0):.2f}) with {q.get('distinct_dimensions_surfaced', 0)} dimensions surfaced",
            })

        # 5. INTER-RATER CONCERNS
        icc_concerns = []
        if isinstance(inter_rater, dict):
            for dim, info in inter_rater.items():
                if isinstance(info, dict):
                    icc = info.get("icc", 1.0)
                    if isinstance(icc, (int, float)) and icc < 0.60:
                        icc_concerns.append({
                            "dimension": dim,
                            "icc": icc,
                            "interpretation": "poor" if icc < 0.40 else "fair",
                        })

        # 6. RE-ADMINISTRATION SIZE
        n_critical = sum(1 for s in classified_spots if s["severity"] == "critical")
        if n_critical >= 5:
            n_sessions = 50
        elif n_critical >= 3:
            n_sessions = 40
        else:
            n_sessions = 30

        # Find personas NOT used for this version in Sprint 4
        version_sessions = [s for s in summaries if s.get("questionnaire_version") == winner_version]
        used_persona_ids = {s.get("persona_id") for s in version_sessions}
        all_persona_ids = {s.get("persona_id") for s in summaries}
        excluded_persona_ids = sorted(all_persona_ids - used_persona_ids)

        # Target stratification from current distribution
        stage_counts = defaultdict(int)
        risk_counts = defaultdict(int)
        for s in version_sessions:
            stage_counts[s.get("persona_journey_stage", "unknown")] += 1
            risk_counts[s.get("persona_risk_level", "unknown")] += 1

        # 7. INTERACTION EFFECTS
        interaction_notes = []
        if "version_x_stage" in interactions:
            vxs = interactions["version_x_stage"]
            v_prefix = f"V{winner_version}_"
            stages = {}
            for k, v in vxs.items():
                if k.startswith(v_prefix):
                    stage = k.replace(v_prefix, "")
                    stages[stage] = v.get("mean", 0)
            if stages:
                worst_stage = min(stages, key=stages.get)
                best_stage = max(stages, key=stages.get)
                interaction_notes.append({
                    "effect": f"V{winner_version} weakest for {worst_stage} (mean={stages[worst_stage]:.2f}), strongest for {best_stage} (mean={stages[best_stage]:.2f})",
                    "p_value": None,
                    "implication": f"Refine preconception/first_trimester probes; probe patterns from {best_stage} may transfer",
                })

        if "version_x_risk" in interactions:
            vxr = interactions["version_x_risk"]
            v_prefix = f"V{winner_version}_"
            risks = {}
            for k, v in vxr.items():
                if k.startswith(v_prefix):
                    risk = k.replace(v_prefix, "")
                    risks[risk] = v.get("mean", 0)
            if risks:
                worst_risk = min(risks, key=risks.get)
                interaction_notes.append({
                    "effect": f"V{winner_version} weakest for {worst_risk}-risk personas (mean={risks[worst_risk]:.2f})",
                    "p_value": None,
                    "implication": f"Consider adversarial persona at {worst_risk}-risk level",
                })

        # 8. ADVERSARIAL PROFILES
        adversarial_profiles = [
            {"profile_type": "low_health_literacy", "test_objective": "Elicit meaningful responses without jargon"},
            {"profile_type": "language_barrier", "test_objective": "Function through simplified communication"},
            {"profile_type": "hostile_distrustful", "test_objective": "Safe adaptive probing past defensive responses"},
        ]
        # Add data-driven profiles
        blind_dims = {s["dimension"] for s in classified_spots}
        if "digital_information_seeking" in blind_dims or "continuity_of_care" in blind_dims:
            adversarial_profiles.append({
                "profile_type": "rural_isolated",
                "test_objective": "Capture experience with fragmented rural care and limited digital access",
            })
        if any("first_trimester" in n.get("effect", "") for n in interaction_notes):
            adversarial_profiles.append({
                "profile_type": "early_pregnancy_ambivalent",
                "test_objective": "Surface depth in early pregnancy where V4 underperforms",
            })
        adversarial_profiles = adversarial_profiles[:5]

        # Build plan
        plan = {
            "diagnostic_timestamp": run.timestamp,
            "run_id": f"diag_{run.timestamp}",
            "winner": {
                "version": winner_version,
                "strategy": strategy_name,
                "composite_score": winner_data["composite"],
                "questionnaire_file": str(q_file),
            },
            "runner_up": {
                "version": runner_up_version,
                "strategy": ru_strategy_name,
                "composite_score": runner_up_data["composite"],
                "questionnaire_file": str(ru_q_file),
                "gap_from_winner_pct": round(gap_pct, 1),
            },
            "refine_runner_up": refine_runner_up,
            "blind_spots": classified_spots,
            "at_risk_dimensions": at_risk,
            "bottom_questions": bottom_qs,
            "top_questions": top_qs,
            "inter_rater_concerns": icc_concerns,
            "interaction_effects": interaction_notes,
            "re_administration_config": {
                "n_sessions": n_sessions,
                "excluded_persona_ids": excluded_persona_ids[:n_sessions * 2],
                "target_stratification": {
                    "journey_stages": dict(stage_counts),
                    "risk_levels": dict(risk_counts),
                },
            },
            "adversarial_test_config": {
                "n_adversarial_personas": len(adversarial_profiles),
                "profiles": adversarial_profiles,
            },
        }

        return plan


def main():
    parser = argparse.ArgumentParser(description="Refinement Diagnostic")
    parser.add_argument("--evaluation", type=str, required=True)
    parser.add_argument("--questionnaires", type=str, required=True)
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    run = TimestampedRun(args.output)
    diag = RefinementDiagnostic(args.evaluation, args.questionnaires, args.plan)
    plan = diag.run_diagnostic(run)

    # Write timestamped + stable pointer
    plan_path = run.output_path("refinement_plan.json")
    with open(plan_path, "w") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    run.stable_pointer("refinement_plan.json", plan_path)

    run.write_manifest("diagnostic", config={"evaluation_dir": args.evaluation})

    # Summary
    log.info(f"Winner: V{plan['winner']['version']} ({plan['winner']['strategy']}) — composite={plan['winner']['composite_score']}")
    log.info(f"Runner-up: V{plan['runner_up']['version']} — gap={plan['runner_up']['gap_from_winner_pct']:.1f}%, refine={plan['refine_runner_up']}")
    log.info(f"Blind spots: {len(plan['blind_spots'])} ({sum(1 for s in plan['blind_spots'] if s['severity']=='critical')} critical)")
    log.info(f"At-risk dimensions: {len(plan['at_risk_dimensions'])}")
    log.info(f"Bottom questions: {len(plan['bottom_questions'])} (replace={sum(1 for q in plan['bottom_questions'] if q['action']=='replace')}, augment={sum(1 for q in plan['bottom_questions'] if q['action']=='augment')})")
    log.info(f"ICC concerns: {len(plan['inter_rater_concerns'])}")
    log.info(f"Re-administration: {plan['re_administration_config']['n_sessions']} sessions")
    log.info(f"Adversarial: {plan['adversarial_test_config']['n_adversarial_personas']} profiles")
    log.info(f"Plan → {plan_path}")


if __name__ == "__main__":
    main()

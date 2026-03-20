"""
Structured Transcript Builder — accumulates interview turns and produces
the final structured JSON transcript with per-turn metadata.
"""
import time
from datetime import datetime

from src.config.models import ENV
from src.questionnaire.frameworks import VERSION_STRATEGIES


class TranscriptBuilder:
    """Builds structured transcripts from interview sessions."""

    def __init__(self, session_config: dict, persona: dict):
        self.session_id = session_config.get("session_id", "unknown")
        self.persona = persona
        self.version = session_config.get("questionnaire_version", 0)
        self.interviewer_model = session_config.get("interviewer_model", "")
        self.persona_model = session_config.get("persona_model", "")
        self.turns = []
        self.start_time = time.time()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.questions_asked = 0
        self.probes_deployed = 0
        self.adaptive_followups = 0
        self.dimensions_covered = set()
        self.latent_dimensions_surfaced = set()
        self.catch_all_response_length = 0

    def add_interviewer_turn(self, text: str, turn_type: str = "question",
                             question_id: str = None, probe_id: str = None,
                             target_dimensions: list = None,
                             target_latent: list = None,
                             in_tok: int = 0, out_tok: int = 0):
        """Record an interviewer turn."""
        self.turns.append({
            "turn_number": len(self.turns) + 1,
            "role": "interviewer",
            "type": turn_type,
            "text": text,
            "question_id": question_id,
            "probe_id": probe_id,
            "target_dimensions": target_dimensions or [],
            "target_latent": target_latent or [],
            "input_tokens": in_tok,
            "output_tokens": out_tok,
        })
        self.total_input_tokens += in_tok
        self.total_output_tokens += out_tok

        if turn_type == "question":
            self.questions_asked += 1
        elif turn_type == "probe":
            self.probes_deployed += 1
        elif turn_type == "adaptive_followup":
            self.adaptive_followups += 1

        if target_dimensions:
            self.dimensions_covered.update(target_dimensions)
        if target_latent:
            self.latent_dimensions_surfaced.update(target_latent)

    def add_persona_turn(self, text: str, responding_to: str = None,
                         in_tok: int = 0, out_tok: int = 0,
                         is_catch_all: bool = False):
        """Record a persona response turn."""
        self.turns.append({
            "turn_number": len(self.turns) + 1,
            "role": "persona",
            "type": "response",
            "text": text,
            "responding_to_question_id": responding_to,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
        })
        self.total_input_tokens += in_tok
        self.total_output_tokens += out_tok

        if is_catch_all:
            self.catch_all_response_length = len(text.split())

    def build(self, status: str = "completed", errors: list = None) -> dict:
        """Build the final structured transcript."""
        duration = round(time.time() - self.start_time, 1)
        strategy = VERSION_STRATEGIES.get(self.version, {})

        # Estimate cost (rough: based on token counts)
        est_cost = (self.total_input_tokens * 0.001 + self.total_output_tokens * 0.002) / 1000

        return {
            "session_id": self.session_id,
            "status": status,
            "persona_id": self.persona.get("composite_id", ""),
            "persona_name": self.persona.get("name", ""),
            "persona_journey_stage": self.persona.get("journey_stage", ""),
            "persona_risk_level": self.persona.get("risk_level", ""),
            "persona_vulnerability_flags": self.persona.get("vulnerability_flags", []),
            "persona_latent_dimensions": list(self.persona.get("latent_dimensions", {}).keys()),
            "questionnaire_version": self.version,
            "questionnaire_strategy": strategy.get("name", ""),
            "interviewer_model": self.interviewer_model,
            "persona_model": self.persona_model,
            "environment": ENV.value,
            "timestamp": datetime.now().isoformat(),
            "turns": self.turns,
            "metadata": {
                "total_turns": len(self.turns),
                "questions_asked": self.questions_asked,
                "probes_deployed": self.probes_deployed,
                "adaptive_followups": self.adaptive_followups,
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "estimated_cost_usd": round(est_cost, 4),
                "duration_seconds": duration,
                "dimensions_covered": sorted(self.dimensions_covered),
                "latent_dimensions_surfaced": sorted(self.latent_dimensions_surfaced),
                "catch_all_response_length": self.catch_all_response_length,
            },
            "errors": errors or [],
        }

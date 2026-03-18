"""
Questionnaire-Driven Interviewer Agent — follows adapted questionnaires with
adaptive probe deployment based on response quality evaluation.
"""
import os, logging
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from src.config.models import get_model, get_provider, get_token_policy, tracker, ENV

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

TASK_NAME = "interviewer"
MAX_PROBES_PER_QUESTION = 3
RICHNESS_THRESHOLD = 3  # score >= 3 → adequate, skip probes


class QuestionnaireInterviewer:
    """Questionnaire-driven interviewer that follows adapted question guides."""

    def __init__(self, questionnaire: dict, persona_summary: str,
                 journey_stage: str):
        self.questions = questionnaire.get("questions", [])
        self.persona_summary = persona_summary
        self.journey_stage = journey_stage
        self.provider = get_provider(TASK_NAME)
        self.model = get_model(TASK_NAME)

        # State
        self.current_question_idx = 0
        self.probes_deployed_for_current = 0
        self.current_probes = []
        self.current_probe_idx = 0
        self.questions_asked = []
        self.total_probes_deployed = 0
        self.dimensions_covered = set()
        self.interview_closed = False

    def generate_opening(self, persona_name: str, journey_stage: str) -> str:
        stage_context = {
            "preconception": "thinking about starting a family",
            "first_trimester": "in the early stages of pregnancy",
            "second_trimester": "in the middle of your pregnancy",
            "third_trimester": "getting closer to your due date",
            "birth": "going through the birth experience",
            "postpartum": "adjusting to life after having your baby",
        }
        ctx = stage_context.get(journey_stage, "going through your maternity journey")

        return (
            f"Hello {persona_name}, thank you so much for taking the time to speak with me today. "
            f"I'm a researcher studying maternity care experiences, and I'm really interested in "
            f"hearing your personal story. I understand you're {ctx}, and I'd love to hear about "
            f"your experience in your own words. There are no right or wrong answers — I'm just "
            f"here to listen and learn from you. Everything you share will help us understand how "
            f"to make maternity care better. Shall we begin?"
        )

    def get_next_action(self, last_response: str = None) -> dict:
        """Determine next interviewer action based on interview state."""
        if self.interview_closed:
            return {"action": "done"}

        # If we just asked a question and got a response, evaluate it
        if last_response and self.current_question_idx > 0:
            should_probe = self._should_probe(last_response)

            if should_probe and self.probes_deployed_for_current < MAX_PROBES_PER_QUESTION:
                probe = self._get_next_probe()
                if probe:
                    return probe

        # Move to next question
        if self.current_question_idx < len(self.questions):
            return self._ask_next_question()

        # All questions done → close
        return self._close_interview()

    def _ask_next_question(self) -> dict:
        """Ask the next question from the questionnaire."""
        q = self.questions[self.current_question_idx]
        self.current_question_idx += 1
        self.probes_deployed_for_current = 0

        # Set up probes for this question
        probes = q.get("probes", [])
        self.current_probes = [p for p in probes if isinstance(p, dict)]
        self.current_probe_idx = 0

        qid = q.get("question_id", f"Q{self.current_question_idx}")
        self.questions_asked.append(qid)

        # Track target dimensions
        for d in q.get("target_latent_dimensions", []):
            if isinstance(d, str):
                self.dimensions_covered.add(d)

        return {
            "action": "ask_question",
            "question_id": qid,
            "text": q.get("question_text", ""),
            "target_kbv": q.get("target_kbv_dimensions", []),
            "target_thematic": q.get("target_thematic_areas", []),
            "target_latent": q.get("target_latent_dimensions", []),
        }

    def _should_probe(self, response: str) -> bool:
        """Quick heuristic evaluation of response richness."""
        # Fast heuristic: word count + emotional indicators
        words = len(response.split())
        if words < 30:
            return True  # Very short → probe

        # Check for depth indicators
        depth_signals = ["because", "felt", "remember", "afraid", "worried",
                         "surprised", "honestly", "actually", "struggled",
                         "difficult", "wonderful", "terrified", "grateful"]
        signal_count = sum(1 for s in depth_signals if s in response.lower())

        if words < 60 and signal_count < 2:
            return True  # Short and shallow → probe
        if words >= 100 and signal_count >= 3:
            return False  # Rich enough → move on

        # Moderate: probe if we haven't probed yet for this question
        return self.probes_deployed_for_current == 0

    def _get_next_probe(self) -> dict:
        """Get the next available probe for the current question."""
        while self.current_probe_idx < len(self.current_probes):
            probe = self.current_probes[self.current_probe_idx]
            self.current_probe_idx += 1
            self.probes_deployed_for_current += 1
            self.total_probes_deployed += 1

            pid = probe.get("probe_id", f"P{self.current_probe_idx}")
            probe_type = probe.get("probe_type", "elaboration")

            # Track dimensions from probe
            for d in probe.get("target_latent_dimensions", []):
                if isinstance(d, str):
                    self.dimensions_covered.add(d)

            return {
                "action": "deploy_probe",
                "probe_id": pid,
                "probe_type": probe_type,
                "text": probe.get("probe_text", ""),
                "target_latent": probe.get("target_latent_dimensions", []),
            }

        return None  # No more probes

    def _close_interview(self) -> dict:
        self.interview_closed = True
        return {
            "action": "close_interview",
            "text": (
                "Thank you so much for sharing all of that with me. Your experiences "
                "and insights are incredibly valuable. Before we finish, is there anything "
                "else about your maternity experience that we haven't covered today — "
                "anything that feels important to you that you'd like to add?"
            ),
        }

    def get_state_summary(self) -> dict:
        return {
            "questions_asked": len(self.questions_asked),
            "total_questions": len(self.questions),
            "probes_deployed": self.total_probes_deployed,
            "dimensions_covered": sorted(self.dimensions_covered),
        }

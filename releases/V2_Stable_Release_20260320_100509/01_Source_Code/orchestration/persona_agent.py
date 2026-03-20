"""
Multi-Provider Persona Role-Play Agent — responds in character using
enriched narrative and EHR data from composite personas.
"""
import os, logging
from dotenv import load_dotenv
load_dotenv(".env", override=True)

from src.config.models import get_token_policy, tracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

TASK_NAME = "persona_roleplay"


def _build_system_prompt(persona: dict) -> str:
    """Build the persona system prompt from composite persona data."""
    name = persona.get("name", "Unknown")
    narrative = persona.get("enriched_narrative") or persona.get("attributes", "")
    stage = persona.get("journey_stage", "pregnancy").replace("_", " ")
    risk = persona.get("risk_level", "unknown")
    demo = persona.get("demographics", {})
    meta = persona.get("source_patient_metadata", {})
    flags = persona.get("vulnerability_flags", [])

    # Build clinical context
    clinical_lines = []
    clinical_lines.append(f"Age: {demo.get('age', 'unknown')}")
    clinical_lines.append(f"Ethnicity: {demo.get('ethnicity', 'unknown')}")
    clinical_lines.append(f"Location: {demo.get('location', 'unknown')}")
    clinical_lines.append(f"Marital status: {demo.get('marital_status', 'unknown')}")
    clinical_lines.append(f"Journey stage: {stage}")
    clinical_lines.append(f"Risk level: {risk}")
    clinical_lines.append(f"Pregnancy count: {meta.get('pregnancy_count', 'unknown')}")
    if meta.get("has_miscarriage_history"):
        clinical_lines.append("History of pregnancy loss: Yes")
    comps = meta.get("complications", [])
    if comps:
        comp_names = [c.get("display", "") for c in comps[:5] if c.get("display")]
        if comp_names:
            clinical_lines.append(f"Complications: {', '.join(comp_names)}")
    if flags:
        readable = [f.replace("_", " ") for f in flags]
        clinical_lines.append(f"Life circumstances: {', '.join(readable)}")

    clinical = "\n".join(f"  {l}" for l in clinical_lines)

    return f"""You are {name}. You are a real person being interviewed about your maternity care experience.

YOUR BACKSTORY:
{narrative}

YOUR CLINICAL PROFILE:
{clinical}

INSTRUCTIONS:
- Respond in the first person as {name}. You ARE this person.
- Stay in character throughout. Express emotions naturally — hesitation, fear, joy, anger, frustration.
- Reference your medical history when relevant but don't recite it like a list.
- If a question touches on a sensitive topic, respond as you genuinely would — you may deflect, become emotional, or give a guarded answer.
- {"Occasionally struggle with medical terminology or use simpler words, reflecting your language barrier." if "language_barrier" in flags else "Use language natural to your background."}
- Do NOT break character or acknowledge that you are an AI.
- Keep responses 100-250 words. Be conversational, not clinical.
- Share specific moments, feelings, and experiences rather than generalities.
- It's okay to express uncertainty, confusion, or mixed feelings."""


class PersonaAgent:
    """Multi-provider persona role-play agent."""

    def __init__(self, persona: dict, provider: str, model: str):
        self.persona = persona
        self.provider = provider
        self.model = model
        self.system_prompt = _build_system_prompt(persona)
        self.history = []  # conversation history for context

        policy = get_token_policy()
        self.max_tokens = max(policy.max_output_tokens, 400)
        # Google thinking models need headroom
        if provider == "google":
            self.max_tokens = max(self.max_tokens * 15, 8000)

    def respond(self, interviewer_message: str) -> tuple:
        """Generate persona response. Returns (text, input_tokens, output_tokens)."""
        # Guard against empty messages (some questions may have empty text)
        if not interviewer_message or not interviewer_message.strip():
            interviewer_message = "Please continue sharing your thoughts."
        self.history.append({"role": "user", "content": interviewer_message})

        try:
            text, in_tok, out_tok = self._call_provider()
            self.history.append({"role": "assistant", "content": text})
            tracker.record(TASK_NAME, self.provider, self.model, in_tok, out_tok)
            return text, in_tok, out_tok

        except Exception as e:
            log.error(f"  Persona agent error ({self.provider}/{self.model}): {e}")
            raise

    def _call_provider(self) -> tuple:
        """Route to the appropriate provider API."""
        if self.provider == "anthropic":
            return self._call_anthropic()
        elif self.provider == "google":
            return self._call_google()
        elif self.provider in ("openai", "xai"):
            return self._call_openai()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _call_anthropic(self) -> tuple:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        r = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=self.history,
        )
        text = r.content[0].text.strip()
        return text, r.usage.input_tokens, r.usage.output_tokens

    def _call_google(self) -> tuple:
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        gm = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=self.system_prompt,
        )

        # Build chat history (Google format)
        chat_history = []
        for msg in self.history[:-1]:  # all except last (which we'll send)
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})

        chat = gm.start_chat(history=chat_history)
        r = chat.send_message(
            self.history[-1]["content"],
            generation_config={"max_output_tokens": self.max_tokens},
        )
        text = r.text.strip()
        try:
            in_tok = r.usage_metadata.prompt_token_count
            out_tok = r.usage_metadata.candidates_token_count
        except AttributeError:
            in_tok, out_tok = 0, 0
        return text, in_tok, out_tok

    def _call_openai(self) -> tuple:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = None
        if self.provider == "xai":
            api_key = os.environ.get("XAI_API_KEY")
            base_url = "https://api.x.ai/v1"

        client = OpenAI(api_key=api_key, base_url=base_url)
        messages = [{"role": "system", "content": self.system_prompt}] + self.history
        # Newer OpenAI models (gpt-5-*) require max_completion_tokens
        token_param = "max_completion_tokens" if "gpt-5" in self.model or "o3" in self.model or "o4" in self.model else "max_tokens"
        r = client.chat.completions.create(
            model=self.model,
            messages=messages,
            **{token_param: self.max_tokens},
        )
        text = r.choices[0].message.content.strip()
        return text, r.usage.prompt_tokens, r.usage.completion_tokens

"""
Multi-Provider Persona Role-Play Agent — responds in character using
enriched narrative and EHR data from composite personas.
"""
import os, logging, time
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


class EmptyResponseError(RuntimeError):
    """The persona produced no usable text (empty, whitespace, or truncated before any content) after a retry.
    Development 3, 23 Aug 2026: such a turn is a recorded failure, never a stored answer."""


TRUNCATION_REASONS = {"length", "max_tokens", "MAX_TOKENS", "FinishReason.MAX_TOKENS", "content_filter"}


class PersonaAgent:
    """Multi-provider persona role-play agent (hardened 23 Aug 2026).

    - one instance (and one conversation history) per persona session
    - output cap from the experiment configuration (default 2,000), with explicit thinking budgets for Google
    - finish-reason check and non-empty assertion, one retry with a doubled cap, then EmptyResponseError
    - Anthropic prompt caching on the system prompt and the growing conversation prefix
    - OpenAI Flex processing and reasoning effort when configured; xAI, Hugging Face router and Ollama via the
      OpenAI-compatible path
    - every call written to the provenance cache with snapshot, request id, finish reason, tokens and cost
    """

    def __init__(self, persona: dict, provider: str, model: str, spec=None, session_id: str = "", stage: str = "persona"):
        self.persona = persona
        self.provider = provider
        self.model = model
        self.session_id = session_id
        self.stage = stage
        self.system_prompt = _build_system_prompt(persona)
        self.history = []  # conversation history for context
        if spec is None:
            try:
                from src.config.experiment import spec_from_model_string
                spec = spec_from_model_string(f"{provider}/{model}")
            except Exception:
                spec = None
        if spec is None:
            from src.config.experiment import ModelSpec
            spec = ModelSpec(provider=provider, model=model)
        self.spec = spec
        self.max_tokens = max(int(spec.max_output_tokens or 0), 2000)
        self.last_usage = {}
        self.empty_retries = 0
        try:
            from src.provenance.request_cache import get_cache
            self.cache = get_cache()
        except Exception:
            self.cache = None

    # ------------------------------------------------------------------ public
    def respond(self, interviewer_message: str) -> tuple:
        """Generate persona response. Returns (text, input_tokens, output_tokens); raises EmptyResponseError."""
        if not interviewer_message or not interviewer_message.strip():
            interviewer_message = "Please continue sharing your thoughts."
        if self.cache is not None:
            self.cache.meter.check(self.stage)
        self.history.append({"role": "user", "content": interviewer_message})
        cap = self.max_tokens
        for attempt in (1, 2):
            t0 = time.time()
            text, usage, meta = self._call_provider(cap)
            latency = time.time() - t0
            truncated = str(meta.get("finish_reason")) in TRUNCATION_REASONS
            empty = not text or not text.strip()
            if self.cache is not None:
                self.cache.record(stage=self.stage, session_id=self.session_id, spec=self.spec,
                                  request={"system": self.system_prompt, "messages": list(self.history), "max_tokens": cap},
                                  response=text, usage=usage, snapshot=meta.get("snapshot"), request_id=meta.get("request_id"),
                                  finish_reason=meta.get("finish_reason"), latency_s=latency,
                                  extra={"attempt": attempt, "empty": empty, "truncated": truncated, "persona_id": self.persona.get("composite_id")})
            else:
                tracker.record(TASK_NAME, self.provider, self.model, usage.get("input_tokens", 0), usage.get("output_tokens", 0))
            if not empty and not truncated:
                break
            if not empty and truncated:
                log.warning(f"  {self.provider}/{self.model}: answer truncated at cap {cap} (finish={meta.get('finish_reason')}); kept, flagged")
                break
            self.empty_retries += 1
            log.warning(f"  {self.provider}/{self.model}: empty response (finish={meta.get('finish_reason')}, cap={cap}); retry {attempt}/2 with cap {cap*2}")
            cap *= 2
        else:
            self.history.pop()
            raise EmptyResponseError(f"{self.provider}/{self.model} returned no text after two attempts (last finish={meta.get('finish_reason')}, cap={cap//2})")
        self.history.append({"role": "assistant", "content": text})
        self.last_usage = dict(usage, **meta, truncated=truncated)
        return text, int(usage.get("input_tokens") or 0), int(usage.get("output_tokens") or 0)

    # ----------------------------------------------------------------- routing
    def _call_provider(self, cap: int) -> tuple:
        if self.provider == "anthropic":
            return self._call_anthropic(cap)
        if self.provider == "google":
            return self._call_google(cap)
        if self.provider in ("openai", "xai", "hf", "ollama", "openai_compatible"):
            return self._call_openai_compatible(cap)
        raise ValueError(f"Unknown provider: {self.provider}")

    def _call_anthropic(self, cap: int) -> tuple:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get(self.spec.api_key_env or "ANTHROPIC_API_KEY"), timeout=float(os.environ.get("SDL_CALL_TIMEOUT_S", "180")), max_retries=2)
        if self.spec.cache:
            system = [{"type": "text", "text": self.system_prompt, "cache_control": {"type": "ephemeral"}}]
            messages = []
            for i, m in enumerate(self.history):
                block = {"type": "text", "text": m["content"]}
                if i == len(self.history) - 1:
                    block["cache_control"] = {"type": "ephemeral"}   # cache the growing prefix incrementally
                messages.append({"role": m["role"], "content": [block]})
        else:
            system, messages = self.system_prompt, list(self.history)
        r = client.messages.create(model=self.model, max_tokens=cap, system=system, messages=messages)
        text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()
        u = r.usage
        usage = {"input_tokens": u.input_tokens + (getattr(u, "cache_read_input_tokens", 0) or 0) + (getattr(u, "cache_creation_input_tokens", 0) or 0),
                 "output_tokens": u.output_tokens, "cached_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
                 "cache_creation_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0}
        meta = {"finish_reason": r.stop_reason, "snapshot": getattr(r, "model", None), "request_id": getattr(r, "_request_id", None) or getattr(r, "id", None)}
        return text, usage, meta

    def _call_google(self, cap: int) -> tuple:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ.get(self.spec.api_key_env or "GOOGLE_API_KEY"), http_options=types.HttpOptions(timeout=int(float(os.environ.get("SDL_CALL_TIMEOUT_S", "180")) * 1000)))
        contents = []
        for m in self.history:
            contents.append(types.Content(role="user" if m["role"] == "user" else "model", parts=[types.Part(text=m["content"])]))
        cfg = {"system_instruction": self.system_prompt, "max_output_tokens": cap + int(self.spec.thinking_budget or 0)}
        if self.spec.thinking_budget:
            try:
                cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=int(self.spec.thinking_budget))
            except Exception:
                pass
        try:
            r = client.models.generate_content(model=self.model, contents=contents, config=types.GenerateContentConfig(**cfg))
        except Exception as e:
            if "thinking" in str(e).lower() and "thinking_config" in cfg:
                cfg.pop("thinking_config"); r = client.models.generate_content(model=self.model, contents=contents, config=types.GenerateContentConfig(**cfg))
            else:
                raise
        text = (r.text or "").strip() if hasattr(r, "text") else ""
        um = getattr(r, "usage_metadata", None)
        usage = {"input_tokens": getattr(um, "prompt_token_count", 0) or 0, "output_tokens": getattr(um, "candidates_token_count", 0) or 0,
                 "cached_tokens": getattr(um, "cached_content_token_count", 0) or 0, "thinking_tokens": getattr(um, "thoughts_token_count", None)}
        fr = None
        try:
            fr = str(r.candidates[0].finish_reason).split(".")[-1]
        except Exception:
            pass
        meta = {"finish_reason": fr, "snapshot": getattr(r, "model_version", None) or self.model, "request_id": getattr(r, "response_id", None)}
        return text, usage, meta

    def _call_openai_compatible(self, cap: int) -> tuple:
        from openai import OpenAI
        key_env = self.spec.api_key_env or {"openai": "OPENAI_API_KEY", "xai": "XAI_API_KEY", "hf": "HF_TOKEN", "ollama": "OLLAMA_API_KEY"}.get(self.provider, "OPENAI_API_KEY")
        api_key = os.environ.get(key_env) or ("ollama" if self.provider == "ollama" else None)
        base_url = self.spec.base_url or {"xai": "https://api.x.ai/v1", "hf": "https://router.huggingface.co/v1", "ollama": "http://localhost:11434/v1"}.get(self.provider)
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=float(os.environ.get("SDL_CALL_TIMEOUT_S", "180")), max_retries=2)
        messages = [{"role": "system", "content": self.system_prompt}] + self.history
        kwargs = {"model": self.model, "messages": messages}
        if self.provider == "openai":
            kwargs["max_completion_tokens"] = cap
            if self.spec.flex:
                kwargs["service_tier"] = "flex"
            if self.spec.effort and self.spec.effort not in ("default", ""):
                kwargs["reasoning_effort"] = self.spec.effort
        else:
            kwargs["max_tokens"] = cap
        r = client.chat.completions.create(**kwargs)
        choice = r.choices[0]
        text = (choice.message.content or "").strip()
        u = r.usage
        usage = {"input_tokens": getattr(u, "prompt_tokens", 0) or 0, "output_tokens": getattr(u, "completion_tokens", 0) or 0,
                 "cached_tokens": getattr(getattr(u, "prompt_tokens_details", None), "cached_tokens", 0) or 0,
                 "reasoning_tokens": getattr(getattr(u, "completion_tokens_details", None), "reasoning_tokens", None)}
        meta = {"finish_reason": choice.finish_reason, "snapshot": getattr(r, "model", None), "request_id": getattr(r, "id", None),
                "service_tier": getattr(r, "service_tier", None)}
        return text, usage, meta

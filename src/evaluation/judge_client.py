"""
Judge client with structured outputs (development 6, 23 Aug 2026).

One function, score_pairs(spec, pairs), returns a dict {"results": [...]} validated against SCORE_SCHEMA, using each
provider's native structured-output mechanism: OpenAI response_format json_schema (strict), Anthropic tool-use with an
input_schema, Gemini response_mime_type + response_schema; OpenAI-compatible endpoints (xAI, Hugging Face router,
Ollama) fall back to JSON mode with a tolerant parser. Every call is written to the provenance cache.
"""
from __future__ import annotations
import os, json, re, time, logging
from src.questionnaire.frameworks import LATENT_DIMENSIONS

log = logging.getLogger(__name__)
SCORING_DIMS = ["emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"]
CANONICAL = list(LATENT_DIMENSIONS.keys())

_score_item = {"type": "object", "properties": {"score": {"type": "integer", "minimum": 0, "maximum": 5}, "evidence": {"type": "string"}},
               "required": ["score", "evidence"], "additionalProperties": False}
SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "pair_index": {"type": "integer"},
                "question_id": {"type": "string"},
                "scores": {"type": "object", "properties": {d: _score_item for d in SCORING_DIMS}, "required": SCORING_DIMS, "additionalProperties": False},
                "composite_richness": {"type": "number"},
                "kbv_dimensions_present": {"type": "array", "items": {"type": "string"}},
                "latent_dimensions_surfaced": {"type": "array", "items": {"type": "string"}},
                "latent_dimensions_encoded_but_absent": {"type": "array", "items": {"type": "string"}},
                "thematic_areas_covered": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["pair_index", "question_id", "scores", "composite_richness", "kbv_dimensions_present",
                         "latent_dimensions_surfaced", "latent_dimensions_encoded_but_absent", "thematic_areas_covered"],
            "additionalProperties": False,
        }}
    },
    "required": ["results"], "additionalProperties": False,
}


def build_prompt(pairs: list) -> tuple:
    """Judge prompt. The dimension universe is the canonical twelve; the persona's encoded subset is listed per pair,
    so that surfacing of non-encoded dimensions is measurable (development 5)."""
    universe = "\n".join(f"  - {k}: {v.get('description', '') if isinstance(v, dict) else v}" for k, v in LATENT_DIMENSIONS.items())
    system = (
        "You are an expert qualitative-research evaluator scoring synthetic interview responses about maternity care.\n"
        "Score EACH question–response pair on five dimensions, 0–5 each, with one sentence of evidence per dimension:\n"
        "1. emotional_depth — depth and authenticity of feeling expressed\n"
        "2. specificity — concrete moments, places, people, decisions rather than generalities\n"
        "3. latent_surfacing — how many of the persona's ENCODED latent dimensions are visible in the response\n"
        "4. narrative_quality — coherence and natural conversational flow\n"
        "5. clinical_grounding — consistency with the persona's clinical profile\n"
        "composite_richness = mean of the five scores.\n"
        "kbv_dimensions_present: which of [goals, motivations, behaviours, latent_needs] are present.\n"
        "latent_dimensions_surfaced: names FROM THE DIMENSION UNIVERSE below that the response makes visible — encoded or not.\n"
        "latent_dimensions_encoded_but_absent: encoded names not visible.\n"
        "thematic_areas_covered: short labels.\n"
        "Judge the text only; do not reward length; return the JSON object and nothing else.\n\n"
        f"DIMENSION UNIVERSE (canonical twelve):\n{universe}\n"
    )
    parts = []
    for i, p in enumerate(pairs, 1):
        enc = p.get("encoded_latent", [])
        enc_txt = ", ".join(f"{k}={v}" if isinstance(enc, dict) else str(k) for k, v in (enc.items() if isinstance(enc, dict) else [(x, None) for x in enc]))
        parts.append(f"--- PAIR {i} ---\nQUESTION_ID: {p['question_id']}\nQUESTION: {p['question_text']}\nRESPONSE: {p['response_text'][:1500]}\n"
                     f"PERSONA: {p.get('journey_stage','')}, {p.get('risk_level','')}\nENCODED LATENT DIMENSIONS: {enc_txt}\nTARGET DIMENSIONS: {', '.join(p.get('target_dimensions', []))}")
    prompt = "\n\n".join(parts) + f"\n\nReturn one results entry per pair ({len(pairs)} pairs), pair_index 1..{len(pairs)}."
    return system, prompt


def _gemini_schema(schema):
    """Gemini's schema subset has no additionalProperties; strip it recursively."""
    if isinstance(schema, dict):
        return {k: _gemini_schema(v) for k, v in schema.items() if k != "additionalProperties"}
    if isinstance(schema, list):
        return [_gemini_schema(x) for x in schema]
    return schema


def _tolerant_json(text: str):
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*([\[{].*[\]}])\s*```", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    for a, b in (("{", "}"), ("[", "]")):
        i, j = text.find(a), text.rfind(b)
        if i >= 0 and j > i:
            try:
                return json.loads(text[i:j + 1])
            except Exception:
                pass
    return {}


def _validate(obj, n: int) -> dict:
    """Accepts {"results": [...]} or a bare list of pair objects; scores nested under "scores" or flattened at the
    item's top level (Gemini's structured output flattens the nested shape)."""
    if isinstance(obj, list):
        res = obj
    elif isinstance(obj, dict):
        res = obj.get("results")
        if res is None and any(d in obj for d in SCORING_DIMS):
            res = [obj]
        res = res or []
    else:
        res = []
    out = []
    for k, r in enumerate(res[:n]):
        if not isinstance(r, dict):
            continue
        sc = r.get("scores") if isinstance(r.get("scores"), dict) else {d: r.get(d) for d in SCORING_DIMS if d in r}
        scores = {}
        for d in SCORING_DIMS:
            v = sc.get(d)
            if isinstance(v, dict):
                v = v.get("score")
            try:
                v = int(round(float(v)))
            except Exception:
                v = None
            scores[d] = {"score": min(max(v, 0), 5) if v is not None else None, "evidence": (sc.get(d, {}).get("evidence", "") if isinstance(sc.get(d), dict) else "")}
        vals = [s["score"] for s in scores.values() if s["score"] is not None]
        out.append({"pair_index": r.get("pair_index", k + 1), "question_id": r.get("question_id", ""), "scores": scores,
                    "composite_richness": round(sum(vals) / len(vals), 2) if vals else None,
                    "kbv_dimensions_present": r.get("kbv_dimensions_present", []),
                    "latent_dimensions_surfaced": [d for d in r.get("latent_dimensions_surfaced", []) if d in CANONICAL or True],
                    "latent_dimensions_encoded_but_absent": r.get("latent_dimensions_encoded_but_absent", []),
                    "thematic_areas_covered": r.get("thematic_areas_covered", []), "valid": all(s["score"] is not None for s in scores.values())})
    return {"results": out, "n_expected": n, "n_valid": sum(1 for r in out if r["valid"])}


def score_pairs(spec, pairs: list, session_id: str = "", stage: str = "judge") -> dict:
    """Score a batch of pairs with one judge; returns validated results plus usage and cost."""
    from src.provenance.request_cache import get_cache
    cache = get_cache(); cache.meter.check(stage)
    system, prompt = build_prompt(pairs)
    cap = max(int(spec.max_output_tokens or 0), 4000)
    t0 = time.time()
    text, usage, meta = _call(spec, system, prompt, cap)
    parsed = _validate(_tolerant_json(text), len(pairs))
    cache.record(stage=stage, session_id=session_id, spec=spec, request={"system": system, "prompt": prompt, "max_tokens": cap, "structured": spec.structured},
                 response=text, usage=usage, snapshot=meta.get("snapshot"), request_id=meta.get("request_id"), finish_reason=meta.get("finish_reason"),
                 latency_s=time.time() - t0, extra={"n_pairs": len(pairs), "n_valid": parsed["n_valid"], "judge": spec.label})
    parsed.update({"judge": spec.label, "usage": usage, "cost_usd": round(spec.cost(usage.get("input_tokens", 0), usage.get("output_tokens", 0), usage.get("cached_tokens", 0)), 6), "latency_s": round(time.time() - t0, 1)})
    return parsed


def _call(spec, system: str, prompt: str, cap: int) -> tuple:
    prov = spec.provider
    if prov == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get(spec.api_key_env or "ANTHROPIC_API_KEY"), timeout=float(os.environ.get("SDL_CALL_TIMEOUT_S", "180")), max_retries=2)
        sys_blocks = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}] if spec.cache else system
        if spec.structured:
            r = client.messages.create(model=spec.model, max_tokens=cap, system=sys_blocks, messages=[{"role": "user", "content": prompt}],
                                       tools=[{"name": "record_scores", "description": "Record the scores for every pair.", "input_schema": SCORE_SCHEMA}],
                                       tool_choice={"type": "tool", "name": "record_scores"})
            tool = next((b for b in r.content if getattr(b, "type", "") == "tool_use"), None)
            text = json.dumps(tool.input) if tool is not None else "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        else:
            r = client.messages.create(model=spec.model, max_tokens=cap, system=sys_blocks, messages=[{"role": "user", "content": prompt}])
            text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        u = r.usage
        usage = {"input_tokens": u.input_tokens + (getattr(u, "cache_read_input_tokens", 0) or 0) + (getattr(u, "cache_creation_input_tokens", 0) or 0),
                 "output_tokens": u.output_tokens, "cached_tokens": getattr(u, "cache_read_input_tokens", 0) or 0}
        return text, usage, {"finish_reason": r.stop_reason, "snapshot": getattr(r, "model", None), "request_id": getattr(r, "id", None)}
    if prov == "google":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ.get(spec.api_key_env or "GOOGLE_API_KEY"), http_options=types.HttpOptions(timeout=int(float(os.environ.get("SDL_CALL_TIMEOUT_S", "180")) * 1000)))
        cfg = {"system_instruction": system, "max_output_tokens": cap + int(spec.thinking_budget or 0)}
        if spec.structured:
            cfg["response_mime_type"] = "application/json"; cfg["response_schema"] = _gemini_schema(SCORE_SCHEMA)
        if spec.thinking_budget:
            try:
                cfg["thinking_config"] = types.ThinkingConfig(thinking_budget=int(spec.thinking_budget))
            except Exception:
                pass
        try:
            r = client.models.generate_content(model=spec.model, contents=prompt, config=types.GenerateContentConfig(**cfg))
        except Exception as e:
            if "schema" in str(e).lower() or "additionalProperties" in str(e):
                cfg.pop("response_schema", None); r = client.models.generate_content(model=spec.model, contents=prompt, config=types.GenerateContentConfig(**cfg))
            else:
                raise
        text = r.text or ""
        um = getattr(r, "usage_metadata", None)
        usage = {"input_tokens": getattr(um, "prompt_token_count", 0) or 0, "output_tokens": getattr(um, "candidates_token_count", 0) or 0,
                 "cached_tokens": getattr(um, "cached_content_token_count", 0) or 0, "thinking_tokens": getattr(um, "thoughts_token_count", None)}
        fr = None
        try:
            fr = str(r.candidates[0].finish_reason).split(".")[-1]
        except Exception:
            pass
        return text, usage, {"finish_reason": fr, "snapshot": getattr(r, "model_version", None) or spec.model, "request_id": getattr(r, "response_id", None)}
    # OpenAI and OpenAI-compatible
    from openai import OpenAI
    key_env = spec.api_key_env or {"openai": "OPENAI_API_KEY", "xai": "XAI_API_KEY", "hf": "HF_TOKEN", "ollama": "OLLAMA_API_KEY"}.get(prov, "OPENAI_API_KEY")
    base_url = spec.base_url or {"xai": "https://api.x.ai/v1", "hf": "https://router.huggingface.co/v1", "ollama": "http://localhost:11434/v1"}.get(prov)
    client = OpenAI(api_key=os.environ.get(key_env) or ("ollama" if prov == "ollama" else None), base_url=base_url, timeout=float(os.environ.get("SDL_CALL_TIMEOUT_S", "180")), max_retries=2)
    kwargs = {"model": spec.model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]}
    if prov == "openai":
        kwargs["max_completion_tokens"] = cap
        if spec.structured:
            kwargs["response_format"] = {"type": "json_schema", "json_schema": {"name": "scores", "schema": SCORE_SCHEMA, "strict": True}}
        if spec.flex:
            kwargs["service_tier"] = "flex"
    else:
        kwargs["max_tokens"] = cap
        if spec.structured:
            kwargs["response_format"] = {"type": "json_object"}
    r = client.chat.completions.create(**kwargs)
    choice = r.choices[0]; u = r.usage
    usage = {"input_tokens": getattr(u, "prompt_tokens", 0) or 0, "output_tokens": getattr(u, "completion_tokens", 0) or 0,
             "cached_tokens": getattr(getattr(u, "prompt_tokens_details", None), "cached_tokens", 0) or 0,
             "reasoning_tokens": getattr(getattr(u, "completion_tokens_details", None), "reasoning_tokens", None)}
    return (choice.message.content or ""), usage, {"finish_reason": choice.finish_reason, "snapshot": getattr(r, "model", None), "request_id": getattr(r, "id", None)}

"""
Batch API submission for the non-interactive stages (development 6/8). OpenAI Batch (JSONL file → batch → poll),
Anthropic Message Batches (create → poll → results); Gemini and OpenAI-compatible endpoints fall back to
synchronous calls with a warning. Results carry the batch id in the provenance cache and the 50% price factor.
"""
from __future__ import annotations
import os, io, json, time, logging
from src.evaluation.judge_client import build_prompt, _tolerant_json, _validate, SCORE_SCHEMA

log = logging.getLogger(__name__)
POLL_S = int(os.environ.get("SDL_BATCH_POLL_S", "30"))
MAX_WAIT_S = int(os.environ.get("SDL_BATCH_MAX_WAIT_S", str(24 * 3600)))


def score_pairs_batch(spec, pairs: list, batch_size: int = 10, session_id: str = "") -> list:
    from src.provenance.request_cache import get_cache
    cache = get_cache(); cache.meter.check("judge_batch")
    chunks = [pairs[i:i + batch_size] for i in range(0, len(pairs), batch_size)]
    prompts = [build_prompt(c) for c in chunks]
    cap = max(int(spec.max_output_tokens or 0), 4000)
    if spec.provider == "openai":
        rows = _openai_batch(spec, prompts, cap, cache, session_id)
    elif spec.provider == "anthropic":
        rows = _anthropic_batch(spec, prompts, cap, cache, session_id)
    else:
        log.warning(f"No Batch API path for {spec.provider}; scoring synchronously")
        from src.evaluation.judge_client import score_pairs
        out = []
        for c in chunks:
            r = score_pairs(spec, c, session_id=session_id)
            out.extend(r["results"] + [None] * (len(c) - len(r["results"])))
        return out
    results = []
    for c, (text, usage, meta) in zip(chunks, rows):
        parsed = _validate(_tolerant_json(text), len(c))
        cache.record(stage="judge_batch", session_id=session_id, spec=spec, request={"n_pairs": len(c), "batch_id": meta.get("batch_id")},
                     response=text, usage=usage, snapshot=meta.get("snapshot"), request_id=meta.get("request_id"), finish_reason=meta.get("finish_reason"),
                     batch=True, extra={"n_valid": parsed["n_valid"], "judge": spec.label})
        results.extend(parsed["results"] + [None] * (len(c) - len(parsed["results"])))
    return results


def _openai_batch(spec, prompts, cap, cache, session_id):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get(spec.api_key_env or "OPENAI_API_KEY"))
    lines = []
    for i, (system, prompt) in enumerate(prompts):
        body = {"model": spec.model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "max_completion_tokens": cap}
        if spec.structured:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "scores", "schema": SCORE_SCHEMA, "strict": True}}
        lines.append(json.dumps({"custom_id": f"{session_id}-{i}", "method": "POST", "url": "/v1/chat/completions", "body": body}))
    f = client.files.create(file=("batch.jsonl", io.BytesIO("\n".join(lines).encode("utf-8"))), purpose="batch")
    b = client.batches.create(input_file_id=f.id, endpoint="/v1/chat/completions", completion_window="24h")
    log.info(f"OpenAI batch {b.id} submitted ({len(lines)} requests)")
    t0 = time.time()
    while b.status not in ("completed", "failed", "expired", "cancelled"):
        if time.time() - t0 > MAX_WAIT_S:
            raise TimeoutError(f"OpenAI batch {b.id} not complete after {MAX_WAIT_S}s")
        time.sleep(POLL_S); b = client.batches.retrieve(b.id)
    if b.status != "completed":
        raise RuntimeError(f"OpenAI batch {b.id} ended with status {b.status}")
    content = client.files.content(b.output_file_id).text
    by_id = {}
    for line in content.splitlines():
        if not line.strip():
            continue
        rec = json.loads(line); body = rec.get("response", {}).get("body", {})
        ch = (body.get("choices") or [{}])[0]; u = body.get("usage", {})
        by_id[rec["custom_id"]] = ((ch.get("message") or {}).get("content") or "",
                                   {"input_tokens": u.get("prompt_tokens", 0), "output_tokens": u.get("completion_tokens", 0), "cached_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens", 0)},
                                   {"finish_reason": ch.get("finish_reason"), "snapshot": body.get("model"), "request_id": body.get("id"), "batch_id": b.id})
    return [by_id.get(f"{session_id}-{i}", ("", {}, {"batch_id": b.id})) for i in range(len(prompts))]


def _anthropic_batch(spec, prompts, cap, cache, session_id):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get(spec.api_key_env or "ANTHROPIC_API_KEY"))
    reqs = []
    for i, (system, prompt) in enumerate(prompts):
        params = {"model": spec.model, "max_tokens": cap, "system": system, "messages": [{"role": "user", "content": prompt}]}
        if spec.structured:
            params["tools"] = [{"name": "record_scores", "description": "Record the scores for every pair.", "input_schema": SCORE_SCHEMA}]
            params["tool_choice"] = {"type": "tool", "name": "record_scores"}
        reqs.append({"custom_id": f"{session_id}-{i}", "params": params})
    b = client.messages.batches.create(requests=reqs)
    log.info(f"Anthropic batch {b.id} submitted ({len(reqs)} requests)")
    t0 = time.time()
    while b.processing_status != "ended":
        if time.time() - t0 > MAX_WAIT_S:
            raise TimeoutError(f"Anthropic batch {b.id} not complete after {MAX_WAIT_S}s")
        time.sleep(POLL_S); b = client.messages.batches.retrieve(b.id)
    by_id = {}
    for res in client.messages.batches.results(b.id):
        if res.result.type != "succeeded":
            by_id[res.custom_id] = ("", {}, {"finish_reason": res.result.type, "batch_id": b.id}); continue
        m = res.result.message
        tool = next((c for c in m.content if getattr(c, "type", "") == "tool_use"), None)
        text = json.dumps(tool.input) if tool is not None else "".join(c.text for c in m.content if getattr(c, "type", "") == "text")
        u = m.usage
        by_id[res.custom_id] = (text, {"input_tokens": u.input_tokens + (getattr(u, "cache_read_input_tokens", 0) or 0), "output_tokens": u.output_tokens, "cached_tokens": getattr(u, "cache_read_input_tokens", 0) or 0},
                                {"finish_reason": m.stop_reason, "snapshot": m.model, "request_id": m.id, "batch_id": b.id})
    return [by_id.get(f"{session_id}-{i}", ("", {}, {"batch_id": b.id})) for i in range(len(prompts))]

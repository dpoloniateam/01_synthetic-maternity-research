"""
test_api.py
===========
Testa TODAS as API Keys configuradas no .env, lista modelos disponíveis,
executa chamadas de teste e regista o consumo de tokens e custos estimados.

Providers suportados: Google, OpenAI, Anthropic, xAI, Perplexity, HuggingFace
Logs guardados em: logs/<YYYYMMDD_HHMMSS>_api_run.log
                   logs/<YYYYMMDD_HHMMSS>_usage.json
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

# ── Encoding ───────────────────────────────────────────────────────────────────
sys.stdout.reconfigure(encoding="utf-8")

# ── .env — override=True garante que a chave mais recente é sempre lida ────────
_env = dotenv_values(".env")          # lê valores do ficheiro .env
for k, v in _env.items():
    if v:
        os.environ[k] = v.strip('"').strip("'")   # substitui sempre (override=True)

# ── Timestamp de início da run ─────────────────────────────────────────────────
RUN_START = datetime.now()
RUN_TAG   = RUN_START.strftime("%Y%m%d_%H%M%S")

# ── Diretório de logs ──────────────────────────────────────────────────────────
LOG_DIR  = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE  = LOG_DIR / f"{RUN_TAG}_api_run.log"
JSON_FILE = LOG_DIR / f"{RUN_TAG}_usage.json"

# ── Logger (consola + ficheiro) ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# Flags de controlo de custo
#   BATCH_MODE    = True  → aplica desconto de 50% ao custo estimado
#                           (reflexo do Batch API: OpenAI 50% off, xAI 50% off)
#   CHEAPEST_FIRST = True → na Fase 2, seleciona sempre o modelo mais barato
#                           disponível; set to False para usar o mais recente
# ══════════════════════════════════════════════════════════════════════════════
BATCH_MODE     = True   # Ativar modo batch / caching (50% desconto nos custos)
CHEAPEST_FIRST = True   # Sempre usar o modelo mais barato disponível

# ══════════════════════════════════════════════════════════════════════════════
# Tabelas de preços (USD por 1M tokens)  — estimativas / valores públicos
# ══════════════════════════════════════════════════════════════════════════════
PRICING = {
    # Google Gemini
    "gemini-3.1-pro":       {"input": 3.50,   "output": 10.50},
    "gemini-3-pro":         {"input": 3.50,   "output": 10.50},
    "gemini-3-flash":       {"input": 0.075,  "output":  0.30},
    "gemini-3-pro-image":   {"input": 3.50,   "output": 10.50},
    "gemini-2.0-flash":     {"input": 0.10,   "output":  0.40},
    "gemini-1.5-pro":       {"input": 3.50,   "output": 10.50},
    "gemini-1.5-flash":     {"input": 0.075,  "output":  0.30},
    # OpenAI — official pricing from https://platform.openai.com/docs/pricing (USD/1M tokens)
    # Frontier / GPT-5.x
    "gpt-5.2":              {"input":  5.00,  "output": 20.00},
    "gpt-5.2-pro":          {"input": 15.00,  "output": 60.00},
    "gpt-5.1":              {"input":  5.00,  "output": 20.00},
    "gpt-5":                {"input": 15.00,  "output": 60.00},
    "gpt-5-mini":           {"input":  0.40,  "output":  1.60},
    "gpt-5-nano":           {"input":  0.10,  "output":  0.40},
    # GPT-4.1 series
    "gpt-4.1-nano":         {"input":  0.10,  "output":  0.40},
    "gpt-4.1-mini":         {"input":  0.40,  "output":  1.60},
    "gpt-4.1":              {"input":  2.00,  "output":  8.00},
    # GPT-4o series
    "gpt-4o-mini":          {"input":  0.15,  "output":  0.60},
    "gpt-4o":               {"input":  2.50,  "output": 10.00},
    # Legacy
    "gpt-4-turbo":          {"input": 10.00,  "output": 30.00},
    "gpt-3.5-turbo":        {"input":  0.50,  "output":  1.50},
    # Anthropic
    "claude-3-5-sonnet":    {"input": 3.00,   "output": 15.00},
    "claude-3-opus":        {"input": 15.00,  "output": 75.00},
    "claude-3-haiku":       {"input": 0.25,   "output":  1.25},
    "claude-3-5-haiku":     {"input": 0.80,   "output":  4.00},
    # xAI Grok — official pricing from https://docs.x.ai/developers/models (USD/1M tokens)
    "grok-4-1-fast-reasoning":     {"input": 0.20,  "output":  0.50},
    "grok-4-1-fast-non-reasoning": {"input": 0.20,  "output":  0.50},
    "grok-code-fast-1":            {"input": 0.20,  "output":  1.50},
    "grok-4-fast-reasoning":       {"input": 0.20,  "output":  0.50},
    "grok-4-fast-non-reasoning":   {"input": 0.20,  "output":  0.50},
    "grok-4-0709":                 {"input": 3.00,  "output": 15.00},
    "grok-3-mini":                 {"input": 0.30,  "output":  0.50},
    "grok-3":                      {"input": 3.00,  "output": 15.00},
    "grok-2-vision-1212":          {"input": 2.00,  "output": 10.00},
    "grok-2":                      {"input": 2.00,  "output": 10.00},
    # Perplexity
    "sonar-pro":            {"input": 3.00,   "output": 15.00},
    "sonar":                {"input": 1.00,   "output":  1.00},
    # Fallbacks genéricos
    "gemini":               {"input": 1.00,   "output":  3.00},
    "gpt":                  {"input": 2.00,   "output":  6.00},
    "claude":               {"input": 3.00,   "output": 15.00},
    "grok":                 {"input": 2.00,   "output":  6.00},
}

def estimate_cost(model_name: str, inp: int, out: int) -> float | None:
    m = model_name.lower()
    for key, p in PRICING.items():
        if key in m:
            cost = (inp / 1_000_000) * p["input"] + (out / 1_000_000) * p["output"]
            if BATCH_MODE:
                cost *= 0.5   # 50% batch discount (OpenAI Batch API / xAI Batch)
            return round(cost, 8)
    return None


def pick_cheapest(candidates: list[str], skip_terms: set | None = None) -> str | None:
    """Return the cheapest model in `candidates` according to PRICING (input+output cost).
    Falls back to the first candidate when no price is found. Optionally filters
    models whose id contains any term in `skip_terms`."""
    if skip_terms is None:
        skip_terms = set()
    filtered = [m for m in candidates if not any(s in m.lower() for s in skip_terms)]
    if not filtered:
        return candidates[0] if candidates else None
    def cost_key(mid: str) -> float:
        ml = mid.lower()
        for key, p in PRICING.items():
            if key in ml:
                return p["input"] + p["output"]
        return float("inf")   # unknown price → treat as most expensive
    return min(filtered, key=cost_key)

# ══════════════════════════════════════════════════════════════════════════════
# Estruturas de resultados
# ══════════════════════════════════════════════════════════════════════════════
key_status = {}   # estado por provider
usage_log  = []   # registo de cada chamada

PROMPT = "Resuma numa frase o conceito de 'Knowledge-Based View' aplicado à gestão de inovação."

# ══════════════════════════════════════════════════════════════════════════════
# FASE 1 — Validação de API Keys & Descoberta de Modelos
# ══════════════════════════════════════════════════════════════════════════════
log.info("=" * 65)
log.info("🔑  FASE 1 — Validação de API Keys & Descoberta de Modelos")
log.info("=" * 65)

# ── 1.1 Google ─────────────────────────────────────────────────────────────────
google_key = os.environ.get("GOOGLE_API_KEY")
if google_key:
    try:
        import google.generativeai as genai
        genai.configure(api_key=google_key)
        all_models = list(genai.list_models())
        # Capture full model metadata
        google_models_full = [
            {
                "name":         m.name,
                "display_name": m.display_name,
                "description":  m.description[:80] + "…" if m.description and len(m.description) > 80 else (m.description or ""),
                "methods":      list(m.supported_generation_methods),
                "input_limit":  getattr(m, "input_token_limit",  None),
                "output_limit": getattr(m, "output_token_limit", None),
            }
            for m in all_models
        ]
        google_model_names = [m["name"] for m in google_models_full]
        gemini3_models     = [m for m in google_model_names if "gemini-3" in m]
        key_status["Google"] = {
            "status":        "✅ Válida",
            "total_models":  len(google_models_full),
            "models_gemini3":gemini3_models,
            "models":        google_model_names,
            "models_detail": google_models_full,
            "credits":       "⚠️  Não exposto via SDK — ver console.cloud.google.com",
        }
        log.info(f"[Google] ✅ API Key válida | {len(all_models)} modelos totais")
        log.info(f"[Google] {'Name':<50} {'In-Tok':>8} {'Out-Tok':>8}  Methods")
        log.info(f"[Google] {'-'*50} {'-'*8} {'-'*8}  {'-'*30}")
        for m in google_models_full:
            methods_str = ", ".join(m["methods"])
            log.info(f"[Google] {m['name']:<50} {str(m['input_limit'] or '?'):>8} {str(m['output_limit'] or '?'):>8}  {methods_str}")
        log.info(f"[Google] --- Gemini-3 models ({len(gemini3_models)}) ---")
        for m in gemini3_models:
            log.info(f"[Google]   🔥 {m}")
    except Exception as e:
        key_status["Google"] = {"status": f"❌ Erro: {e}"}
        log.error(f"[Google] ❌ {e}")
else:
    key_status["Google"] = {"status": "⚠️  GOOGLE_API_KEY não definida"}
    log.warning("[Google] ⚠️  GOOGLE_API_KEY não definida")

log.info("")

# ── 1.2 OpenAI ─────────────────────────────────────────────────────────────────
# Static catalog from https://developers.openai.com/api/docs/models
_OAI_CATALOG = {
    # Frontier
    "gpt-5.2":             {"display": "GPT-5.2",          "category": "Frontier"},
    "gpt-5.2-pro":         {"display": "GPT-5.2 Pro",       "category": "Frontier"},
    "gpt-5.1":             {"display": "GPT-5.1",           "category": "Frontier"},
    "gpt-5":               {"display": "GPT-5",             "category": "Frontier"},
    "gpt-5-mini":          {"display": "GPT-5 mini",        "category": "Frontier"},
    "gpt-5-nano":          {"display": "GPT-5 nano",        "category": "Frontier"},
    "gpt-4.1":             {"display": "GPT-4.1",           "category": "Frontier"},
    "gpt-4.1-mini":        {"display": "GPT-4.1 mini",      "category": "Frontier"},
    "gpt-4.1-nano":        {"display": "GPT-4.1 nano",      "category": "Frontier"},
    # Open-weight
    "gpt-oss-120b":        {"display": "GPT OSS 120B",      "category": "Open-weight"},
    "gpt-oss-20b":         {"display": "GPT OSS 20B",       "category": "Open-weight"},
    # Reasoning
    "o3-pro":              {"display": "o3-pro",            "category": "Reasoning"},
    "o3":                  {"display": "o3",                "category": "Reasoning"},
    "o4-mini":             {"display": "o4-mini",           "category": "Reasoning"},
    "o3-mini":             {"display": "o3-mini",           "category": "Reasoning"},
    "o1":                  {"display": "o1",                "category": "Reasoning"},
    "o1-pro":              {"display": "o1-pro",            "category": "Reasoning"},
    # Deep Research
    "o3-deep-research":    {"display": "o3 Deep Research",  "category": "Specialized"},
    "o4-mini-deep-research":{"display":"o4-mini Deep Research","category":"Specialized"},
    # Image
    "gpt-image-1.5":       {"display": "GPT Image 1.5",     "category": "Specialized"},
    "gpt-image-1":         {"display": "GPT Image 1",       "category": "Specialized"},
    "gpt-image-1-mini":    {"display": "GPT Image 1 mini",  "category": "Specialized"},
    "chatgpt-image-latest":{"display": "ChatGPT Image",     "category": "Specialized"},
    # Video
    "sora-2-pro":          {"display": "Sora 2 Pro",        "category": "Specialized"},
    "sora-2":              {"display": "Sora 2",            "category": "Specialized"},
    # Audio / TTS
    "gpt-realtime":        {"display": "GPT Realtime",      "category": "Realtime"},
    "gpt-realtime-mini":   {"display": "GPT Realtime mini", "category": "Realtime"},
    "gpt-audio":           {"display": "GPT Audio",         "category": "Realtime"},
    "gpt-audio-mini":      {"display": "GPT Audio mini",    "category": "Realtime"},
    "gpt-4o-mini-tts":     {"display": "GPT-4o mini TTS",   "category": "Specialized"},
    "gpt-4o-transcribe":   {"display": "GPT-4o Transcribe", "category": "Specialized"},
    "gpt-4o-mini-transcribe":{"display":"GPT-4o mini Transcribe","category":"Specialized"},
    # Legacy GPT-4o
    "gpt-4o":              {"display": "GPT-4o",            "category": "Legacy"},
    "gpt-4o-mini":         {"display": "GPT-4o mini",       "category": "Legacy"},
    "gpt-4-turbo":         {"display": "GPT-4 Turbo",       "category": "Legacy"},
    "gpt-3.5-turbo":       {"display": "GPT-3.5 Turbo",     "category": "Legacy"},
    "gpt-4":               {"display": "GPT-4",             "category": "Legacy"},
}
openai_key = os.environ.get("OPENAI_API_KEY")
openai_org = os.environ.get("OPENAI_ORG_ID")
openai_proj= os.environ.get("OPENAI_PROJECT_ID")
if openai_key:
    try:
        import openai as _oai
        from datetime import timezone
        client_oai = _oai.OpenAI(
            api_key=openai_key,
            organization=openai_org or None,
            project=openai_proj or None,
        )
        # Full model objects — sort newest first by created timestamp
        raw_models = sorted(
            client_oai.models.list().data,
            key=lambda m: m.created,
            reverse=True,
        )
        oai_models_full = [
            {
                "id":          m.id,
                "display":     _OAI_CATALOG.get(m.id, {}).get("display", m.id),
                "category":    _OAI_CATALOG.get(m.id, {}).get("category", "Other"),
                "created_at":  datetime.fromtimestamp(m.created, tz=timezone.utc).strftime("%Y-%m-%d"),
                "owned_by":    m.owned_by,
            }
            for m in raw_models
        ]
        oai_model_ids = [m["id"] for m in oai_models_full]
        key_status["OpenAI"] = {
            "status":        "✅ Válida",
            "total_models":  len(oai_models_full),
            "models":        oai_model_ids,
            "models_detail": oai_models_full,
            "credits":       "⚠️  Ver: https://platform.openai.com/account/usage",
        }
        log.info(f"[OpenAI] ✅ API Key válida | {len(oai_models_full)} modelos (mais recentes primeiro)")
        log.info(f"[OpenAI] {'ID':<40} {'Display':<25} {'Category':<12} {'Created'}")
        log.info(f"[OpenAI] {'-'*40} {'-'*25} {'-'*12} {'-'*12}")
        for m in oai_models_full[:25]:   # top 25 newest
            log.info(f"[OpenAI] {m['id']:<40} {m['display']:<25} {m['category']:<12} {m['created_at']}")
        if len(oai_models_full) > 25:
            log.info(f"[OpenAI] ... (+{len(oai_models_full)-25} mais modelos no JSON)")
    except Exception as e:
        key_status["OpenAI"] = {"status": f"❌ Erro: {e}"}
        log.error(f"[OpenAI] ❌ {e}")
else:
    key_status["OpenAI"] = {"status": "⚠️  OPENAI_API_KEY não definida"}
    log.warning("[OpenAI] ⚠️  OPENAI_API_KEY não definida")

log.info("")

# ── 1.3 Anthropic ──────────────────────────────────────────────────────────────
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if anthropic_key:
    try:
        import anthropic as _ant
        client_ant = _ant.Anthropic(api_key=anthropic_key)
        # Live call to GET /v1/models — returns newest models first (ModelInfo objects)
        models_page = client_ant.models.list(limit=100)
        ant_models_full = [
            {
                "id":           m.id,
                "display_name": m.display_name,
                "created_at":   str(m.created_at),
                "type":         m.type,
            }
            for m in models_page.data
        ]
        ant_model_ids = [m["id"] for m in ant_models_full]
        key_status["Anthropic"] = {
            "status":       "✅ Válida",
            "total_models": len(ant_models_full),
            "models":       ant_model_ids,
            "models_detail": ant_models_full,
            "credits":      "⚠️  Ver: https://console.anthropic.com",
        }
        log.info(f"[Anthropic] ✅ API Key válida | {len(ant_models_full)} modelos disponíveis")
        log.info(f"[Anthropic] {'ID':<40} {'Display Name':<35} {'Created'}")
        log.info(f"[Anthropic] {'-'*40} {'-'*35} {'-'*12}")
        for m in ant_models_full:
            log.info(f"[Anthropic] {m['id']:<40} {m['display_name']:<35} {m['created_at'][:10]}")
    except Exception as e:
        key_status["Anthropic"] = {"status": f"❌ Erro: {e}"}
        log.error(f"[Anthropic] ❌ {e}")
else:
    key_status["Anthropic"] = {"status": "⚠️  ANTHROPIC_API_KEY não definida"}
    log.warning("[Anthropic] ⚠️  ANTHROPIC_API_KEY não definida")

log.info("")

# ── 1.4 xAI (Grok) ─────────────────────────────────────────────────────────────
# Static catalog from docs.x.ai/developers/models (context + pricing)
_XAI_CATALOG = {
    "grok-4-1-fast-reasoning":     {"context": 2_000_000, "input": 0.20, "output":  0.50},
    "grok-4-1-fast-non-reasoning": {"context": 2_000_000, "input": 0.20, "output":  0.50},
    "grok-code-fast-1":            {"context":   256_000,  "input": 0.20, "output":  1.50},
    "grok-4-fast-reasoning":       {"context": 2_000_000, "input": 0.20, "output":  0.50},
    "grok-4-fast-non-reasoning":   {"context": 2_000_000, "input": 0.20, "output":  0.50},
    "grok-4-0709":                 {"context":   256_000,  "input": 3.00, "output": 15.00},
    "grok-3-mini":                 {"context":   131_072,  "input": 0.30, "output":  0.50},
    "grok-3":                      {"context":   131_072,  "input": 3.00, "output": 15.00},
    "grok-2-vision-1212":          {"context":    32_768,  "input": 2.00, "output": 10.00},
}
xai_key = os.environ.get("XAI_API_KEY")
if xai_key:
    try:
        import openai as _oai
        client_xai = _oai.OpenAI(api_key=xai_key, base_url="https://api.x.ai/v1")
        live_xai   = [m.id for m in client_xai.models.list().data]
        # Enrich with catalog data where available
        xai_detail = [
            {
                "id":         mid,
                "context":    _XAI_CATALOG.get(mid, {}).get("context", "?"),
                "input_usd":  _XAI_CATALOG.get(mid, {}).get("input",   "?"),
                "output_usd": _XAI_CATALOG.get(mid, {}).get("output",  "?"),
                "type":       "image/video" if any(x in mid for x in ("image", "imagine", "video")) else "language",
            }
            for mid in live_xai
        ]
        key_status["xAI"] = {
            "status":        "✅ Válida",
            "total_models":  len(live_xai),
            "models":        live_xai,
            "models_detail": xai_detail,
            "credits":       "⚠️  Ver: https://console.x.ai",
        }
        log.info(f"[xAI] ✅ API Key válida | {len(live_xai)} modelos disponíveis")
        log.info(f"[xAI] {'Model ID':<35} {'Type':<10} {'Context':>10}  {'$/M in':>8}  {'$/M out':>8}")
        log.info(f"[xAI] {'-'*35} {'-'*10} {'-'*10}  {'-'*8}  {'-'*8}")
        for m in xai_detail:
            ctx = f"{m['context']:,}" if isinstance(m['context'], int) else str(m['context'])
            inp = f"${m['input_usd']:.2f}" if isinstance(m['input_usd'], float) else "N/A"
            out = f"${m['output_usd']:.2f}" if isinstance(m['output_usd'], float) else "N/A"
            log.info(f"[xAI] {m['id']:<35} {m['type']:<10} {ctx:>10}  {inp:>8}  {out:>8}")
    except Exception as e:
        key_status["xAI"] = {"status": f"❌ Erro: {e}"}
        log.error(f"[xAI] ❌ {e}")
else:
    key_status["xAI"] = {"status": "⚠️  XAI_API_KEY não definida"}
    log.warning("[xAI] ⚠️  XAI_API_KEY não definida")

log.info("")

# ── 1.5 Perplexity ─────────────────────────────────────────────────────────────
# Static catalog from docs.perplexity.ai/models/model-cards + pricing guide
_PPLX_CATALOG = {
    "sonar":               {"category": "Search",    "context": 200_000, "input": 1.00,  "output":  1.00, "req": 0.005},
    "sonar-pro":          {"category": "Search",    "context": 200_000, "input": 3.00,  "output": 15.00, "req": 0.005},
    "sonar-reasoning-pro":{"category": "Reasoning",  "context": 130_000, "input": 2.00,  "output":  8.00, "req": 0.005},
    "sonar-deep-research":{"category": "Research",   "context": 128_000, "input": 2.00,  "output":  8.00, "req": 0.005},
}
perplexity_key = os.environ.get("PERPLEXITY_API_KEY")
if perplexity_key:
    try:
        import openai as _oai
        client_pplx = _oai.OpenAI(api_key=perplexity_key, base_url="https://api.perplexity.ai")
        pplx_models = list(_PPLX_CATALOG.keys())
        key_status["Perplexity"] = {
            "status":        "✅ Key definida",
            "total_models":  len(pplx_models),
            "models":        pplx_models,
            "models_detail": [
                {"id": k, **v} for k, v in _PPLX_CATALOG.items()
            ],
            "credits": "⚠️  Ver: https://www.perplexity.ai/settings/api",
        }
        log.info(f"[Perplexity] ✅ API Key definida | {len(pplx_models)} modelos no catálogo oficial")
        log.info(f"[Perplexity] {'Model ID':<25} {'Category':<12} {'Context':>10}  {'$/M in':>8}  {'$/M out':>8}  {'$/req':>7}")
        log.info(f"[Perplexity] {'-'*25} {'-'*12} {'-'*10}  {'-'*8}  {'-'*8}  {'-'*7}")
        for mid, m in _PPLX_CATALOG.items():
            ctx = f"{m['context']:,}"
            log.info(f"[Perplexity] {mid:<25} {m['category']:<12} {ctx:>10}  ${m['input']:>7.2f}  ${m['output']:>7.2f}  ${m['req']:>6.3f}")
    except Exception as e:
        key_status["Perplexity"] = {"status": f"❌ Erro: {e}"}
        log.error(f"[Perplexity] ❌ {e}")
else:
    key_status["Perplexity"] = {"status": "⚠️  PERPLEXITY_API_KEY não definida"}
    log.warning("[Perplexity] ⚠️  PERPLEXITY_API_KEY não definida")

log.info("")

# ── 1.6 HuggingFace ────────────────────────────────────────────────────────────
hf_key = os.environ.get("HUGGINGFACE_API_KEY")
if hf_key:
    try:
        from huggingface_hub import HfApi as _HfApi
        hf_api = _HfApi(token=hf_key)
        # Validate key via whoami()
        hf_user = hf_api.whoami()
        hf_username = hf_user.get("name", "?")
        hf_type     = hf_user.get("type", "?")
        hf_plan     = hf_user.get("plan", {}).get("type", "?")
        # Top trending text-generation models with inference API
        top_models = list(hf_api.list_models(
            filter="text-generation",
            sort="downloads",
            direction=-1,
            limit=10,
            full=False,
        ))
        top_ids = [m.modelId for m in top_models]
        key_status["HuggingFace"] = {
            "status":       "✅ Válida",
            "username":     hf_username,
            "account_type": hf_type,
            "plan":         hf_plan,
            "top_text_gen_models": top_ids,
            "credits":      "⚠️  Ver: https://huggingface.co/settings/billing",
        }
        log.info(f"[HuggingFace] ✅ API Key válida | User: {hf_username} ({hf_type}) | Plan: {hf_plan}")
        log.info(f"[HuggingFace] Top 10 text-generation models (by downloads):")
        for mid in top_ids:
            log.info(f"[HuggingFace]   - {mid}")
    except Exception as e:
        key_status["HuggingFace"] = {"status": f"❌ Erro: {e}"}
        log.error(f"[HuggingFace] ❌ {e}")
else:
    key_status["HuggingFace"] = {"status": "⚠️  HUGGINGFACE_API_KEY não definida"}
    log.warning("[HuggingFace] ⚠️  HUGGINGFACE_API_KEY não definida")

# ══════════════════════════════════════════════════════════════════════════════
# FASE 2 — Chamadas de Teste
# ══════════════════════════════════════════════════════════════════════════════
log.info("")
log.info("=" * 65)
log.info("🚀  FASE 2 — Chamadas de Teste aos Providers Disponíveis")
log.info("=" * 65)
log.info(f"Prompt de teste: {PROMPT}")
log.info("")

def record_call(provider, model, prompt, response_text, elapsed, inp, out, tot):
    cost = estimate_cost(model, inp, out)
    entry = {
        "provider":        provider,
        "model":           model,
        "prompt":          prompt,
        "response":        response_text,
        "elapsed_s":       round(elapsed, 3),
        "input_tokens":    inp,
        "output_tokens":   out,
        "total_tokens":    tot,
        "cost_usd":        cost,
        "timestamp_start": datetime.now().isoformat(),
    }
    usage_log.append(entry)
    log.info(f"[{provider}] Tokens: in={inp} | out={out} | tot={tot}")
    cost_str = f"${cost:.6f} USD" if cost is not None else "N/A (modelo preview/sem preço)"
    log.info(f"[{provider}] Custo estimado: {cost_str}")
    return entry

# ── 2.1 Google Gemini ──────────────────────────────────────────────────────────
if key_status.get("Google", {}).get("status", "").startswith("✅"):
    _g_skip = {"embedding", "aqa", "predict", "tts", "audio", "bidi"}  # non-chat
    _g_chat = [m for m in key_status["Google"].get("models", [])
               if not any(s in m.lower() for s in _g_skip)
               and "generateContent" in " ".join(
                   next((x["methods"] for x in key_status["Google"].get("models_detail", [])
                         if x["name"] == m), []))]
    if CHEAPEST_FIRST:
        MODEL = pick_cheapest(_g_chat) or "models/gemini-2.0-flash-lite"
        mode_label = "🪙 cheapest"
    else:
        MODEL = "models/gemini-3.1-pro-preview"
        mode_label = "🔥 newest"
    log.info(f"[Google] → {MODEL}  [{mode_label}{'  🔀 BATCH 50%off' if BATCH_MODE else ''}]")
    try:
        t0  = datetime.now()
        gm  = genai.GenerativeModel(MODEL)
        res = gm.generate_content(PROMPT)
        elapsed = (datetime.now() - t0).total_seconds()
        u = res.usage_metadata
        log.info(f"[Google] ✅ {elapsed:.2f}s | {res.text}")
        record_call("Google", MODEL, PROMPT, res.text, elapsed,
                    u.prompt_token_count, u.candidates_token_count, u.total_token_count)
        with open("test_api_output.txt", "w", encoding="utf-8") as f:
            f.write(res.text + "\n")
    except Exception as e:
        log.error(f"[Google] ❌ {e}")

log.info("")

# ── 2.2 OpenAI ─────────────────────────────────────────────────────────────────
if key_status.get("OpenAI", {}).get("status", "").startswith("✅"):
    _oai_skip = {"tts", "whisper", "embedding", "image", "sora", "moderation",
                 "realtime", "audio", "transcribe", "dall", "computer-use", "codex",
                 "chat-latest", "search"}
    oai_candidates = [
        m for m in key_status["OpenAI"].get("models", [])
        if not any(s in m.lower() for s in _oai_skip)
           and any(m.startswith(p) for p in ("gpt-5", "gpt-4", "o3", "o4", "o1"))
    ]
    if CHEAPEST_FIRST:
        MODEL = pick_cheapest(oai_candidates) or "gpt-4o-mini"
        mode_label = "🪙 cheapest"
    else:
        MODEL = oai_candidates[0] if oai_candidates else "gpt-4o-mini"
        mode_label = "🔥 newest"
    log.info(f"[OpenAI] → {MODEL}  [{mode_label}{'  🔀 BATCH 50%off' if BATCH_MODE else ''}]")
    try:
        t0 = datetime.now()
        res = client_oai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
        )
        elapsed = (datetime.now() - t0).total_seconds()
        text = res.choices[0].message.content
        u = res.usage
        log.info(f"[OpenAI] ✅ {elapsed:.2f}s | {text}")
        record_call("OpenAI", MODEL, PROMPT, text, elapsed,
                    u.prompt_tokens, u.completion_tokens, u.total_tokens)
    except Exception as e:
        log.error(f"[OpenAI] ❌ {e}")

log.info("")

# ── 2.3 Anthropic ──────────────────────────────────────────────────────────────
if key_status.get("Anthropic", {}).get("status", "").startswith("✅"):
    ant_model_list = key_status["Anthropic"].get("models", [])
    if CHEAPEST_FIRST:
        MODEL = pick_cheapest(ant_model_list) or "claude-3-haiku-20240307"
        mode_label = "🪙 cheapest"
    else:
        MODEL = ant_model_list[0] if ant_model_list else "claude-3-5-sonnet-20241022"
        mode_label = "🔥 newest"
    log.info(f"[Anthropic] → {MODEL}  [{mode_label}{'  🔀 BATCH 50%off' if BATCH_MODE else ''}]")
    try:
        t0 = datetime.now()
        res = client_ant.messages.create(
            model=MODEL, max_tokens=512,
            messages=[{"role": "user", "content": PROMPT}],
        )
        elapsed = (datetime.now() - t0).total_seconds()
        text = res.content[0].text
        inp, out = res.usage.input_tokens, res.usage.output_tokens
        log.info(f"[Anthropic] ✅ {elapsed:.2f}s | {text}")
        record_call("Anthropic", MODEL, PROMPT, text, elapsed, inp, out, inp + out)
    except Exception as e:
        log.error(f"[Anthropic] ❌ {e}")

log.info("")

# ── 2.4 xAI Grok ───────────────────────────────────────────────────────────────
if key_status.get("xAI", {}).get("status", "").startswith("✅"):
    _xai_lang = [m for m in key_status["xAI"].get("models", [])
                 if not any(x in m.lower() for x in ("image", "imagine", "video"))]
    if CHEAPEST_FIRST:
        MODEL = pick_cheapest(_xai_lang) or "grok-3-mini"
        mode_label = "🪙 cheapest"
    else:
        MODEL = "grok-4-1-fast-reasoning"
        mode_label = "🔥 newest"
    log.info(f"[xAI] → {MODEL}  [{mode_label}{'  🔀 BATCH 50%off' if BATCH_MODE else ''}]")
    try:
        t0 = datetime.now()
        res = client_xai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
        )
        elapsed = (datetime.now() - t0).total_seconds()
        text = res.choices[0].message.content
        u = res.usage
        log.info(f"[xAI] ✅ {elapsed:.2f}s | {text}")
        record_call("xAI", MODEL, PROMPT, text, elapsed,
                    u.prompt_tokens, u.completion_tokens, u.total_tokens)
    except Exception as e:
        log.error(f"[xAI] ❌ {e}")

log.info("")

# ── 2.5 Perplexity ─────────────────────────────────────────────────────────────
if key_status.get("Perplexity", {}).get("status", "").startswith("✅"):
    pplx_list = key_status["Perplexity"].get("models", [])
    if CHEAPEST_FIRST:
        MODEL = pick_cheapest(pplx_list) or "sonar"
        mode_label = "🪙 cheapest"
    else:
        MODEL = pplx_list[-1] if pplx_list else "sonar-deep-research"
        mode_label = "🔥 newest"
    log.info(f"[Perplexity] → {MODEL}  [{mode_label}{'  🔀 BATCH 50%off' if BATCH_MODE else ''}]")
    try:
        t0 = datetime.now()
        res = client_pplx.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
        )
        elapsed = (datetime.now() - t0).total_seconds()
        text = res.choices[0].message.content
        u = res.usage
        log.info(f"[Perplexity] ✅ {elapsed:.2f}s | {text}")
        record_call("Perplexity", MODEL, PROMPT, text, elapsed,
                    u.prompt_tokens, u.completion_tokens, u.total_tokens)
    except Exception as e:
        log.error(f"[Perplexity] ❌ {e}")

# ══════════════════════════════════════════════════════════════════════════════
# FASE 3 — Sumário de Tokens & Custos
# ══════════════════════════════════════════════════════════════════════════════
RUN_END = datetime.now()
log.info("")
log.info("=" * 65)
log.info("📊  FASE 3 — Sumário de Tokens & Custos por Chamada")
log.info("=" * 65)

total_tokens = 0
total_cost   = 0.0

for e in usage_log:
    log.info(f"  Provider   : {e['provider']}")
    log.info(f"  Modelo     : {e['model']}")
    log.info(f"  Duração    : {e['elapsed_s']}s")
    log.info(f"  Tokens in/out/tot : {e['input_tokens']} / {e['output_tokens']} / {e['total_tokens']}")
    cost_str = f"${e['cost_usd']:.6f} USD" if e['cost_usd'] is not None else "N/A"
    log.info(f"  Custo est. : {cost_str}")
    log.info("-" * 40)
    total_tokens += e["total_tokens"]
    if e["cost_usd"]:
        total_cost += e["cost_usd"]

log.info(f"  TOTAL TOKENS  : {total_tokens}")
log.info(f"  CUSTO TOTAL   : ${total_cost:.6f} USD")
log.info(f"  DURAÇÃO TOTAL : {(RUN_END - RUN_START).total_seconds():.2f}s")

# ══════════════════════════════════════════════════════════════════════════════
# Guardar JSON de usage
# ══════════════════════════════════════════════════════════════════════════════
json_payload = {
    "run_start":      RUN_START.isoformat(),
    "run_end":        RUN_END.isoformat(),
    "run_duration_s": round((RUN_END - RUN_START).total_seconds(), 3),
    "api_keys":       key_status,
    "calls":          usage_log,
    "summary": {
        "total_tokens":     total_tokens,
        "total_cost_usd":   round(total_cost, 8),
        "providers_tested": list({e["provider"] for e in usage_log}),
    },
}

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(json_payload, f, indent=2, ensure_ascii=False)

log.info("")
log.info(f"✅  Log completo  : {LOG_FILE}")
log.info(f"✅  JSON de usage : {JSON_FILE}")
log.info(f"⏱️   Run terminada : {RUN_END.strftime('%Y-%m-%d %H:%M:%S')}")
"""
Model Configuration & Cost Management
=======================================
Central configuration for all LLM calls across the pipeline.
Three tiers (INTENSO/MODERADO/BAIXO) × three providers × three environments (dev/test/prod).

Token-saving mechanisms:
  - Batch API (Anthropic, OpenAI): 50% cost reduction, 24h turnaround
  - Delayed responses: queue non-urgent calls for batch processing
  - Prompt caching (Anthropic): reuse system prompts across calls
  - Context pruning: strip unnecessary fields before sending to LLM

Usage:
    from src.config.models import get_model, get_cost, ENV, estimate_cost
    
    model = get_model("narrative_enrichment")  # returns model string for current ENV
    cost = estimate_cost("narrative_enrichment", input_tokens=1500, output_tokens=600)
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════════

class Environment(str, Enum):
    DEV  = "dev"    # Fast iteration, cheapest models, small samples
    TEST = "test"   # Validation runs, moderate models, full samples
    PROD = "prod"   # Final generation, best models where needed, batch enabled

ENV = Environment(os.environ.get("PIPELINE_ENV", "dev"))

# ═══════════════════════════════════════════════════════════════════════════════
# TIERS
# ═══════════════════════════════════════════════════════════════════════════════

class Tier(str, Enum):
    INTENSO  = "intenso"
    MODERADO = "moderado"
    BAIXO    = "baixo"

# ═══════════════════════════════════════════════════════════════════════════════
# PROVIDER × TIER MODEL STRINGS
# ═══════════════════════════════════════════════════════════════════════════════

MODELS = {
    "anthropic": {
        Tier.INTENSO:  "claude-opus-4-6",
        Tier.MODERADO: "claude-sonnet-4-6",
        Tier.BAIXO:    "claude-haiku-4-5",
    },
    "openai": {
        Tier.INTENSO:  "gpt-5.4-pro-2026-03-05",
        Tier.MODERADO: "gpt-5.4-2026-03-05",
        Tier.BAIXO:    "gpt-5-mini-2025-08-07",
    },
    "google": {
        Tier.INTENSO:  "gemini-3.1-pro-preview",
        Tier.MODERADO: "gemini-3-flash-preview",
        Tier.BAIXO:    "gemini-3.1-flash-lite-preview",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# COST PER 1M TOKENS (USD)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CostRate:
    input_per_1m: float
    output_per_1m: float
    batch_discount: float = 0.50  # 50% off for batch API

COSTS = {
    "anthropic": {
        Tier.INTENSO:  CostRate(input_per_1m=5.0,   output_per_1m=25.0),
        Tier.MODERADO: CostRate(input_per_1m=3.0,   output_per_1m=15.0),
        Tier.BAIXO:    CostRate(input_per_1m=1.0,   output_per_1m=5.0),
    },
    "openai": {
        Tier.INTENSO:  CostRate(input_per_1m=30.0,  output_per_1m=180.0),
        Tier.MODERADO: CostRate(input_per_1m=2.5,   output_per_1m=15.0),
        Tier.BAIXO:    CostRate(input_per_1m=0.25,  output_per_1m=2.0),
    },
    "google": {
        Tier.INTENSO:  CostRate(input_per_1m=7.0,   output_per_1m=21.0),
        Tier.MODERADO: CostRate(input_per_1m=0.075,  output_per_1m=0.3),
        Tier.BAIXO:    CostRate(input_per_1m=0.075,  output_per_1m=0.3),
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# TOKEN-SAVING POLICIES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TokenPolicy:
    use_batch_api: bool = False        # Queue for batch processing (50% off)
    use_prompt_cache: bool = False     # Cache system prompts (Anthropic)
    use_delayed_response: bool = False # Queue non-urgent, process in batch window
    max_output_tokens: int = 1024      # Cap output length
    strip_ehr_fields: bool = False     # Remove non-essential EHR fields from prompts
    compress_persona_text: bool = False # Summarise long persona descriptions

TOKEN_POLICIES = {
    Environment.DEV: TokenPolicy(
        use_batch_api=False,       # Immediate feedback during development
        use_prompt_cache=True,
        use_delayed_response=False,
        max_output_tokens=512,
        strip_ehr_fields=True,     # Minimal context for fast iteration
        compress_persona_text=True,
    ),
    Environment.TEST: TokenPolicy(
        use_batch_api=True,        # Batch for cost savings
        use_prompt_cache=True,
        use_delayed_response=True,
        max_output_tokens=800,
        strip_ehr_fields=False,
        compress_persona_text=False,
    ),
    Environment.PROD: TokenPolicy(
        use_batch_api=True,        # Always batch in production
        use_prompt_cache=True,
        use_delayed_response=True,
        max_output_tokens=1024,
        strip_ehr_fields=False,
        compress_persona_text=False,
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# TASK → MODEL ASSIGNMENT (per environment)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TaskConfig:
    """Configuration for a specific pipeline task."""
    provider: str
    tier: Tier
    batch_eligible: bool = True      # Can this task be batched?
    cache_system_prompt: bool = True  # Reuse system prompt across calls?
    description: str = ""

# Each task maps to a specific provider+tier per environment.
# Logic: expensive/quality-critical tasks use higher tiers in prod;
# everything drops to BAIXO in dev for fast iteration.

TASK_ASSIGNMENTS = {
    # ── Persona Construction ──────────────────────────────────────────
    "persona_matching": {
        # LLM-assisted compatibility scoring (if enabled)
        Environment.DEV:  TaskConfig("google",    Tier.BAIXO,    batch_eligible=True,  description="Persona-EHR matching"),
        Environment.TEST: TaskConfig("google",    Tier.BAIXO,    batch_eligible=True,  description="Persona-EHR matching"),
        Environment.PROD: TaskConfig("google",    Tier.MODERADO, batch_eligible=True,  description="Persona-EHR matching"),
    },
    "narrative_enrichment": {
        # Generating 250-350 word enriched backstories — quality matters
        Environment.DEV:  TaskConfig("google",    Tier.MODERADO, batch_eligible=True,  description="Persona narrative generation"),
        Environment.TEST: TaskConfig("anthropic", Tier.MODERADO, batch_eligible=True,  description="Persona narrative generation"),
        Environment.PROD: TaskConfig("anthropic", Tier.MODERADO, batch_eligible=True,  description="Persona narrative generation"),
    },
    
    # ── Questionnaire Generation ──────────────────────────────────────
    "questionnaire_generation": {
        # Complex reasoning for questionnaire design — needs quality
        Environment.DEV:  TaskConfig("anthropic", Tier.MODERADO, batch_eligible=False, description="Questionnaire version generation"),
        Environment.TEST: TaskConfig("anthropic", Tier.MODERADO, batch_eligible=False, description="Questionnaire version generation"),
        Environment.PROD: TaskConfig("anthropic", Tier.INTENSO,  batch_eligible=False, description="Questionnaire version generation"),
    },
    "ehr_question_adaptation": {
        # Adapting questions to individual EHR profiles
        Environment.DEV:  TaskConfig("google",    Tier.BAIXO,    batch_eligible=True,  description="EHR-contextual question adaptation"),
        Environment.TEST: TaskConfig("google",    Tier.MODERADO, batch_eligible=True,  description="EHR-contextual question adaptation"),
        Environment.PROD: TaskConfig("anthropic", Tier.BAIXO,    batch_eligible=True,  description="EHR-contextual question adaptation"),
    },
    
    # ── Synthetic Interviews ──────────────────────────────────────────
    "interviewer": {
        # Asking questions — consistent and systematic
        Environment.DEV:  TaskConfig("openai",    Tier.BAIXO,    batch_eligible=True,  description="Interview question generation"),
        Environment.TEST: TaskConfig("openai",    Tier.BAIXO,    batch_eligible=True,  description="Interview question generation"),
        Environment.PROD: TaskConfig("openai",    Tier.MODERADO, batch_eligible=True,  description="Interview question generation"),
    },
    "persona_roleplay": {
        # Responding in character — rotate across providers for diversity
        # NOTE: This task rotates; the config here is the PRIMARY provider.
        # The orchestrator cycles through all three providers.
        Environment.DEV:  TaskConfig("google",    Tier.BAIXO,    batch_eligible=True,  description="Persona role-play responses"),
        Environment.TEST: TaskConfig("anthropic", Tier.BAIXO,    batch_eligible=True,  description="Persona role-play responses"),
        Environment.PROD: TaskConfig("anthropic", Tier.MODERADO, batch_eligible=True,  description="Persona role-play responses"),
    },
    
    # ── Evaluation ────────────────────────────────────────────────────
    "quality_scoring": {
        # Evaluating response quality — needs good judgment
        Environment.DEV:  TaskConfig("google",    Tier.MODERADO, batch_eligible=True,  description="Response quality evaluation"),
        Environment.TEST: TaskConfig("anthropic", Tier.MODERADO, batch_eligible=True,  description="Response quality evaluation"),
        Environment.PROD: TaskConfig("anthropic", Tier.MODERADO, batch_eligible=True,  description="Response quality evaluation"),
    },
    "coverage_analysis": {
        # Mapping responses to dimensions — structured output
        Environment.DEV:  TaskConfig("google",    Tier.BAIXO,    batch_eligible=True,  description="Topic coverage mapping"),
        Environment.TEST: TaskConfig("google",    Tier.MODERADO, batch_eligible=True,  description="Topic coverage mapping"),
        Environment.PROD: TaskConfig("anthropic", Tier.MODERADO, batch_eligible=True,  description="Topic coverage mapping"),
    },
    "service_mapping": {
        # Extracting expectations/perceptions/gaps
        Environment.DEV:  TaskConfig("google",    Tier.BAIXO,    batch_eligible=True,  description="Service provision gap mapping"),
        Environment.TEST: TaskConfig("anthropic", Tier.BAIXO,    batch_eligible=True,  description="Service provision gap mapping"),
        Environment.PROD: TaskConfig("anthropic", Tier.MODERADO, batch_eligible=True,  description="Service provision gap mapping"),
    },
    "inter_rater_reliability": {
        # Must use ALL THREE providers for cross-model agreement
        Environment.DEV:  TaskConfig("google",    Tier.BAIXO,    batch_eligible=True,  description="Multi-model agreement check"),
        Environment.TEST: TaskConfig("anthropic", Tier.BAIXO,    batch_eligible=True,  description="Multi-model agreement check"),
        Environment.PROD: TaskConfig("anthropic", Tier.MODERADO, batch_eligible=True,  description="Multi-model agreement check"),
    },
    
    # ── Utility ───────────────────────────────────────────────────────
    "llm_relevance_scoring": {
        # FinePersonas LLM filter — bulk, cost-sensitive
        Environment.DEV:  TaskConfig("google",    Tier.BAIXO,    batch_eligible=True,  description="Persona relevance scoring"),
        Environment.TEST: TaskConfig("google",    Tier.BAIXO,    batch_eligible=True,  description="Persona relevance scoring"),
        Environment.PROD: TaskConfig("anthropic", Tier.BAIXO,    batch_eligible=True,  description="Persona relevance scoring"),
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# PERSONA ROLE-PLAY MODEL ROTATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_persona_rotation_models(env: Environment = None) -> list:
    """
    Returns the list of models to rotate through for persona role-play.
    Ensures cross-provider diversity in synthetic interview responses.
    """
    if env is None:
        env = ENV
    
    if env == Environment.DEV:
        return [
            f"google/{MODELS['google'][Tier.BAIXO]}",
            f"anthropic/{MODELS['anthropic'][Tier.BAIXO]}",
            f"openai/{MODELS['openai'][Tier.BAIXO]}",
        ]
    elif env == Environment.TEST:
        return [
            f"anthropic/{MODELS['anthropic'][Tier.BAIXO]}",
            f"google/{MODELS['google'][Tier.MODERADO]}",
            f"openai/{MODELS['openai'][Tier.BAIXO]}",
        ]
    else:  # PROD
        return [
            f"anthropic/{MODELS['anthropic'][Tier.MODERADO]}",
            f"google/{MODELS['google'][Tier.MODERADO]}",
            f"openai/{MODELS['openai'][Tier.MODERADO]}",
        ]

# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def get_task_config(task_name: str, env: Environment = None) -> TaskConfig:
    """Get the full task configuration for the current environment."""
    if env is None:
        env = ENV
    assignments = TASK_ASSIGNMENTS.get(task_name)
    if not assignments:
        raise ValueError(f"Unknown task: {task_name}. Available: {list(TASK_ASSIGNMENTS.keys())}")
    return assignments[env]


def get_model(task_name: str, env: Environment = None) -> str:
    """Get the model string for a task in the current environment."""
    cfg = get_task_config(task_name, env)
    return MODELS[cfg.provider][cfg.tier]


def get_provider(task_name: str, env: Environment = None) -> str:
    """Get the provider name for a task."""
    return get_task_config(task_name, env).provider


def get_tier(task_name: str, env: Environment = None) -> Tier:
    """Get the tier for a task."""
    return get_task_config(task_name, env).tier


def get_token_policy(env: Environment = None) -> TokenPolicy:
    """Get token-saving policy for the current environment."""
    if env is None:
        env = ENV
    return TOKEN_POLICIES[env]


def is_batch_eligible(task_name: str, env: Environment = None) -> bool:
    """Check if a task should use batch API."""
    cfg = get_task_config(task_name, env)
    policy = get_token_policy(env)
    return cfg.batch_eligible and policy.use_batch_api


def estimate_cost(task_name: str, input_tokens: int, output_tokens: int,
                  env: Environment = None, use_batch: bool = None) -> float:
    """
    Estimate cost for a single LLM call in USD.
    
    Args:
        task_name: Pipeline task identifier
        input_tokens: Estimated input token count
        output_tokens: Estimated output token count
        env: Override environment (default: current ENV)
        use_batch: Override batch flag (default: auto from policy)
    
    Returns:
        Estimated cost in USD
    """
    cfg = get_task_config(task_name, env)
    rate = COSTS[cfg.provider][cfg.tier]
    
    cost = (input_tokens / 1_000_000) * rate.input_per_1m + \
           (output_tokens / 1_000_000) * rate.output_per_1m
    
    if use_batch is None:
        use_batch = is_batch_eligible(task_name, env)
    
    if use_batch:
        cost *= rate.batch_discount
    
    return cost


def estimate_pipeline_cost(env: Environment = None) -> dict:
    """
    Estimate total pipeline cost for a full run.
    Based on expected call volumes from the sprint plan.
    """
    if env is None:
        env = ENV
    
    # Expected volumes per task
    volumes = {
        "narrative_enrichment":     {"calls": 150, "avg_input": 1500, "avg_output": 500},
        "questionnaire_generation": {"calls": 6,   "avg_input": 3000, "avg_output": 2000},
        "ehr_question_adaptation":  {"calls": 900, "avg_input": 800,  "avg_output": 400},
        "interviewer":              {"calls": 4800,"avg_input": 1200, "avg_output": 300},  # 240 sessions × 20 turns
        "persona_roleplay":         {"calls": 4800,"avg_input": 1500, "avg_output": 500},
        "quality_scoring":          {"calls": 240, "avg_input": 3000, "avg_output": 800},
        "coverage_analysis":        {"calls": 240, "avg_input": 2500, "avg_output": 600},
        "service_mapping":          {"calls": 240, "avg_input": 2500, "avg_output": 800},
        "inter_rater_reliability":  {"calls": 90,  "avg_input": 3000, "avg_output": 800},  # 30 transcripts × 3 models
        "llm_relevance_scoring":    {"calls": 175, "avg_input": 1000, "avg_output": 500},  # 3500 personas / batch 20
    }
    
    breakdown = {}
    total = 0.0
    
    for task, vol in volumes.items():
        per_call = estimate_cost(task, vol["avg_input"], vol["avg_output"], env)
        task_total = per_call * vol["calls"]
        breakdown[task] = {
            "model": f"{get_provider(task, env)}/{get_model(task, env)}",
            "tier": get_tier(task, env).value,
            "calls": vol["calls"],
            "cost_per_call": round(per_call, 5),
            "total_cost": round(task_total, 3),
            "batch": is_batch_eligible(task, env),
        }
        total += task_total
    
    return {
        "environment": env.value,
        "total_estimated_usd": round(total, 2),
        "breakdown": breakdown,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# COST TRACKER (runtime accumulator)
# ═══════════════════════════════════════════════════════════════════════════════

class CostTracker:
    """Accumulates actual costs during pipeline execution."""
    
    def __init__(self):
        self.calls = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
    
    def record(self, task_name: str, provider: str, model: str,
               input_tokens: int, output_tokens: int,
               batch: bool = False, env: Environment = None):
        """Record a single LLM call."""
        cfg = get_task_config(task_name, env)
        rate = COSTS[provider][cfg.tier]
        
        cost = (input_tokens / 1_000_000) * rate.input_per_1m + \
               (output_tokens / 1_000_000) * rate.output_per_1m
        if batch:
            cost *= rate.batch_discount
        
        self.calls.append({
            "task": task_name,
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "batch": batch,
        })
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += cost
    
    def summary(self) -> dict:
        """Get cost summary."""
        by_task = {}
        for c in self.calls:
            t = c["task"]
            if t not in by_task:
                by_task[t] = {"calls": 0, "cost": 0.0}
            by_task[t]["calls"] += 1
            by_task[t]["cost"] += c["cost_usd"]
        
        return {
            "total_calls": len(self.calls),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "by_task": {k: {"calls": v["calls"], "cost_usd": round(v["cost"], 4)}
                        for k, v in by_task.items()},
        }

# Global tracker instance
tracker = CostTracker()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json
    
    print(f"Current environment: {ENV.value}")
    print(f"Token policy: {get_token_policy()}")
    print()
    
    # Print task assignments for current env
    print(f"{'Task':<30} {'Provider':<12} {'Model':<35} {'Tier':<10} {'Batch'}")
    print("-" * 100)
    for task in sorted(TASK_ASSIGNMENTS.keys()):
        cfg = get_task_config(task)
        model = get_model(task)
        batch = "✓" if is_batch_eligible(task) else "✗"
        print(f"{task:<30} {cfg.provider:<12} {model:<35} {cfg.tier.value:<10} {batch}")
    
    print()
    
    # Cost estimates for all environments
    for env in Environment:
        est = estimate_pipeline_cost(env)
        print(f"\n{'='*60}")
        print(f"PIPELINE COST ESTIMATE — {env.value.upper()}: ${est['total_estimated_usd']:.2f}")
        print(f"{'='*60}")
        for task, info in sorted(est["breakdown"].items(), key=lambda x: -x[1]["total_cost"]):
            batch_flag = " [batch]" if info["batch"] else ""
            print(f"  {task:<30} {info['model']:<40} {info['calls']:>5} calls  ${info['total_cost']:>8.3f}{batch_flag}")

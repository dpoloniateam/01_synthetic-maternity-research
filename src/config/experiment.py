"""
Experiment configuration (development 2, 23 Aug 2026).

One YAML file (config/experiment.yaml) defines every arm, role, model, snapshot, region, output cap,
saving flag, price, seed and repetition. Model choice no longer depends on PIPELINE_ENV.

    from src.config.experiment import load_experiment, current_arm
    exp = load_experiment()                 # EXPERIMENT_CONFIG or config/experiment.yaml
    arm = current_arm(exp)                  # EXPERIMENT_ARM or exp.default_arm
    spec = arm.voice_for(session_index)     # round-robin over the arm's persona voices
"""
from __future__ import annotations
import os, hashlib, json, logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

ROLE_NAMES = ("classifier", "mapping", "generation", "narratives", "refinement")


@dataclass
class ModelSpec:
    provider: str
    model: str
    snapshot: Optional[str] = None
    region: str = "global"
    base_url: Optional[str] = None
    api_key_env: Optional[str] = None
    effort: str = "default"              # default | none | low | medium | high  (OpenAI reasoning_effort when not default)
    max_output_tokens: int = 2000
    thinking_budget: Optional[int] = None  # Google: explicit thinking budget (tokens)
    flex: bool = False                   # OpenAI service_tier=flex
    cache: bool = False                  # Anthropic cache_control on system/prefix; OpenAI caches automatically
    batch: bool = False                  # eligible for the provider's Batch API (non-interactive stages)
    structured: bool = False             # use structured output / JSON mode
    price_in: float = 0.0                # USD per 1M input tokens (list)
    price_cached: float = 0.0            # USD per 1M cached input tokens
    price_out: float = 0.0               # USD per 1M output tokens (reasoning tokens included by the providers)
    price_batch_factor: float = 0.5
    retention: str = ""

    @property
    def label(self) -> str:
        return f"{self.provider}/{self.model}"

    def cost(self, input_tokens: int, output_tokens: int, cached_tokens: int = 0, batch: bool = False) -> float:
        uncached = max(input_tokens - cached_tokens, 0)
        usd = uncached / 1e6 * self.price_in + cached_tokens / 1e6 * self.price_cached + output_tokens / 1e6 * self.price_out
        return usd * (self.price_batch_factor if batch else 1.0)

    @staticmethod
    def from_dict(d: dict) -> "ModelSpec":
        known = {k: v for k, v in d.items() if k in ModelSpec.__dataclass_fields__}
        return ModelSpec(**known)


@dataclass
class Arm:
    name: str
    description: str = ""
    persona_voices: list = field(default_factory=list)
    judges: list = field(default_factory=list)
    open_rater: Optional[ModelSpec] = None
    roles: dict = field(default_factory=dict)      # classifier, mapping, generation, narratives, refinement
    interviewer: str = "scripted"

    def voice_for(self, index: int) -> ModelSpec:
        if not self.persona_voices:
            raise ValueError(f"Arm {self.name} has no persona voices")
        return self.persona_voices[index % len(self.persona_voices)]

    def all_specs(self) -> list:
        specs = list(self.persona_voices) + list(self.judges) + list(self.roles.values())
        if self.open_rater:
            specs.append(self.open_rater)
        return specs

    def spec_for(self, provider: str, model: str) -> ModelSpec:
        for s in self.all_specs():
            if s.provider == provider and s.model == model:
                return s
        log.warning(f"No spec for {provider}/{model} in arm {self.name}; using defaults with zero prices")
        return ModelSpec(provider=provider, model=model)


@dataclass
class Experiment:
    name: str
    version: int
    default_arm: str
    seeds: list
    repetitions: int
    cost_halt_usd: float
    output_root: str
    persona_pool: str
    dimension_universe: str
    arms: dict
    source_path: str = ""
    fingerprint: str = ""

    def arm(self, name: Optional[str] = None) -> Arm:
        name = name or os.environ.get("EXPERIMENT_ARM") or self.default_arm
        if name not in self.arms:
            raise KeyError(f"Unknown arm {name!r}; available: {sorted(self.arms)}")
        return self.arms[name]

    def to_manifest(self) -> dict:
        return {
            "name": self.name, "version": self.version, "default_arm": self.default_arm, "seeds": self.seeds,
            "repetitions": self.repetitions, "cost_halt_usd": self.cost_halt_usd, "persona_pool": self.persona_pool,
            "dimension_universe": self.dimension_universe, "source_path": self.source_path, "fingerprint": self.fingerprint,
            "arms": {n: {"description": a.description, "persona_voices": [asdict(s) for s in a.persona_voices],
                         "judges": [asdict(s) for s in a.judges], "open_rater": asdict(a.open_rater) if a.open_rater else None,
                         "roles": {r: asdict(s) for r, s in a.roles.items()}, "interviewer": a.interviewer}
                     for n, a in self.arms.items()},
        }


_CACHE: dict = {}


def load_experiment(path: Optional[str] = None, force: bool = False) -> Experiment:
    import yaml
    path = path or os.environ.get("EXPERIMENT_CONFIG") or "config/experiment.yaml"
    p = Path(path)
    if not force and str(p) in _CACHE:
        return _CACHE[str(p)]
    raw = p.read_text(encoding="utf-8")
    doc = yaml.safe_load(raw)
    e = doc.get("experiment", {})
    arms = {}
    for name, a in (doc.get("arms") or {}).items():
        voices = [ModelSpec.from_dict(v) for v in a.get("persona_voices", [])]
        judges = [ModelSpec.from_dict(v) for v in a.get("judges", [])]
        open_rater = ModelSpec.from_dict(a["open_rater"]) if a.get("open_rater") else None
        roles = {r: ModelSpec.from_dict(a[r]) for r in ROLE_NAMES if a.get(r)}
        arms[name] = Arm(name=name, description=a.get("description", ""), persona_voices=voices, judges=judges,
                         open_rater=open_rater, roles=roles, interviewer=a.get("interviewer", "scripted"))
    exp = Experiment(
        name=e.get("name", "experiment"), version=int(e.get("version", 1)), default_arm=e.get("default_arm", next(iter(arms))),
        seeds=list(e.get("seeds", [0])), repetitions=int(e.get("repetitions", 1)), cost_halt_usd=float(e.get("cost_halt_usd", 50.0)),
        output_root=e.get("output_root", "data/runs"), persona_pool=e.get("persona_pool", "data/composite_personas/composites.jsonl"),
        dimension_universe=e.get("dimension_universe", "canonical_twelve"), arms=arms, source_path=str(p),
        fingerprint=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    )
    _CACHE[str(p)] = exp
    return exp


def current_arm(exp: Optional[Experiment] = None) -> Arm:
    exp = exp or load_experiment()
    return exp.arm()


def spec_from_model_string(model_str: str, exp: Optional[Experiment] = None) -> ModelSpec:
    """'provider/model' → ModelSpec from the current arm (zero-priced default if absent)."""
    provider, _, model = model_str.partition("/")
    if not model:
        provider, model = "google", provider
    try:
        return current_arm(exp).spec_for(provider, model)
    except Exception as ex:  # no config available
        log.warning(f"Experiment config unavailable ({ex}); default spec for {model_str}")
        return ModelSpec(provider=provider, model=model)

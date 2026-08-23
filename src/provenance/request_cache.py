"""
Provenance layer (development 8, 23 Aug 2026).

Every model call is written, request and response included, to <run_dir>/requests.jsonl with the model
snapshot actually served, region, provider request id, finish reason, token counts (cached and reasoning
where reported) and cost at the configured list prices. A CostMeter accumulates spend per stage and halts
the run at the configured ceiling (owner's rule: USD 50 without approval).

    from src.provenance.request_cache import get_cache
    cache = get_cache()                         # SDL_RUN_DIR or data/runs/<run_id>
    cache.meter.check("persona")                # raises CostHaltError once the ceiling is reached
    cache.record(stage="persona", session_id=..., spec=..., request=..., response=..., usage=..., extra=...)
"""
from __future__ import annotations
import os, json, time, hashlib, threading, subprocess, sys, platform
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class CostHaltError(RuntimeError):
    """Raised when cumulative spend reaches the halt ceiling. The run must stop and the owner be asked."""


@dataclass
class CostMeter:
    halt_usd: float = 50.0
    by_stage: dict = field(default_factory=dict)
    calls: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def total(self) -> float:
        return float(sum(self.by_stage.values()))

    def check(self, stage: str = "") -> None:
        if self.total >= self.halt_usd:
            raise CostHaltError(f"Cost halt: USD {self.total:.2f} ≥ {self.halt_usd:.2f} (stage {stage}); approval required to continue")

    def add(self, stage: str, usd: float) -> float:
        with self._lock:
            self.by_stage[stage] = self.by_stage.get(stage, 0.0) + float(usd)
            self.calls += 1
            return self.total


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "unknown"


def _sdk_versions() -> dict:
    out = {}
    try:
        import importlib.metadata as m
        for p in ("openai", "anthropic", "google-genai", "google-generativeai", "scipy", "numpy", "pyyaml"):
            try:
                out[p] = m.version(p)
            except Exception:
                out[p] = None
    except Exception:
        pass
    return out


class RequestCache:
    def __init__(self, run_dir: str, halt_usd: float = 50.0, experiment_manifest: Optional[dict] = None):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.run_dir / "requests.jsonl"
        self.meter = CostMeter(halt_usd=halt_usd)
        self._lock = threading.Lock()
        self.started = datetime.now(timezone.utc).isoformat()
        self.experiment_manifest = experiment_manifest or {}
        self.counts: dict = {}
        # resume safety: prior spend in this run directory counts towards the halt
        if self.path.exists():
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    try:
                        r = json.loads(line)
                    except Exception:
                        continue
                    self.meter.add(r.get("stage", "?"), float(r.get("cost_usd") or 0))
                    self.counts[r.get("stage", "?")] = self.counts.get(r.get("stage", "?"), 0) + 1
            self.meter.calls = sum(self.counts.values())

    def record(self, stage: str, session_id: str, spec, request, response: str, usage: dict,
               snapshot: str = None, request_id: str = None, finish_reason: str = None,
               batch: bool = False, extra: dict = None, latency_s: float = None) -> dict:
        cached = int(usage.get("cached_tokens") or 0)
        usd = spec.cost(int(usage.get("input_tokens") or 0), int(usage.get("output_tokens") or 0), cached, batch=batch)
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "stage": stage, "session_id": session_id,
            "provider": spec.provider, "model": spec.model, "snapshot": snapshot or spec.snapshot,
            "region": spec.region, "base_url": spec.base_url, "request_id": request_id, "finish_reason": finish_reason,
            "input_tokens": int(usage.get("input_tokens") or 0), "output_tokens": int(usage.get("output_tokens") or 0),
            "cached_tokens": cached, "reasoning_tokens": usage.get("reasoning_tokens"), "thinking_tokens": usage.get("thinking_tokens"),
            "cost_usd": round(usd, 6), "batch": batch, "latency_s": round(latency_s, 3) if latency_s is not None else None,
            "request": request, "response": response,
            "sha256": hashlib.sha256((json.dumps(request, ensure_ascii=False, sort_keys=True) + "\n" + (response or "")).encode("utf-8")).hexdigest(),
            "extra": extra or {},
        }
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            self.counts[stage] = self.counts.get(stage, 0) + 1
        self.meter.add(stage, usd)
        return rec

    def manifest(self, extra: dict = None) -> dict:
        m = {
            "run_dir": str(self.run_dir), "started": self.started, "written": datetime.now(timezone.utc).isoformat(),
            "git_commit": _git_commit(), "python": sys.version.split()[0], "platform": platform.platform(),
            "sdk_versions": _sdk_versions(), "experiment": self.experiment_manifest,
            "calls_by_stage": dict(self.counts), "cost_by_stage_usd": {k: round(v, 4) for k, v in self.meter.by_stage.items()},
            "cost_total_usd": round(self.meter.total, 4), "cost_halt_usd": self.meter.halt_usd,
            "requests_file": str(self.path), "requests_sha256": _sha256_file(self.path) if self.path.exists() else None,
        }
        if extra:
            m.update(extra)
        with open(self.run_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2, ensure_ascii=False)
        return m


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


_CACHE: Optional[RequestCache] = None


def get_cache() -> RequestCache:
    """Process-wide cache. SDL_RUN_DIR selects the run directory; SDL_COST_HALT_USD the ceiling (default 50)."""
    global _CACHE
    if _CACHE is None:
        run_dir = os.environ.get("SDL_RUN_DIR") or os.path.join("data", "runs", datetime.now().strftime("run_%Y%m%d_%H%M%S"))
        halt = float(os.environ.get("SDL_COST_HALT_USD", "50"))
        manifest = {}
        try:
            from src.config.experiment import load_experiment
            manifest = load_experiment().to_manifest()
        except Exception:
            pass
        _CACHE = RequestCache(run_dir, halt_usd=halt, experiment_manifest=manifest)
    return _CACHE


def set_cache(cache: RequestCache) -> None:
    global _CACHE
    _CACHE = cache

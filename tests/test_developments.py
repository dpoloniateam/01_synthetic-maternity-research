"""Unit tests for the nine developments of 23 Aug 2026 (offline; no API calls)."""
import json, os, sys, tempfile, types
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.chdir(Path(__file__).resolve().parents[1])


def test_experiment_config_loads_and_prices():
    from src.config.experiment import load_experiment
    exp = load_experiment(force=True)
    arm = exp.arm("P")
    assert [s.provider for s in arm.persona_voices] == ["openai", "anthropic", "google"]
    assert all(s.max_output_tokens >= 2000 for s in arm.persona_voices)
    opus = arm.spec_for("anthropic", "claude-opus-5")
    assert abs(opus.cost(1000, 500, cached_tokens=800) - (200 / 1e6 * 5 + 800 / 1e6 * 0.5 + 500 / 1e6 * 25)) < 1e-9
    assert abs(opus.cost(1000, 500, batch=True) - 0.5 * (1000 / 1e6 * 5 + 500 / 1e6 * 25)) < 1e-9
    assert exp.fingerprint and len(exp.fingerprint) == 64


def test_phase_normalisation_and_probe_keys():
    from src.questionnaire.ehr_adapter import normalise_phase, normalise_probe
    assert normalise_phase("intrapartum") == "birth" and normalise_phase("postnatal") == "postpartum"
    assert normalise_phase("any") == "*" and normalise_phase("cross-phase") == "*" and normalise_phase("full_journey") == "*"
    p = normalise_probe({"text": "How?", "target_dimension": "dignity_respect", "added_in_refinement": True})
    assert p["probe_text"] == "How?" and p["target_latent_dimensions"] == ["dignity_respect"]


def test_refined_instrument_is_administered():
    from src.questionnaire.administration_check import compare_versions
    personas = [json.loads(l) for l in open("data/composite_personas/composites.jsonl", encoding="utf-8") if l.strip()][:10]
    rep = compare_versions(json.load(open("data/questionnaires/Q_V4.json")), json.load(open("data/questionnaires/refined/Q_V4_R1.json")), personas)
    assert not rep["identical_for_all"] and rep["personas_with_difference"] == 10
    assert rep["mean_extra_questions_b"] > 0 and rep["mean_extra_probes_b"] > 0


def test_scipy_statistics_replace_the_broken_routine():
    from src.evaluation.version_comparator import kruskal_wallis_h, wilcoxon_signed_rank
    import random
    random.seed(1)
    null = [[random.choice([3, 4]) for _ in range(40)] for _ in range(5)]
    h, p = kruskal_wallis_h(null)
    assert p > 0.05 and h < 15, "null groups must not be significant"
    shifted = [[random.choice([2, 3]) for _ in range(40)], [random.choice([4, 5]) for _ in range(40)]]
    h2, p2 = kruskal_wallis_h(shifted)
    assert p2 < 1e-6
    s, pw = wilcoxon_signed_rank([1, 2, -1, 3, 2, 1, -2, 4, 1, 2])
    assert 0 < pw < 1


def test_icc_matches_shrout_fleiss():
    from src.evaluation.reliability import icc2_1, icc2_k, icc_by_dimension
    sf = [[9, 2, 5, 8], [6, 1, 3, 2], [8, 4, 6, 8], [7, 1, 2, 6], [10, 5, 6, 9], [6, 2, 4, 7]]
    assert abs(icc2_1(sf) - 0.29) < 0.005 and abs(icc2_k(sf) - 0.62) < 0.005
    out = icc_by_dimension({"d": sf})
    assert out["d"]["n"] == 6 and out["d"]["k"] == 4


def test_judge_validation_is_tolerant_and_strict():
    from src.evaluation.judge_client import _tolerant_json, _validate, SCORE_SCHEMA, build_prompt
    txt = 'Here you go:\n```json\n{"results":[{"pair_index":1,"question_id":"Q","scores":{"emotional_depth":{"score":4,"evidence":"e"},"specificity":3,"latent_surfacing":5,"narrative_quality":4,"clinical_grounding":4},"composite_richness":4,"kbv_dimensions_present":[],"latent_dimensions_surfaced":["dignity_respect"],"latent_dimensions_encoded_but_absent":[],"thematic_areas_covered":[]}]}\n```'
    v = _validate(_tolerant_json(txt), 1)
    assert v["n_valid"] == 1 and v["results"][0]["composite_richness"] == 4.0
    bad = _validate(_tolerant_json("no json here"), 2)
    assert bad["n_valid"] == 0
    assert set(SCORE_SCHEMA["properties"]["results"]["items"]["properties"]["scores"]["required"]) == {"emotional_depth", "specificity", "latent_surfacing", "narrative_quality", "clinical_grounding"}
    system, prompt = build_prompt([{"question_id": "Q", "question_text": "q", "response_text": "r", "encoded_latent": {"power_dynamics": 0.2}, "target_dimensions": []}])
    assert "DIMENSION UNIVERSE" in system and system.count("\n  - ") == 12


def test_cost_meter_halts_and_cache_records():
    from src.provenance.request_cache import RequestCache, CostHaltError
    from src.config.experiment import ModelSpec
    d = tempfile.mkdtemp()
    c = RequestCache(d, halt_usd=0.02)
    spec = ModelSpec(provider="openai", model="x", price_in=4, price_out=20)
    c.record("persona", "S", spec, {"messages": []}, "hello", {"input_tokens": 1000, "output_tokens": 500})
    assert abs(c.meter.total - (1000 / 1e6 * 4 + 500 / 1e6 * 20)) < 1e-9
    c.record("persona", "S", spec, {"messages": []}, "again", {"input_tokens": 1000, "output_tokens": 500})
    with pytest.raises(CostHaltError):
        c.meter.check("persona")
    lines = [json.loads(l) for l in open(Path(d) / "requests.jsonl")]
    assert len(lines) == 2 and lines[0]["sha256"] and lines[0]["response"] == "hello"
    m = c.manifest()
    assert m["cost_total_usd"] > 0 and (Path(d) / "manifest.json").exists()


def test_persona_agent_retries_then_raises_on_empty(monkeypatch):
    from src.orchestration import persona_agent as pa
    from src.provenance.request_cache import RequestCache, set_cache
    set_cache(RequestCache(tempfile.mkdtemp(), halt_usd=50))
    persona = {"composite_id": "t", "name": "T", "journey_stage": "birth", "risk_level": "low", "demographics": {}, "vulnerability_flags": []}
    a = pa.PersonaAgent(persona, "openai", "gpt-5.6-sol", session_id="T")
    calls = []

    def fake(cap):
        calls.append(cap)
        return ("", {"input_tokens": 10, "output_tokens": 0}, {"finish_reason": "length", "snapshot": "m", "request_id": "r"}) if len(calls) < 3 else ("fine", {"input_tokens": 10, "output_tokens": 5}, {"finish_reason": "stop", "snapshot": "m", "request_id": "r"})
    monkeypatch.setattr(a, "_call_provider", fake)
    with pytest.raises(pa.EmptyResponseError):
        a.respond("Q?")
    assert calls == [2000, 4000] and a.history == []      # retry with a doubled cap, then the question is withdrawn from history
    calls.clear()
    b = pa.PersonaAgent(persona, "openai", "gpt-5.6-sol", session_id="T")
    monkeypatch.setattr(b, "_call_provider", lambda cap: ("", {"input_tokens": 10, "output_tokens": 0}, {"finish_reason": "length"}) if not calls.append(cap) and len(calls) == 1 else ("ok", {"input_tokens": 10, "output_tokens": 3}, {"finish_reason": "stop"}))
    text, i, o = b.respond("Q?")
    assert text == "ok" and b.empty_retries == 1 and b.history[-1]["content"] == "ok"


def test_transcript_turn_carries_meta():
    from src.orchestration.transcript_builder import TranscriptBuilder
    tb = TranscriptBuilder({"session_id": "S", "questionnaire_version": 4}, {"composite_id": "c", "latent_dimensions": {}})
    tb.add_persona_turn("", responding_to="Q1", meta={"finish_reason": "length", "truncated": True, "snapshot": "m"})
    t = tb.turns[-1]
    assert t["empty"] is True and t["truncated"] is True and t["finish_reason"] == "length"


def test_plan_v2_stratifies_voices():
    from src.orchestration.plan_repetitions import build_plan_v2
    plan = json.load(open("data/config/administration_plan.json"))
    v2 = build_plan_v2(plan, "P", repetitions=2, limit=12)
    assert len(v2) == 24 and {s["repetition"] for s in v2} == {1, 2}
    assert all(s["persona_pool"].endswith("composites_v2.jsonl") for s in v2)
    from collections import Counter
    cells = Counter((s["persona_model"], s["questionnaire_version"]) for s in v2)
    assert len(cells) == 6

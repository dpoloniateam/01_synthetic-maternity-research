"""
Administration check (development 4, 23 Aug 2026): does the revised instrument actually reach the personas?

For every persona, adapt two instrument versions and compare the administered question ids and the
probes the interviewer can deploy (those with probe_text). Exit code 1 if the two versions are
administered identically to every persona — the failure of the March 2026 run.

    python -m src.questionnaire.administration_check --a data/questionnaires/Q_V4.json \
        --b data/questionnaires/refined/Q_V4_R1.json --personas data/composite_personas/composites.jsonl
"""
import json, argparse, copy, sys
from src.questionnaire.ehr_adapter import adapt_questionnaire


def _questions(doc):
    return doc.get("questions", doc) if isinstance(doc, dict) else doc


def _deployable(qs):
    return sum(1 for q in qs for p in q.get("probes", []) if isinstance(p, dict) and p.get("probe_text"))


def compare_versions(a_doc, b_doc, personas: list) -> dict:
    qa, qb = _questions(a_doc), _questions(b_doc)
    per = []
    for persona in personas:
        aa = _questions(adapt_questionnaire(copy.deepcopy(qa), persona))
        bb = _questions(adapt_questionnaire(copy.deepcopy(qb), persona))
        ida = {q.get("question_id") for q in aa}; idb = {q.get("question_id") for q in bb}
        per.append({"persona_id": persona.get("composite_id"), "stage": persona.get("journey_stage"),
                    "a_questions": len(ida), "b_questions": len(idb), "only_in_b": sorted(idb - ida), "only_in_a": sorted(ida - idb),
                    "a_deployable_probes": _deployable(aa), "b_deployable_probes": _deployable(bb)})
    n_diff = sum(1 for r in per if r["only_in_b"] or r["only_in_a"] or r["a_deployable_probes"] != r["b_deployable_probes"])
    return {"personas": len(per), "personas_with_difference": n_diff, "identical_for_all": n_diff == 0,
            "mean_extra_questions_b": round(sum(len(r["only_in_b"]) for r in per) / max(len(per), 1), 2),
            "mean_extra_probes_b": round(sum(r["b_deployable_probes"] - r["a_deployable_probes"] for r in per) / max(len(per), 1), 2),
            "per_persona": per}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
    ap.add_argument("--personas", default="data/composite_personas/composites.jsonl")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--output", default="")
    a = ap.parse_args()
    personas = [json.loads(l) for l in open(a.personas, encoding="utf-8") if l.strip()]
    if a.limit: personas = personas[:a.limit]
    rep = compare_versions(json.load(open(a.a, encoding="utf-8")), json.load(open(a.b, encoding="utf-8")), personas)
    summary = {k: v for k, v in rep.items() if k != "per_persona"}
    print(json.dumps(summary, indent=2))
    if a.output:
        json.dump(rep, open(a.output, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    sys.exit(1 if rep["identical_for_all"] else 0)


if __name__ == "__main__":
    main()

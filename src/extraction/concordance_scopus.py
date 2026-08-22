"""concordance_scopus.py — literature retrieval for the codified-standards concordance.

This is the literature-retrieval script named in the paper's data availability statement.
It resolves, against Scopus, the sources that codify each criterion applied by
`src/questionnaire/standards_audit.py`, and emits a concordance mapping every audited
criterion to the literature that authorises it.

Retrieval is by DOI where a DOI exists and by exact title otherwise. Every response is
cached verbatim, so the concordance is reproducible without a Scopus key: `--offline`
rebuilds it from the cache alone, which is what the reproducibility package ships.

Non-coverage is reported, not hidden. Several standards in this field are codified in
monographs (Bradburn et al., 2004; Foddy, 1993) that Scopus does not index; the concordance
records them as `not_covered` with the reason, which is itself an auditable result.

Where the Scopus entitlement is unavailable (no key, or an expired one returning 401), the
script falls back to Crossref for identifier resolution and labels those rows
`covered_via_crossref`, so the concordance never silently reports a source as unresolved
when its identity is in fact verifiable.

Credentials: `SCOPUS_API_KEY`, optionally with `SCOPUS_INSTTOKEN` for institutional entitlement.
Never hard-code either; both are read from the environment.

Usage:
    python -m src.extraction.concordance_scopus --out data/literature --offline
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

SCOPUS_SEARCH = "https://api.elsevier.com/content/search/scopus"

# Each criterion applied by the standards audit, with the source that codifies it.
CONCORDANCE = [
    {
        "criterion": "leading_loaded_wording",
        "audited_as": "Leading / loaded terms column; lexicon of presupposition markers, "
                      "agreement-seeking tags and evaluatively charged terms",
        "sources": [
            {"key": "bradburn2004", "authors": "Bradburn, N. M., Sudman, S., & Wansink, B.",
             "year": 2004, "title": "Asking Questions: The Definitive Guide to Questionnaire Design",
             "type": "monograph", "doi": None},
            {"key": "foddy1993", "authors": "Foddy, W.", "year": 1993,
             "title": "Constructing Questions for Interviews and Questionnaires: Theory and Practice in Social Research",
             "type": "monograph", "doi": None},
        ],
    },
    {
        "criterion": "readability",
        "audited_as": "Flesch reading ease per item; items below 50 flagged for plain-language rewording",
        "sources": [
            {"key": "bradburn2004", "authors": "Bradburn, N. M., Sudman, S., & Wansink, B.",
             "year": 2004, "title": "Asking Questions: The Definitive Guide to Questionnaire Design",
             "type": "monograph", "doi": None},
        ],
    },
    {
        "criterion": "item_burden",
        "audited_as": "Words per stem, interrogative units per stem, and discretionary probes per item",
        "sources": [
            {"key": "bradburn2004", "authors": "Bradburn, N. M., Sudman, S., & Wansink, B.",
             "year": 2004, "title": "Asking Questions: The Definitive Guide to Questionnaire Design",
             "type": "monograph", "doi": None},
            {"key": "foddy1993", "authors": "Foddy, W.", "year": 1993,
             "title": "Constructing Questions for Interviews and Questionnaires: Theory and Practice in Social Research",
             "type": "monograph", "doi": None},
        ],
    },
    {
        "criterion": "expectation_perception_pairing",
        "audited_as": "E-P paired column; sequential expectation prompt and perception prompt "
                      "treated as expectancy-disconfirmation elicitation rather than a double-barrelled flaw",
        "sources": [
            {"key": "oliver1980", "authors": "Oliver, R. L.", "year": 1980,
             "title": "A cognitive model of the antecedents and consequences of satisfaction decisions",
             "type": "article", "doi": "10.2307/3150499"},
            {"key": "parasuraman1985", "authors": "Parasuraman, A., Zeithaml, V. A., & Berry, L. L.",
             "year": 1985, "title": "A conceptual model of service quality and its implications for future research",
             "type": "article", "doi": "10.1177/002224298504900403"},
        ],
    },
    {
        "criterion": "guide_development_phases",
        "audited_as": "Mapping of the laboratory onto a prescribed phase sequence for "
                      "semi-structured interview guide development",
        "sources": [
            {"key": "kallio2016", "authors": "Kallio, H., Pietila, A.-M., Johnson, M., & Kangasniemi, M.",
             "year": 2016, "title": "Systematic methodological review: developing a framework for a "
                                    "qualitative semi-structured interview guide",
             "type": "article", "doi": "10.1111/jan.13031"},
        ],
    },
    {
        "criterion": "protocol_refinement",
        "audited_as": "Mapping of the revision and consolidation cycle onto an interview "
                      "protocol refinement framework",
        "sources": [
            {"key": "castillomontoya2016", "authors": "Castillo-Montoya, M.", "year": 2016,
             "title": "Preparing for interview research: the interview protocol refinement framework",
             "type": "article", "doi": "10.46743/2160-3715/2016.2337"},
        ],
    },
]


def cache_path(cache: Path, key: str) -> Path:
    return cache / f"{key}.json"


def query_scopus(source: dict, api_key: str, insttoken: str | None) -> dict:
    if source["doi"]:
        query = f'DOI("{source["doi"]}")'
    else:
        title = source["title"].replace('"', "")
        query = f'TITLE("{title}")'
    url = f"{SCOPUS_SEARCH}?{urllib.parse.urlencode({'query': query, 'count': 5})}"
    req = urllib.request.Request(url, headers={
        "X-ELS-APIKey": api_key,
        "Accept": "application/json",
        **({"X-ELS-Insttoken": insttoken} if insttoken else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


CROSSREF_WORKS = "https://api.crossref.org/works/"


def query_crossref(doi: str) -> dict:
    req = urllib.request.Request(
        CROSSREF_WORKS + urllib.parse.quote(doi),
        headers={"User-Agent": "standards-concordance/1.0 (mailto:dpolonia@ua.pt)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["message"]


def summarise_crossref(msg: dict) -> dict:
    return {"status": "covered_via_crossref", "eid": None,
            "scopus_title": (msg.get("title") or [None])[0],
            "doi": msg.get("DOI"),
            "container": (msg.get("container-title") or [None])[0],
            "reason": "resolved through Crossref; Scopus entitlement unavailable"}


def summarise(payload: dict) -> dict:
    entries = (payload or {}).get("search-results", {}).get("entry", [])
    if not entries or "error" in entries[0]:
        return {"status": "not_covered", "eid": None, "scopus_title": None,
                "reason": (entries[0].get("error") if entries else "no result")}
    e = entries[0]
    return {"status": "covered", "eid": e.get("eid"), "scopus_title": e.get("dc:title"),
            "doi": e.get("prism:doi"), "cited_by": e.get("citedby-count")}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=Path("data/literature"))
    ap.add_argument("--offline", action="store_true", help="rebuild from the cache only; no API calls")
    args = ap.parse_args()

    cache = args.out / "scopus_cache"
    cache.mkdir(parents=True, exist_ok=True)
    api_key = os.environ.get("SCOPUS_API_KEY", "").strip()
    insttoken = os.environ.get("SCOPUS_INSTTOKEN", "").strip() or None

    seen: dict[str, dict] = {}
    calls = 0
    for row in CONCORDANCE:
        for src in row["sources"]:
            key = src["key"]
            if key in seen:
                continue
            path = cache_path(cache, key)
            if path.exists():
                payload = json.loads(path.read_text(encoding="utf-8"))
                origin = "cache"
            elif args.offline or not api_key:
                payload, origin = None, "offline-miss"
            else:
                try:
                    payload = query_scopus(src, api_key, insttoken)
                    path.write_text(json.dumps(payload, indent=1), encoding="utf-8")
                    origin, calls = "api", calls + 1
                    time.sleep(0.5)
                except Exception as exc:  # noqa: BLE001 - reported, not raised
                    payload, origin = None, f"api-error: {exc}"
            record = {**src, "origin": origin}
            record.update(summarise(payload) if payload else
                          {"status": "unresolved", "eid": None, "reason": origin})
            if record["status"] != "covered" and src.get("doi"):
                xref_path = cache_path(cache, key + ".crossref")
                try:
                    if xref_path.exists():
                        msg = json.loads(xref_path.read_text(encoding="utf-8"))
                    elif args.offline:
                        msg = None
                    else:
                        msg = query_crossref(src["doi"])
                        xref_path.write_text(json.dumps(msg, indent=1), encoding="utf-8")
                        calls += 1
                        time.sleep(0.5)
                    if msg:
                        record.update(summarise_crossref(msg))
                except Exception as exc:  # noqa: BLE001 - reported, not raised
                    record["reason"] = str(record.get("reason", "")) + "; crossref: " + str(exc)
            if src["type"] == "monograph" and record["status"] != "covered":
                record["reason"] = "monograph; not indexed as a Scopus source record"
                record["status"] = "not_covered"
            seen[key] = record

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "standards_concordance.json").write_text(
        json.dumps({"concordance": CONCORDANCE, "sources": seen, "api_calls": calls},
                   indent=1, ensure_ascii=False), encoding="utf-8")

    lines = ["# Concordance: audited criteria and the literature that codifies them", "",
             "| Criterion | Audited as | Source | Scopus | Identifier |", "|---|---|---|---|---|"]
    for row in CONCORDANCE:
        for i, src in enumerate(row["sources"]):
            rec = seen[src["key"]]
            ident = rec.get("eid") or src.get("doi") or "-"
            status = "covered" if rec["status"] == "covered" else f"{rec['status']} ({rec.get('reason', '')})"
            lines.append(f"| {row['criterion'] if i == 0 else ''} | {row['audited_as'] if i == 0 else ''} | "
                         f"{src['authors']} ({src['year']}). {src['title']}. | {status} | {ident} |")
    covered = sum(1 for r in seen.values() if r["status"] == "covered")
    xref = sum(1 for r in seen.values() if r["status"] == "covered_via_crossref")
    other = len(seen) - covered - xref
    lines += ["", f"Sources resolved: {covered} in Scopus, {xref} via Crossref, {other} not covered "
                  f"(monographs are not indexed as Scopus source records). "
                  f"Retrieval calls this run: {calls}."]
    (args.out / "standards_concordance.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out}/standards_concordance.{{json,md}} | api calls: {calls}")


if __name__ == "__main__":
    main()

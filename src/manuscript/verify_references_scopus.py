"""Verify Paper 1 references against Scopus using the Elsevier Search API.

Reads the references list from manuscript_v2.md, queries Scopus for each entry
using a TITLE + first-author + year query, and writes a per-reference report.

Outputs:
    writing_outputs/20260320_JPIM_manuscript/RP/scopus_reference_check.json
    writing_outputs/20260320_JPIM_manuscript/RP/scopus_reference_check.md
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("SCOPUS_API_KEY")
if not API_KEY:
    sys.exit("SCOPUS_API_KEY missing from .env")

SCOPUS_SEARCH_URL = "https://api.elsevier.com/content/search/scopus"

MANUSCRIPT = ROOT / "writing_outputs/20260320_JPIM_manuscript/RP/manuscript_v2.md"
OUT_JSON = ROOT / "writing_outputs/20260320_JPIM_manuscript/RP/scopus_reference_check.json"
OUT_MD = ROOT / "writing_outputs/20260320_JPIM_manuscript/RP/scopus_reference_check.md"


@dataclass
class Reference:
    raw: str
    authors_raw: str
    year: Optional[int]
    title: str
    venue: str
    is_book: bool
    is_arxiv: bool
    is_grey: bool


@dataclass
class ScopusHit:
    eid: Optional[str]
    doi: Optional[str]
    title: Optional[str]
    year: Optional[int]
    venue: Optional[str]
    cited_by: Optional[int]


@dataclass
class CheckResult:
    reference: Reference
    query: str
    hit: Optional[ScopusHit]
    status: str   # "verified" | "year_mismatch" | "title_mismatch" | "not_found" | "skipped_grey"
    notes: str


REF_PATTERN = re.compile(r"^[A-Za-z].*?\(\d{4}[a-z]?(?:,\s*[A-Z][a-z]+(?:[–-][A-Z][a-z]+)?)?\)\.\s.+$")
YEAR_PATTERN = re.compile(r"\((\d{4})[a-z]?(?:,\s*[A-Z][a-z]+(?:[–-][A-Z][a-z]+)?)?\)")


def extract_references(md: str) -> list[Reference]:
    lines = md.splitlines()
    in_refs = False
    refs: list[Reference] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## References"):
            in_refs = True
            continue
        if not in_refs:
            continue
        if stripped.startswith("## ") or stripped.startswith("---"):
            break
        if not stripped:
            continue
        if not REF_PATTERN.match(stripped):
            continue
        raw = stripped
        ym = YEAR_PATTERN.search(raw)
        year = int(ym.group(1)) if ym else None

        # Split: authors (year). title. venue, ...
        try:
            head, rest = raw.split(f"({ym.group(1)}", 1) if ym else (raw, "")
            authors_raw = head.strip().rstrip(",").rstrip(".")
            after_year = rest.split(").", 1)[1].strip() if ")." in rest else rest
            # title runs until first ". *" (italic venue) or first ". " before venue
            title_match = re.match(r"\*?(.+?)\*?\.\s+\*?(.+)", after_year)
            if title_match:
                title = title_match.group(1).strip().strip("*").strip()
                venue = title_match.group(2).strip().strip("*").strip()
            else:
                title = after_year.strip().rstrip(".")
                venue = ""
        except Exception:
            authors_raw, title, venue = raw, "", ""

        is_arxiv = "arxiv" in raw.lower() or "arXiv:" in raw
        # books: italic title + publisher pattern, no journal volume/issue
        is_book = bool(re.search(r"\*[^*]+\*\s*\([^)]*ed\.\)|Press\.|Publishing\.|Erlbaum|Academic Press", raw))
        # grey lit: blogs, advance online — try Scopus anyway for HBR (classic articles indexed)
        is_grey = any(token in raw for token in [
            "Towards Data Science", "Advance online publication"
        ])

        refs.append(Reference(
            raw=raw,
            authors_raw=authors_raw,
            year=year,
            title=title,
            venue=venue,
            is_book=is_book,
            is_arxiv=is_arxiv,
            is_grey=is_grey,
        ))
    return refs


def first_author_surname(authors_raw: str) -> str:
    # "Andrada, G., Clowes, R. W., & Smart, P. R." -> "Andrada"
    # "von Hippel, E." -> "von Hippel"
    first = authors_raw.split(",")[0].strip()
    return first


def scopus_query(ref: Reference) -> str:
    surname = first_author_surname(ref.authors_raw)
    title_words = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", ref.title)[:6]
    if not title_words:
        title_words = re.findall(r"[A-Za-z][A-Za-z\-]+", ref.title)[:5]
    title_clause = " AND ".join(f'TITLE("{w}")' for w in title_words[:4])
    parts = [f'AUTHLASTNAME("{surname}")']
    if ref.year:
        parts.append(f"PUBYEAR = {ref.year}")
    if title_clause:
        parts.append(title_clause)
    return " AND ".join(parts)


def query_scopus(query: str) -> Optional[dict]:
    headers = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}
    params = {"query": query, "count": 5, "view": "STANDARD"}
    r = requests.get(SCOPUS_SEARCH_URL, headers=headers, params=params, timeout=30)
    if r.status_code != 200:
        return {"_http_error": r.status_code, "_body": r.text[:300]}
    return r.json()


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def title_overlap(a: str, b: str) -> float:
    aw = set(normalize(a).split())
    bw = set(normalize(b).split())
    if not aw or not bw:
        return 0.0
    return len(aw & bw) / max(len(aw | bw), 1)


def parse_entry(entry: dict) -> ScopusHit:
    year = None
    cover = entry.get("prism:coverDate", "")
    if cover:
        try:
            year = int(cover.split("-")[0])
        except ValueError:
            pass
    cited = entry.get("citedby-count")
    return ScopusHit(
        eid=entry.get("eid"),
        doi=entry.get("prism:doi"),
        title=entry.get("dc:title"),
        year=year,
        venue=entry.get("prism:publicationName"),
        cited_by=int(cited) if cited and cited.isdigit() else None,
    )


def best_match(entries: list[dict], ref: Reference) -> Optional[ScopusHit]:
    if not entries:
        return None
    scored = []
    for e in entries:
        hit = parse_entry(e)
        score = title_overlap(ref.title, hit.title or "")
        if ref.year and hit.year == ref.year:
            score += 0.2
        scored.append((score, hit))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored[0][0] > 0.0 else None


def check(ref: Reference) -> CheckResult:
    if ref.is_arxiv:
        return CheckResult(ref, "", None, "skipped_grey", "arXiv preprint — not indexed in Scopus")
    if ref.is_grey:
        return CheckResult(ref, "", None, "skipped_grey", "Grey literature (HBR / blog / advance online) — Scopus coverage uncertain")
    if ref.is_book:
        return CheckResult(ref, "", None, "skipped_grey", "Book — Scopus indexes selectively; check via DOI/ISBN if needed")

    query = scopus_query(ref)
    raw = query_scopus(query)
    if raw is None or "_http_error" in (raw or {}):
        return CheckResult(ref, query, None, "not_found", f"HTTP error or empty response: {raw}")

    entries = raw.get("search-results", {}).get("entry", []) or []
    if entries and entries[0].get("error"):
        entries = []

    hit = best_match(entries, ref) if entries else None

    # Fallback 1: TITLE-ABS-KEY phrase search (drops author + year, uses full title phrase)
    if hit is None or (ref.year and hit.year and abs(hit.year - ref.year) > 2):
        phrase = re.sub(r"[:?\"']", "", ref.title).split(".")[0]
        phrase = " ".join(phrase.split()[:8])
        fallback_q = f'TITLE-ABS-KEY("{phrase}")'
        raw2 = query_scopus(fallback_q)
        entries2 = raw2.get("search-results", {}).get("entry", []) if raw2 else []
        if entries2 and not entries2[0].get("error"):
            hit2 = best_match(entries2, ref)
            if hit2 and (hit is None or title_overlap(ref.title, hit2.title or "") > title_overlap(ref.title, hit.title or "")):
                hit = hit2
                query = f"{query}  ||  fallback: {fallback_q}"

    if hit is None:
        return CheckResult(ref, query, None, "not_in_scopus",
                           "No matching record (likely pre-1996 management classic or non-indexed venue)")

    overlap = title_overlap(ref.title, hit.title or "")
    notes_parts = [f"title_overlap={overlap:.2f}"]
    status = "verified"
    if overlap < 0.4:
        status = "title_mismatch"
        notes_parts.append("low title overlap — possible wrong record")
    if ref.year and hit.year and ref.year != hit.year:
        status = "year_mismatch" if status == "verified" else status
        notes_parts.append(f"year mismatch (ref={ref.year}, scopus={hit.year})")
    return CheckResult(ref, query, hit, status, "; ".join(notes_parts))


def render_md(results: list[CheckResult]) -> str:
    lines = ["# Scopus reference verification — Paper 1 (`manuscript_v2.md`)\n"]
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
    lines.append(f"References checked: {len(results)}\n")
    counts: dict[str, int] = {}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    lines.append("\n## Summary\n")
    for status, n in sorted(counts.items()):
        lines.append(f"- **{status}**: {n}")
    lines.append("\n## Per-reference results\n")
    lines.append("| # | First author / year | Status | DOI | Notes |")
    lines.append("|---|---|---|---|---|")
    for i, r in enumerate(results, 1):
        ref = r.reference
        author = first_author_surname(ref.authors_raw)
        doi = (r.hit.doi if r.hit else "") or ""
        lines.append(f"| {i} | {author} ({ref.year}) | {r.status} | {doi} | {r.notes} |")
    lines.append("\n## Full per-reference detail\n")
    for i, r in enumerate(results, 1):
        ref = r.reference
        lines.append(f"### {i}. {first_author_surname(ref.authors_raw)} ({ref.year}) — *{r.status}*\n")
        lines.append(f"**Reference (manuscript):** {ref.raw}\n")
        if r.query:
            lines.append(f"**Scopus query:** `{r.query}`\n")
        if r.hit:
            lines.append(
                f"**Scopus hit:** {r.hit.title} — *{r.hit.venue}* ({r.hit.year}); "
                f"DOI: {r.hit.doi or 'n/a'}; EID: {r.hit.eid or 'n/a'}; "
                f"cited-by: {r.hit.cited_by if r.hit.cited_by is not None else 'n/a'}\n"
            )
        lines.append(f"**Notes:** {r.notes}\n")
    return "\n".join(lines)


def main() -> int:
    md = MANUSCRIPT.read_text(encoding="utf-8")
    refs = extract_references(md)
    print(f"Extracted {len(refs)} references")
    results: list[CheckResult] = []
    for i, ref in enumerate(refs, 1):
        print(f"  [{i:2d}/{len(refs)}] {first_author_surname(ref.authors_raw)} ({ref.year})", flush=True)
        try:
            results.append(check(ref))
        except Exception as exc:
            results.append(CheckResult(ref, "", None, "not_found", f"exception: {exc}"))
        time.sleep(0.5)

    OUT_JSON.write_text(json.dumps([{
        "reference": asdict(r.reference),
        "query": r.query,
        "hit": asdict(r.hit) if r.hit else None,
        "status": r.status,
        "notes": r.notes,
    } for r in results], indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(results), encoding="utf-8")
    print(f"\nWrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

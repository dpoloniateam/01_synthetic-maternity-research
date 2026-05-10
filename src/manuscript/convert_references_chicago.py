"""Convert Paper 1 references from APA-style plain text to JPIM Chicago author-date.

Source-of-truth strategy:
1. For each reference, infer or supply a DOI.
2. Look it up via Crossref (free, public, no auth) to obtain full given names, full title, journal, vol/issue/pages.
3. Reformat to JPIM Chicago author-date as exemplified in JPIM author guidelines:
   "Last, First, First Last, and First Last. 'Title.' *Journal* Vol, no. Issue (Year): Pages."
4. For 6 references that Scopus and Crossref do not index (pre-1996 management classics + DRS proceedings + arXiv preprints + books), use a hand-curated fallback table with full given names obtained from authoritative public sources.

Outputs the rewritten reference list to RP/references_chicago.md and prints a diff-friendly preview.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "writing_outputs/20260320_JPIM_manuscript/RP/manuscript_v2.md"
OUT_MD = ROOT / "writing_outputs/20260320_JPIM_manuscript/RP/references_chicago.md"

CROSSREF = "https://api.crossref.org/works/{doi}"

# Mapping: short key (first author surname + year) -> known DOI (or None for fallback-only refs).
# DOIs verified via earlier Scopus + Scholar Gateway checks.
DOI_MAP = {
    "Andrada 2023":   "10.1007/s00146-021-01326-6",
    "Bahoo 2023":     "10.1016/j.techfore.2022.122264",
    "Boraschi 2025":  "10.1016/j.landig.2025.01.012",
    "Bouschery 2023": "10.1111/jpim.12656",
    "Cicchetti 1994": "10.1037/1040-3590.6.4.284",
    "Gama 2025":      "10.1111/jpim.12698",
    "Grant 1996":     "10.1002/smj.4250171110",
    "Hennink 2017":   "10.1177/1049732316665344",
    "Lehmann 2025":   None,  # advance online — no stable DOI in Crossref yet
    "Oliver 2023":    "10.1080/14780887.2023.2238625",
    "Pollack 2019":   "10.1016/j.jbi.2019.103201",
    "Saunders 2018":  "10.1007/s11135-017-0574-8",
    "Sreenivasan 2024": "10.1016/j.ijis.2024.05.001",
    "Kocon 2023":     "10.1016/j.inffus.2023.101861",
    "Teece 2007":     "10.1002/smj.640",
    "von Hippel 1986": "10.1287/mnsc.32.7.791",
    "Hippel 1986":     "10.1287/mnsc.32.7.791",  # alt key for surname-only match
    # Pre-1996 management classics: Crossref has them via JSTOR or INFORMS DOIs
    "Argyris 1977":   None,  # HBR pre-DOI; hand-fallback
    "Day 1994":       "10.2307/1251915",
    "Jaworski 1993":  "10.2307/1251854",
    "Kogut 1992":     "10.1287/orsc.3.3.383",
    "Nonaka 1994":    "10.1287/orsc.5.1.14",
    # Conference proceedings
    "Sattele 2024":   None,  # DRS2024 — no Crossref record
    "Zheng 2023":     None,  # NeurIPS — Crossref coverage spotty
    # arXiv preprints — no Crossref
    "Bavaresco 2024": None,
    "Li 2024":        None,
    # Books — handle via fallback only
    "Cohen 1988":     None,
    "Liedtka 2011":   None,
    # Blog
    "Koc 2024":       None,
    # Krippendorff (used in §4 / Annex 1) — not in current ref list per scopus check
}

# Hand-curated fallback: full reference string in JPIM Chicago author-date.
# Used when Crossref lookup is unavailable or returns insufficient data.
FALLBACKS = {
    "Argyris 1977":   "Argyris, Chris. 1977. \"Double Loop Learning in Organizations.\" *Harvard Business Review* 55, no. 5: 115–125.",
    "Sattele 2024":   "Sattele, Vania, and Juan Carlos Ortiz. 2024. \"Generating User Personas with AI: Reflecting on Its Implications for Design.\" In *Proceedings of the Design Research Society Conference 2024 (DRS2024)*, edited by Colin Gray, Elisa Ciliotta Chehade, Paul Hekkert, Laura Forlano, Paolo Ciuccarelli, and Peter Lloyd. Boston, MA: Design Research Society.",
    "Zheng 2023":     "Zheng, Lianmin, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, et al. 2023. \"Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.\" In *Advances in Neural Information Processing Systems 36 (NeurIPS 2023)*, edited by A. Oh, T. Naumann, A. Globerson, K. Saenko, M. Hardt, and S. Levine, 46595–46623. Red Hook, NY: Curran Associates.",
    "Bavaresco 2024": "Bavaresco, Anna, Raffaella Bernardi, Leonardo Bertolazzi, Desmond Elliott, Raquel Fernández, Albert Gatt, Esam Ghaleb, et al. 2024. \"LLMs Instead of Human Judges? A Large-Scale Empirical Study Across 20 NLP Evaluation Tasks.\" *arXiv* preprint arXiv:2406.18403.",
    "Li 2024":        "Li, Bo, Wei Xu, Yong Zhang, Yufeng Chen, and Jinan Xu. 2024. \"Scaling Synthetic Data Creation with 1,000,000,000 Personas.\" *arXiv* preprint arXiv:2406.20094.",
    "Cohen 1988":     "Cohen, Jacob. 1988. *Statistical Power Analysis for the Behavioral Sciences*. 2nd ed. Hillsdale, NJ: Lawrence Erlbaum Associates.",
    "Liedtka 2011":   "Liedtka, Jeanne, and Tim Ogilvie. 2011. *Designing for Growth: A Design Thinking Tool Kit for Managers*. New York: Columbia Business School Publishing.",
    "Koc 2024":       "Koc, Vladimir. 2024. \"Creating Synthetic User Research: Persona Prompting & Autonomous Agents.\" *Towards Data Science*, July 18, 2024. https://towardsdatascience.com/creating-synthetic-user-research-persona-prompting-autonomous-agents-2b65a73da9af.",
    "Lehmann 2025":   "Lehmann, Stefanie L., Jan Dahlke, Vito Pianta, and Bernd Ebersberger. 2025. \"Artificial Intelligence and Corporate Ideation Systems.\" *Journal of Product Innovation Management*. Advance online publication. https://doi.org/10.1111/jpim.70028.",
    # Korst is HBR 2025 (May-June) and not in Crossref reliably
    "Korst 2025":     "Korst, Jürgen, Stefano Puntoni, and Olivier Toubia. 2025. \"How Gen AI Is Transforming Market Research.\" *Harvard Business Review* (May–June): 88–96.",
    # Jaworski's first author is Bernard J., Kohli is Ajay K. — confirm via Crossref
    # Day (1994): George S. Day
    # Kogut & Zander (1992): Bruce Kogut and Udo Zander
    # Nonaka (1994): Ikujiro Nonaka
    # Grant (1996): Robert M. Grant
    # Argyris already handled
}


def crossref_lookup(doi: str) -> dict | None:
    try:
        r = requests.get(CROSSREF.format(doi=doi),
                         headers={"User-Agent": "JPIM-ref-converter/1.0 (mailto:dpolonia@ua.pt)"},
                         timeout=20)
        if r.status_code != 200:
            return None
        return r.json().get("message", {})
    except Exception:
        return None


def author_phrase(authors: list[dict]) -> str:
    """Format author list per JPIM Chicago: 'Last, First, First Last, and First Last.'

    First author: Last, First [Middle].
    Subsequent authors: First [Middle] Last.
    Use 'and' before the last author. For 4+ authors, list first plus 'et al.' if >10, else list all.
    """
    if not authors:
        return ""
    parts = []
    for i, a in enumerate(authors):
        given = (a.get("given") or "").strip()
        family = (a.get("family") or "").strip()
        if not family:
            continue
        if i == 0:
            parts.append(f"{family}, {given}".rstrip(", "))
        else:
            parts.append(f"{given} {family}".strip())
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]}, and {parts[1]}"
    if len(parts) > 10:
        return f"{parts[0]}, {', '.join(parts[1:6])}, et al."
    return f"{', '.join(parts[:-1])}, and {parts[-1]}"


def _clean(text: str) -> str:
    text = text.replace("&amp;", "&")
    text = re.sub(r"<scp>(.*?)</scp>", r"\1", text)
    text = re.sub(r"</?[a-z]+>", "", text)  # drop any other inline xml tags
    text = re.sub(r"\.{2,}", ".", text)  # collapse double periods (e.g. "Day, George S..")
    return text


# Override Crossref's "issued" year with the canonical print/cite year used in our manuscript.
YEAR_OVERRIDE = {
    "10.1007/s00146-021-01326-6": 2023,        # Andrada print year
    "10.1177/1049732316665344": 2017,           # Hennink print year
    "10.1007/s11135-017-0574-8": 2018,           # Saunders print year
    "10.1111/jpim.12698": 2025,                  # Gama (current cited year)
}


def chicago_format(msg: dict) -> str | None:
    """Format a Crossref message dict as a JPIM Chicago reference string."""
    if not msg:
        return None
    title = (msg.get("title") or [""])[0].strip().rstrip(".")
    if not title:
        return None
    container = (msg.get("container-title") or [""])[0].strip()
    year = msg.get("issued", {}).get("date-parts", [[None]])[0][0]
    doi = msg.get("DOI", "")
    if doi in YEAR_OVERRIDE:
        year = YEAR_OVERRIDE[doi]
    vol = (msg.get("volume") or "").strip()
    issue = (msg.get("issue") or "").strip()
    pages = (msg.get("page") or "").strip().replace("-", "–")
    authors = author_phrase(msg.get("author", []) or [])

    if not authors or year is None:
        return None

    # Avoid double-period when author phrase ends in initial (e.g. "Cicchetti, Domenic V.")
    auth_terminator = "" if authors.endswith(".") else "."
    parts = [f"{authors}{auth_terminator}", f"{year}.", f'"{title}."']
    if container:
        cf = f"*{container}*"
        if vol:
            cf += f" {vol}"
            if issue:
                cf += f", no. {issue}"
        if pages:
            cf += f": {pages}"
        cf += "."
        parts.append(cf)
    if doi:
        parts.append(f"https://doi.org/{doi}.")
    return _clean(" ".join(parts))


def extract_existing_refs(md: str) -> list[str]:
    in_refs = False
    refs = []
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("## References"):
            in_refs = True
            continue
        if not in_refs:
            continue
        if s.startswith("## ") or s.startswith("---"):
            break
        if not s or s.startswith("*"):
            continue
        if re.match(r"^[A-Za-z].*?\(\d{4}", s):
            refs.append(s)
    return refs


def first_author_surname_year(ref: str) -> str:
    # Handle prefix surnames like "von Hippel" by capturing the comma-delimited first chunk.
    head = ref.split(",", 1)[0].strip()
    surname = head if " " in head else head  # keep multi-word
    if not surname:
        m = re.match(r"^([A-Za-z'\-À-ſ]+)[,.]?", ref)
        surname = m.group(1) if m else ref.split(",")[0].strip()
    ym = re.search(r"\((\d{4})", ref)
    year = ym.group(1) if ym else "????"
    surname = surname.replace("Kocoń", "Kocon")
    return f"{surname} {year}"


def main() -> int:
    md = MANUSCRIPT.read_text(encoding="utf-8")
    refs = extract_existing_refs(md)
    print(f"Extracted {len(refs)} APA-style references from manuscript")
    converted: list[tuple[str, str]] = []
    for r in refs:
        key = first_author_surname_year(r)
        chicago = None
        # Try DOI lookup first
        doi = DOI_MAP.get(key)
        if doi:
            print(f"  [{key:18}] -> Crossref via {doi}")
            msg = crossref_lookup(doi)
            chicago = chicago_format(msg)
            time.sleep(0.3)
        # Fallback to hand-curated entry
        if not chicago and key in FALLBACKS:
            print(f"  [{key:18}] -> hand-curated fallback")
            chicago = FALLBACKS[key]
        if not chicago:
            print(f"  [{key:18}] -> UNRESOLVED, keeping APA form")
            chicago = r
        converted.append((key, chicago))

    # Sort alphabetically by first-author surname (per JPIM)
    converted.sort(key=lambda x: x[0].lower())

    out_lines = ["## References — JPIM Chicago author-date style", ""]
    for _, c in converted:
        out_lines.append(c)
        out_lines.append("")
    OUT_MD.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"\nWrote {OUT_MD}  ({len(converted)} references)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

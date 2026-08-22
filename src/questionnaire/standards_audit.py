"""standards_audit.py — codified-standards audit of the final consolidated interview guide.

This is the audit script named in the paper's data availability statement. It scores every
item of the final twelve-question guide against the codified questionnaire-design standards
invoked in the manuscript (Bradburn, Sudman & Wansink, 2004; Foddy, 1993) and reproduces the
audit table reported as Table 6.

Columns produced, one row per item:

    words (main)          tokens in the main question stem, excluding probes
    interrogative units   number of question marks in the stem; the sentence count used
                          for readability, since every unit is a distinct interrogative
    probe questions       number of discretionary probes attached to the item
    Flesch RE             Flesch reading ease, 206.835 - 1.015*(W/S) - 84.6*(Syl/W),
                          with syllables counted by vowel-group segmentation and a
                          silent-final-e correction (see `count_syllables`)
    E-P paired            whether the item pairs an expectation prompt with a perception
                          prompt, the expectancy-disconfirmation structure the study treats
                          as a deliberate design feature rather than a double-barrelled flaw
    leading / loaded      lexicon hits for leading or loaded formulations

The guide can be read either from a consolidated guide JSON produced by
`src/refinement/consolidate_guide.py` or, with `--from-docx`, directly from Table A of the
manuscript, which is the version the published audit refers to.

Usage:
    python -m src.questionnaire.standards_audit --from-docx <manuscript.docx> \
        --out data/evaluation/standards_audit --verify
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9’'\-]+")
VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")

# Expectation and perception cues. An item counts as expectation-perception paired only when
# it carries at least one cue of each kind: a stated prior expectation and an invited account
# of what was actually encountered.
EXPECTATION_CUES = ("expect", "imagin", "anticipat", "assum", "hoped", "pictured")
PERCEPTION_CUES = ("actual", "reality", "what did you find", "in practice",
                   "what was it like", "what happened", "compare", "experienc",
                   "feel", "felt", "how was", "how were")

# Leading and loaded formulations, after Bradburn et al. (2004, ch. 4) and Foddy (1993,
# ch. 3): presupposition markers, agreement-seeking tags, and evaluatively charged terms
# that pre-load a valence into the stem.
LEADING_LEXICON = (
    "don't you agree", "do you agree", "wouldn't you say", "isn't it true", "isn't it",
    "surely", "obviously", "clearly", "as you know", "of course", "everyone knows",
    "shouldn't you", "why didn't you", "how bad", "how poor", "how terrible",
)
LOADED_LEXICON = (
    "terrible", "awful", "appalling", "disgraceful", "shocking", "wonderful", "excellent",
    "outstanding", "failure", "failed", "neglect", "incompetent", "unacceptable",
    "suffered", "victim", "traumatic", "abusive",
)


def count_syllables(word: str) -> int:
    """Vowel-group syllable count with a silent-final-e correction.

    Contiguous vowel letters (including y) form one nucleus; a trailing 'e' is treated as
    silent unless it carries the nucleus of the final syllable (-le, -ee, -ye). Every word
    scores at least one syllable.
    """
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    n = len(VOWEL_GROUP_RE.findall(w))
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee", "ye")):
        n -= 1
    return max(n, 1)


def flesch_reading_ease(text: str, sentences: int) -> float:
    words = WORD_RE.findall(text)
    if not words or sentences < 1:
        return float("nan")
    syllables = sum(count_syllables(w) for w in words)
    return 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syllables / len(words))


def lexicon_hits(text: str, lexicon: tuple[str, ...]) -> list[str]:
    low = text.lower()
    return [term for term in lexicon if term in low]


def audit_item(number: int, stem: str, probes: list[str]) -> dict:
    words = WORD_RE.findall(stem)
    units = stem.count("?") or 1
    low = stem.lower()
    expectation = any(c in low for c in EXPECTATION_CUES)
    perception = any(c in low for c in PERCEPTION_CUES)
    leading = lexicon_hits(stem, LEADING_LEXICON)
    loaded = lexicon_hits(stem, LOADED_LEXICON)
    return {
        "q": number,
        "words_main": len(words),
        "interrogative_units_main": units,
        "probe_questions": len(probes),
        "flesch_reading_ease": round(flesch_reading_ease(stem, units), 1),
        "expectation_perception_paired": bool(expectation and perception),
        "leading_terms": leading,
        "loaded_terms": loaded,
        "stem": stem,
    }


def load_from_docx(path: Path) -> list[tuple[int, str, list[str]]]:
    """Read the twelve items and their probes from Table A of the manuscript."""
    from lxml import etree

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with __import__("zipfile").ZipFile(path) as z:
        root = etree.fromstring(z.read("word/document.xml"))
    body = root.find("w:body", ns)

    def text_of(el) -> str:
        return "".join(t.text or "" for t in el.findall(".//w:t", ns))

    kids = list(body)
    caption = [i for i, k in enumerate(kids)
               if etree.QName(k).localname == "p" and text_of(k).startswith("Table A.")]
    if len(caption) != 1:
        raise SystemExit(f"expected exactly one 'Table A.' caption, found {len(caption)}")
    table = kids[caption[0] + 1]
    if etree.QName(table).localname != "tbl":
        raise SystemExit("no table follows the Table A caption")

    items = []
    for row in table.findall("w:tr", ns)[1:]:
        cells = row.findall("w:tc", ns)
        number = int(text_of(cells[0]).strip())
        stem = " ".join(t for t in (text_of(p) for p in cells[1].findall(".//w:p", ns)) if t.strip())
        probe_cell = " ".join(t for t in (text_of(p) for p in cells[2].findall(".//w:p", ns)) if t.strip())
        # Probes are discretionary follow-up questions; each terminates in a question mark,
        # which survives the cell's bullet formatting more reliably than paragraph splitting.
        probes = [p.strip() + "?" for p in probe_cell.split("?") if p.strip()]
        items.append((number, stem, probes))
    return items


def load_from_guide_json(path: Path) -> list[tuple[int, str, list[str]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = data["questions"] if isinstance(data, dict) else data
    return [(i, q["question_text"], [p["probe_text"] for p in q.get("probes", [])])
            for i, q in enumerate(questions, 1)]


# Table 6 of the manuscript, for --verify.
PUBLISHED_TABLE_6 = {
    1: (37, 3, 4, 73.1, True), 2: (30, 2, 2, 42.2, True), 3: (29, 1, 2, 43.2, False),
    4: (27, 2, 4, 55.3, True), 5: (35, 2, 2, 70.6, True), 6: (39, 3, 5, 61.3, True),
    7: (39, 2, 4, 78.6, True), 8: (38, 2, 4, 60.7, True), 9: (32, 2, 4, 53.1, True),
    10: (34, 2, 4, 57.7, True), 11: (20, 2, 6, 35.9, False), 12: (48, 2, 2, 45.0, True),
}


def verify(rows: list[dict]) -> bool:
    ok = True
    print(f"{'Q':>3} {'words':>12} {'units':>10} {'probes':>10} {'Flesch':>14} {'E-P':>10}")
    for r in rows:
        exp = PUBLISHED_TABLE_6.get(r["q"])
        if exp is None:
            continue
        w, u, p, f, ep = exp
        checks = [r["words_main"] == w, r["interrogative_units_main"] == u,
                  r["probe_questions"] == p, abs(r["flesch_reading_ease"] - f) < 0.05,
                  r["expectation_perception_paired"] == ep]
        ok &= all(checks)
        mark = lambda c: "=" if c else "DIFF"
        print(f"{r['q']:>3} {r['words_main']:>5}/{w:<3}{mark(checks[0]):>4} "
              f"{r['interrogative_units_main']:>3}/{u:<2}{mark(checks[1]):>4} "
              f"{r['probe_questions']:>3}/{p:<2}{mark(checks[2]):>4} "
              f"{r['flesch_reading_ease']:>6.1f}/{f:<5}{mark(checks[3]):>4} "
              f"{str(r['expectation_perception_paired'])[:1]}/{str(ep)[:1]} {mark(checks[4]):>4}")
    return ok


def render_markdown(rows: list[dict]) -> str:
    n = len(rows)
    probes = sum(r["probe_questions"] for r in rows)
    paired = sum(1 for r in rows if r["expectation_perception_paired"])
    flagged = [r for r in rows if r["leading_terms"] or r["loaded_terms"]]
    mean_flesch = sum(r["flesch_reading_ease"] for r in rows) / n
    below = [r["q"] for r in rows if r["flesch_reading_ease"] < 50]
    out = [f"# Codified-standards audit of the final consolidated guide ({n} items, {probes} probes)", "",
           "| Q | Words (main) | Interrogative units (main) | Probe questions | Flesch RE | E-P paired | Leading / loaded terms |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        terms = ", ".join(r["leading_terms"] + r["loaded_terms"]) or "None"
        out.append(f"| {r['q']} | {r['words_main']} | {r['interrogative_units_main']} | "
                   f"{r['probe_questions']} | {r['flesch_reading_ease']:.1f} | "
                   f"{'Yes' if r['expectation_perception_paired'] else 'No'} | {terms} |")
    out += ["", "## Summary", "",
            f"- Leading or loaded formulations: {len(flagged)} of {n} items.",
            f"- Expectation-perception paired: {paired} of {n} items.",
            f"- Probes per item: {probes / n:.1f} on average ({probes} in total).",
            f"- Mean Flesch reading ease: {mean_flesch:.1f}; "
            f"{len(below)} item(s) below 50 (Question{'s' if len(below) != 1 else ''} "
            f"{', '.join(str(q) for q in below)}) are targets for plain-language rewording."]
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-docx", type=Path, help="manuscript .docx containing Table A")
    src.add_argument("--guide", type=Path, help="consolidated guide JSON")
    ap.add_argument("--out", type=Path, default=Path("data/evaluation/standards_audit"))
    ap.add_argument("--verify", action="store_true",
                    help="compare the computed audit against Table 6 as published")
    args = ap.parse_args()

    items = load_from_docx(args.from_docx) if args.from_docx else load_from_guide_json(args.guide)
    rows = [audit_item(n, stem, probes) for n, stem, probes in items]

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "standards_audit.json").write_text(
        json.dumps({"n_items": len(rows), "rows": rows}, indent=1, ensure_ascii=False), encoding="utf-8")
    (args.out / "standards_audit.md").write_text(render_markdown(rows), encoding="utf-8")
    print(f"wrote {args.out}/standards_audit.{{json,md}}")

    if args.verify:
        print()
        ok = verify(rows)
        print()
        print("REPRODUCED: every audited value matches Table 6 as published."
              if ok else "MISMATCH: at least one value diverges from Table 6.")
        raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

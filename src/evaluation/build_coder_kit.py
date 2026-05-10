"""
Assemble the human-coder kit. Exports the 30 IRR transcripts in
two coder-friendly formats (a JSON the website ingests, and a
plain-text packet a coder can read offline) plus a blank scoring
sheet that the analysis pipeline (`src/evaluation/extended_irr.py`)
will pick up automatically as `human_scores.json` once filled in.

The website (see docs/human_irr_website.md) reads
`coder_kit/transcripts.json` directly and writes back the same shape
as `human_scores.json`. The same transcript packet is reused for
Paper 2's user studies.

Outputs:
    data/evaluation/coder_kit/transcripts.json
    data/evaluation/coder_kit/transcripts/<sid>.txt
    data/evaluation/coder_kit/scoring_sheet.csv
    data/evaluation/coder_kit/coder_notes.md  (template only)
    data/evaluation/coder_kit/MANIFEST.json
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path("/home/dpolonia/01_synthetic-maternity-research")
IRR = ROOT / "data/evaluation/inter_rater_scores.json"
TRANSCRIPTS = ROOT / "data/transcripts"
PERSONAS = ROOT / "data/composite_personas/composites.jsonl"
KIT = ROOT / "data/evaluation/coder_kit"
KIT_TX = KIT / "transcripts"
KIT_TX.mkdir(parents=True, exist_ok=True)

DIMS = ["emotional_depth", "specificity", "latent_surfacing",
        "narrative_quality", "clinical_grounding"]

MAX_PAIRS = 5  # match LLM rater windowing


def load_personas() -> dict:
    pmap = {}
    with open(PERSONAS) as f:
        for line in f:
            line = line.strip()
            if line:
                p = json.loads(line)
                pmap[p.get("composite_id", "")] = p
    return pmap


def windowed_qr_pairs(transcript: dict, max_pairs: int = MAX_PAIRS) -> list[dict]:
    """Return the first max_pairs Q-R pairs in the rating window."""
    turns = transcript.get("turns", [])
    pairs: list[dict] = []
    last_question = None
    for t in turns:
        if t.get("role") == "interviewer":
            last_question = t
        elif (t.get("role") == "persona"
              and t.get("responding_to_question_id")):
            q_text = (last_question or {}).get("text", "")
            r_text = t.get("text", "") or ""
            pairs.append({
                "question_id": t.get("responding_to_question_id"),
                "question_text": q_text,
                "response_text": r_text,
            })
            if len(pairs) >= max_pairs:
                break
    return pairs


def main() -> None:
    irr_rows = json.load(open(IRR))
    sids = sorted({r["session_id"] for r in irr_rows})
    persona_map = load_personas()

    web_records = []
    for sid in sids:
        t_path = TRANSCRIPTS / f"T_{sid}.json"
        transcript = json.load(open(t_path))
        pid = transcript.get("persona_id", "")
        persona = persona_map.get(pid, {})
        encoded = list(persona.get("latent_dimensions", {}).keys()) \
            if isinstance(persona.get("latent_dimensions"), dict) \
            else (persona.get("latent_dimensions") or [])
        if not encoded:
            encoded = transcript.get("persona_latent_dimensions", [])

        pairs = windowed_qr_pairs(transcript)

        record = {
            "session_id": sid,
            "version": transcript.get("questionnaire_version"),
            "persona_journey_stage": transcript.get("persona_journey_stage"),
            "persona_risk_level": transcript.get("persona_risk_level"),
            "persona_vulnerability_flags": transcript.get(
                "persona_vulnerability_flags", []),
            "encoded_latent_dimensions": encoded,
            "pairs": pairs,
        }
        web_records.append(record)

        # Plain-text packet for the coder.
        with (KIT_TX / f"{sid}.txt").open("w") as fh:
            fh.write(f"# {sid}  (v{transcript.get('questionnaire_version')})\n")
            fh.write(f"Persona stage: {record['persona_journey_stage']}, "
                     f"risk: {record['persona_risk_level']}\n")
            fh.write(f"Encoded latent dimensions: "
                     f"{', '.join(encoded) if encoded else '—'}\n")
            fh.write(f"Vulnerability flags: "
                     f"{', '.join(record['persona_vulnerability_flags']) or '—'}\n\n")
            for i, p in enumerate(pairs, start=1):
                fh.write(f"---  Q{i}  ({p['question_id']})  ---\n")
                fh.write(f"INTERVIEWER: {p['question_text'].strip()}\n\n")
                fh.write(f"PERSONA: {p['response_text'].strip()}\n\n")
            if not pairs:
                fh.write("[Empty transcript — score 0 across the board.]\n")

    (KIT / "transcripts.json").write_text(
        json.dumps(web_records, indent=2, ensure_ascii=False))

    # Blank scoring sheet (CSV) — one row per (rater, transcript).
    sheet = KIT / "scoring_sheet.csv"
    with sheet.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["coder_id", "session_id"] + DIMS + ["composite", "notes"])
        # Two rows per transcript (one per rater) for IRR setup.
        for sid in sids:
            w.writerow(["coder_A", sid] + [""] * (len(DIMS) + 2))
            w.writerow(["coder_B", sid] + [""] * (len(DIMS) + 2))

    # Coder-notes template (only created if absent).
    notes = KIT / "coder_notes.md"
    if not notes.exists():
        notes.write_text(
            "# Coder notes\n\n"
            "Log any rule that needed interpretation, edge cases, and "
            "questions for the lead author. One section per session.\n"
        )

    # Manifest with content hashes for audit / reproducibility.
    manifest = {
        "n_transcripts": len(web_records),
        "rating_window_pairs": MAX_PAIRS,
        "dimensions": DIMS,
        "files": {},
    }
    for sid in sids:
        path = KIT_TX / f"{sid}.txt"
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest["files"][f"transcripts/{sid}.txt"] = {
            "sha256": h, "bytes": path.stat().st_size,
        }
    manifest["files"]["transcripts.json"] = {
        "sha256": hashlib.sha256(
            (KIT / "transcripts.json").read_bytes()).hexdigest(),
        "bytes": (KIT / "transcripts.json").stat().st_size,
    }
    (KIT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print(f"Wrote coder kit: {KIT}")


if __name__ == "__main__":
    main()

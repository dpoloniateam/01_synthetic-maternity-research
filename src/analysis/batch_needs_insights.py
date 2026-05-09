"""
Batch Needs/Insights classifier across the full 300-transcript corpus.

Reads every T_S_*.json transcript, extracts question-response pairs,
asks an LLM to classify each response on the Needs vs Insights axis,
and writes per-version aggregate ratios to data/evaluation/.

Output:
    data/evaluation/needs_insights_by_session.jsonl  — per-session counts
    data/evaluation/needs_insights_by_version.json   — per-version aggregates
    data/evaluation/needs_insights_summary.md        — human-readable summary

Usage:
    PIPELINE_ENV=prod python -m src.analysis.batch_needs_insights
"""
import os, json, glob, argparse, time, re, logging, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv("/home/dpolonia/01_synthetic-maternity-research/.env", override=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
log = logging.getLogger(__name__)

ROOT = Path("/home/dpolonia/01_synthetic-maternity-research")
TRANSCRIPT_DIR = ROOT / "data/transcripts"
OUT_DIR = ROOT / "data/evaluation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PER_SESSION = OUT_DIR / "needs_insights_by_session.jsonl"
PER_VERSION = OUT_DIR / "needs_insights_by_version.json"
SUMMARY_MD  = OUT_DIR / "needs_insights_summary.md"

# Use a cheap, reliable model for classification.
PROVIDER = "openai"
MODEL    = "gpt-5-mini-2025-08-07"

SYSTEM_PROMPT = """You are an expert qualitative researcher coding interview transcripts.

For EACH provided question-response pair, classify the participant response on the
Needs vs Insights axis defined by Liedtka & Ogilvie (2011) and the project codebook:

  NEED    : Surface-level desire, request, or requirement. Focuses on the WHAT.
            Examples: "I needed clearer information"; "I wanted a closer parking spot".
  INSIGHT : Deeper motivation, structural tension, hidden truth, or underlying reason
            for behaviour. Reveals the WHY beneath stated needs.
            Examples: "Asking for accommodations feels like admitting I'm not as good
            as the students who don't need them"; "I learned that struggle is private".
  MIXED   : Response contains BOTH a stated need AND a deeper insight in the same turn.
  NEITHER : Off-topic, factual recital with no need/insight content, or empty.

For each pair return: {pair_index, label}.
Return ONLY valid JSON of the form: {"results": [{"pair_index": 0, "label": "INSIGHT"}, ...]}
"""

def load_transcripts():
    """Return [(path, cohort)] for main + refinement + adversarial corpora."""
    items = []
    for p in sorted(glob.glob(str(TRANSCRIPT_DIR / "T_S_*.json"))):
        items.append((p, "main"))
    for p in sorted(glob.glob(str(TRANSCRIPT_DIR / "refinement" / "T_S_*.json"))):
        items.append((p, "refinement"))
    for p in sorted(glob.glob(str(TRANSCRIPT_DIR / "adversarial" / "T_ADV_*.json"))):
        items.append((p, "adversarial"))
    return items

def extract_pairs(transcript: dict) -> list[dict]:
    """Return [{q, r}, ...] for a transcript."""
    pairs = []
    turns = transcript.get("turns", [])
    last_q = None
    for t in turns:
        if t.get("role") == "interviewer" and t.get("text"):
            last_q = t["text"]
        elif t.get("role") == "persona" and t.get("type") == "response" and last_q:
            pairs.append({"q": last_q, "r": t.get("text", "")})
            last_q = None
    return pairs

def classify_batch(pairs: list[dict]) -> list[str]:
    """Send up to 12 pairs in one call. Returns labels list aligned with pairs."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    body = []
    for i, p in enumerate(pairs):
        body.append(
            f"--- PAIR {i} ---\nQUESTION: {p['q'][:600]}\nRESPONSE: {p['r'][:1500]}"
        )
    prompt = "\n\n".join(body) + "\n\nReturn JSON now."
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=2000,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(m.group(0)) if m else {"results": []}
    labels = ["NEITHER"] * len(pairs)
    for r in data.get("results", []):
        idx = r.get("pair_index")
        lab = (r.get("label") or "NEITHER").upper().strip()
        if isinstance(idx, int) and 0 <= idx < len(pairs):
            labels[idx] = lab if lab in ("NEED", "INSIGHT", "MIXED", "NEITHER") else "NEITHER"
    return labels, resp.usage.prompt_tokens, resp.usage.completion_tokens

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Process only N transcripts (0 = all)")
    parser.add_argument("--batch", type=int, default=12, help="Pairs per LLM call")
    parser.add_argument("--resume", action="store_true", help="Skip sessions already in the output JSONL")
    args = parser.parse_args()

    paths = load_transcripts()
    if args.limit:
        paths = paths[: args.limit]
    log.info(f"Discovered {len(paths)} transcripts (main+refinement+adversarial).")

    done = set()
    if args.resume and PER_SESSION.exists():
        with open(PER_SESSION) as f:
            for line in f:
                try:
                    done.add(json.loads(line)["session_id"])
                except Exception:
                    pass
        log.info(f"Resuming; {len(done)} sessions already classified.")

    open_mode = "a" if args.resume else "w"
    out = open(PER_SESSION, open_mode, encoding="utf-8")

    total_in = total_out = 0
    t0 = time.time()
    n_processed = 0
    n_skipped = 0
    n_failed = 0

    for i, (path, cohort) in enumerate(paths, 1):
        try:
            with open(path) as f:
                tr = json.load(f)
            sid = tr.get("session_id") or Path(path).stem
            if sid in done:
                n_skipped += 1
                continue
            version = tr.get("questionnaire_version")
            persona = tr.get("persona_id")
            stage = tr.get("persona_journey_stage")
            risk = tr.get("persona_risk_level")
            pairs = extract_pairs(tr)
            if not pairs:
                continue

            counts = {"NEED": 0, "INSIGHT": 0, "MIXED": 0, "NEITHER": 0}
            for k in range(0, len(pairs), args.batch):
                batch = pairs[k : k + args.batch]
                try:
                    labels, in_tok, out_tok = classify_batch(batch)
                    total_in += in_tok
                    total_out += out_tok
                except Exception as e:
                    log.warning(f"  batch error in {sid} @{k}: {e}")
                    labels = ["NEITHER"] * len(batch)
                for lab in labels:
                    counts[lab] = counts.get(lab, 0) + 1

            rec = {
                "session_id": sid,
                "version": version,
                "cohort": cohort,
                "persona_id": persona,
                "journey_stage": stage,
                "risk_level": risk,
                "n_pairs": len(pairs),
                "counts": counts,
            }
            out.write(json.dumps(rec) + "\n")
            out.flush()
            n_processed += 1

            if i % 10 == 0 or i == len(paths):
                elapsed = time.time() - t0
                rate = n_processed / max(elapsed, 1)
                eta = (len(paths) - i) / max(rate, 0.001)
                log.info(
                    f"[{i}/{len(paths)}] processed={n_processed} skipped={n_skipped} "
                    f"failed={n_failed} | in={total_in} out={total_out} | "
                    f"rate={rate:.2f}/s | eta={eta/60:.1f}min"
                )
        except Exception as e:
            n_failed += 1
            log.error(f"  fatal in {path}: {e}")
            continue

    out.close()
    log.info(
        f"Done. processed={n_processed} skipped={n_skipped} failed={n_failed} "
        f"total_input_tokens={total_in} total_output_tokens={total_out} "
        f"elapsed={(time.time()-t0)/60:.1f}min"
    )

    # Aggregate by version+cohort
    by_version = defaultdict(lambda: {"NEED": 0, "INSIGHT": 0, "MIXED": 0, "NEITHER": 0, "n_pairs": 0, "n_sessions": 0})
    overall = {"NEED": 0, "INSIGHT": 0, "MIXED": 0, "NEITHER": 0, "n_pairs": 0, "n_sessions": 0}
    cohort_suffix = {"main": "", "refinement": "_R", "adversarial": "_ADV"}
    with open(PER_SESSION) as f:
        for line in f:
            r = json.loads(line)
            cohort = r.get("cohort", "main")
            v = f"V{r['version']}{cohort_suffix.get(cohort, '')}"
            for k in ("NEED", "INSIGHT", "MIXED", "NEITHER"):
                by_version[v][k] += r["counts"].get(k, 0)
                overall[k] += r["counts"].get(k, 0)
            by_version[v]["n_pairs"] += r["n_pairs"]
            by_version[v]["n_sessions"] += 1
            overall["n_pairs"] += r["n_pairs"]
            overall["n_sessions"] += 1

    def pct(numer, denom):
        return 100.0 * numer / max(denom, 1)

    summary = {"by_version": {}, "overall": {}}
    for v, c in by_version.items():
        denom = c["NEED"] + c["INSIGHT"] + c["MIXED"]
        summary["by_version"][v] = {
            **c,
            "needs_pct": round(pct(c["NEED"], denom), 1),
            "insights_pct": round(pct(c["INSIGHT"], denom), 1),
            "mixed_pct": round(pct(c["MIXED"], denom), 1),
            "insights_to_needs_ratio": round(c["INSIGHT"] / max(c["NEED"], 1), 2),
        }
    denom = overall["NEED"] + overall["INSIGHT"] + overall["MIXED"]
    summary["overall"] = {
        **overall,
        "needs_pct": round(pct(overall["NEED"], denom), 1),
        "insights_pct": round(pct(overall["INSIGHT"], denom), 1),
        "mixed_pct": round(pct(overall["MIXED"], denom), 1),
        "insights_to_needs_ratio": round(overall["INSIGHT"] / max(overall["NEED"], 1), 2),
    }

    with open(PER_VERSION, "w") as f:
        json.dump(summary, f, indent=2)

    with open(SUMMARY_MD, "w") as f:
        f.write(f"# Needs vs Insights — Batch Classification\n\n")
        f.write(f"Generated: {datetime.utcnow().isoformat()}Z  \n")
        f.write(f"Model: `{PROVIDER}/{MODEL}`  \n")
        f.write(f"Sessions classified: {overall['n_sessions']}; total Q-R pairs: {overall['n_pairs']}\n\n")
        f.write(f"## Overall\n\n")
        f.write(f"- NEEDS: {overall['NEED']} ({summary['overall']['needs_pct']}%)\n")
        f.write(f"- INSIGHTS: {overall['INSIGHT']} ({summary['overall']['insights_pct']}%)\n")
        f.write(f"- MIXED: {overall['MIXED']} ({summary['overall']['mixed_pct']}%)\n")
        f.write(f"- NEITHER (off-topic / empty): {overall['NEITHER']}\n")
        f.write(f"- **Insights-to-Needs ratio: {summary['overall']['insights_to_needs_ratio']}**\n\n")
        f.write(f"## By version\n\n")
        f.write(f"| Version | Sessions | Q-R pairs | NEEDS | INSIGHTS | MIXED | I:N ratio |\n")
        f.write(f"|---|---|---|---|---|---|---|\n")
        for v in sorted(by_version.keys()):
            s = summary["by_version"][v]
            f.write(
                f"| {v} | {s['n_sessions']} | {s['n_pairs']} | "
                f"{s['NEED']} ({s['needs_pct']}%) | "
                f"{s['INSIGHT']} ({s['insights_pct']}%) | "
                f"{s['MIXED']} ({s['mixed_pct']}%) | "
                f"{s['insights_to_needs_ratio']} |\n"
            )

    log.info(f"Wrote {PER_VERSION} and {SUMMARY_MD}")

if __name__ == "__main__":
    main()

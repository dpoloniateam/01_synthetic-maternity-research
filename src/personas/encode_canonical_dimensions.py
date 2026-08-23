"""
Canonical-dimension encoding of the persona pool (development 5, 23 Aug 2026).

The March 2026 pool encodes nine latent-dimension names, five of which belong to the canonical twelve of
src.questionnaire.frameworks.LATENT_DIMENSIONS (a sixth, trust_distrust_providers, is an alias of trust_distrust).
Six canonical dimensions were therefore never encoded, and the judge — which is shown only the encoded names —
could never report them as surfaced: the "critical blind spots" of the paper were this artefact.

This script writes composites_v2.jsonl, keeping every original field and adding:
  latent_dimensions_canonical   — all twelve canonical names with a 0–1 salience value
  latent_dimensions_extra       — the three non-canonical names of the original encoding, preserved
  latent_dimensions_provenance  — per dimension: source (encoded | alias | heuristic), basis (flags, keywords, demographics)

Mode "heuristic" (default) derives the six missing dimensions deterministically from vulnerability flags,
demographics and keyword evidence in the persona narrative; it costs nothing and is fully auditable, but it is a
*reference for the judge*, not new persona content — the narratives are unchanged. Mode "llm" (Claude Opus 5,
structured output, ≈ USD 2 for 150 personas) is provided for the owner's decision and is not run by default.

    python -m src.personas.encode_canonical_dimensions --mode heuristic
"""
import json, argparse, re, sys, hashlib
from datetime import datetime
from pathlib import Path
from src.questionnaire.frameworks import LATENT_DIMENSIONS

CANON = list(LATENT_DIMENSIONS.keys())
ALIASES = {"trust_distrust_providers": "trust_distrust"}
KEYWORDS = {
    "dignity_respect": ["dismiss", "ignored", "rude", "respect", "judged", "talked down", "condescend", "humiliat", "listen to me", "treated like", "belittl", "dignity"],
    "continuity_of_care": ["different doctor", "different midwife", "handed over", "handover", "referral", "referred", "specialist", "transfer", "new provider", "rotating", "never the same", "continuity", "kept switching", "another clinic"],
    "partner_role": ["my partner", "my husband", "my wife", "my boyfriend", "the father", "he wasn't", "he was", "on my own", "alone", "by myself", "co-parent", "single"],
    "digital_information_seeking": ["app", "forum", "online", "google", "internet", "instagram", "facebook", "reddit", "tiktok", "youtube", "group chat", "whatsapp", "website", "searched", "scrolling"],
    "body_image_autonomy": ["my body", "weight", "scar", "stretch", "examination", "exam", "touch", "exposed", "naked", "gown", "speculum", "cervical check", "swollen", "mirror", "bodily", "consent"],
    "intergenerational_patterns": ["my mother", "my mom", "my mum", "grandmother", "my family", "tradition", "culture", "generation", "back home", "my aunt", "my sister had", "the way we do", "elders", "in my country"],
}
FLAG_WEIGHTS = {
    "dignity_respect": {"immigration": 0.2, "language_barrier": 0.2, "low_income": 0.15, "previous_trauma": 0.2, "mental_health": 0.1, "single_parent": 0.1},
    "continuity_of_care": {"rural_isolation": 0.2, "high_risk_medical": 0.25, "mental_health": 0.15, "immigration": 0.1, "previous_loss": 0.1},
    "partner_role": {"single_parent": 0.35, "low_social_support": 0.2},
    "digital_information_seeking": {"rural_isolation": 0.15, "language_barrier": 0.1},
    "body_image_autonomy": {"previous_trauma": 0.3, "fear_of_childbirth": 0.2, "high_risk_medical": 0.1},
    "intergenerational_patterns": {"immigration": 0.25, "language_barrier": 0.1, "previous_loss": 0.1},
}


def _clip(x):
    return round(max(0.0, min(1.0, x)), 2)


def heuristic_value(dim: str, persona: dict) -> tuple:
    text = (persona.get("enriched_narrative") or persona.get("attributes") or "")
    text = text.lower() if isinstance(text, str) else ""
    flags = set(persona.get("vulnerability_flags", []))
    demo = persona.get("demographics", {}) or {}
    basis = []
    v = 0.2  # every dimension has some baseline salience in maternity care
    for f, w in FLAG_WEIGHTS.get(dim, {}).items():
        if f in flags:
            v += w; basis.append(f"flag:{f}")
    hits = [k for k in KEYWORDS.get(dim, []) if k in text]
    v += 0.08 * min(len(hits), 5)
    if hits:
        basis.append("keywords:" + ",".join(hits[:5]))
    if dim == "partner_role":
        ms = str(demo.get("marital_status", "")).lower()
        if ms in ("married", "partnered", "cohabiting"):
            v += 0.15; basis.append(f"marital_status:{ms}")
        elif ms:
            v += 0.1; basis.append(f"marital_status:{ms}")
    if dim == "digital_information_seeking":
        age = demo.get("age")
        if isinstance(age, (int, float)):
            if age < 30: v += 0.2; basis.append(f"age:{age}")
            elif age < 38: v += 0.1; basis.append(f"age:{age}")
    if dim == "intergenerational_patterns":
        age = demo.get("age")
        if isinstance(age, (int, float)) and age < 25:
            v += 0.1; basis.append(f"age:{age}")
    return _clip(v), basis


def encode(persona: dict) -> dict:
    p = dict(persona)
    orig = persona.get("latent_dimensions", {}) or {}
    canon, prov, extra = {}, {}, {}
    for name, val in orig.items():
        if name in CANON:
            canon[name] = val; prov[name] = {"source": "encoded", "basis": ["march-2026 pool"]}
        elif name in ALIASES:
            canon[ALIASES[name]] = val; prov[ALIASES[name]] = {"source": "alias", "basis": [f"{name} → {ALIASES[name]}"]}
        else:
            extra[name] = val
    for dim in CANON:
        if dim not in canon:
            v, basis = heuristic_value(dim, persona)
            canon[dim] = v; prov[dim] = {"source": "heuristic", "basis": basis}
    p["latent_dimensions_canonical"] = {d: canon[d] for d in CANON}
    p["latent_dimensions_extra"] = extra
    p["latent_dimensions_provenance"] = prov
    p["encoding_method"] = "heuristic_v1"
    p["encoding_date"] = datetime.now().strftime("%Y-%m-%d")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/composite_personas/composites.jsonl")
    ap.add_argument("--output", default="data/composite_personas/composites_v2.jsonl")
    ap.add_argument("--mode", choices=["heuristic", "llm"], default="heuristic")
    a = ap.parse_args()
    if a.mode == "llm":
        sys.exit("LLM mode is a decision for the owner (≈ USD 2 on Claude Opus 5); not run by default.")
    recs = [json.loads(l) for l in open(a.input, encoding="utf-8") if l.strip()]
    out = [encode(r) for r in recs]
    with open(a.output, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # provenance note
    src_counts = {}
    for r in out:
        for d, pv in r["latent_dimensions_provenance"].items():
            src_counts.setdefault(d, {}).setdefault(pv["source"], 0); src_counts[d][pv["source"]] += 1
    means = {d: round(sum(r["latent_dimensions_canonical"][d] for r in out) / len(out), 2) for d in CANON}
    note = Path(a.output).with_name(f"ENCODING_PROVENANCE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(note, "w", encoding="utf-8") as f:
        f.write(f"# Canonical-dimension encoding — {a.mode} — {datetime.now():%d %B %Y, %H:%M}\n\n")
        f.write(f"Input `{a.input}` ({len(recs)} personas, sha256 {hashlib.sha256(open(a.input,'rb').read()).hexdigest()[:16]}…) → `{a.output}`.\n\n")
        f.write("| Dimension | Source counts | Mean salience |\n|---|---|---|\n")
        for d in CANON:
            f.write(f"| {d} | {src_counts[d]} | {means[d]} |\n")
        f.write("\nHeuristic rules: baseline 0.2; vulnerability-flag weights and narrative keyword hits (0.08 each, max five) per dimension as in `FLAG_WEIGHTS` and `KEYWORDS`; marital status and age for partner_role / digital_information_seeking / intergenerational_patterns. The narratives are unchanged: these values are the judge's reference for what each persona *could* surface, not new persona content. Decision point for the authors: accept the heuristic reference, run the LLM mode, or re-derive the pool.\n")
    print(f"wrote {a.output} ({len(out)} personas) and {note.name}")
    print("source counts:", {d: src_counts[d] for d in CANON})


if __name__ == "__main__":
    main()

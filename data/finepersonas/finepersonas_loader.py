"""
FinePersonas Maternity Filter
==============================
Loads argilla/FinePersonas-v0.1-clustering-100k from HuggingFace,
filters for maternity/pregnancy-relevant personas using tiered keyword
matching and optional LLM-based semantic scoring, then exports results.

Usage:
    python -m src.ingestion.finepersonas_loader           # keyword filter only
    python -m src.ingestion.finepersonas_loader --llm      # + LLM relevance scoring
    python -m src.ingestion.finepersonas_loader --full      # use full 21M dataset (slow)
"""

import os
import re
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
log = logging.getLogger(__name__)

# ─── Keyword tiers ────────────────────────────────────────────────────────────
# Tier 1: Direct pregnancy/maternity terms (highest relevance)
TIER1_KEYWORDS = [
    r"\bpregnan\w*\b", r"\bmaternit\w*\b", r"\bobstetric\w*\b",
    r"\bmidwi\w*\b", r"\bprenatal\b", r"\bantenatal\b", r"\bpostnatal\b",
    r"\bpostpartum\b", r"\bneonatal\b", r"\bperinatal\b", r"\bchildbirth\b",
    r"\blabou?r\b(?!.*market)", r"\bdelivery\b(?!.*service|.*driver|.*food)",
    r"\bbreastfeed\w*\b", r"\bnursing mother\b", r"\bdoula\b",
    r"\bfertility\b", r"\bivf\b", r"\bconception\b", r"\bmiscarriage\b",
    r"\bstillbirth\b", r"\bc-section\b", r"\bcaesarean\b", r"\bcesarean\b",
    r"\btrimester\b", r"\bgestational\b", r"\bpreeclampsia\b",
    r"\beclampsia\b", r"\bepidural\b", r"\binduction\b(?!.*magnet)",
    r"\bnewborn\b", r"\binfant\b(?!.*ry)", r"\bbirth\s*plan\b",
    r"\bmorning sickness\b", r"\bhyperemesis\b",
]

# Tier 2: Healthcare/caregiving contexts that often overlap maternity
TIER2_KEYWORDS = [
    r"\bnurse\b", r"\bnursing\b(?!.*home)", r"\bhealthcare\b",
    r"\bpatient care\b", r"\bclinical\b", r"\bpediatric\w*\b",
    r"\bgynecolog\w*\b", r"\breproductive\b", r"\bwomen'?s health\b",
    r"\bfamily planning\b", r"\bparent\w*\b", r"\bmother\w*\b",
    r"\bchild\s*care\b", r"\binfant care\b", r"\bbaby\b",
    r"\bsocial work\w*\b", r"\bmental health\b(?!.*app)",
    r"\bcounsell?or\b", r"\btherapist\b", r"\bpsycholog\w*\b",
    r"\bdomestic\b", r"\bcaregiv\w*\b",
]

# Tier 3: Broader service/experience contexts relevant to maternity research
TIER3_KEYWORDS = [
    r"\bservice quality\b", r"\bpatient experience\b",
    r"\bpatient satisfaction\b", r"\bhospital\b", r"\bclinic\b",
    r"\bhealth system\b", r"\bprimary care\b", r"\bpublic health\b",
    r"\bhealth equity\b", r"\bhealth disparit\w*\b",
    r"\bvulnerab\w*\b", r"\bstigma\b", r"\btrauma\b",
    r"\bdomestic violence\b", r"\babuse\b",
    r"\blow.income\b", r"\bpoverty\b", r"\brural\b",
    r"\bimmigra\w*\b", r"\brefugee\b", r"\bethnicit\w*\b",
]


def compile_patterns(keyword_list):
    """Pre-compile regex patterns for performance."""
    return [re.compile(kw, re.IGNORECASE) for kw in keyword_list]


TIER1_PATTERNS = compile_patterns(TIER1_KEYWORDS)
TIER2_PATTERNS = compile_patterns(TIER2_KEYWORDS)
TIER3_PATTERNS = compile_patterns(TIER3_KEYWORDS)


def score_persona(text: str) -> dict:
    """
    Score a persona description against the keyword tiers.
    Returns a dict with tier scores and total weighted score.
    
    Scoring logic:
      - Each Tier 1 match: +10 points
      - Each Tier 2 match: +3 points  
      - Each Tier 3 match: +1 point
      - Minimum threshold for inclusion: 10 (at least one Tier 1 match)
        OR 6+ from Tier 2 matches (two+ healthcare terms)
    """
    t1_matches = [p.pattern for p in TIER1_PATTERNS if p.search(text)]
    t2_matches = [p.pattern for p in TIER2_PATTERNS if p.search(text)]
    t3_matches = [p.pattern for p in TIER3_PATTERNS if p.search(text)]
    
    t1_score = len(t1_matches) * 10
    t2_score = len(t2_matches) * 3
    t3_score = len(t3_matches) * 1
    total = t1_score + t2_score + t3_score
    
    return {
        "total_score": total,
        "tier1_score": t1_score,
        "tier2_score": t2_score,
        "tier3_score": t3_score,
        "tier1_matches": t1_matches,
        "tier2_matches": t2_matches,
        "tier3_matches": t3_matches,
    }


def classify_relevance(score_dict: dict) -> str:
    """Classify persona into relevance category."""
    total = score_dict["total_score"]
    t1 = score_dict["tier1_score"]
    
    if t1 >= 20:  # 2+ direct pregnancy terms
        return "DIRECT_MATERNITY"
    elif t1 >= 10:  # 1 direct pregnancy term
        return "MATERNITY_ADJACENT"
    elif total >= 9:  # Strong healthcare/caregiving context
        return "HEALTHCARE_CONTEXT"
    elif total >= 6:  # Moderate service/vulnerability context
        return "SERVICE_CONTEXT"
    else:
        return "NOT_RELEVANT"


def load_finepersonas(use_full_dataset: bool = False):
    """
    Load FinePersonas from HuggingFace.
    Default: 100k clustering subset (fast, ~200MB)
    Full: 21M+ personas (~143GB with embeddings)
    """
    from datasets import load_dataset
    
    token = os.environ.get("HUGGINGFACE_API_KEY")
    
    if use_full_dataset:
        log.info("Loading FULL FinePersonas-v0.1 dataset (21M+ personas)...")
        log.info("This will take several minutes and significant disk space.")
        ds = load_dataset(
            "argilla/FinePersonas-v0.1",
            split="train",
            token=token,
            streaming=True,  # Stream to avoid loading all into RAM
        )
        return ds, "full"
    else:
        log.info("Loading FinePersonas-v0.1-clustering-100k subset...")
        ds = load_dataset(
            "argilla/FinePersonas-v0.1-clustering-100k",
            split="train",
            token=token,
        )
        log.info(f"Loaded {len(ds)} personas from 100k subset.")
        return ds, "100k"


def filter_maternity_personas(dataset, dataset_type: str = "100k",
                               min_score: int = 6, max_streaming: int = 500000):
    """
    Filter dataset for maternity-relevant personas.
    
    For the 100k subset: iterate all rows.
    For the full dataset (streaming): iterate up to max_streaming rows.
    """
    results = {
        "DIRECT_MATERNITY": [],
        "MATERNITY_ADJACENT": [],
        "HEALTHCARE_CONTEXT": [],
        "SERVICE_CONTEXT": [],
    }
    
    total_scanned = 0
    total_matched = 0
    
    log.info("Scanning personas for maternity relevance...")
    
    iterable = dataset if dataset_type == "full" else dataset
    
    for i, row in enumerate(iterable):
        persona_text = row.get("persona", "")
        if not persona_text:
            continue
            
        total_scanned += 1
        
        scores = score_persona(persona_text)
        
        if scores["total_score"] >= min_score:
            category = classify_relevance(scores)
            if category != "NOT_RELEVANT":
                total_matched += 1
                entry = {
                    "finepersona_id": row.get("id", f"FP_{i:06d}"),
                    "persona": persona_text,
                    "cluster_label": row.get("label", row.get("labels", "unknown")),
                    "relevance_category": category,
                    "scores": scores,
                }
                results[category].append(entry)
        
        if total_scanned % 10000 == 0:
            log.info(f"  Scanned {total_scanned:,} | Matched {total_matched:,} "
                     f"(T1:{len(results['DIRECT_MATERNITY'])} "
                     f"T2:{len(results['MATERNITY_ADJACENT'])} "
                     f"HC:{len(results['HEALTHCARE_CONTEXT'])} "
                     f"SC:{len(results['SERVICE_CONTEXT'])})")
        
        if dataset_type == "full" and total_scanned >= max_streaming:
            log.info(f"Reached streaming limit ({max_streaming:,}). Stopping.")
            break
    
    log.info(f"\n{'='*60}")
    log.info(f"SCAN COMPLETE")
    log.info(f"  Total scanned:     {total_scanned:,}")
    log.info(f"  Total matched:     {total_matched:,}")
    log.info(f"  DIRECT_MATERNITY:  {len(results['DIRECT_MATERNITY'])}")
    log.info(f"  MATERNITY_ADJACENT:{len(results['MATERNITY_ADJACENT'])}")
    log.info(f"  HEALTHCARE_CONTEXT:{len(results['HEALTHCARE_CONTEXT'])}")
    log.info(f"  SERVICE_CONTEXT:   {len(results['SERVICE_CONTEXT'])}")
    log.info(f"{'='*60}\n")
    
    return results


def llm_relevance_score(personas: list, batch_size: int = 20) -> list:
    """
    Use Claude Haiku to score filtered personas for maternity-care
    research relevance (0-10 scale). Cost-efficient second pass.
    """
    import anthropic
    
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    scored = []
    
    log.info(f"Running LLM relevance scoring on {len(personas)} personas (batch_size={batch_size})...")
    
    for batch_start in range(0, len(personas), batch_size):
        batch = personas[batch_start:batch_start + batch_size]
        
        persona_list = "\n".join(
            f"[{i}] {p['persona']}" for i, p in enumerate(batch)
        )
        
        prompt = f"""You are evaluating persona descriptions for their relevance to maternity-care 
user research. We need personas that could realistically represent pregnant women, new mothers, 
maternity healthcare providers, or individuals with direct experience of maternity services.

Score each persona 0-10:
- 9-10: Directly represents a pregnant woman, new mother, or maternity patient
- 7-8: Maternity healthcare professional (midwife, OB-GYN, nurse in maternity)
- 5-6: Healthcare/social care professional who regularly encounters pregnant women
- 3-4: General healthcare or social context tangentially related to maternity
- 0-2: Not relevant to maternity-care research

Respond ONLY as a JSON array of objects: [{{"index": 0, "score": 8, "rationale": "brief reason"}}]

Personas:
{persona_list}"""

        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            
            text = response.content[0].text.strip()
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                scores = json.loads(json_match.group())
                for s in scores:
                    idx = s["index"]
                    if 0 <= idx < len(batch):
                        batch[idx]["llm_score"] = s["score"]
                        batch[idx]["llm_rationale"] = s.get("rationale", "")
                        scored.append(batch[idx])
            
            log.info(f"  Scored batch {batch_start//batch_size + 1}/"
                     f"{(len(personas)-1)//batch_size + 1}")
                     
        except Exception as e:
            log.error(f"  LLM scoring failed for batch at {batch_start}: {e}")
            # Keep personas without LLM score
            for p in batch:
                p["llm_score"] = -1
                p["llm_rationale"] = f"scoring_error: {str(e)}"
                scored.append(p)
    
    return scored


def export_results(results: dict, output_dir: str, with_llm: bool = False):
    """Export filtered personas to JSONL and summary files."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Combine all categories into a single list, sorted by score
    all_personas = []
    for category, personas in results.items():
        all_personas.extend(personas)
    
    all_personas.sort(key=lambda x: x.get("llm_score", x["scores"]["total_score"]),
                      reverse=True)
    
    # Export JSONL (one persona per line)
    jsonl_path = out / f"maternity_personas_{timestamp}.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for p in all_personas:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    
    log.info(f"Exported {len(all_personas)} personas to {jsonl_path}")
    
    # Export summary
    summary = {
        "timestamp": timestamp,
        "total_personas": len(all_personas),
        "by_category": {cat: len(personas) for cat, personas in results.items()},
        "llm_scored": with_llm,
        "top_10_examples": [
            {"persona": p["persona"][:200], "category": p["relevance_category"],
             "score": p.get("llm_score", p["scores"]["total_score"])}
            for p in all_personas[:10]
        ],
    }
    
    summary_path = out / f"filter_summary_{timestamp}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    log.info(f"Summary written to {summary_path}")
    
    # Also export a stable reference file (overwritten each run)
    stable_path = out / "maternity_personas.jsonl"
    with open(stable_path, "w", encoding="utf-8") as f:
        for p in all_personas:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    
    log.info(f"Stable reference file: {stable_path}")
    
    return all_personas


def main():
    parser = argparse.ArgumentParser(description="FinePersonas Maternity Filter")
    parser.add_argument("--full", action="store_true",
                        help="Use full 21M dataset (streaming, slow)")
    parser.add_argument("--llm", action="store_true",
                        help="Add LLM-based relevance scoring (costs ~$0.50)")
    parser.add_argument("--min-score", type=int, default=6,
                        help="Minimum keyword score threshold (default: 6)")
    parser.add_argument("--output", type=str,
                        default="data/finepersonas",
                        help="Output directory")
    parser.add_argument("--llm-min-score", type=int, default=5,
                        help="Minimum LLM score to keep (default: 5)")
    
    args = parser.parse_args()
    
    # Step 1: Load dataset
    dataset, dtype = load_finepersonas(use_full_dataset=args.full)
    
    # Step 2: Keyword filtering
    results = filter_maternity_personas(dataset, dtype, min_score=args.min_score)
    
    # Step 3: Optional LLM scoring
    if args.llm:
        # Combine all matched personas for LLM scoring
        all_matched = []
        for category, personas in results.items():
            all_matched.extend(personas)
        
        scored = llm_relevance_score(all_matched)
        
        # Re-categorise by LLM score and filter out low-relevance
        results_llm = {
            "DIRECT_MATERNITY": [],
            "MATERNITY_ADJACENT": [],
            "HEALTHCARE_CONTEXT": [],
            "SERVICE_CONTEXT": [],
        }
        
        for p in scored:
            if p.get("llm_score", 0) >= args.llm_min_score:
                if p["llm_score"] >= 9:
                    results_llm["DIRECT_MATERNITY"].append(p)
                elif p["llm_score"] >= 7:
                    results_llm["MATERNITY_ADJACENT"].append(p)
                elif p["llm_score"] >= 5:
                    results_llm["HEALTHCARE_CONTEXT"].append(p)
                else:
                    results_llm["SERVICE_CONTEXT"].append(p)
        
        results = results_llm
        log.info(f"After LLM filtering (min_score={args.llm_min_score}):")
        for cat, personas in results.items():
            log.info(f"  {cat}: {len(personas)}")
    
    # Step 4: Export
    all_personas = export_results(results, args.output, with_llm=args.llm)
    
    # Step 5: Print sample
    log.info("\n--- TOP 5 PERSONAS ---")
    for p in all_personas[:5]:
        score = p.get("llm_score", p["scores"]["total_score"])
        log.info(f"  [{p['relevance_category']}] (score={score}) "
                 f"{p['persona'][:120]}...")
    
    return all_personas


if __name__ == "__main__":
    main()

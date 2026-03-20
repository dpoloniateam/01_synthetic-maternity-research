"""
FinePersonas Maternity Filter
Usage:
    python -m src.ingestion.finepersonas_loader
    python -m src.ingestion.finepersonas_loader --llm
"""
import os, re, json, argparse, logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

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

def compile_patterns(kws): return [re.compile(k, re.IGNORECASE) for k in kws]
T1P = compile_patterns(TIER1_KEYWORDS)
T2P = compile_patterns(TIER2_KEYWORDS)
T3P = compile_patterns(TIER3_KEYWORDS)

def score_persona(text):
    t1 = [p.pattern for p in T1P if p.search(text)]
    t2 = [p.pattern for p in T2P if p.search(text)]
    t3 = [p.pattern for p in T3P if p.search(text)]
    return {"total_score": len(t1)*10+len(t2)*3+len(t3)*1, "tier1_score": len(t1)*10, "tier2_score": len(t2)*3, "tier3_score": len(t3)*1, "tier1_matches": t1, "tier2_matches": t2, "tier3_matches": t3}

def classify_relevance(sd):
    if sd["tier1_score"] >= 20: return "DIRECT_MATERNITY"
    elif sd["tier1_score"] >= 10: return "MATERNITY_ADJACENT"
    elif sd["total_score"] >= 9: return "HEALTHCARE_CONTEXT"
    elif sd["total_score"] >= 6: return "SERVICE_CONTEXT"
    return "NOT_RELEVANT"

def load_finepersonas(use_full=False):
    from datasets import load_dataset
    token = os.environ.get("HUGGINGFACE_API_KEY")
    if use_full:
        log.info("Loading FULL FinePersonas-v0.1 (21M+, streaming)...")
        ds = load_dataset("argilla/FinePersonas-v0.1", split="train", token=token, streaming=True)
        return ds, "full"
    else:
        log.info("Loading FinePersonas-v0.1-clustering-100k...")
        ds = load_dataset("argilla/FinePersonas-v0.1-clustering-100k", split="train", token=token)
        log.info(f"Loaded {len(ds)} personas.")
        return ds, "100k"

def filter_maternity_personas(dataset, dtype="100k", min_score=6, max_stream=500000):
    results = {"DIRECT_MATERNITY": [], "MATERNITY_ADJACENT": [], "HEALTHCARE_CONTEXT": [], "SERVICE_CONTEXT": []}
    total_scanned, total_matched = 0, 0
    log.info("Scanning personas for maternity relevance...")
    for i, row in enumerate(dataset):
        text = row.get("persona", "")
        if not text: continue
        total_scanned += 1
        scores = score_persona(text)
        if scores["total_score"] >= min_score:
            cat = classify_relevance(scores)
            if cat != "NOT_RELEVANT":
                total_matched += 1
                entry = {"finepersona_id": row.get("id", f"FP_{i:06d}"), "persona": text, "cluster_label": row.get("label", row.get("labels", "unknown")), "relevance_category": cat, "scores": scores}
                results[cat].append(entry)
        if total_scanned % 10000 == 0:
            log.info(f"  Scanned {total_scanned:,} | Matched {total_matched:,} (T1:{len(results['DIRECT_MATERNITY'])} T2:{len(results['MATERNITY_ADJACENT'])} HC:{len(results['HEALTHCARE_CONTEXT'])} SC:{len(results['SERVICE_CONTEXT'])})")
        if dtype == "full" and total_scanned >= max_stream: break
    log.info(f"\n{'='*60}")
    log.info(f"SCAN COMPLETE: scanned={total_scanned:,} matched={total_matched:,}")
    for k,v in results.items(): log.info(f"  {k}: {len(v)}")
    log.info(f"{'='*60}\n")
    return results

def llm_relevance_score(personas, batch_size=20):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    scored = []
    log.info(f"LLM scoring {len(personas)} personas...")
    for bs in range(0, len(personas), batch_size):
        batch = personas[bs:bs+batch_size]
        pl = "\n".join(f"[{i}] {p['persona']}" for i,p in enumerate(batch))
        prompt = f"""Score each persona 0-10 for maternity-care research relevance:
9-10: Directly a pregnant woman/new mother/maternity patient
7-8: Maternity healthcare professional
5-6: Healthcare/social care with pregnant women exposure
3-4: Tangentially related
0-2: Not relevant
Respond ONLY as JSON array: [{{"index":0,"score":8,"rationale":"brief"}}]

Personas:
{pl}"""
        try:
            r = client.messages.create(model="claude-3-haiku-20240307", max_tokens=2000, messages=[{"role":"user","content":prompt}])
            text = r.content[0].text.strip()
            jm = re.search(r'\[.*\]', text, re.DOTALL)
            if jm:
                for s in json.loads(jm.group()):
                    idx = s["index"]
                    if 0 <= idx < len(batch):
                        batch[idx]["llm_score"] = s["score"]
                        batch[idx]["llm_rationale"] = s.get("rationale","")
                        scored.append(batch[idx])
            log.info(f"  Batch {bs//batch_size+1}/{(len(personas)-1)//batch_size+1}")
        except Exception as e:
            log.error(f"  LLM error at {bs}: {e}")
            for p in batch: p["llm_score"]=-1; p["llm_rationale"]=str(e); scored.append(p)
    return scored

def export_results(results, output_dir, with_llm=False):
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    all_p = []
    for cat, personas in results.items(): all_p.extend(personas)
    all_p.sort(key=lambda x: x.get("llm_score", x["scores"]["total_score"]), reverse=True)
    stable = out / "maternity_personas.jsonl"
    with open(stable, "w", encoding="utf-8") as f:
        for p in all_p: f.write(json.dumps(p, ensure_ascii=False)+"\n")
    log.info(f"Exported {len(all_p)} personas to {stable}")
    summary = {"timestamp": ts, "total_personas": len(all_p), "by_category": {c:len(v) for c,v in results.items()}, "llm_scored": with_llm, "top_10": [{"persona":p["persona"][:200],"category":p["relevance_category"],"score":p.get("llm_score",p["scores"]["total_score"])} for p in all_p[:10]]}
    sp = out / f"filter_summary_{ts}.json"
    with open(sp, "w", encoding="utf-8") as f: json.dump(summary, f, indent=2, ensure_ascii=False)
    log.info(f"Summary: {sp}")
    return all_p

def main():
    parser = argparse.ArgumentParser(description="FinePersonas Maternity Filter")
    parser.add_argument("--full", action="store_true", help="Use full 21M dataset")
    parser.add_argument("--llm", action="store_true", help="Add LLM scoring (~$0.50)")
    parser.add_argument("--min-score", type=int, default=6)
    parser.add_argument("--output", type=str, default="data/finepersonas")
    parser.add_argument("--llm-min-score", type=int, default=5)
    args = parser.parse_args()
    dataset, dtype = load_finepersonas(use_full=args.full)
    results = filter_maternity_personas(dataset, dtype, min_score=args.min_score)
    if args.llm:
        all_m = []
        for cat, personas in results.items(): all_m.extend(personas)
        scored = llm_relevance_score(all_m)
        results = {"DIRECT_MATERNITY":[], "MATERNITY_ADJACENT":[], "HEALTHCARE_CONTEXT":[], "SERVICE_CONTEXT":[]}
        for p in scored:
            if p.get("llm_score",0) >= args.llm_min_score:
                if p["llm_score"]>=9: results["DIRECT_MATERNITY"].append(p)
                elif p["llm_score"]>=7: results["MATERNITY_ADJACENT"].append(p)
                elif p["llm_score"]>=5: results["HEALTHCARE_CONTEXT"].append(p)
                else: results["SERVICE_CONTEXT"].append(p)
    all_p = export_results(results, args.output, with_llm=args.llm)
    log.info("\n--- TOP 5 PERSONAS ---")
    for p in all_p[:5]:
        sc = p.get("llm_score", p["scores"]["total_score"])
        log.info(f"  [{p['relevance_category']}] (score={sc}) {p['persona'][:120]}...")
    return all_p

if __name__ == "__main__":
    main()

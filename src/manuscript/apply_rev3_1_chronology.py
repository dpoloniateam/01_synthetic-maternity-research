"""apply_rev3_1_chronology.py — rev3.1: corrects the account of the consolidation step in the rev3 manuscript.

The record (annex of 9 May 2026; audit of 23 April 2026; `consolidate_guide.py` docstring of 2 June 2026) shows that
the twelve-question guide was the research team's manual selection from V4_R1 made in April–May 2026, and that the
deterministic set-cover procedure was constructed afterwards to give that selection an explicit rule; rev3 had the
order reversed. Three edits: the §4.4 consolidation paragraph, Table 7 row 6, and one sentence of §4.7.
"""
import sys, json, hashlib
from pathlib import Path
from docx import Document
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.manuscript.apply_rev3_restatement import find_par, find_table, set_par_text

EDITS = [
 dict(id="E21a", section="4.4", kind="para", prefix="A final consolidation step then reduced",
  new="A final consolidation step then reduced the longer instrument — 40 questions, 32 of them populated with probes — to twelve core questions. The research team made the selection by manual review in April–May 2026, choosing for each journey phase the items that together covered the phase and the dimensions flagged by the original diagnostics, merging overlapping items, dropping highly specific ones in favour of broader applicability, excluding probes judged intrusive or potentially biasing, and adjusting sequence and tone so that more concrete, less sensitive issues appeared earlier and more emotionally demanding topics later, with an introductory section added to establish rapport and empathy before delicate matters were raised. A deterministic, reproducible multi-criteria set-cover procedure was then constructed, in June 2026, to give the selection an explicit rule: applying the version-comparison weights (quality 0.40, coverage 0.25, innovation relevance 0.20, breadth 0.15) under hard constraints — three questions per journey phase, all twelve canonical latent dimensions covered by the items’ design targets, intrusive or biasing items excluded — it selects twelve items that preserve 100% of the targeted latent-dimension coverage at essentially constant mean composite richness (from 2.83 to 2.82). Five of its twelve items coincide with the team’s selection; the other seven differ, because the team weighted journey coverage and the flagged dimensions above measured richness where the two conflicted. The item-by-item correspondence and the rationale for each choice are recorded in the reproducibility package.",
  basis="Record of April–June 2026: annex_1.md (9 May), AUDITORIA_REV_230426.md, consolidate_guide.py docstring (2 June); TABLE_A_PROVENANCE.md v2"),
 dict(id="E36.6.1a", section="Table 7", kind="cell", header="What is included in the study", row=6, col=1,
  new="38 rule-typed changes, not administered in the re-administration round (implementation defects); researcher consolidation of the 32 populated items to 12 (April–May 2026), given an explicit rule afterwards by a deterministic set-cover that reproduces five of the twelve", basis="as E21a"),
 dict(id="E34a", section="4.7", kind="sub", prefix="These capability elements can be specified",
  old="consolidation applied a deterministic set-cover procedure under explicit constraints followed by documented researcher revision",
  new="consolidation was a documented researcher selection of twelve items, given an explicit rule afterwards by a deterministic set-cover procedure that reproduces five of them", basis="as E21a"),
]

def apply(doc):
    log=[]
    for e in EDITS:
        if e["kind"]=="para":
            p=find_par(doc, e["prefix"]); old=p.text; set_par_text(p, e["new"]); log.append((e["id"], e["section"], e["basis"], old, e["new"]))
        elif e["kind"]=="cell":
            t=find_table(doc, e["header"]); c=t.rows[e["row"]].cells[e["col"]]; old=c.text; set_par_text(c.paragraphs[0], e["new"]); log.append((e["id"], e["section"], e["basis"], old, e["new"]))
        elif e["kind"]=="sub":
            p=find_par(doc, e["prefix"]); assert p.text.count(e["old"])==1, e["id"]
            done=False
            for r in p.runs:
                if e["old"] in r.text: r.text=r.text.replace(e["old"], e["new"]); done=True; break
            if not done: set_par_text(p, p.text.replace(e["old"], e["new"]))
            log.append((e["id"], e["section"], e["basis"], e["old"], e["new"]))
    return log

def main():
    src=Path(sys.argv[1]); out=Path(sys.argv[2]); r3=sys.argv[3]; ts=sys.argv[4]; logs={}
    for s,d in [(f"Technovation_Anonymized_Manuscript_rev3_{r3}.docx", f"Technovation_Anonymized_Manuscript_rev3_1_{ts}.docx"), (f"Technovation_Manuscript_with_Authors_rev3_{r3}.docx", f"Technovation_Manuscript_with_Authors_rev3_1_{ts}.docx")]:
        doc=Document(src/s); logs[d]=apply(doc); doc.save(out/d); print(d, len(logs[d]), "edits")
    json.dump(logs, open(out/f"_edits_applied_rev3_1_{ts}.json","w",encoding="utf8"), ensure_ascii=False, indent=1)

if __name__=="__main__": main()

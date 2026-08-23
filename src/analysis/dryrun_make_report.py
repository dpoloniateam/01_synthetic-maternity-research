"""Build the dry-run 2 report (markdown) from the run directory: sessions, costs, judge panel, budget extrapolation, paper changes."""
import json, sys, collections, statistics
from pathlib import Path
from datetime import datetime
run = Path(sys.argv[1]); out_md = Path(sys.argv[2]); now = datetime.now().strftime("%d %B %Y, %H:%M WEST")
A = json.load(open(sys.argv[3]))     # analysis json (re-generated after the judge re-run)
R = [json.loads(l) for l in open(run / "requests.jsonl", encoding="utf-8")]
EURUSD = 1.10
sess = A["sessions"]; bym = A["by_model"]; bys = A["by_stage"]
persona_usd = bys.get("persona", {}).get("usd", 0); judge_usd = sum(v["usd"] for k, v in bys.items() if k.startswith("judge"))
legacy_est = 0.15
total_usd = A["total_usd"]
vc = A["voice_session_cost_mean"]
# judge per pair
judge_calls = sum(v["calls"] for k, v in bys.items() if k.startswith("judge")); pairs = A["judged_pairs"]
judge_per_pair = judge_usd / pairs if pairs else 0
# --- extrapolation
N_MAIN, N_READMIN, N_ADV = 300, 50, 5; N = N_MAIN + N_READMIN + N_ADV
split = {"openai/gpt-5.6-sol": 118, "anthropic/claude-opus-5": 118, "google/gemini-3.1-pro-preview": 119}
persona_full = sum(split[v] * vc.get(v, 0) for v in split)
readmin_uplift = N_READMIN * statistics.mean(vc.values()) * 0.30   # V4_R1 now administers ~30% more questions to birth/postpartum personas
pairs_per_session = pairs / max(len(sess), 1)
judge_full = N * pairs_per_session * judge_per_pair
judge_full_batch = judge_full * 0.5
other = {"classifier (Sol, Batch)": 11, "service mapping (Gemini 3.1 Pro, Batch)": 5, "generation + refinement (Fable 5)": 5, "narratives (Gemini, Batch)": 1, "inter-rater (3 × 30)": 1}
other_sum = sum(other.values())
pilot = 30 * statistics.mean(vc.values()) * 3 + 30 * pairs_per_session * judge_per_pair * 3 * 0.5
full_opt = persona_full + readmin_uplift + judge_full_batch + other_sum
full_list = persona_full + readmin_uplift + judge_full + other_sum
dur = [s["duration_s"] for s in sess]; mean_dur = statistics.mean(dur)
hours_seq = N * mean_dur / 3600
L = [f"# Dry run 2 — results, costs, full-run budget and consequences for the manuscript (v01, {now})", "",
f"**Run.** `{run}` — arm **P** of `config/experiment.yaml` (fingerprint 9a07bae6…): voices GPT-5.6 Sol (Flex), Claude Opus 5 (prompt caching), Gemini 3.1 Pro (thinking budget 4,096); judges Gemini 3.1 Pro and Claude Opus 5 with structured outputs; six full sessions (two per voice, personas comp_038, comp_141, comp_011; versions V1 and V2); persona pool v2 (canonical twelve). Every model call is in `requests.jsonl` ({len(R)} records) with served snapshot, request id, finish reason, tokens and cost at list prices; `manifest.json` carries the git commit, SDK versions and the configuration fingerprint.",
"",
"## 1. What happened",
"",
"| Event | Outcome |",
"|---|---|",
"| Sessions | 6 of 6 completed; **0 empty and 0 truncated persona answers** in 155 persona calls (the March run had 25% empties) |",
"| Hang | the first Gemini session stalled at 11:38 on a request that never returned; the process was stopped at 11:59, per-call timeouts (180 s, `SDL_CALL_TIMEOUT_S`) added to every client, and the run **resumed in the same directory**: five sessions skipped as completed, the sixth re-run, prior spend preloaded into the meter |",
"| Judge stage, first pass | the scorer fell through to the March single judge (gemini-3-flash, old SDK) because the panel patch had not applied; 138 pairs scored **outside the provenance cache** (≈ USD 0.15 unmetered, estimated from 14 calls); the records are preserved as `quality_scores_LEGACY_gemini-3-flash_unmetered.jsonl` and excluded from the results below |",
"| Judge stage, second pass | panel path asserted into the scorer (a panel failure is now an error, not a fallback); Gemini 3.1 Pro + Opus 5 re-scored the 138 pairs with structured outputs — results in §3 |",
"",
"## 2. Sessions and persona-stage costs",
"",
"| Session | Voice | V | Turns | Q + P | Words/answer | Tokens in / out | Cached in | Duration | USD |",
"|---|---|---|---|---|---|---|---|---|---|"]
cached_by_session = collections.Counter(); in_by_session = collections.Counter()
for r in R:
    if r["stage"] == "persona": cached_by_session[r["session_id"]] += r.get("cached_tokens") or 0; in_by_session[r["session_id"]] += r["input_tokens"]
for s in sess:
    cb = cached_by_session[s["session_id"]]; ib = in_by_session[s["session_id"]]
    L.append(f"| {s['session_id']} | {s['voice'].split('/')[1]} | {s['version']} | {s['turns']} | {s['questions']} + {s['probes']} | {s['words_mean']} | {s['in_tok']:,} / {s['out_tok']:,} | {cb/ib*100:.0f}% | {s['duration_s']:.0f} s | {A['per_session_persona_cost'].get(s['session_id'],0):.3f} |")
L += ["", "Persona-stage calls only (judge calls are in §3):", "", "| Voice | Calls | Input tokens | of which cached | Output | Reasoning/thinking | Median latency | Max latency | USD | USD / session |", "|---|---|---|---|---|---|---|---|---|---|"]
for k, v in bym.items():
    if v["calls"] and k in split:
        L.append(f"| {k} | {v['calls']} | {v['in']:,} | {v['cached']:,} ({v['cached']/max(v['in'],1)*100:.0f}%) | {v['out']:,} | {v['reasoning']:,} | {v['latency_median_s']} s | {v['latency_max_s']} s | {v['usd']:.3f} | {vc.get(k,0):.3f} |")
L += ["", f"Persona stage: **USD {persona_usd:.3f} ≈ EUR {persona_usd/EURUSD:.2f}** for six sessions. Caching worked where it exists: OpenAI's automatic cache served {bym['openai/gpt-5.6-sol']['cached']/bym['openai/gpt-5.6-sol']['in']*100:.0f}% of Sol's input and Anthropic's explicit cache {bym['anthropic/claude-opus-5']['cached']/bym['anthropic/claude-opus-5']['in']*100:.0f}% of Opus 5's; Gemini's implicit cache served {bym['google/gemini-3.1-pro-preview']['cached']/bym['google/gemini-3.1-pro-preview']['in']*100:.0f}%, and its thinking ({bym['google/gemini-3.1-pro-preview']['reasoning']:,} tokens) is billed as output — hence Gemini costs as much as Opus 5 per session despite lower list prices. Sol's reasoning stayed light ({bym['openai/gpt-5.6-sol']['reasoning']:,} tokens over {bym['openai/gpt-5.6-sol']['calls']} calls).", ""]
# --- judge
L += ["## 3. Judge panel (Gemini 3.1 Pro + Claude Opus 5, structured outputs)", ""]
if A.get("judge_mean_composite"):
    L += [f"{pairs} question–response pairs ({pairs_per_session:.1f} per session), {judge_calls} judge calls, **USD {judge_usd:.3f} ≈ EUR {judge_usd/EURUSD:.2f}** ({judge_per_pair*100:.2f} cents per pair, two judges, synchronous; Batch would halve it).", "",
          "| Judge | Calls | Input tokens | Output tokens | USD | Mean composite (0–5) |", "|---|---|---|---|---|---|"] + [f"| {j} | {A['judge_by_model'].get(j,{}).get('calls','—')} | {A['judge_by_model'].get(j,{}).get('in',0):,} | {A['judge_by_model'].get(j,{}).get('out',0):,} | {A['judge_by_model'].get(j,{}).get('usd',0):.3f} | {v} |" for j, v in A["judge_mean_composite"].items()] + ["", "**Judge × voice** (mean composite — the self-preference check):", "", "| Judge \\ voice | " + " | ".join(v.split('/')[1] for v in split) + " |", "|---|" + "---|" * len(split)]
    for j, d in A["judge_x_voice"].items():
        L.append(f"| {j} | " + " | ".join(str(d.get(v, '—')) for v in split) + " |")
    icc = A.get("pooled_icc", {})
    if icc:
        L += ["", "**Inter-judge reliability** (pooled over all pairs scored by both judges; ICC(2,1) single judge, ICC(2,k) panel mean):", "", "| Dimension | ICC(2,1) | ICC(2,k) | n |", "|---|---|---|---|"] + [f"| {d} | {v['icc2_1']} | {v['icc2_k']} | {v['n']} |" for d, v in icc.items()]
    L += ["", "**Dimensions surfaced** (counts over the judged pairs; the canonical twelve were offered):", "", "| Dimension | Pairs |", "|---|---|"] + [f"| {d} | {c} |" for d, c in A.get("surfaced_dimension_counts", {}).items()]
else:
    L += ["(judge results pending)"]
L += ["", "## 4. Full-run budget, extrapolated from measured costs", "",
f"Assumptions: 355 sessions (300 main + 50 re-administration + 5 adversarial) split 118 / 118 / 119 across the three voices; per-session persona cost as measured (V1–V2, 14 questions after stage filtering); the re-administration sessions carry V4_R1, which now reaches birth/postpartum personas with ≈ 30% more questions; {pairs_per_session:.1f} judged pairs per session at the measured panel cost; the other stages from `Rerun_cost_estimate_v06` (Batch prices); list prices of 23 Aug 2026; EUR at USD/{EURUSD}.", "",
"| Stage | Basis | USD | EUR |", "|---|---|---|---|",
f"| Persona sessions, 355 | {' + '.join(f'{n} × {vc.get(v,0):.3f}' for v, n in split.items())} | {persona_full:.0f} | {persona_full/EURUSD:.0f} |",
f"| V4_R1 uplift on the 50 re-administration sessions | +30% questions | {readmin_uplift:.0f} | {readmin_uplift/EURUSD:.0f} |",
f"| Judge panel, two judges, ≈ {N*pairs_per_session:,.0f} pairs | {judge_per_pair*100:.2f} c/pair synchronous → Batch ×0.5 | {judge_full_batch:.0f} (synchronous {judge_full:.0f}) | {judge_full_batch/EURUSD:.0f} |"]
for k, v in other.items():
    L.append(f"| {k} | v06 | {v} | {v/EURUSD:.0f} |")
L += [f"| **Full run, arm P, with savings** | | **{full_opt:.0f}** | **{full_opt/EURUSD:.0f}** |",
f"| Full run without Batch on the judge | | {full_list:.0f} | {full_list/EURUSD:.0f} |",
f"| Pilot first: 30 sessions × 3 repetitions + judge | run-to-run variance | {pilot:.0f} | {pilot/EURUSD:.0f} |",
f"| **Pilot + full run** | | **{full_opt+pilot:.0f}** | **{(full_opt+pilot)/EURUSD:.0f}** |", "",
f"Against the estimate of 23 Aug morning (`Rerun_cost_estimate_v06`: USD 145–195 with savings for arm P, ceiling 420), the measured persona stage comes in **lower** — caching hit rates of 90% or more on Sol and Opus 5 — while the judge stage is **higher** than estimated because the panel has two judges returning structured records with evidence. Every figure above exceeds the USD 50 halt; the run must go in approved slices (the meter preloads prior spend, so slices resume safely). Wall-clock: mean session {mean_dur:.0f} s → {hours_seq:.0f} h sequential, ≈ {hours_seq/3:.0f} h at three parallel sessions, ≈ {hours_seq/6:.0f} h at six; the judge stage runs after the sessions (or as Batch jobs, within 24 h).", "",
"A four-arm comparison (P + O-hosted + O-cloud + O-self) adds the open arms at the v06 figures (≈ USD 110–120, 20–125 flat, 10–20) — ≈ USD 300–380 in total with the pilot.", "",
"## 5. Consequences for the existing manuscript (rev3.1, withdrawn; the resubmission reports the new study)", "",
"| Section of the paper | What the dry run changes |", "|---|---|",
"| §3 Method — models | Persona voices GPT-5.6 Sol, Claude Opus 5, Gemini 3.1 Pro (served snapshots recorded per call); judge panel Gemini 3.1 Pro + Claude Opus 5 with structured outputs, replacing a single Gemini 3 Flash judge; the March models appear only as the pilot's history |",
"| §3 Method — interview loop | Output caps of 2,000 with explicit thinking budgets; finish-reason check and non-empty assertion with retry; a session with an empty answer is a failed session. The March corpus's 25% empty answers become a reported limitation of the first run, not a property of the method |",
"| §3 Method — instrument revision | V4_R1 is actually administered (19 vs 14 questions for birth-stage personas; +3.7 questions and +14 probes per persona on average), so the refinement effect is testable for the first time; the chronology addendum of 23 Aug (team selection in April–May, set-cover formalisation in June) is superseded by a refinement that runs inside the laboratory |",
"| §3 Method — dimensions | The twelve canonical dimensions are encoded for every persona (six by a documented heuristic — a decision point) and offered to the judge; surfacing of any dimension is measurable, so the 'seven critical blind spots' of the lodged paper — which were the seven dimensions no persona encoded — cannot recur as an artefact |",
"| §3 Method — statistics | Kruskal–Wallis and Wilcoxon from scipy (the in-house routine would have called any comparison significant); ICC(2,1)/ICC(2,k) per dimension across judges; judge × voice table for self-preference; length confound reported |",
"| §3 Method — reproducibility | Container, `experiment.yaml` (fingerprint in the manifest), request/response cache with snapshot ids, cost meter; TRIPOD-LLM checklist; the run directory is the deposit |",
"| §4 Results — Table 3 (quality by version) | Must be re-derived on the full run; the dry run cannot say which version is best (six sessions, V1–V2) — only that answers are 210–240 words, rich (composites 4–5), and without empties |",
"| §4 Results — Table 4 / refinement | The refinement effect (V4 → V4_R1) becomes a real comparison; expect the claim to change from 'not testable' (restatement of 23 Aug) to a measured effect of either sign |",
"| §4 Results — Table 5 (blind spots) | Replace the encoded-vs-surfaced artefact with surfacing counts over the canonical twelve; in 138 pairs the least-surfaced dimensions were intergenerational_patterns (9), body_image_autonomy (13) and digital_information_seeking (15) — candidates for genuine blind spots, to be confirmed on the full run |",
"| §4 Results — judge reliability | A new subsection: per-dimension ICC between the two judges, severity (Gemini scores lower than Opus), the judge × voice table; the ICC of 0.141 restated on 23 Aug is replaced by the panel's figures |",
"| §4 Results — cost | Measured per-session cost USD 0.19 (Sol) to 0.39 (Opus 5, Gemini 3.1 Pro) with caching; the full run ≈ USD 150–200 with savings; the lodged paper's cost statement (USD 0.64, corrected to 46.95–47.58) is replaced by metered figures from the provenance cache |",
"| §5 Discussion | The capability claim gains its strongest support from what the first run lacked: output-truncation detection, judge independence, instrument-revision fidelity, and provenance — the 'risk-control layer' the cover letter advertised is now code, not prose |",
"| Data availability | The run directory (requests.jsonl, manifest, transcripts, scores) is deposited with a DOI; the v2 persona pool and its provenance note included; the March package cited as the pilot |",
"| Title / framing | A new submission ('Synthetic Design Laboratory 2'), not a revision; the special-issue deadline of 30 November 2026 governs the timetable (pilot September, full runs October, writing November) |",
"", "## 6. Files", "", f"`{run}/` — `plan.json`, `transcripts/T_*.json`, `requests.jsonl`, `manifest.json`, `quality_scores.jsonl` (panel), `quality_scores_LEGACY_gemini-3-flash_unmetered.jsonl` (first pass, excluded), `run.log`. This report: markdown, DOCX and PDF in `verification_20260823/`."]
out_md.write_text("\n".join(L) + "\n", encoding="utf-8"); print("report written", out_md.name)

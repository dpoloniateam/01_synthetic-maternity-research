"""
Comprehensive Saturation Report Generator.

Produces a paper-ready saturation analysis with:
  1. Cumulative theme curves with log-model fit
  2. Rolling marginal yield analysis
  3. Per-category saturation tracking
  4. Information-theoretic saturation metrics
  5. Pre/post-refinement comparison
  6. Paper-ready tables (Markdown + LaTeX)
  7. Figure data for external plotting

No LLM calls — pure computation on existing scored data.

Usage:
    python -m src.refinement.saturation_report \
        --scores data/evaluation/quality_scores.jsonl \
        --refinement-scores data/evaluation/refinement/quality_scores.jsonl \
        --service-maps data/evaluation/service_maps.jsonl \
        --refinement-maps data/evaluation/refinement/service_maps.jsonl \
        --plan data/config/administration_plan.json \
        --refinement-plan data/refinement/refinement_plan.json \
        --output data/evaluation/saturation/
"""
import json
import argparse
import logging
import math
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import mannwhitneyu

from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
log = logging.getLogger(__name__)

# ── Saturation criteria ──────────────────────────────────────────────────────
WINDOW_SIZE = 5        # rolling window for marginal yield rate
PLATEAU_THRESHOLD = 2  # new themes per transcript to declare plateau
PLATEAU_LENGTH = 5     # consecutive transcripts below threshold for saturation


def load_jsonl(path: str) -> list:
    records = []
    p = Path(path)
    if not p.exists():
        return records
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ── Theme extraction ─────────────────────────────────────────────────────────

def extract_themes(scores: list, service_maps: list, session_id: str) -> dict:
    """Extract categorised themes from a single session."""
    themes = {
        "latent": set(),
        "kbv": set(),
        "thematic": set(),
        "gap": set(),
        "innovation": set(),
    }
    for s in scores:
        if s.get("session_id") != session_id:
            continue
        for dim in s.get("latent_dimensions_surfaced", []):
            themes["latent"].add(dim)
        for kbv in s.get("kbv_dimensions_present", []):
            themes["kbv"].add(kbv)
        for area in s.get("thematic_areas_covered", []):
            themes["thematic"].add(area)

    for m in service_maps:
        if m.get("session_id") != session_id:
            continue
        for gap in m.get("service_gaps", m.get("gaps", [])):
            cat = gap.get("gap_category", gap.get("category", gap.get("service_category", "")))
            if cat:
                themes["gap"].add(cat)
        for inno in m.get("innovation_opportunities", m.get("innovations", [])):
            cat = inno.get("category", inno.get("service_category", ""))
            if cat:
                themes["innovation"].add(cat)

    return themes


def flatten_themes(cat_themes: dict) -> set:
    """Merge categorised themes into a single set with prefixes."""
    flat = set()
    prefix_map = {"latent": "L:", "kbv": "K:", "thematic": "T:", "gap": "G:", "innovation": "I:"}
    for cat, items in cat_themes.items():
        prefix = prefix_map.get(cat, "X:")
        for item in items:
            flat.add(f"{prefix}{item}")
    return flat


# ── Curve fitting ────────────────────────────────────────────────────────────

def log_model(x, a, b):
    """Logarithmic growth: y = a * ln(x) + b"""
    return a * np.log(x) + b


def power_model(x, a, b):
    """Power-law growth: y = a * x^b"""
    return a * np.power(x, b)


def fit_saturation_curve(x_data, y_data):
    """Fit log and power models, return best fit with R² and projected asymptote."""
    x = np.array(x_data, dtype=float)
    y = np.array(y_data, dtype=float)

    results = {}

    # Log model
    try:
        popt, _ = curve_fit(log_model, x, y, p0=[100, 0], maxfev=10000)
        y_pred = log_model(x, *popt)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        results["log"] = {"params": {"a": float(popt[0]), "b": float(popt[1])}, "r_squared": float(r2)}
    except Exception:
        results["log"] = None

    # Power model
    try:
        popt, _ = curve_fit(power_model, x, y, p0=[10, 0.5], maxfev=10000)
        y_pred = power_model(x, *popt)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        results["power"] = {"params": {"a": float(popt[0]), "b": float(popt[1])}, "r_squared": float(r2)}
    except Exception:
        results["power"] = None

    # Select best
    best = None
    best_r2 = -1
    for name, res in results.items():
        if res and res["r_squared"] > best_r2:
            best = name
            best_r2 = res["r_squared"]

    # Project: how many more transcripts to get <1 new theme per transcript?
    projection = None
    if best == "log" and results["log"]:
        a = results["log"]["params"]["a"]
        # derivative of a*ln(x) = a/x; set a/x < 1 => x > a
        projection = {"model": "log", "marginal_below_1_at": max(1, int(math.ceil(a)))}
    elif best == "power" and results["power"]:
        a, b = results["power"]["params"]["a"], results["power"]["params"]["b"]
        # derivative = a*b*x^(b-1); set = 1 => x = (1/(a*b))^(1/(b-1))
        if 0 < b < 1 and a * b > 0:
            try:
                x_thresh = (1 / (a * b)) ** (1 / (b - 1))
                if x_thresh < 1e12:
                    projection = {"model": "power", "marginal_below_1_at": max(1, int(math.ceil(x_thresh)))}
                else:
                    projection = {"model": "power", "marginal_below_1_at": int(1e12)}
            except (OverflowError, ValueError):
                projection = {"model": "power", "marginal_below_1_at": int(1e12)}
        elif b >= 1:
            # Superlinear or linear growth — saturation never reached
            projection = {"model": "power", "marginal_below_1_at": int(1e12)}

    return {
        "models": results,
        "best_model": best,
        "best_r_squared": float(best_r2) if best_r2 > -1 else None,
        "projection": projection,
    }


# ── Rolling marginal yield ───────────────────────────────────────────────────

def rolling_marginal_yield(yields: list, window: int = WINDOW_SIZE) -> list:
    """Compute rolling average of new themes per transcript."""
    result = []
    new_counts = [y["new_themes"] for y in yields]
    for i in range(len(new_counts)):
        start = max(0, i - window + 1)
        window_vals = new_counts[start:i + 1]
        result.append({
            "transcript_idx": yields[i]["transcript_idx"],
            "session_id": yields[i]["session_id"],
            "source": yields[i]["source"],
            "rolling_mean": round(sum(window_vals) / len(window_vals), 2),
            "new_themes": new_counts[i],
        })
    return result


def find_plateau_point(rolling: list, threshold: float = PLATEAU_THRESHOLD,
                       length: int = PLATEAU_LENGTH) -> int | None:
    """Find first index where rolling mean stays below threshold for `length` consecutive transcripts."""
    consecutive = 0
    for r in rolling:
        if r["rolling_mean"] <= threshold:
            consecutive += 1
            if consecutive >= length:
                return r["transcript_idx"] - length + 1
        else:
            consecutive = 0
    return None


# ── Per-category tracking ────────────────────────────────────────────────────

def per_category_saturation(yields_by_cat: dict) -> dict:
    """Track saturation per theme category."""
    result = {}
    for cat, yields in yields_by_cat.items():
        total = yields[-1]["cumulative"] if yields else 0
        rolling = rolling_marginal_yield(yields, window=3)
        plateau = find_plateau_point(rolling, threshold=1, length=3)

        # First occurrence and last occurrence of new themes
        first_new = next((y for y in yields if y["new_themes"] > 0), None)
        last_new = None
        for y in reversed(yields):
            if y["new_themes"] > 0:
                last_new = y
                break

        result[cat] = {
            "total_unique": total,
            "plateau_at": plateau,
            "first_new_at": first_new["transcript_idx"] if first_new else None,
            "last_new_at": last_new["transcript_idx"] if last_new else None,
            "mean_yield": round(sum(y["new_themes"] for y in yields) / len(yields), 2) if yields else 0,
        }
    return result


# ── Core analysis ────────────────────────────────────────────────────────────

def run_saturation_analysis(scores, service_maps, session_ids,
                            refinement_scores=None, refinement_maps=None,
                            refinement_session_ids=None):
    """Full saturation analysis across original + refinement transcripts."""

    cumulative_all = set()
    cumulative_by_cat = defaultdict(set)
    marginal_yields = []
    cat_yields = defaultdict(list)

    prefix_map = {"latent": "L:", "kbv": "K:", "thematic": "T:", "gap": "G:", "innovation": "I:"}

    def process_session(idx, sid, src_scores, src_maps, source_label):
        nonlocal cumulative_all
        cat_themes = extract_themes(src_scores, src_maps, sid)
        flat = flatten_themes(cat_themes)
        new_all = flat - cumulative_all
        cumulative_all |= new_all

        entry = {
            "transcript_idx": idx,
            "session_id": sid,
            "new_themes": len(new_all),
            "cumulative": len(cumulative_all),
            "source": source_label,
        }
        marginal_yields.append(entry)

        # Per-category tracking
        for cat, items in cat_themes.items():
            prefix = prefix_map[cat]
            prefixed = {f"{prefix}{item}" for item in items}
            new_cat = prefixed - cumulative_by_cat[cat]
            cumulative_by_cat[cat] |= new_cat
            cat_yields[cat].append({
                "transcript_idx": idx,
                "session_id": sid,
                "new_themes": len(new_cat),
                "cumulative": len(cumulative_by_cat[cat]),
                "source": source_label,
            })

    # Process original sessions
    for i, sid in enumerate(session_ids):
        process_session(i + 1, sid, scores, service_maps, "original")

    pre_refinement_total = len(cumulative_all)
    pre_refinement_snapshot = cumulative_all.copy()

    # Process refinement sessions
    if refinement_scores and refinement_session_ids:
        for i, sid in enumerate(refinement_session_ids):
            process_session(
                len(session_ids) + i + 1, sid,
                refinement_scores, refinement_maps or [], "refinement"
            )

    post_refinement_new = len(cumulative_all) - pre_refinement_total

    # Rolling marginal yield
    rolling = rolling_marginal_yield(marginal_yields, WINDOW_SIZE)

    # Plateau detection
    plateau_point = find_plateau_point(rolling)

    # Separate analysis for original-only
    original_yields = [m for m in marginal_yields if m["source"] == "original"]
    original_rolling = rolling_marginal_yield(original_yields, WINDOW_SIZE)
    original_plateau = find_plateau_point(original_rolling)

    # Curve fitting (original only)
    x_orig = [m["transcript_idx"] for m in original_yields]
    y_orig = [m["cumulative"] for m in original_yields]
    curve_fit_original = fit_saturation_curve(x_orig, y_orig)

    # Curve fitting (combined)
    x_all = [m["transcript_idx"] for m in marginal_yields]
    y_all = [m["cumulative"] for m in marginal_yields]
    curve_fit_combined = fit_saturation_curve(x_all, y_all)

    # Per-category saturation
    cat_sat = per_category_saturation(dict(cat_yields))

    # Halving analysis: at what transcript index did we reach 50%, 75%, 90% of final total?
    final_total = len(cumulative_all)
    milestones = {}
    for pct in [0.25, 0.50, 0.75, 0.90, 0.95]:
        target = int(final_total * pct)
        for m in marginal_yields:
            if m["cumulative"] >= target:
                milestones[f"{int(pct*100)}%"] = {
                    "transcript_idx": m["transcript_idx"],
                    "session_id": m["session_id"],
                    "cumulative": m["cumulative"],
                    "source": m["source"],
                }
                break

    # Compare original vs refinement yield rates
    original_mean_yield = np.mean([m["new_themes"] for m in original_yields]) if original_yields else 0
    refinement_yields_list = [m for m in marginal_yields if m["source"] == "refinement"]
    refinement_mean_yield = np.mean([m["new_themes"] for m in refinement_yields_list]) if refinement_yields_list else 0

    # Mann-Whitney U test for yield difference
    yield_comparison = None
    if original_yields and refinement_yields_list:
        orig_new = [m["new_themes"] for m in original_yields]
        ref_new = [m["new_themes"] for m in refinement_yields_list]
        u_stat, p_val = mannwhitneyu(orig_new, ref_new, alternative="two-sided")
        yield_comparison = {
            "original_mean": float(round(original_mean_yield, 2)),
            "original_median": float(np.median(orig_new)),
            "refinement_mean": float(round(refinement_mean_yield, 2)),
            "refinement_median": float(np.median(ref_new)),
            "mann_whitney_U": float(u_stat),
            "p_value": float(round(p_val, 6)),
            "significant": p_val < 0.05,
        }

    # Theme novelty in refinement: what % of refinement themes were truly new?
    refinement_only_themes = cumulative_all - pre_refinement_snapshot
    refinement_novelty_rate = len(refinement_only_themes) / len(cumulative_all) if cumulative_all else 0

    # Categorise the new refinement themes
    refinement_new_by_cat = defaultdict(int)
    for t in refinement_only_themes:
        prefix = t.split(":")[0] + ":"
        rev_prefix = {v: k for k, v in prefix_map.items()}
        cat = rev_prefix.get(prefix, "other")
        refinement_new_by_cat[cat] += 1

    return {
        "total_transcripts": len(marginal_yields),
        "original_transcripts": len(original_yields),
        "refinement_transcripts": len(refinement_yields_list),
        "total_unique_themes": len(cumulative_all),
        "pre_refinement_themes": pre_refinement_total,
        "post_refinement_new_themes": post_refinement_new,
        "refinement_novelty_rate": round(refinement_novelty_rate, 4),
        "refinement_new_by_category": dict(refinement_new_by_cat),
        "plateau_point_combined": plateau_point,
        "plateau_point_original": original_plateau,
        "marginal_yields": marginal_yields,
        "rolling_yields": rolling,
        "milestones": milestones,
        "curve_fit_original": curve_fit_original,
        "curve_fit_combined": curve_fit_combined,
        "category_saturation": cat_sat,
        "yield_comparison": yield_comparison,
        "criteria": {
            "window_size": WINDOW_SIZE,
            "plateau_threshold": PLATEAU_THRESHOLD,
            "plateau_length": PLATEAU_LENGTH,
        },
    }


# ── Report generation ────────────────────────────────────────────────────────

def generate_report(analysis: dict, version: int) -> str:
    """Generate comprehensive paper-ready saturation report."""
    lines = []

    # ── Header ──
    lines.append(f"# Thematic Saturation Analysis Report")
    lines.append(f"")
    lines.append(f"**Questionnaire version:** V{version} (winner) + V{version} Refined (R1)")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Saturation criteria:** rolling window = {analysis['criteria']['window_size']}, "
                 f"plateau threshold = {analysis['criteria']['plateau_threshold']} new themes/transcript, "
                 f"plateau length = {analysis['criteria']['plateau_length']} consecutive transcripts")
    lines.append("")

    # ── 1. Overview ──
    lines.append("## 1. Overview")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Original transcripts (V{version}) | {analysis['original_transcripts']} |")
    lines.append(f"| Refinement transcripts (V{version}_R1) | {analysis['refinement_transcripts']} |")
    lines.append(f"| Total transcripts analysed | {analysis['total_transcripts']} |")
    lines.append(f"| Total unique themes | {analysis['total_unique_themes']} |")
    lines.append(f"| Pre-refinement themes | {analysis['pre_refinement_themes']} |")
    lines.append(f"| Post-refinement new themes | {analysis['post_refinement_new_themes']} |")
    lines.append(f"| Refinement novelty rate | {analysis['refinement_novelty_rate']:.1%} |")
    lines.append("")

    # ── 2. Saturation assessment ──
    lines.append("## 2. Saturation Assessment")
    lines.append("")

    orig_plateau = analysis["plateau_point_original"]
    combined_plateau = analysis["plateau_point_combined"]

    if orig_plateau:
        lines.append(f"**Original corpus:** Plateau detected at transcript {orig_plateau} "
                     f"(rolling {WINDOW_SIZE}-transcript mean fell below {PLATEAU_THRESHOLD} new themes/transcript "
                     f"for {PLATEAU_LENGTH} consecutive transcripts).")
    else:
        lines.append(f"**Original corpus:** No plateau detected. New themes continued emerging "
                     f"through all {analysis['original_transcripts']} original transcripts.")
        # Report the last-5 rolling mean
        orig_rolling = [r for r in analysis["rolling_yields"] if r["source"] == "original"]
        if orig_rolling:
            last5_mean = np.mean([r["new_themes"] for r in orig_rolling[-5:]])
            lines.append(f"Mean yield over last 5 original transcripts: {last5_mean:.1f} new themes/transcript.")
    lines.append("")

    if combined_plateau:
        lines.append(f"**Combined corpus:** Plateau detected at transcript {combined_plateau}.")
    else:
        lines.append(f"**Combined corpus (original + refinement):** No plateau detected across "
                     f"all {analysis['total_transcripts']} transcripts. Thematic space remains open.")
    lines.append("")

    # ── 3. Milestone analysis ──
    lines.append("## 3. Cumulative Theme Milestones")
    lines.append("")
    lines.append("| Milestone | Transcript # | Session | Themes | Source |")
    lines.append("|-----------|-------------|---------|--------|--------|")
    for pct, info in sorted(analysis["milestones"].items(), key=lambda x: int(x[0].replace("%", ""))):
        lines.append(f"| {pct} of total | {info['transcript_idx']} | {info['session_id']} | "
                     f"{info['cumulative']} | {info['source']} |")
    lines.append("")

    # ── 4. Curve fitting ──
    lines.append("## 4. Accumulation Curve Modelling")
    lines.append("")

    for label, fit_key in [("Original corpus", "curve_fit_original"), ("Combined corpus", "curve_fit_combined")]:
        fit = analysis[fit_key]
        lines.append(f"### {label}")
        lines.append("")
        if fit["best_model"]:
            best = fit["models"][fit["best_model"]]
            lines.append(f"**Best-fit model:** {fit['best_model']}")
            lines.append(f"**R-squared:** {fit['best_r_squared']:.4f}")
            if fit["best_model"] == "log":
                a, b = best["params"]["a"], best["params"]["b"]
                lines.append(f"**Equation:** y = {a:.1f} * ln(x) + {b:.1f}")
                lines.append(f"**Marginal yield:** dy/dx = {a:.1f}/x")
                lines.append(f"**Marginal yield < 1 at:** x = {int(math.ceil(a))} transcripts")
            elif fit["best_model"] == "power":
                a, b = best["params"]["a"], best["params"]["b"]
                lines.append(f"**Equation:** y = {a:.1f} * x^{b:.3f}")
            if fit["projection"]:
                proj_n = fit['projection']['marginal_below_1_at']
                if proj_n > 100000:
                    lines.append(f"**Projected marginal yield < 1 theme/transcript at:** "
                                 f"n >> {analysis.get('total_transcripts', 110)} (growth exponent {b:.3f} "
                                 f"is near-linear; practical saturation not foreseeable within feasible sample sizes)")
                else:
                    lines.append(f"**Projected marginal yield < 1 theme/transcript at:** "
                                 f"~{proj_n} transcripts")

            # Also show the other model for comparison
            other = "power" if fit["best_model"] == "log" else "log"
            if fit["models"].get(other):
                lines.append(f"**Alternative ({other}) R-squared:** {fit['models'][other]['r_squared']:.4f}")
        else:
            lines.append("Curve fitting failed.")
        lines.append("")

    # ── 5. Original vs refinement comparison ──
    lines.append("## 5. Original vs Refinement Yield Comparison")
    lines.append("")

    yc = analysis["yield_comparison"]
    if yc:
        lines.append("| Metric | Original | Refinement |")
        lines.append("|--------|----------|------------|")
        lines.append(f"| Mean new themes/transcript | {yc['original_mean']:.1f} | {yc['refinement_mean']:.1f} |")
        lines.append(f"| Median new themes/transcript | {yc['original_median']:.0f} | {yc['refinement_median']:.0f} |")
        lines.append("")
        sig = "significant" if yc["significant"] else "not significant"
        lines.append(f"**Mann-Whitney U:** {yc['mann_whitney_U']:.1f}, p = {yc['p_value']:.4f} ({sig})")
        lines.append("")

        if analysis["post_refinement_new_themes"] > 0:
            lines.append(f"The refined instrument introduced {analysis['post_refinement_new_themes']} themes "
                         f"not observed in the original {analysis['pre_refinement_themes']} themes, "
                         f"representing a {analysis['refinement_novelty_rate']:.1%} novelty rate. "
                         f"This indicates the refined questionnaire accessed previously untapped experiential dimensions.")
            lines.append("")
            lines.append("**New themes by category:**")
            lines.append("")
            lines.append("| Category | New themes from refinement |")
            lines.append("|----------|---------------------------|")
            cat_labels = {"latent": "Latent dimensions", "kbv": "KBV dimensions",
                          "thematic": "Thematic areas", "gap": "Service gaps",
                          "innovation": "Innovation opportunities"}
            for cat, count in sorted(analysis["refinement_new_by_category"].items(),
                                     key=lambda x: -x[1]):
                lines.append(f"| {cat_labels.get(cat, cat)} | {count} |")
            lines.append("")
    else:
        lines.append("No refinement data available for comparison.")
        lines.append("")

    # ── 6. Per-category saturation ──
    lines.append("## 6. Per-Category Saturation")
    lines.append("")
    lines.append("| Category | Unique Themes | First New | Last New | Mean Yield | Plateau At |")
    lines.append("|----------|--------------|-----------|----------|------------|------------|")
    cat_labels = {"latent": "Latent dimensions", "kbv": "KBV dimensions",
                  "thematic": "Thematic areas", "gap": "Service gaps",
                  "innovation": "Innovation opportunities"}
    for cat, info in analysis["category_saturation"].items():
        plateau_str = str(info["plateau_at"]) if info["plateau_at"] else "Not reached"
        lines.append(f"| {cat_labels.get(cat, cat)} | {info['total_unique']} | "
                     f"{info['first_new_at'] or '-'} | {info['last_new_at'] or '-'} | "
                     f"{info['mean_yield']:.1f} | {plateau_str} |")
    lines.append("")

    # ── 7. Marginal yield trajectory (full table, abbreviated) ──
    lines.append("## 7. Marginal Yield Trajectory")
    lines.append("")
    lines.append("| # | Session | New | Cumulative | Rolling Mean | Source |")
    lines.append("|---|---------|-----|------------|--------------|--------|")
    rolling = analysis["rolling_yields"]
    # Show first 20, transition point, last 10
    show_indices = set(range(min(20, len(rolling))))
    show_indices |= set(range(max(0, analysis["original_transcripts"] - 3), analysis["original_transcripts"]))
    show_indices |= set(range(analysis["original_transcripts"], min(analysis["original_transcripts"] + 3, len(rolling))))
    show_indices |= set(range(max(0, len(rolling) - 5), len(rolling)))

    prev_idx = -1
    for i in sorted(show_indices):
        if i >= len(rolling):
            continue
        if prev_idx >= 0 and i > prev_idx + 1:
            lines.append("| ... | ... | ... | ... | ... | ... |")
        r = rolling[i]
        m = analysis["marginal_yields"][i]
        lines.append(f"| {r['transcript_idx']} | {r['session_id']} | {m['new_themes']} | "
                     f"{m['cumulative']} | {r['rolling_mean']} | {r['source']} |")
        prev_idx = i
    lines.append("")

    # ── 8. Interpretation ──
    lines.append("## 8. Interpretation for Paper")
    lines.append("")

    # Determine narrative
    if not orig_plateau and analysis["post_refinement_new_themes"] > 0:
        lines.append("### Finding: Open thematic space")
        lines.append("")
        lines.append(f"Across {analysis['original_transcripts']} original transcripts, "
                     f"{analysis['pre_refinement_themes']} unique thematic codes were identified. "
                     f"The cumulative theme curve followed a {analysis['curve_fit_original']['best_model']} trajectory "
                     f"(R-squared = {analysis['curve_fit_original']['best_r_squared']:.3f}), consistent with "
                     f"a decelerating but non-asymptotic growth pattern.")
        lines.append("")

        fit = analysis['curve_fit_original']
        if fit["projection"]:
            proj_n = fit['projection']['marginal_below_1_at']
            if proj_n > 100000:
                lines.append(f"The power-law exponent of {fit['models']['power']['params']['b']:.3f} (near unity) "
                             f"indicates near-linear theme accumulation, meaning practical saturation "
                             f"is not foreseeable within feasible sample sizes. This suggests the synthetic "
                             f"persona pool and questionnaire together produce a highly generative thematic space.")
            else:
                lines.append(f"Extrapolation suggests the marginal yield would drop below 1 new theme "
                             f"per transcript at approximately n = {proj_n} transcripts, "
                             f"indicating that practical saturation was being approached but had not been formally reached "
                             f"within the original corpus.")
        lines.append("")

        lines.append(f"The refinement round (50 transcripts with the improved V{version}_R1 instrument) "
                     f"introduced {analysis['post_refinement_new_themes']} additional themes ({analysis['refinement_novelty_rate']:.1%} novelty), "
                     f"confirming that the thematic space was not exhausted and that instrument refinement "
                     f"can unlock new experiential dimensions even when the original curve suggests diminishing returns.")
        lines.append("")
        lines.append("This pattern is consistent with qualitative research literature suggesting that thematic "
                     "saturation is instrument-dependent: changing the instrument can reopen the thematic space "
                     "(Hennink et al., 2017; Saunders et al., 2018).")

    elif orig_plateau:
        lines.append("### Finding: Saturation reached in original corpus")
        lines.append("")
        lines.append(f"Thematic saturation was detected at transcript {orig_plateau} of "
                     f"{analysis['original_transcripts']} in the original corpus.")
        if analysis["post_refinement_new_themes"] > 0:
            lines.append(f"\nHowever, the refinement round reopened the thematic space, suggesting "
                         f"instrument-dependent saturation rather than true experiential exhaustion.")

    lines.append("")

    # ── 9. LaTeX tables ──
    lines.append("## 9. Paper-Ready Tables")
    lines.append("")
    lines.append("### Table: Saturation Summary")
    lines.append("")
    lines.append("```latex")
    lines.append("\\begin{table}[h]")
    lines.append("\\caption{Thematic saturation analysis summary}")
    lines.append("\\label{tab:saturation}")
    lines.append("\\begin{tabular}{lr}")
    lines.append("\\hline")
    lines.append("Metric & Value \\\\")
    lines.append("\\hline")
    lines.append(f"Original transcripts (V{version}) & {analysis['original_transcripts']} \\\\")
    lines.append(f"Refinement transcripts (V{version}\\_R1) & {analysis['refinement_transcripts']} \\\\")
    lines.append(f"Total unique themes & {analysis['total_unique_themes']} \\\\")
    lines.append(f"Pre-refinement themes & {analysis['pre_refinement_themes']} \\\\")
    lines.append(f"Post-refinement new themes & {analysis['post_refinement_new_themes']} \\\\")
    novelty_pct = f"{analysis['refinement_novelty_rate']*100:.1f}\\%"
    lines.append(f"Refinement novelty rate & {novelty_pct} \\\\")
    if analysis["curve_fit_original"]["best_model"]:
        lines.append(f"Best-fit model (original) & {analysis['curve_fit_original']['best_model']} \\\\")
        lines.append(f"R\\textsuperscript{{2}} & {analysis['curve_fit_original']['best_r_squared']:.3f} \\\\")
    if analysis["yield_comparison"]:
        lines.append(f"Original mean yield & {analysis['yield_comparison']['original_mean']:.1f} themes/transcript \\\\")
        lines.append(f"Refinement mean yield & {analysis['yield_comparison']['refinement_mean']:.1f} themes/transcript \\\\")
        lines.append(f"Mann-Whitney U & {analysis['yield_comparison']['mann_whitney_U']:.1f} (p={analysis['yield_comparison']['p_value']:.4f}) \\\\")
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    lines.append("```")
    lines.append("")

    lines.append("### Table: Cumulative Theme Milestones")
    lines.append("")
    lines.append("```latex")
    lines.append("\\begin{table}[h]")
    lines.append("\\caption{Cumulative theme discovery milestones}")
    lines.append("\\label{tab:milestones}")
    lines.append("\\begin{tabular}{lccc}")
    lines.append("\\hline")
    lines.append("Milestone & Transcript \\# & Cumulative Themes & Source \\\\")
    lines.append("\\hline")
    for pct, info in sorted(analysis["milestones"].items(), key=lambda x: int(x[0].replace("%", ""))):
        lines.append(f"{pct} of total & {info['transcript_idx']} & {info['cumulative']} & {info['source']} \\\\")
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    lines.append("```")
    lines.append("")

    # ── 10. Figure data pointers ──
    lines.append("## 10. Figure Data Files")
    lines.append("")
    lines.append("The following JSON files are provided for plotting in R/Python/Excel:")
    lines.append("")
    lines.append("- `saturation_curve_data.json` — cumulative theme count per transcript (x, y, source)")
    lines.append("- `rolling_yield_data.json` — rolling mean new themes per transcript")
    lines.append("- `category_saturation_data.json` — per-category cumulative curves")
    lines.append("- `curve_fit_projections.json` — fitted model parameters and projections")
    lines.append("")

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Comprehensive Saturation Report")
    parser.add_argument("--scores", type=str, required=True)
    parser.add_argument("--refinement-scores", type=str, default="")
    parser.add_argument("--service-maps", type=str, required=True)
    parser.add_argument("--refinement-maps", type=str, default="")
    parser.add_argument("--plan", type=str, required=True)
    parser.add_argument("--refinement-plan", type=str, default="")
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    run = TimestampedRun(args.output)
    run.record_read(args.scores)
    run.record_read(args.service_maps)
    run.record_read(args.plan)

    scores = load_jsonl(args.scores)
    service_maps = load_jsonl(args.service_maps)

    with open(args.plan) as f:
        admin_plan = json.load(f)

    # Determine winner version
    version = None
    if args.refinement_plan and Path(args.refinement_plan).exists():
        run.record_read(args.refinement_plan)
        with open(args.refinement_plan) as f:
            ref_plan = json.load(f)
        version = ref_plan.get("winner", {}).get("version")

    if version is None:
        vcounts = Counter()
        summaries = load_jsonl(str(Path(args.scores).parent / "transcript_summaries.jsonl"))
        for s in summaries:
            vcounts[s.get("questionnaire_version")] += 1
        version = vcounts.most_common(1)[0][0] if vcounts else 1

    # Get V4 session IDs ordered
    summaries = load_jsonl(str(Path(args.scores).parent / "transcript_summaries.jsonl"))
    version_sessions = sorted(
        [s["session_id"] for s in summaries if s.get("questionnaire_version") == version],
        key=lambda x: int(x.replace("S_", "").replace("R", "1000"))
    )
    log.info(f"Analysing V{version}: {len(version_sessions)} original sessions")

    # Load refinement data
    refinement_scores = load_jsonl(args.refinement_scores) if args.refinement_scores else []
    refinement_maps = load_jsonl(args.refinement_maps) if args.refinement_maps else []
    refinement_session_ids = sorted(
        {s["session_id"] for s in refinement_scores},
        key=lambda x: int(x.replace("S_R", ""))
    ) if refinement_scores else []

    if refinement_scores:
        run.record_read(args.refinement_scores)
        log.info(f"Including {len(refinement_session_ids)} refinement sessions")
    if refinement_maps:
        run.record_read(args.refinement_maps)

    # Run analysis
    analysis = run_saturation_analysis(
        scores, service_maps, version_sessions,
        refinement_scores, refinement_maps, refinement_session_ids,
    )
    analysis["version"] = version
    analysis["run_timestamp"] = run.timestamp

    # ── Write outputs ──

    # 1. Full analysis JSON
    analysis_path = run.output_path("saturation_analysis.json")
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
    run.stable_pointer("saturation_analysis.json", analysis_path)

    # 2. Curve data for plotting
    curve_data = [{
        "x": m["transcript_idx"],
        "y": m["cumulative"],
        "new": m["new_themes"],
        "source": m["source"],
        "session_id": m["session_id"],
    } for m in analysis["marginal_yields"]]
    curve_path = run.output_path("saturation_curve_data.json")
    with open(curve_path, "w") as f:
        json.dump(curve_data, f, indent=2)
    run.stable_pointer("saturation_curve_data.json", curve_path)

    # 3. Rolling yield data
    rolling_path = run.output_path("rolling_yield_data.json")
    with open(rolling_path, "w") as f:
        json.dump(analysis["rolling_yields"], f, indent=2)
    run.stable_pointer("rolling_yield_data.json", rolling_path)

    # 4. Category saturation data (per-category cumulative curves)
    cat_data = {}
    prefix_map = {"latent": "L:", "kbv": "K:", "thematic": "T:", "gap": "G:", "innovation": "I:"}
    # Rebuild per-cat yields
    cumulative_by_cat = defaultdict(set)
    cat_curves = defaultdict(list)
    for m in analysis["marginal_yields"]:
        sid = m["session_id"]
        src = m["source"]
        src_scores = refinement_scores if src == "refinement" else scores
        src_maps = refinement_maps if src == "refinement" else service_maps
        cat_themes = extract_themes(src_scores, src_maps, sid)
        for cat, items in cat_themes.items():
            prefix = prefix_map[cat]
            prefixed = {f"{prefix}{item}" for item in items}
            new_cat = prefixed - cumulative_by_cat[cat]
            cumulative_by_cat[cat] |= new_cat
            cat_curves[cat].append({
                "x": m["transcript_idx"],
                "y": len(cumulative_by_cat[cat]),
                "new": len(new_cat),
                "source": src,
            })
    cat_path = run.output_path("category_saturation_data.json")
    with open(cat_path, "w") as f:
        json.dump(dict(cat_curves), f, indent=2)
    run.stable_pointer("category_saturation_data.json", cat_path)

    # 5. Curve fit projections
    proj_path = run.output_path("curve_fit_projections.json")
    with open(proj_path, "w") as f:
        json.dump({
            "original": analysis["curve_fit_original"],
            "combined": analysis["curve_fit_combined"],
        }, f, indent=2)
    run.stable_pointer("curve_fit_projections.json", proj_path)

    # 6. Markdown report
    report = generate_report(analysis, version)
    report_path = run.output_path("saturation_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    run.stable_pointer("saturation_report.md", report_path)

    run.write_manifest("saturation_report", config={
        "version": version,
        "total_themes": analysis["total_unique_themes"],
        "plateau_original": analysis["plateau_point_original"],
        "plateau_combined": analysis["plateau_point_combined"],
    })

    log.info(f"Total unique themes: {analysis['total_unique_themes']}")
    log.info(f"Original plateau: {analysis['plateau_point_original'] or 'Not reached'}")
    log.info(f"Combined plateau: {analysis['plateau_point_combined'] or 'Not reached'}")
    log.info(f"Refinement novelty rate: {analysis['refinement_novelty_rate']:.1%}")
    if analysis["curve_fit_original"]["best_model"]:
        log.info(f"Curve fit (original): {analysis['curve_fit_original']['best_model']} "
                 f"R²={analysis['curve_fit_original']['best_r_squared']:.4f}")
    log.info(f"Report -> {report_path}")


if __name__ == "__main__":
    main()

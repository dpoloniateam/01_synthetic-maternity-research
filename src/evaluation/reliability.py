"""
Reliability statistics (development 7, 23 Aug 2026) — verified implementations.

icc2_1: ICC(2,1), two-way random effects, single rater, absolute agreement (Shrout & Fleiss 1979; McGraw & Wong 1996 ICC(A,1)).
icc2_k: ICC(2,k), average of k raters.
Verified in tests/test_developments.py against the Shrout & Fleiss (1979) Table 2 data: ICC(2,1) = 0.290.
"""
from __future__ import annotations
import numpy as np


def _anova_terms(matrix):
    x = np.asarray(matrix, dtype=float)
    n, k = x.shape
    grand = x.mean()
    row_means = x.mean(axis=1)
    col_means = x.mean(axis=0)
    ms_r = k * ((row_means - grand) ** 2).sum() / (n - 1)
    ms_c = n * ((col_means - grand) ** 2).sum() / (k - 1)
    resid = x - row_means[:, None] - col_means[None, :] + grand
    ms_e = (resid ** 2).sum() / ((n - 1) * (k - 1))
    return n, k, ms_r, ms_c, ms_e


def icc2_1(matrix) -> float:
    """Subjects in rows, raters in columns; no missing values."""
    x = np.asarray(matrix, dtype=float)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 2:
        return float("nan")
    n, k, ms_r, ms_c, ms_e = _anova_terms(x)
    denom = ms_r + (k - 1) * ms_e + k * (ms_c - ms_e) / n
    return float((ms_r - ms_e) / denom) if denom != 0 else float("nan")


def icc2_k(matrix) -> float:
    x = np.asarray(matrix, dtype=float)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 2:
        return float("nan")
    n, k, ms_r, ms_c, ms_e = _anova_terms(x)
    denom = ms_r + (ms_c - ms_e) / n
    return float((ms_r - ms_e) / denom) if denom != 0 else float("nan")


def icc_by_dimension(ratings: dict) -> dict:
    """ratings: {dimension: [[r1, r2, ...] per subject]} → {dimension: {"icc2_1", "icc2_k", "n", "k"}}"""
    out = {}
    for dim, m in ratings.items():
        x = np.asarray(m, dtype=float)
        if x.ndim == 2 and x.shape[0] >= 2 and x.shape[1] >= 2:
            out[dim] = {"icc2_1": round(icc2_1(x), 3), "icc2_k": round(icc2_k(x), 3), "n": int(x.shape[0]), "k": int(x.shape[1])}
    return out


def length_partial_correlation(scores, lengths, covariate_scores=None) -> dict:
    """Correlation of a judge's scores with response length, and the partial correlation of two judges'
    scores controlling for length (Emirtekin & Özarslan 2026: length is a confound of rubric scores)."""
    from scipy import stats
    s = np.asarray(scores, dtype=float); L = np.asarray(lengths, dtype=float)
    out = {"r_score_length": round(float(stats.spearmanr(s, L).statistic), 3) if len(s) > 2 else None}
    if covariate_scores is not None:
        c = np.asarray(covariate_scores, dtype=float)
        # partial correlation r(s,c | L) via residuals of linear fits
        def resid(y, x):
            A = np.vstack([x, np.ones_like(x)]).T
            beta, *_ = np.linalg.lstsq(A, y, rcond=None)
            return y - A @ beta
        rs, rc = resid(s, L), resid(c, L)
        out["r_judges"] = round(float(stats.pearsonr(s, c).statistic), 3) if len(s) > 2 else None
        out["r_judges_partial_length"] = round(float(stats.pearsonr(rs, rc).statistic), 3) if len(s) > 3 else None
    return out

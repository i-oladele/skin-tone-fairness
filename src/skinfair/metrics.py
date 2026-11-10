"""Clinical performance metrics: per-class sensitivity/specificity, AUC, bootstrap CIs and
binary (referral) operating points."""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, roc_auc_score


def _safe_div(a: float, b: float) -> float:
    return float(a / b) if b else float("nan")


def _auc(y_bin: np.ndarray, score: np.ndarray) -> float:
    if y_bin.all() or not y_bin.any():
        return float("nan")  # AUC is undefined when only one class is present
    return float(roc_auc_score(y_bin, score))


def per_class_metrics(y_true: np.ndarray, probs: np.ndarray, classes: list[str]) -> pd.DataFrame:
    """One-vs-rest metrics for each class, using the arg-max prediction."""
    y_pred = probs.argmax(1)
    rows = []
    for k, name in enumerate(classes):
        t, p = y_true == k, y_pred == k
        tp, fn, fp, tn = (t & p).sum(), (t & ~p).sum(), (~t & p).sum(), (~t & ~p).sum()
        rows.append(
            {
                "class": name,
                "support": int(t.sum()),
                "sensitivity": _safe_div(tp, tp + fn),
                "specificity": _safe_div(tn, tn + fp),
                "ppv": _safe_div(tp, tp + fp),
                "f1": _safe_div(2 * tp, 2 * tp + fp + fn),
                "auc": _auc(t, probs[:, k]),
            }
        )
    return pd.DataFrame(rows).set_index("class")


def summary_metrics(y_true: np.ndarray, probs: np.ndarray) -> dict[str, float]:
    y_pred = probs.argmax(1)
    present = np.unique(y_true)
    aucs = [_auc(y_true == k, probs[:, k]) for k in present]
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        # Mean per-class sensitivity; the headline metric of the ISIC 2018 challenge.
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, labels=present, average="macro", zero_division=0)),
        "macro_auc": float(np.nanmean(aucs)),
    }


def bootstrap_ci(
    metric_fn: Callable[[np.ndarray], dict[str, float]],
    n: int,
    groups: np.ndarray | None = None,
    n_boot: int = 1000,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, tuple[float, float]]:
    """Percentile bootstrap confidence intervals.

    `metric_fn(indices)` computes a dict of metrics on a resample. When `groups` (e.g. lesion
    IDs) is given, whole groups are resampled, because images of the same lesion are not
    independent observations.
    """
    rng = np.random.default_rng(seed)
    if groups is None:
        members = [np.array([i]) for i in range(n)]
    else:
        _, inverse = np.unique(groups, return_inverse=True)
        order = np.argsort(inverse, kind="stable")
        members = np.split(order, np.flatnonzero(np.diff(inverse[order])) + 1)

    samples: dict[str, list[float]] = {}
    for _ in range(n_boot):
        picked = rng.integers(0, len(members), len(members))
        idx = np.concatenate([members[g] for g in picked])
        for key, value in metric_fn(idx).items():
            samples.setdefault(key, []).append(value)

    lo, hi = 100 * alpha / 2, 100 * (1 - alpha / 2)
    return {
        key: (float(np.nanpercentile(v, lo)), float(np.nanpercentile(v, hi)))
        for key, v in samples.items()
    }


def threshold_for_sensitivity(y_bin: np.ndarray, score: np.ndarray, target: float) -> float:
    """Highest threshold whose sensitivity (score >= threshold) is at least `target`.

    Choose this on the validation set, then apply it unchanged to the test set.
    """
    pos = np.sort(score[y_bin.astype(bool)])[::-1]
    if len(pos) == 0:
        raise ValueError("No positive cases to set a threshold from.")
    k = int(np.ceil(target * len(pos))) - 1
    return float(pos[max(k, 0)])


def binary_metrics(y_bin: np.ndarray, score: np.ndarray, threshold: float) -> dict[str, float]:
    y_bin = y_bin.astype(bool)
    pred = score >= threshold
    tp, fn = (y_bin & pred).sum(), (y_bin & ~pred).sum()
    fp, tn = (~y_bin & pred).sum(), (~y_bin & ~pred).sum()
    return {
        "threshold": float(threshold),
        "sensitivity": _safe_div(tp, tp + fn),
        "specificity": _safe_div(tn, tn + fp),
        "ppv": _safe_div(tp, tp + fp),
        "npv": _safe_div(tn, tn + fn),
        "auc": _auc(y_bin, score),
        "n_positive": int(y_bin.sum()),
        "n_negative": int((~y_bin).sum()),
    }


def group_bootstrap(
    groups: np.ndarray,
    metric_fn: Callable[[np.ndarray], dict[str, float]],
    group_order: list[str],
    gap: tuple[str, str] | None = None,
    n_boot: int = 1000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[dict[str, dict[str, tuple[float, float]]], dict[str, tuple[float, float]]]:
    """Bootstrap confidence intervals for each group, and for the gap between two groups.

    Each group is resampled within itself, so group sizes stay fixed. `metric_fn(indices)`
    returns a dict of metrics for those rows. With gap=("I-II", "V-VI"), the second result
    holds CIs for metric(I-II) - metric(V-VI); an interval that excludes 0 indicates a
    difference unlikely to be explained by sampling alone.
    """
    rng = np.random.default_rng(seed)
    members = {g: np.flatnonzero(groups == g) for g in group_order}
    samples: dict[str, dict[str, list[float]]] = {g: {} for g in group_order}
    gaps: dict[str, list[float]] = {}
    for _ in range(n_boot):
        res = {g: metric_fn(rng.choice(idx, len(idx), replace=True)) for g, idx in members.items() if len(idx)}
        for g, metrics in res.items():
            for k, v in metrics.items():
                samples[g].setdefault(k, []).append(v)
        if gap and gap[0] in res and gap[1] in res:
            for k in res[gap[0]]:
                gaps.setdefault(k, []).append(res[gap[0]][k] - res[gap[1]][k])

    lo, hi = 100 * alpha / 2, 100 * (1 - alpha / 2)

    def interval(v: list[float]) -> tuple[float, float]:
        return float(np.nanpercentile(v, lo)), float(np.nanpercentile(v, hi))

    group_ci = {g: {k: interval(v) for k, v in s.items()} for g, s in samples.items()}
    return group_ci, {k: interval(v) for k, v in gaps.items()}

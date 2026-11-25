"""Repeat the skin-type comparison within each image source.

The two atlases differ in population and photography, and models score much higher on Atlas
Dermatologico images. Dark-skin test images come disproportionately from that atlas, so a
pooled comparison mixes skin type with image source. This script recomputes the per-group
metrics and the light-vs-dark gap separately within each source, using each run's saved test
predictions and referral threshold (no images or GPU needed).

Example:
    python scripts/check_by_source.py runs/all_types runs/light_only runs/size_matched \
        --names "A: all skin types" "B: light skin only (I-II)" "C: all skin types, same size as B" \
        --out results/within_source.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from evaluate import fmt, md_table, per_group  # scripts/ is on the path when run as a script
from skinfair.data import GROUPS, LABELS

SOURCES = ["DermaAmin", "Atlas Dermatologico"]
METRICS = {
    "balanced_accuracy": "Balanced accuracy",
    "malignant_auc": "Malignant AUC",
    "malignant_sensitivity": "Malignant sensitivity",
    "malignant_specificity": "Malignant specificity",
}


def load_run(run: Path) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, float]:
    preds = pd.read_csv(run / "evaluation" / "predictions_test.csv")
    threshold = json.loads((run / "evaluation" / "metrics.json").read_text())["threshold"]
    y = preds["three_partition_label"].map(LABELS.index).to_numpy()
    probs = preds[[f"p_{c}" for c in LABELS]].to_numpy()
    return preds, y, probs, threshold


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("runs", nargs="+", type=Path)
    p.add_argument("--names", nargs="+", default=None, help="Display names, one per run, in the same order.")
    p.add_argument("--n-boot", type=int, default=1000)
    p.add_argument("--out", type=Path, default=None, help="Write the markdown tables here.")
    args = p.parse_args()
    names = args.names or [r.name for r in args.runs]
    if len(names) != len(args.runs):
        raise SystemExit("Give one --names entry per run.")

    runs = {name: load_run(run) for name, run in zip(names, args.runs)}
    preds = next(iter(runs.values()))[0]
    y = next(iter(runs.values()))[1]

    md = ["# Skin type results within each image source", "",
          "Test images by source and skin type group (malignant in brackets):", ""]
    rows = []
    for s in SOURCES:
        cells = []
        for g in GROUPS:
            m = ((preds["source"] == s) & (preds["group"] == g)).to_numpy()
            cells.append(f"{m.sum():,} ({(y[m] == LABELS.index('malignant')).sum()})")
        rows.append([s, *cells])
    md += [md_table(["Source", *(f"Type {g}" for g in GROUPS)], rows), ""]
    md += ["Each model's referral threshold is the one set on its validation set (all sources and skin types). "
           "95% CIs from bootstrap resampling within each group. The last column is the gap between light "
           "(I-II) and dark (V-VI) skin.", ""]

    for s in SOURCES:
        md += [f"## {s}", ""]
        results = {}
        for name, (df, y_run, probs, threshold) in runs.items():
            groups = df["group"].to_numpy(dtype=object).copy()
            groups[(df["source"] != s).to_numpy()] = None
            results[name] = per_group(groups, y_run, probs, threshold, args.n_boot)
        for key, label in METRICS.items():
            md += [f"### {label}", ""]
            rows = []
            for name, (table, gap) in results.items():
                cells = [fmt(table.loc[g, key], table.loc[g, f"{key}_lo"], table.loc[g, f"{key}_hi"])
                         if g in table.index else "n/a" for g in GROUPS]
                cells.append(fmt(gap[key]["value"], *gap[key]["ci"]) if gap else "n/a")
                rows.append([name, *cells])
            md += [md_table(["Experiment", *(f"Type {g}" for g in GROUPS), "Gap I-II minus V-VI"], rows), ""]

    text = "\n".join(md)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)


if __name__ == "__main__":
    main()

"""Compare evaluated runs by skin type group (e.g. the training-composition experiments).

Example:
    python scripts/compare_runs.py runs/all_types runs/light_only runs/size_matched \
        --names "A: all skin types" "B: light skin only" "C: all types, size of B" \
        --out results/composition_comparison.md --figure docs/figures/composition_comparison.png
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from skinfair.data import GROUPS
from skinfair.plots import plot_group_metrics

METRICS = {
    "balanced_accuracy": "Balanced accuracy",
    "malignant_auc": "Malignant AUC",
    "malignant_sensitivity": "Malignant sensitivity",
    "malignant_specificity": "Malignant specificity",
}


def fmt(v, lo=None, hi=None) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "n/a"
    return f"{v:.3f}" if lo is None else f"{v:.3f} ({lo:.2f} to {hi:.2f})"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("runs", nargs="+", type=Path)
    p.add_argument("--names", nargs="+", default=None, help="Display names, one per run, in the same order.")
    p.add_argument("--out", type=Path, default=None, help="Write the markdown tables here.")
    p.add_argument("--figure", type=Path, default=None, help="Write the comparison figure here.")
    args = p.parse_args()
    names = args.names or [r.name for r in args.runs]
    if len(names) != len(args.runs):
        raise SystemExit("Give one --names entry per run.")

    tables, gaps, configs = {}, {}, {}
    for name, run in zip(names, args.runs):
        m = json.loads((run / "evaluation" / "metrics.json").read_text())
        tables[name] = pd.DataFrame.from_dict(m["groups"]["primary"], orient="index")
        gaps[name] = m["gaps"]["primary"]
        configs[name] = json.loads((run / "config.json").read_text())

    md = ["Test-set performance by Fitzpatrick skin type group, with 95% CIs. "
          "The last column is the gap between light (I-II) and dark (V-VI) skin.", ""]
    md.append("| Experiment | Training images (I-II / III-IV / V-VI) |")
    md.append("|---|---|")
    for name, c in configs.items():
        by = c.get("train_images_by_group", {})
        md.append(f"| {name} | {c['train_images']:,} ({' / '.join(f'{by.get(g, 0):,}' for g in GROUPS)}) |")
    md.append("")
    for key, label in METRICS.items():
        md += [f"### {label}", "", "| Experiment | " + " | ".join(f"Type {g}" for g in GROUPS) + " | Gap I-II minus V-VI |",
               "|---|" + "---|" * (len(GROUPS) + 1)]
        for name, t in tables.items():
            cells = [fmt(t.loc[g, key], t.loc[g, f"{key}_lo"], t.loc[g, f"{key}_hi"]) if g in t.index else "n/a"
                     for g in GROUPS]
            gap = gaps[name].get(key)
            cells.append(fmt(gap["value"], *gap["ci"]) if gap else "n/a")
            md.append(f"| {name} | " + " | ".join(cells) + " |")
        md.append("")

    text = "\n".join(md)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n")
    if args.figure:
        args.figure.parent.mkdir(parents=True, exist_ok=True)
        plot_group_metrics(tables, METRICS, args.figure, "Test performance by skin type and training data", GROUPS)
        print(f"Figure saved to {args.figure}")


if __name__ == "__main__":
    main()

"""Evaluate a model on the test set, overall and separately for each skin type group.

Reports, with 95% bootstrap confidence intervals:
  * overall and per-class performance (benign / malignant / non-neoplastic)
  * for each Fitzpatrick group (I-II, III-IV, V-VI): accuracy, balanced accuracy, and the
    malignant-vs-rest referral decision (AUC; sensitivity and specificity at ONE threshold,
    fixed on the validation set for 90% sensitivity across all skin types)
  * the gap between light (I-II) and dark (V-VI) skin for each metric
  * robustness checks: the same analysis with the second annotator's skin types, and with
    only the images where both annotators agree on the group
  * performance by image source (the two atlases)

Example:
    python scripts/evaluate.py --run runs/all_types
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score
from torch.utils.data import DataLoader

from skinfair.data import GROUPS, LABELS, SkinDataset, build_transforms
from skinfair.engine import predict
from skinfair.metrics import (
    binary_metrics,
    bootstrap_ci,
    group_bootstrap,
    per_class_metrics,
    summary_metrics,
    threshold_for_sensitivity,
)
from skinfair.model import get_device, load_checkpoint
from skinfair.plots import plot_group_metrics

MAL = LABELS.index("malignant")
METRICS = {
    "accuracy": "Accuracy",
    "balanced_accuracy": "Balanced accuracy",
    "malignant_auc": "Malignant AUC",
    "malignant_sensitivity": "Malignant sensitivity",
    "malignant_specificity": "Malignant specificity",
}
PLOT_METRICS = {k: METRICS[k] for k in ("balanced_accuracy", "malignant_auc",
                                         "malignant_sensitivity", "malignant_specificity")}
GAP = ("I-II", "V-VI")


def group_metrics(y: np.ndarray, probs: np.ndarray, threshold: float) -> dict[str, float]:
    pred = probs.argmax(1)
    b = binary_metrics(y == MAL, probs[:, MAL], threshold)
    return {
        "accuracy": float((pred == y).mean()),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "malignant_auc": b["auc"],
        "malignant_sensitivity": b["sensitivity"],
        "malignant_specificity": b["specificity"],
    }


def per_group(groups: np.ndarray, y: np.ndarray, probs: np.ndarray, threshold: float,
              n_boot: int) -> tuple[pd.DataFrame, dict]:
    """Per-group table with CIs, and the I-II minus V-VI gap with its CI."""
    fn = lambda idx: group_metrics(y[idx], probs[idx], threshold)  # noqa: E731
    ci, gap_ci = group_bootstrap(groups, fn, GROUPS, gap=GAP, n_boot=n_boot)
    rows = []
    for g in GROUPS:
        idx = np.flatnonzero(groups == g)
        if not len(idx):
            continue
        row = {"group": g, "n": len(idx), "n_malignant": int((y[idx] == MAL).sum())}
        for k, v in fn(idx).items():
            row[k] = v
            row[f"{k}_lo"], row[f"{k}_hi"] = ci[g][k]
        rows.append(row)
    table = pd.DataFrame(rows).set_index("group")
    gap = {}
    if all(g in table.index for g in GAP):
        gap = {k: {"value": float(table.loc[GAP[0], k] - table.loc[GAP[1], k]), "ci": list(gap_ci[k])}
               for k in METRICS}
    return table, gap


def fmt(v: float, lo: float | None = None, hi: float | None = None) -> str:
    if v is None or np.isnan(v):
        return "n/a"
    return f"{v:.3f}" if lo is None else f"{v:.3f} ({lo:.2f} to {hi:.2f})"


def md_table(header: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(out + ["| " + " | ".join(map(str, r)) + " |" for r in rows])


def group_section(title: str, table: pd.DataFrame, gap: dict, note: str = "") -> list[str]:
    md = [f"### {title}", ""] + ([note, ""] if note else [])
    rows = [[f"Type {g}", int(r["n"]), int(r["n_malignant"]),
             *[fmt(r[k], r[f"{k}_lo"], r[f"{k}_hi"]) for k in METRICS]] for g, r in table.iterrows()]
    if gap:
        rows.append([f"**Gap: {GAP[0]} minus {GAP[1]}**", "", "",
                     *[fmt(gap[k]["value"], *gap[k]["ci"]) for k in METRICS]])
    md.append(md_table(["Skin type", "Images", "Malignant", *METRICS.values()], rows))
    return md + [""]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--data-dir", type=Path, default=Path("data/processed"))
    p.add_argument("--target-sensitivity", type=float, default=0.90)
    p.add_argument("--n-boot", type=int, default=1000)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--device", default=None)
    args = p.parse_args()
    warnings.filterwarnings("ignore")

    device = get_device(args.device)
    model, ckpt = load_checkpoint(args.run, device)
    config = json.loads((args.run / "config.json").read_text())
    transform = build_transforms(ckpt["img_size"], train=False)
    out_dir = args.run / "evaluation"
    out_dir.mkdir(exist_ok=True)

    meta = pd.read_csv(args.data_dir / "metadata.csv")
    preds = {}
    for split in ("val", "test"):
        df = meta[meta["split"] == split].reset_index(drop=True)
        loader = DataLoader(SkinDataset(df, args.data_dir / "images", transform),
                            batch_size=args.batch_size, num_workers=args.num_workers)
        print(f"Predicting {split} ({len(df)} images)...")
        probs, y = predict(model, loader, device)
        preds[split] = (df, probs, y)

    val_df, val_probs, val_y = preds["val"]
    threshold = threshold_for_sensitivity(val_y == MAL, val_probs[:, MAL], args.target_sensitivity)
    df, probs, y = preds["test"]
    out = df.copy()
    out["pred"] = [LABELS[i] for i in probs.argmax(1)]
    for k, c in enumerate(LABELS):
        out[f"p_{c}"] = probs[:, k]
    out.to_csv(out_dir / "predictions_test.csv", index=False)

    # Overall
    summary = summary_metrics(y, probs)
    per_class = per_class_metrics(y, probs, LABELS)
    overall = group_metrics(y, probs, threshold)
    ci = bootstrap_ci(lambda idx: {**summary_metrics(y[idx], probs[idx]),
                                   **group_metrics(y[idx], probs[idx], threshold)}, len(y), n_boot=args.n_boot)

    # By skin type: primary labels, second annotator, and agreed subset
    tables, gaps = {}, {}
    tables["primary"], gaps["primary"] = per_group(df["group"].to_numpy(), y, probs, threshold, args.n_boot)
    tables["second_annotator"], gaps["second_annotator"] = per_group(
        df["group_centaur"].to_numpy(), y, probs, threshold, args.n_boot)
    agreed = df["group"].to_numpy(dtype=object).copy()
    agreed[(df["group"] != df["group_centaur"]).to_numpy()] = None
    tables["agreed"], gaps["agreed"] = per_group(agreed, y, probs, threshold, args.n_boot)

    # By image source
    sources = {s: group_metrics(y[idx], probs[idx], threshold) | {"n": len(idx)}
               for s, idx in df.groupby("source").indices.items() if len(idx) >= 30}

    plot_group_metrics({args.run.name: tables["primary"]}, PLOT_METRICS, out_dir / "by_skin_type.png",
                       f"{args.run.name}: test performance by Fitzpatrick skin type", GROUPS)

    trained_on = config.get("train_images_by_group", {})
    md = [f"# Evaluation: {args.run.name}", "",
          f"Trained on {config.get('train_images', '?'):,} images "
          f"({', '.join(f'type {g}: {n:,}' for g, n in trained_on.items())}). "
          f"Best epoch {ckpt['epoch']}.",
          f"Malignant referral threshold, set on the validation set (all skin types) for "
          f"{args.target_sensitivity:.0%} sensitivity: {threshold:.3f}. The same threshold is applied to every group.",
          "", f"## Overall (test set, {len(df):,} images)", ""]
    md.append(md_table(["Metric", "Value (95% CI)"], [
        [label, fmt(v, *ci[k])] for k, label in
        [("balanced_accuracy", "Balanced accuracy"), ("accuracy", "Accuracy"), ("macro_auc", "Macro AUC"),
         ("malignant_auc", "Malignant AUC"), ("malignant_sensitivity", "Malignant sensitivity"),
         ("malignant_specificity", "Malignant specificity")]
        for v in [overall.get(k, summary.get(k))]]))
    md += ["", md_table(["Class", "Images", "Sensitivity", "Specificity", "AUC"],
                        [[c, int(r["support"]), fmt(r["sensitivity"]), fmt(r["specificity"]), fmt(r["auc"])]
                         for c, r in per_class.iterrows()]), ""]
    md += ["## By Fitzpatrick skin type", ""]
    md += group_section("Primary skin type labels (Scale AI)", tables["primary"], gaps["primary"],
                        "95% CIs from bootstrap resampling within each group. A gap whose CI excludes 0 is "
                        "unlikely to be explained by sampling variation alone.")
    md += group_section("Robustness: second annotator's labels (Centaur Labs)", tables["second_annotator"],
                        gaps["second_annotator"])
    md += group_section("Robustness: only images where both annotators agree on the group",
                        tables["agreed"], gaps["agreed"])
    md += ["## By image source", "",
           md_table(["Source", "Images", *METRICS.values()],
                    [[s, m["n"], *[fmt(m[k]) for k in METRICS]] for s, m in sources.items()]), ""]

    results = {"threshold": threshold, "overall": {**summary, **overall}, "overall_ci": ci,
               "per_class": per_class.to_dict(orient="index"),
               "groups": {k: t.to_dict(orient="index") for k, t in tables.items()},
               "gaps": gaps, "sources": sources, "trained_on": trained_on}
    (out_dir / "metrics.json").write_text(json.dumps(results, indent=2, default=float))
    (out_dir / "report.md").write_text("\n".join(md))
    print("\n".join(md))
    print(f"\nSaved to {out_dir}/")


if __name__ == "__main__":
    main()

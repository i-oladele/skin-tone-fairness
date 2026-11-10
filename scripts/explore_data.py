"""Describe the dataset before any modelling: how skin types are represented, how much
cleaning removed, and how far the two skin type annotators agree.

Needs only the metadata files (no images).

Outputs:
    results/data_overview.md
    docs/figures/images_by_skin_type.png
    docs/figures/annotator_agreement.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

from skinfair.data import FST_GROUP, GROUPS, LABELS, load_metadata
from skinfair.plots import plot_agreement, plot_counts_by_type

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}


def md_table(df: pd.DataFrame, index_name: str, percent_cols: tuple[str, ...] = ()) -> str:
    cols = [index_name, *map(str, df.columns)]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for idx, row in df.iterrows():
        cells = [f"{v:.1%}" if c in percent_cols else f"{int(v):,}" for c, v in row.items()]
        lines.append("| " + " | ".join([str(idx), *cells]) + " |")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    p.add_argument("--out", type=Path, default=Path("results/data_overview.md"))
    p.add_argument("--fig-dir", type=Path, default=Path("docs/figures"))
    args = p.parse_args()
    args.fig_dir.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    original = pd.read_csv(args.raw_dir / "fitzpatrick17k.csv")
    meta = load_metadata(args.raw_dir)
    known = meta[meta["fst"] > 0]

    # Representation
    by_type = known["fst"].value_counts().sort_index()
    by_type.index = [ROMAN[i] for i in by_type.index]
    plot_counts_by_type(by_type, args.fig_dir / "images_by_skin_type.png",
                        "Fitzpatrick17k-C: images per Fitzpatrick skin type")
    mix = pd.crosstab(known["group"], known["three_partition_label"]).reindex(index=GROUPS, columns=LABELS)
    mix["total"] = mix.sum(axis=1)
    share = (mix["total"] / mix["total"].sum()).rename("share of images")

    # Annotator agreement (both annotators gave a type 1-6)
    both = known[known["fst_centaur"] > 0]
    exact = (both["fst"] == both["fst_centaur"]).mean()
    within1 = ((both["fst"] - both["fst_centaur"]).abs() <= 1).mean()
    kappa = cohen_kappa_score(both["fst"], both["fst_centaur"], weights="quadratic")
    same_group = (both["fst"].map(FST_GROUP) == both["fst_centaur"].map(FST_GROUP)).mean()
    differ = both[both["fst"] != both["fst_centaur"]]
    centaur_lighter = (differ["fst_centaur"] < differ["fst"]).mean()
    matrix = pd.crosstab(both["fst"], both["fst_centaur"]).rename(index=ROMAN, columns=ROMAN)
    plot_agreement(matrix, args.fig_dir / "annotator_agreement.png",
                   "Fitzpatrick type given by two annotation services", "Centaur Labs", "Scale AI")

    md = [
        "# Data overview", "",
        f"- Original Fitzpatrick17k: {len(original):,} images.",
        f"- Fitzpatrick17k-C (duplicates and erroneous images removed): {len(meta):,} images "
        f"({1 - len(meta) / len(original):.0%} removed).",
        f"- With a Fitzpatrick skin type: {len(known):,} images.", "",
        "## Skin type representation", "",
        md_table(mix.join(share), "Skin type group", percent_cols=("share of images",)), "",
        "## Agreement between the two skin type annotators", "",
        f"Images typed by both Scale AI and Centaur Labs: {len(both):,}.", "",
        f"- Same Fitzpatrick type: {exact:.1%}",
        f"- Within one type: {within1:.1%}",
        f"- Same group (I-II / III-IV / V-VI): {same_group:.1%}",
        f"- Quadratic-weighted Cohen's kappa: {kappa:.2f}",
        f"- When they disagree, Centaur Labs gives the lighter type {centaur_lighter:.0%} of the time", "",
    ]
    args.out.write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()

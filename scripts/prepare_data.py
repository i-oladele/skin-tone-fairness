"""Resize the downloaded images and write the analysis metadata.

Starts from Fitzpatrick17k-C (Abhishek et al., 2025), which removes duplicate and erroneous
images from Fitzpatrick17k and defines leakage-free train/val/test splits. Then excludes:
  * images with no Fitzpatrick skin type (annotated -1)
  * images a dermatologist marked "wrongly labelled" in the quality-control subset
  * images that could not be obtained or opened

Outputs in data/processed/:
    images/<md5hash>.jpg    shorter side resized to 256 px
    metadata.csv            one row per usable image, with split, label, skin type and source
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from PIL import Image
from tqdm import tqdm

from skinfair.data import GROUPS, LABELS, load_metadata


def resize(src: Path, dst: Path, size: int) -> bool:
    if dst.exists():
        return True
    try:
        with Image.open(src) as im:
            im = im.convert("RGB")
            w, h = im.size
            scale = size / min(w, h)
            im.resize((round(w * scale), round(h * scale)), Image.LANCZOS).save(dst, quality=95)
        return True
    except Exception as e:  # unreadable or truncated file
        print(f"Could not read {src.name}: {e}")
        return False


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    p.add_argument("--out-dir", type=Path, default=Path("data/processed"))
    p.add_argument("--size", type=int, default=256)
    args = p.parse_args()

    meta = load_metadata(args.raw_dir)
    steps = [("Fitzpatrick17k-C", len(meta))]

    meta = meta[meta["group"].notna()]
    steps.append(("with a Fitzpatrick skin type", len(meta)))
    meta = meta[meta["qc"] != "3 Wrongly labelled"]
    steps.append(("not marked wrongly labelled", len(meta)))

    out_images = args.out_dir / "images"
    out_images.mkdir(parents=True, exist_ok=True)
    raw_images = args.raw_dir / "images"
    ok = [
        (raw_images / f"{h}.jpg").exists() and resize(raw_images / f"{h}.jpg", out_images / f"{h}.jpg", args.size)
        for h in tqdm(meta["md5hash"], desc="resizing")
    ]
    meta = meta[ok]
    steps.append(("image available", len(meta)))

    meta.to_csv(args.out_dir / "metadata.csv", index=False)

    print("\nImages kept at each step:")
    for name, n in steps:
        print(f"  {name:32} {n:6,}")
    print("\nImages per split, skin type group and diagnosis group:")
    table = pd.crosstab([meta["split"], meta["group"]], meta["three_partition_label"])
    print(table.reindex(columns=LABELS).to_string())
    missing = [g for g in GROUPS if g not in set(meta["group"])]
    if missing:
        print(f"\nWarning: no images for skin type group(s) {missing}")


if __name__ == "__main__":
    main()

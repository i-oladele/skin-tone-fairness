"""Fine-tune an ImageNet-pretrained CNN to classify clinical skin images as benign,
malignant or non-neoplastic.

The skin types in the training set can be restricted, to test how training-data
composition affects performance on other skin types. The validation set always contains
all skin types, so model selection is the same for every experiment.

Examples:
    # A: all skin types
    python scripts/train.py --run-name all_types
    # B: light skin only (Fitzpatrick I-II)
    python scripts/train.py --run-name light_only --train-groups I-II
    # C: all skin types, but the same size and diagnosis mix as B
    python scripts/train.py --run-name all_types_size_matched --size-match I-II
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, WeightedRandomSampler

from skinfair.data import GROUPS, LABELS, SkinDataset, build_transforms
from skinfair.engine import predict, train_one_epoch, warmup_cosine
from skinfair.metrics import summary_metrics
from skinfair.model import ARCHS, build_model, get_device


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", type=Path, default=Path("data/processed"))
    p.add_argument("--runs-dir", type=Path, default=Path("runs"))
    p.add_argument("--run-name", required=True)
    p.add_argument("--train-groups", default=",".join(GROUPS),
                   help=f"Comma-separated skin type groups to train on (from {GROUPS}).")
    p.add_argument("--size-match", default=None, metavar="GROUPS",
                   help="Subsample the training set to the size and diagnosis mix these groups would "
                        "have on their own (e.g. I-II), drawing from all --train-groups.")
    p.add_argument("--arch", default="efficientnet_b0", choices=ARCHS)
    p.add_argument("--img-size", type=int, default=224)
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--weight-decay", type=float, default=1e-2)
    p.add_argument("--imbalance", choices=["weighted_loss", "sampler", "none"], default="weighted_loss")
    p.add_argument("--patience", type=int, default=6)
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--limit", type=int, default=None, help="Use only N train and N val images (smoke test).")
    p.add_argument("--device", default=None)
    return p.parse_args()


def parse_groups(text: str) -> list[str]:
    groups = [g.strip() for g in text.split(",") if g.strip()]
    unknown = set(groups) - set(GROUPS)
    if unknown:
        raise SystemExit(f"Unknown skin type group(s) {sorted(unknown)}; choose from {GROUPS}")
    return groups


def size_matched(pool: pd.DataFrame, reference: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Sample from `pool` the same number of images per diagnosis group as `reference` has."""
    counts = reference["three_partition_label"].value_counts()
    parts = [pool[pool["three_partition_label"] == label].sample(n, random_state=seed)
             for label, n in counts.items()]
    return pd.concat(parts)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    device = get_device(args.device)
    run_dir = args.runs_dir / args.run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = pd.read_csv(args.data_dir / "metadata.csv")
    train_df = meta[(meta["split"] == "train") & meta["group"].isin(parse_groups(args.train_groups))]
    if args.size_match:
        reference = meta[(meta["split"] == "train") & meta["group"].isin(parse_groups(args.size_match))]
        train_df = size_matched(train_df, reference, args.seed)
    val_df = meta[meta["split"] == "val"]
    if args.limit:
        train_df = train_df.sample(min(args.limit, len(train_df)), random_state=args.seed)
        val_df = val_df.sample(min(args.limit, len(val_df)), random_state=args.seed)

    image_dir = args.data_dir / "images"
    train_ds = SkinDataset(train_df, image_dir, build_transforms(args.img_size, train=True))
    val_ds = SkinDataset(val_df, image_dir, build_transforms(args.img_size, train=False))

    labels = np.array(train_ds.labels)
    counts = np.bincount(labels, minlength=len(LABELS)).clip(min=1)
    print(f"Device: {device} | train {len(train_ds)} | val {len(val_ds)}")
    print("Training images by skin type group:", train_df["group"].value_counts().reindex(GROUPS, fill_value=0).to_dict())
    print("Training images by diagnosis group:", dict(zip(LABELS, counts.tolist())))

    loader_kw = dict(num_workers=args.num_workers, persistent_workers=args.num_workers > 0)
    sampler, class_weights = None, None
    if args.imbalance == "weighted_loss":
        class_weights = torch.tensor(len(labels) / (len(LABELS) * counts), dtype=torch.float32)
    elif args.imbalance == "sampler":
        sampler = WeightedRandomSampler(1.0 / counts[labels], num_samples=len(labels), replacement=True)

    train_loader = DataLoader(train_ds, args.batch_size, shuffle=sampler is None, sampler=sampler,
                              drop_last=True, **loader_kw)
    val_loader = DataLoader(val_ds, args.batch_size * 2, shuffle=False, **loader_kw)

    model = build_model(args.arch, len(LABELS)).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights.to(device) if class_weights is not None else None)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = warmup_cosine(optimizer, warmup_steps=len(train_loader), total_steps=args.epochs * len(train_loader))

    config = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}
    config.update(device=str(device), train_images=len(train_ds), val_images=len(val_ds),
                  train_images_by_group=train_df["group"].value_counts().reindex(GROUPS, fill_value=0).to_dict())
    (run_dir / "config.json").write_text(json.dumps(config, indent=2))
    train_df[["md5hash"]].to_csv(run_dir / "train_images.csv", index=False)

    history, best, stale = [], -1.0, 0
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, scheduler, device)
        probs, y = predict(model, val_loader, device)
        m = summary_metrics(y, probs)
        val_loss = float(-np.log(probs[np.arange(len(y)), y].clip(1e-12)).mean())
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss,
                        **{f"val_{k}": v for k, v in m.items()}, "seconds": time.time() - t0})
        print(f"Epoch {epoch:2d}/{args.epochs} | train loss {train_loss:.3f} | val loss {val_loss:.3f} | "
              f"bal acc {m['balanced_accuracy']:.3f} | macro AUC {m['macro_auc']:.3f} | {time.time() - t0:.0f}s")

        if m["balanced_accuracy"] > best:
            best, stale = m["balanced_accuracy"], 0
            torch.save({"model": model.state_dict(), "arch": args.arch, "classes": LABELS,
                        "img_size": args.img_size, "epoch": epoch, "val_metrics": m}, run_dir / "best.pt")
        else:
            stale += 1
            if stale >= args.patience:
                print(f"No improvement for {args.patience} epochs; stopping early.")
                break

    pd.DataFrame(history).to_csv(run_dir / "history.csv", index=False)
    print(f"\nBest validation balanced accuracy: {best:.3f}. Saved to {run_dir}/best.pt")


if __name__ == "__main__":
    main()

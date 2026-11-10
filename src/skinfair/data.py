"""Labels, skin-type groups, metadata, the PyTorch dataset and image transforms."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms as T

# Diagnosis groups from Fitzpatrick17k's "three_partition_label". Index i in model output = LABELS[i].
LABELS = ["benign", "malignant", "non-neoplastic"]

# Fitzpatrick skin types grouped into light / medium / dark, as in most dermatology fairness work.
FST_GROUP = {1: "I-II", 2: "I-II", 3: "III-IV", 4: "III-IV", 5: "V-VI", 6: "V-VI"}
GROUPS = ["I-II", "III-IV", "V-VI"]

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def source_of(url: str) -> str:
    if "dermaamin" in str(url):
        return "DermaAmin"
    if "atlasdermatologico" in str(url):
        return "Atlas Dermatologico"
    return "unknown"


def load_metadata(raw_dir: Path) -> pd.DataFrame:
    """Fitzpatrick17k-C (cleaned rows and splits) joined with both skin-type annotations.

    fst:          Fitzpatrick type from Scale AI (the label used in the original paper)
    fst_centaur:  Fitzpatrick type from Centaur Labs (second annotation, for robustness checks)
    -1 means the annotator could not tell; those images get no group.
    """
    raw_dir = Path(raw_dir)
    cleaned = pd.read_csv(raw_dir / "Fitzpatrick17k-C.csv")
    original = pd.read_csv(raw_dir / "fitzpatrick17k.csv",
                           usecols=["md5hash", "fitzpatrick_scale", "fitzpatrick_centaur"])
    df = cleaned[["md5hash", "partition", "label", "nine_partition_label", "three_partition_label", "qc", "url"]]
    df = df.merge(original, on="md5hash", how="left", validate="one_to_one")
    df = df.rename(columns={"partition": "split", "label": "condition", "fitzpatrick_scale": "fst",
                            "fitzpatrick_centaur": "fst_centaur"})
    df["group"] = df["fst"].map(FST_GROUP)
    df["group_centaur"] = df["fst_centaur"].map(FST_GROUP)
    df["source"] = df["url"].map(source_of)
    return df


class SkinDataset(Dataset):
    """Loads `<image_dir>/<md5hash>.jpg` and returns (image_tensor, label_index)."""

    def __init__(self, df: pd.DataFrame, image_dir: Path, transform):
        self.ids = df["md5hash"].tolist()
        self.labels = df["three_partition_label"].map(LABELS.index).tolist()
        self.image_dir = Path(image_dir)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.ids)

    def __getitem__(self, i: int):
        with Image.open(self.image_dir / f"{self.ids[i]}.jpg") as im:
            img = im.convert("RGB")
        return self.transform(img), self.labels[i]


def build_transforms(img_size: int = 224, train: bool = False) -> T.Compose:
    normalise = [T.ToTensor(), T.Normalize(IMAGENET_MEAN, IMAGENET_STD)]
    if not train:
        return T.Compose([T.Resize(img_size), T.CenterCrop(img_size), *normalise])
    return T.Compose(
        [
            T.RandomResizedCrop(img_size, scale=(0.5, 1.0)),
            T.RandomHorizontalFlip(),
            T.RandomVerticalFlip(),
            # Brightness and contrast only: hue and saturation changes would alter apparent skin
            # tone, which is the very attribute this project studies.
            T.ColorJitter(brightness=0.15, contrast=0.15),
            *normalise,
        ]
    )

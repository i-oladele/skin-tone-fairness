"""Model construction (ImageNet-pretrained CNNs from torchvision) and checkpoint loading."""

from __future__ import annotations

from pathlib import Path

import torch
from torch import nn
from torchvision import models

ARCHS = ["efficientnet_b0", "resnet50", "convnext_tiny"]


def build_model(arch: str, num_classes: int, pretrained: bool = True) -> nn.Module:
    if arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights="IMAGENET1K_V1" if pretrained else None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif arch == "resnet50":
        model = models.resnet50(weights="IMAGENET1K_V2" if pretrained else None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    elif arch == "convnext_tiny":
        model = models.convnext_tiny(weights="IMAGENET1K_V1" if pretrained else None)
        model.classifier[2] = nn.Linear(model.classifier[2].in_features, num_classes)
    else:
        raise ValueError(f"Unknown architecture {arch!r}; choose from {ARCHS}")
    return model



def get_device(name: str | None = None) -> torch.device:
    if name:
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_checkpoint(run_dir: Path, device: torch.device) -> tuple[nn.Module, dict]:
    ckpt = torch.load(Path(run_dir) / "best.pt", map_location="cpu", weights_only=True)
    model = build_model(ckpt["arch"], len(ckpt["classes"]), pretrained=False)
    model.load_state_dict(ckpt["model"])
    return model.to(device).eval(), ckpt

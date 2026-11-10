"""Figures. Colours and mark styles follow one fixed, colour-blind-checked palette."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
# Categorical slots in fixed order; the first three are distinguishable for colour-blind readers.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK_2, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "font.size": 10, "legend.frameon": False,
})


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_group_metrics(results: dict[str, pd.DataFrame], metrics: dict[str, str], path: Path,
                       title: str, groups: list[str]) -> None:
    """Point estimates with 95% CI per skin type group, one panel per metric.

    results: {series name: DataFrame indexed by group with columns <metric>, <metric>_lo, <metric>_hi}.
    Series colours follow the order of `results`, so pass experiments in a fixed order.
    """
    names = list(results)
    fig, axes = plt.subplots(1, len(metrics), figsize=(3.3 * len(metrics), 3.6), sharey=True, squeeze=False)
    offsets = np.linspace(-0.18, 0.18, len(names)) if len(names) > 1 else [0.0]
    x = np.arange(len(groups))
    for ax, (key, label) in zip(axes[0], metrics.items()):
        for name, off, colour in zip(names, offsets, SERIES):
            df = results[name].reindex(groups)
            ax.errorbar(x + off, df[key], yerr=[df[key] - df[f"{key}_lo"], df[f"{key}_hi"] - df[key]],
                        fmt="none", ecolor=colour, elinewidth=1.5, capsize=0)
            ax.plot(x + off, df[key], "o", color=colour, markersize=7, markeredgecolor=SURFACE,
                    markeredgewidth=1.5, label=name, zorder=3)
        ax.set_xticks(x, [f"Type {g}" for g in groups])
        ax.set_xlim(-0.6, len(groups) - 0.4)
        ax.set_ylim(0, 1.02)
        ax.set_title(label, fontsize=10)
    axes[0][0].set_ylabel("Score (95% CI)")
    if len(names) > 1:
        fig.legend(*axes[0][0].get_legend_handles_labels(), loc="upper center",
                   bbox_to_anchor=(0.5, 1.0), ncol=len(names), fontsize=9)
        fig.suptitle(title, y=1.08, fontsize=11)
    else:
        fig.suptitle(title, fontsize=11)
    _save(fig, path)


def plot_counts_by_type(counts: pd.Series, path: Path, title: str) -> None:
    """Single-series column chart of image counts per Fitzpatrick type."""
    fig, ax = plt.subplots(figsize=(6, 3.4))
    x = np.arange(len(counts))
    ax.bar(x, counts.values, width=0.5, color=SERIES[0])
    for xi, v in zip(x, counts.values):
        ax.text(xi, v, f"{v:,}", ha="center", va="bottom", fontsize=9, color=INK_2)
    ax.set_xticks(x, [f"Type {i}" for i in counts.index])
    ax.set_ylim(0, counts.max() * 1.12)
    ax.set_ylabel("Images")
    ax.set_title(title, fontsize=11)
    _save(fig, path)


def plot_agreement(matrix: pd.DataFrame, path: Path, title: str, xlabel: str, ylabel: str) -> None:
    """Heatmap of counts with a single-hue sequential ramp."""
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list("seq", SEQUENTIAL)
    values = matrix.to_numpy()
    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    ax.imshow(values, cmap=cmap)
    ax.grid(False)
    threshold = values.max() * 0.55
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(j, i, f"{values[i, j]:,}", ha="center", va="center", fontsize=8,
                    color="#ffffff" if values[i, j] > threshold else INK)
    ax.set_xticks(range(values.shape[1]), matrix.columns)
    ax.set_yticks(range(values.shape[0]), matrix.index)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)
    for spine in ax.spines.values():
        spine.set_visible(False)
    _save(fig, path)

"""Fast tests that need no images or GPU."""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from skinfair.data import FST_GROUP, GROUPS, LABELS, source_of
from skinfair.metrics import (
    binary_metrics,
    group_bootstrap,
    per_class_metrics,
    summary_metrics,
    threshold_for_sensitivity,
)

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_skin_type_groups():
    assert [FST_GROUP[t] for t in range(1, 7)] == ["I-II", "I-II", "III-IV", "III-IV", "V-VI", "V-VI"]
    assert -1 not in FST_GROUP  # unknown skin type gets no group
    assert set(FST_GROUP.values()) == set(GROUPS)


def test_source_of():
    assert source_of("https://www.dermaamin.com/site/images/x.jpg") == "DermaAmin"
    assert source_of("http://atlasdermatologico.com.br/img?imageId=1") == "Atlas Dermatologico"
    assert source_of(float("nan")) == "unknown"


def test_size_matched_copies_reference_label_mix():
    train = load_script("train")
    rng = np.random.default_rng(0)
    pool = pd.DataFrame({"three_partition_label": rng.choice(LABELS, 1000),
                         "group": rng.choice(GROUPS, 1000)})
    reference = pool[pool["group"] == "I-II"]
    sample = train.size_matched(pool, reference, seed=0)
    assert len(sample) == len(reference)
    assert sample["three_partition_label"].value_counts().equals(reference["three_partition_label"].value_counts())
    assert sample["group"].nunique() == 3  # drawn from all groups, not just I-II


def test_metrics_on_perfect_predictions():
    y = np.repeat(np.arange(3), 10)
    probs = np.eye(3)[y] * 0.9 + 0.1 / 3
    pc = per_class_metrics(y, probs, LABELS)
    assert (pc[["sensitivity", "specificity", "f1", "auc"]] == 1).all().all()
    assert summary_metrics(y, probs)["balanced_accuracy"] == 1


def test_threshold_reaches_target_sensitivity():
    rng = np.random.default_rng(1)
    y = rng.random(500) < 0.2
    score = rng.random(500) + y * 0.3
    for target in (0.8, 0.9, 0.95):
        thr = threshold_for_sensitivity(y, score, target)
        assert binary_metrics(y, score, thr)["sensitivity"] >= target


def test_group_bootstrap_detects_a_real_gap_and_not_a_fake_one():
    rng = np.random.default_rng(2)
    groups = np.repeat(["I-II", "III-IV", "V-VI"], 300)
    correct_real = np.concatenate([rng.random(300) < 0.9, rng.random(300) < 0.8, rng.random(300) < 0.6])
    correct_none = rng.random(900) < 0.8

    for correct, expect_gap in [(correct_real, True), (correct_none, False)]:
        ci, gap = group_bootstrap(groups, lambda idx: {"acc": correct[idx].mean()}, GROUPS,
                                  gap=("I-II", "V-VI"), n_boot=300)
        lo, hi = gap["acc"]
        assert (lo > 0) == expect_gap
        for g in GROUPS:
            point = correct[groups == g].mean()
            assert ci[g]["acc"][0] <= point <= ci[g]["acc"][1]


def test_group_bootstrap_ignores_missing_groups():
    groups = np.array(["I-II"] * 50 + [None] * 10, dtype=object)
    ci, gap = group_bootstrap(groups, lambda idx: {"n": float(len(idx))}, GROUPS, gap=("I-II", "V-VI"), n_boot=20)
    assert ci["I-II"]["n"] == (50.0, 50.0)
    assert ci["V-VI"] == {} and gap == {}

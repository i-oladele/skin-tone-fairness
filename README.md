# Skin tone fairness

**Evaluating how skin disease classification performs across Fitzpatrick skin types**

Dermatology AI is mostly trained on images of lighter skin. This project measures whether a skin disease classifier performs worse on darker skin. It also tests how much of any gap comes from the skin-type mix of the training data rather than simply its size.

> **Research and education only.** Not a medical device and not for clinical use.

**Status:** complete. Three models were trained on the full image set (11,394 images, every one checked against its MD5 fingerprint) on a Google Colab T4 GPU. See [Results](#results).

**In short:** a model trained on all skin types performed about equally on light and dark skin. A model trained only on light skin did much worse on dark skin (balanced accuracy 0.48 vs 0.66). Training on all skin types with the *same number* of images closed most of that gap, so the cause was the missing skin types, not the smaller training set. Equal performance in the pooled test set partly reflects which atlas the images came from: within a single atlas, a smaller gap of about 5 points remains possible.

## Questions

1. Does a classifier trained on all skin types perform equally well on light (Fitzpatrick I–II), medium (III–IV) and dark (V–VI) skin?
2. If it is trained only on light skin, how much does performance on darker skin drop?
3. Is that drop caused by the *lack of diverse skin types*, or just by *less training data*?

## Scope

- **Images:** clinical photographs (not dermoscopy) from two online dermatology atlases, DermaAmin and Atlas Dermatologico, covering 114 skin conditions.
- **Task:** classify each image as **benign**, **malignant** or **non-neoplastic** (inflammatory, genetic and other conditions), the dataset's three-way grouping. The malignant-vs-rest decision is also analysed as a referral decision.
- **Skin tone:** measured with the Fitzpatrick scale. It was designed to classify how skin reacts to sun, not skin colour, and here it was estimated from photographs by crowd annotators. It is an imperfect proxy (see [Annotator agreement](#annotator-agreement)).

This is a companion to [MelanCare](https://github.com/i-oladele/melancare), which classifies dermoscopic images of pigmented lesions. That dataset (HAM10000) has no skin tone labels and is predominantly lighter skin, which motivates this project.

## Data

[Fitzpatrick17k](https://github.com/mattgroh/fitzpatrick17k) (Groh et al., 2021) contains 16,577 clinical images with Fitzpatrick skin type labels from two annotation services, Scale AI and Centaur Labs.

An independent audit (Abhishek et al., 2025) found duplicate images, train/test leakage and erroneous images in it. It released a cleaned version, **[Fitzpatrick17k-C](https://zenodo.org/records/12739457)**, with leakage-free train/validation/test splits. This project uses Fitzpatrick17k-C and its splits. It then excludes images with no skin type label (296) and images a dermatologist marked "wrongly labelled" (12).

| Step | Images |
|---|---:|
| Fitzpatrick17k | 16,577 |
| Fitzpatrick17k-C (duplicates and erroneous images removed) | 11,394 (31% removed) |
| With a Fitzpatrick skin type | 11,098 |

### Data access

Images are distributed as links to the original atlas websites. In November 2026, **every DermaAmin link tested was broken** (15 of 15 sampled; DermaAmin hosts 76% of the images), while most Atlas Dermatologico links still worked (14 of 15). The dataset authors provide the full image set on request. [`download_images.py`](scripts/download_images.py) handles both routes and checks every image against the MD5 fingerprint in the metadata, so images from any source are matched exactly. The results below use the authors' full set, in which all 11,394 Fitzpatrick17k-C images matched.

### Skin type representation

<img src="docs/figures/images_by_skin_type.png" width="560" alt="Bar chart of images per Fitzpatrick skin type: I 2,353; II 3,649; III 2,160; IV 1,684; V 879; VI 373">

| Skin type group | Benign | Malignant | Non-neoplastic | Total | Share |
|---|---:|---:|---:|---:|---:|
| I–II (light) | 824 | 934 | 4,244 | 6,002 | 54.1% |
| III–IV (medium) | 514 | 559 | 2,771 | 3,844 | 34.6% |
| V–VI (dark) | 125 | 130 | 997 | 1,252 | 11.3% |

Dark skin makes up 11% of the images, and there are only 130 malignant lesions on type V–VI skin in the whole dataset (about 22 in the test set). Any estimate of malignancy detection on dark skin will therefore carry wide confidence intervals. This scarcity is itself one of the problems the project highlights.

### Annotator agreement

<img src="docs/figures/annotator_agreement.png" width="440" alt="Heatmap comparing Fitzpatrick types given by Scale AI and Centaur Labs; most disagreements lie one type apart, with Centaur Labs usually giving the lighter type">

For the 10,635 images typed by both services:

| Measure | Value |
|---|---:|
| Same Fitzpatrick type | 48.8% |
| Within one type | 91.3% |
| Same group (I–II / III–IV / V–VI) | 78.3% |
| Quadratic-weighted Cohen's kappa | 0.78 |
| Disagreements where Centaur Labs gave the lighter type | 79% |

The two services agree on the exact type for fewer than half the images, and their disagreements are **systematic**: Centaur Labs usually rates skin lighter. Which group an image falls into, and so any "performance on dark skin" figure, depends partly on who did the labelling. The analysis therefore repeats every skin-type result with the second annotator's labels, and with only the images on which both agree.

## Methods

**Model.** An ImageNet-pretrained EfficientNet-B0, fine-tuned on 224×224 images with a class-weighted loss. In the [MelanCare imbalance comparison](https://github.com/i-oladele/melancare#class-imbalance-comparison) this gave the best balanced accuracy. Augmentations are crops, flips and mild brightness/contrast changes. **Hue and saturation are deliberately not augmented**, because changing colour would alter apparent skin tone, the attribute under study.

**Three training-set compositions**, all evaluated on the same test set:

| Experiment | Training images | Purpose |
|---|---|---|
| A: all skin types | 7,770 | Baseline: is performance equal across skin types? |
| B: light skin only (I–II) | 4,202 | What happens when darker skin is absent from training? |
| C: all skin types, same size and diagnosis mix as B | 4,202 | Separates *diversity* from *quantity*: B vs C differ only in skin types |

The validation set always contains all skin types, so model selection is identical across experiments.

**Evaluation**, for each skin type group:
- accuracy and balanced accuracy (benign / malignant / non-neoplastic);
- malignant-vs-rest AUC;
- sensitivity and specificity at **one referral threshold**, set on the validation set for 90% sensitivity across all skin types, as a deployed tool would use. A different threshold per group would hide the disparity;
- **95% bootstrap confidence intervals** within each group, plus a confidence interval for the **gap between light and dark skin**. A gap whose interval excludes zero is unlikely to be explained by sampling variation alone;
- **robustness checks**: the second annotator's skin types, and the subset where both annotators agree;
- results by image source (the two atlases differ in population and photography).

## Results

All three models were evaluated on the same test set of 2,217 images:

| Skin type group | Test images | Malignant |
|---|---:|---:|
| I–II (light) | 1,195 | 201 |
| III–IV (medium) | 786 | 102 |
| V–VI (dark) | 236 | 22 |

<img src="docs/figures/composition_comparison.png" width="100%" alt="Four panels (balanced accuracy, malignant AUC, malignant sensitivity, malignant specificity), each showing experiments A, B and C for skin types I-II, III-IV and V-VI with 95% confidence intervals. Experiment B (light skin only) drops clearly on type V-VI skin; A and C stay level across skin types.">

Values are point estimates with 95% confidence intervals. "Gap" is light (I–II) minus dark (V–VI); a positive gap means the model does worse on dark skin.

**Balanced accuracy** (benign / malignant / non-neoplastic)

| Experiment | I–II | III–IV | V–VI | Gap |
|---|---|---|---|---|
| A: all skin types | 0.71 (0.67 to 0.74) | 0.75 (0.70 to 0.79) | 0.71 (0.62 to 0.80) | 0.00 (−0.11 to 0.09) |
| B: light skin only | 0.66 (0.62 to 0.69) | 0.61 (0.57 to 0.66) | **0.48** (0.39 to 0.59) | **0.18 (0.07 to 0.28)** |
| C: all skin types, same size as B | 0.69 (0.66 to 0.72) | 0.72 (0.67 to 0.76) | 0.67 (0.57 to 0.77) | 0.02 (−0.08 to 0.13) |

**Malignant AUC** (malignant vs everything else)

| Experiment | I–II | III–IV | V–VI | Gap |
|---|---|---|---|---|
| A: all skin types | 0.92 (0.89 to 0.94) | 0.93 (0.90 to 0.96) | 0.91 (0.81 to 0.99) | 0.01 (−0.07 to 0.11) |
| B: light skin only | 0.90 (0.88 to 0.93) | 0.90 (0.87 to 0.93) | **0.79** (0.68 to 0.89) | **0.12 (0.01 to 0.22)** |
| C: all skin types, same size as B | 0.91 (0.88 to 0.93) | 0.90 (0.86 to 0.94) | 0.88 (0.78 to 0.97) | 0.02 (−0.06 to 0.12) |

**Malignancies referred** at each model's single referral threshold (sensitivity)

| Experiment | I–II | III–IV | V–VI |
|---|---|---|---|
| A: all skin types | 178 of 201 (89%) | 94 of 102 (92%) | 20 of 22 (91%) |
| B: light skin only | 187 of 201 (93%) | 96 of 102 (94%) | **17 of 22 (77%)** |
| C: all skin types, same size as B | 187 of 201 (93%) | 90 of 102 (88%) | 20 of 22 (91%) |

Full tables, including specificity and the robustness checks: [composition comparison](results/composition_comparison.md), [within each image source](results/within_source.md), and the per-model reports for [A](results/all_types/report.md), [B](results/light_only/report.md) and [C](results/size_matched/report.md).

### Findings

**1. Trained on all skin types, the model showed no detectable gap between light and dark skin in the pooled test set.** Balanced accuracy was 0.71 on both light and dark skin, malignant AUC was 0.92 and 0.91, and it referred 20 of 22 dark-skin malignancies. The one clear difference runs the other way: at the same threshold, specificity was *higher* on dark skin (0.82 vs 0.71; gap −0.11, CI −0.17 to −0.05). The model raised fewer false alarms for dark-skin patients and more for light-skin patients. (Finding 4 qualifies the "no gap" result.)

**2. Trained on light skin only, the model performed much worse on dark skin.** Balanced accuracy on type V–VI skin fell to 0.48, against 0.66 on light skin (gap 0.18, CI 0.07 to 0.28). Malignant AUC fell to 0.79 (gap 0.12, CI 0.01 to 0.22). At a threshold set to catch 90% of malignancies, the model referred 17 of 22 dark-skin malignancies (77%), against 93% on light skin. That sensitivity gap is large, but with 22 cases its confidence interval just includes zero (−0.02 to 0.34). Medium skin was also affected (balanced accuracy 0.61, against 0.75 for model A).

- The balanced-accuracy gap holds with the second annotator's skin types (0.27, CI 0.15 to 0.36) and on the images where both annotators agree (0.25, CI 0.09 to 0.38).
- The AUC gap holds with the second annotator's labels (0.16, CI 0.05 to 0.30). On the agreed subset its interval includes zero (0.08, CI −0.02 to 0.18); that subset contains only 8 dark-skin malignancies.

**3. The drop came from the missing skin types, not from the smaller training set.** Model C was trained on the same number of images as B (4,202) with the same diagnosis mix, but drawn from all skin types. On dark skin, its balanced accuracy recovered from 0.48 to 0.67 and its malignant AUC from 0.79 to 0.88, and the light-vs-dark gap closed (0.02, CI −0.08 to 0.13). C had 45% fewer light-skin training images than B, yet it did no worse on light skin (0.69 vs 0.66). Nearly doubling the training set (A, 7,770 images, vs C) gave smaller gains across all groups (overall balanced accuracy 0.72 vs 0.70).

**4. Image source is entangled with skin type, and the pooled results partly hide a gap.** Every model scored far higher on Atlas Dermatologico images than on DermaAmin images (model A balanced accuracy 0.87 vs 0.69). Atlas Dermatologico supplies 43% of the dark-skin test images (101 of 236) but only 8% of the light-skin ones (99 of 1,195), which flatters the pooled dark-skin results. Within DermaAmin alone (1,734 test images, 133 of them type V–VI with 12 malignant):

| Experiment | Balanced accuracy I–II / V–VI | Gap | Malignant AUC I–II / V–VI | Gap | Dark-skin malignancies referred |
|---|---|---|---|---|---|
| A: all skin types | 0.69 / 0.63 | 0.05 (−0.06 to 0.18) | 0.90 / 0.84 | 0.06 (−0.07 to 0.25) | 10 of 12 |
| B: light skin only | 0.64 / **0.40** | **0.24 (0.13 to 0.34)** | 0.89 / **0.64** | **0.25 (0.10 to 0.42)** | **7 of 12** |
| C: all skin types, same size as B | 0.67 / 0.61 | 0.05 (−0.08 to 0.18) | 0.89 / 0.83 | 0.06 (−0.07 to 0.25) | 11 of 12 |

Within one source, the effect of light-only training is *larger*, so it is not an artefact of the source mix. For models A and C, a gap of about 5 points of balanced accuracy appears within DermaAmin. Its confidence interval includes zero, but with only 12 dark-skin malignancies the test cannot rule out a real gap of that size either. "No detectable gap" here means *not measurable with this data*, not *equal performance*.

### What this shows

- **Representation, not volume.** In this dataset, leaving dark skin out of training hurt dark-skin performance far more than halving the training set did.
- **A pooled fairness check can mislead.** The headline "no gap" for model A depends partly on which atlas the dark-skin images came from. Subgroup results need to be checked against confounders such as image source.
- **Dark-skin malignancies are too scarce to certify fairness.** With 22 such test images (12 in the larger source), only large gaps such as model B's can be detected. Closing this gap needs data collection, not just modelling.

## Limitations

- **Fitzpatrick type is a coarse, noisy proxy for skin tone.** It describes sun reactivity, was estimated from photographs, and the two annotators often disagree (see above).
- **Few dark-skin malignancies:** 22 malignant test images on type V–VI skin (12 in DermaAmin), so malignancy results for this group are imprecise. Only large gaps can be detected.
- **Atlas images are not clinic images.** They are curated, often show classic presentations, and come from two websites with different populations and photography. Skin type is entangled with source (see [finding 4](#findings)), so results are also reported within each source.
- **Diagnosis labels** come from the atlases and were not independently verified (except a small dermatologist-reviewed subset).
- **Single training run per experiment:** confidence intervals reflect test-set sampling, not run-to-run variation. Differences of a few points, such as between A and C, may not survive repeated runs. Model B's drop on dark skin is much larger.
- **One model architecture** (EfficientNet-B0). Other architectures or fairness interventions were not tested.

## How to run

**On Google Colab (recommended, free GPU):** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/i-oladele/skin-tone-fairness/blob/main/notebooks/colab_experiments.ipynb)

Choose *Runtime → Change runtime type → T4 GPU*, paste the full-image link into `FULL_IMAGES_URL` if you have one, then *Runtime → Run all*.

**Locally:**

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Labels
mkdir -p data/raw
curl -L -o data/raw/fitzpatrick17k.csv https://raw.githubusercontent.com/mattgroh/fitzpatrick17k/main/fitzpatrick17k.csv
curl -L -o data/raw/Fitzpatrick17k-C.csv "https://zenodo.org/api/records/12739457/files/Fitzpatrick17k-C.csv/content"

# Data overview (labels only, no images needed)
python scripts/explore_data.py

# Images: from the original links, or from the authors' archive
python scripts/download_images.py                       # original links (partial)
python scripts/download_images.py --archive images.zip  # full set from the authors
python scripts/prepare_data.py

# Experiments A, B, C
python scripts/train.py --run-name all_types
python scripts/train.py --run-name light_only --train-groups I-II
python scripts/train.py --run-name size_matched --size-match I-II
for r in all_types light_only size_matched; do python scripts/evaluate.py --run runs/$r; done
python scripts/compare_runs.py runs/all_types runs/light_only runs/size_matched \
    --names "A: all skin types" "B: light skin only (I-II)" "C: all skin types, same size as B" \
    --figure docs/figures/composition_comparison.png --out results/composition_comparison.md
python scripts/check_by_source.py runs/all_types runs/light_only runs/size_matched \
    --names "A: all skin types" "B: light skin only (I-II)" "C: all skin types, same size as B" \
    --out results/within_source.md

pytest
```

## Project structure

```
src/skinfair/
  data.py        labels, skin type groups, metadata, dataset, augmentations
  metrics.py     sensitivity/specificity/AUC, bootstrap CIs, per-group CIs and gaps
  model.py       model construction and checkpoint loading
  engine.py      training and prediction loops
  plots.py       figures (colour-blind-checked palette)
scripts/         explore_data, download_images, prepare_data, train, evaluate, compare_runs,
                 check_by_source
notebooks/       Google Colab notebook for experiments A-C
results/         data overview, comparison tables, and each model's config, metrics and report
docs/figures/    figures used in this README
tests/           unit tests (no images needed)
```

## References

- Groh M, et al. Evaluating deep neural networks trained on clinical images in dermatology with the Fitzpatrick 17k dataset. *CVPR Workshops* (2021).
- Groh M, et al. Towards transparency in dermatology image datasets with skin tone annotations by experts, crowds, and an algorithm. *Proc. ACM Hum.-Comput. Interact.* 6, CSCW2 (2022).
- Abhishek K, Jain A, Hamarneh G. Investigating the quality of DermaMNIST and Fitzpatrick17k dermatological image datasets. *Scientific Data* (2025). [Project page](https://derm.cs.sfu.ca/critique/).
- Daneshjou R, et al. Disparities in dermatology AI performance on a diverse, curated clinical image set. *Science Advances* 8, eabq6147 (2022).
- Fitzpatrick TB. The validity and practicality of sun-reactive skin types I through VI. *Archives of Dermatology* 124, 869–871 (1988).
- Tan M, Le Q. EfficientNet: rethinking model scaling for convolutional neural networks. *ICML* (2019).

Dataset licences: Fitzpatrick17k images CC BY-NC-SA 3.0; Fitzpatrick17k-C metadata CC BY 4.0.

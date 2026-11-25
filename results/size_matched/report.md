# Evaluation: size_matched

Trained on 4,202 images (type I-II: 2,302, type III-IV: 1,440, type V-VI: 460). Best epoch 19.
Malignant referral threshold, set on the validation set (all skin types) for 90% sensitivity: 0.004. The same threshold is applied to every group.

## Overall (test set, 2,217 images)

| Metric | Value (95% CI) |
|---|---|
| Balanced accuracy | 0.697 (0.67 to 0.72) |
| Accuracy | 0.797 (0.78 to 0.81) |
| Macro AUC | 0.857 (0.84 to 0.87) |
| Malignant AUC | 0.906 (0.89 to 0.93) |
| Malignant sensitivity | 0.914 (0.88 to 0.94) |
| Malignant specificity | 0.603 (0.58 to 0.62) |

| Class | Images | Sensitivity | Specificity | AUC |
|---|---|---|---|---|
| benign | 288 | 0.521 | 0.921 | 0.812 |
| malignant | 325 | 0.705 | 0.940 | 0.906 |
| non-neoplastic | 1604 | 0.866 | 0.703 | 0.852 |

## By Fitzpatrick skin type

### Primary skin type labels (Scale AI)

95% CIs from bootstrap resampling within each group. A gap whose CI excludes 0 is unlikely to be explained by sampling variation alone.

| Skin type | Images | Malignant | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|---|
| Type I-II | 1195 | 201 | 0.784 (0.76 to 0.81) | 0.690 (0.66 to 0.72) | 0.907 (0.88 to 0.93) | 0.930 (0.89 to 0.96) | 0.574 (0.54 to 0.60) |
| Type III-IV | 786 | 102 | 0.812 (0.79 to 0.84) | 0.716 (0.67 to 0.76) | 0.904 (0.86 to 0.94) | 0.882 (0.81 to 0.94) | 0.632 (0.59 to 0.67) |
| Type V-VI | 236 | 22 | 0.818 (0.77 to 0.86) | 0.667 (0.57 to 0.77) | 0.885 (0.78 to 0.97) | 0.909 (0.78 to 1.00) | 0.640 (0.58 to 0.71) |
| **Gap: I-II minus V-VI** |  |  | -0.034 (-0.09 to 0.02) | 0.023 (-0.08 to 0.13) | 0.022 (-0.06 to 0.12) | 0.021 (-0.09 to 0.15) | -0.066 (-0.14 to 0.00) |

### Robustness: second annotator's labels (Centaur Labs)

| Skin type | Images | Malignant | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|---|
| Type I-II | 1323 | 229 | 0.789 (0.77 to 0.81) | 0.692 (0.66 to 0.73) | 0.907 (0.88 to 0.93) | 0.926 (0.89 to 0.96) | 0.587 (0.56 to 0.62) |
| Type III-IV | 596 | 71 | 0.820 (0.79 to 0.85) | 0.699 (0.65 to 0.75) | 0.905 (0.86 to 0.94) | 0.873 (0.79 to 0.95) | 0.636 (0.59 to 0.68) |
| Type V-VI | 209 | 13 | 0.818 (0.77 to 0.87) | 0.626 (0.51 to 0.74) | 0.897 (0.82 to 0.97) | 1.000 (1.00 to 1.00) | 0.643 (0.57 to 0.71) |
| **Gap: I-II minus V-VI** |  |  | -0.029 (-0.09 to 0.02) | 0.066 (-0.05 to 0.18) | 0.010 (-0.07 to 0.10) | -0.074 (-0.11 to -0.04) | -0.056 (-0.13 to 0.02) |

### Robustness: only images where both annotators agree on the group

| Skin type | Images | Malignant | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|---|
| Type I-II | 1069 | 183 | 0.786 (0.76 to 0.81) | 0.684 (0.65 to 0.72) | 0.907 (0.88 to 0.93) | 0.929 (0.89 to 0.96) | 0.584 (0.55 to 0.62) |
| Type III-IV | 451 | 51 | 0.818 (0.78 to 0.85) | 0.718 (0.66 to 0.78) | 0.910 (0.86 to 0.95) | 0.863 (0.75 to 0.95) | 0.665 (0.62 to 0.71) |
| Type V-VI | 144 | 8 | 0.826 (0.76 to 0.88) | 0.611 (0.46 to 0.76) | 0.886 (0.77 to 0.98) | 1.000 (1.00 to 1.00) | 0.691 (0.61 to 0.76) |
| **Gap: I-II minus V-VI** |  |  | -0.041 (-0.10 to 0.03) | 0.074 (-0.08 to 0.23) | 0.021 (-0.07 to 0.13) | -0.071 (-0.11 to -0.04) | -0.108 (-0.19 to -0.03) |

## By image source

| Source | Images | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|
| Atlas Dermatologico | 476 | 0.842 | 0.799 | 0.963 | 0.959 | 0.651 |
| DermaAmin | 1734 | 0.785 | 0.665 | 0.881 | 0.894 | 0.591 |

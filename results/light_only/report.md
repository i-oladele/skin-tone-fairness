# Evaluation: light_only

Trained on 4,202 images (type I-II: 4,202, type III-IV: 0, type V-VI: 0). Best epoch 11.
Malignant referral threshold, set on the validation set (all skin types) for 90% sensitivity: 0.012. The same threshold is applied to every group.

## Overall (test set, 2,217 images)

| Metric | Value (95% CI) |
|---|---|
| Balanced accuracy | 0.629 (0.60 to 0.65) |
| Accuracy | 0.715 (0.70 to 0.73) |
| Macro AUC | 0.823 (0.81 to 0.84) |
| Malignant AUC | 0.896 (0.88 to 0.91) |
| Malignant sensitivity | 0.923 (0.89 to 0.95) |
| Malignant specificity | 0.601 (0.58 to 0.62) |

| Class | Images | Sensitivity | Specificity | AUC |
|---|---|---|---|---|
| benign | 288 | 0.424 | 0.866 | 0.752 |
| malignant | 325 | 0.689 | 0.901 | 0.896 |
| non-neoplastic | 1604 | 0.773 | 0.698 | 0.820 |

## By Fitzpatrick skin type

### Primary skin type labels (Scale AI)

95% CIs from bootstrap resampling within each group. A gap whose CI excludes 0 is unlikely to be explained by sampling variation alone.

| Skin type | Images | Malignant | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|---|
| Type I-II | 1195 | 201 | 0.746 (0.72 to 0.77) | 0.660 (0.62 to 0.69) | 0.904 (0.88 to 0.93) | 0.930 (0.89 to 0.96) | 0.607 (0.57 to 0.64) |
| Type III-IV | 786 | 102 | 0.701 (0.67 to 0.73) | 0.614 (0.57 to 0.66) | 0.903 (0.87 to 0.93) | 0.941 (0.89 to 0.98) | 0.605 (0.57 to 0.64) |
| Type V-VI | 236 | 22 | 0.610 (0.55 to 0.67) | 0.480 (0.39 to 0.59) | 0.787 (0.68 to 0.89) | 0.773 (0.60 to 0.94) | 0.565 (0.50 to 0.63) |
| **Gap: I-II minus V-VI** |  |  | 0.135 (0.07 to 0.20) | 0.180 (0.07 to 0.28) | 0.118 (0.01 to 0.22) | 0.158 (-0.02 to 0.34) | 0.041 (-0.04 to 0.11) |

### Robustness: second annotator's labels (Centaur Labs)

| Skin type | Images | Malignant | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|---|
| Type I-II | 1323 | 229 | 0.746 (0.72 to 0.77) | 0.664 (0.63 to 0.70) | 0.908 (0.89 to 0.93) | 0.934 (0.90 to 0.97) | 0.613 (0.59 to 0.64) |
| Type III-IV | 596 | 71 | 0.708 (0.67 to 0.74) | 0.591 (0.54 to 0.64) | 0.904 (0.86 to 0.94) | 0.915 (0.84 to 0.97) | 0.596 (0.55 to 0.63) |
| Type V-VI | 209 | 13 | 0.579 (0.51 to 0.65) | 0.398 (0.30 to 0.51) | 0.744 (0.61 to 0.86) | 0.846 (0.62 to 1.00) | 0.551 (0.48 to 0.62) |
| **Gap: I-II minus V-VI** |  |  | 0.167 (0.09 to 0.24) | 0.266 (0.15 to 0.36) | 0.164 (0.05 to 0.30) | 0.088 (-0.07 to 0.31) | 0.062 (-0.01 to 0.14) |

### Robustness: only images where both annotators agree on the group

| Skin type | Images | Malignant | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|---|
| Type I-II | 1069 | 183 | 0.753 (0.73 to 0.78) | 0.667 (0.63 to 0.70) | 0.907 (0.88 to 0.93) | 0.934 (0.90 to 0.97) | 0.613 (0.58 to 0.64) |
| Type III-IV | 451 | 51 | 0.732 (0.69 to 0.77) | 0.630 (0.57 to 0.69) | 0.927 (0.89 to 0.96) | 0.961 (0.90 to 1.00) | 0.627 (0.58 to 0.67) |
| Type V-VI | 144 | 8 | 0.604 (0.53 to 0.68) | 0.421 (0.30 to 0.57) | 0.829 (0.73 to 0.92) | 0.875 (0.60 to 1.00) | 0.596 (0.51 to 0.67) |
| **Gap: I-II minus V-VI** |  |  | 0.149 (0.07 to 0.23) | 0.246 (0.09 to 0.38) | 0.078 (-0.02 to 0.18) | 0.059 (-0.09 to 0.34) | 0.017 (-0.07 to 0.11) |

## By image source

| Source | Images | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|
| Atlas Dermatologico | 476 | 0.691 | 0.622 | 0.947 | 1.000 | 0.577 |
| DermaAmin | 1734 | 0.721 | 0.619 | 0.874 | 0.890 | 0.608 |

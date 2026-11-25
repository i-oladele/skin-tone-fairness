# Evaluation: all_types

Trained on 7,770 images (type I-II: 4,202, type III-IV: 2,681, type V-VI: 887). Best epoch 16.
Malignant referral threshold, set on the validation set (all skin types) for 90% sensitivity: 0.013. The same threshold is applied to every group.

## Overall (test set, 2,217 images)

| Metric | Value (95% CI) |
|---|---|
| Balanced accuracy | 0.723 (0.70 to 0.75) |
| Accuracy | 0.813 (0.80 to 0.83) |
| Macro AUC | 0.879 (0.86 to 0.89) |
| Malignant AUC | 0.924 (0.91 to 0.94) |
| Malignant sensitivity | 0.898 (0.87 to 0.93) |
| Malignant specificity | 0.740 (0.72 to 0.76) |

| Class | Images | Sensitivity | Specificity | AUC |
|---|---|---|---|---|
| benign | 288 | 0.549 | 0.925 | 0.835 |
| malignant | 325 | 0.748 | 0.940 | 0.924 |
| non-neoplastic | 1604 | 0.873 | 0.746 | 0.877 |

## By Fitzpatrick skin type

### Primary skin type labels (Scale AI)

95% CIs from bootstrap resampling within each group. A gap whose CI excludes 0 is unlikely to be explained by sampling variation alone.

| Skin type | Images | Malignant | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|---|
| Type I-II | 1195 | 201 | 0.797 (0.77 to 0.82) | 0.710 (0.67 to 0.74) | 0.917 (0.89 to 0.94) | 0.886 (0.84 to 0.93) | 0.706 (0.68 to 0.74) |
| Type III-IV | 786 | 102 | 0.835 (0.81 to 0.86) | 0.750 (0.70 to 0.79) | 0.935 (0.90 to 0.96) | 0.922 (0.86 to 0.97) | 0.765 (0.73 to 0.80) |
| Type V-VI | 236 | 22 | 0.822 (0.78 to 0.87) | 0.707 (0.62 to 0.80) | 0.911 (0.81 to 0.99) | 0.909 (0.77 to 1.00) | 0.818 (0.76 to 0.87) |
| **Gap: I-II minus V-VI** |  |  | -0.025 (-0.08 to 0.03) | 0.003 (-0.11 to 0.09) | 0.005 (-0.07 to 0.11) | -0.024 (-0.14 to 0.12) | -0.112 (-0.17 to -0.05) |

### Robustness: second annotator's labels (Centaur Labs)

| Skin type | Images | Malignant | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|---|
| Type I-II | 1323 | 229 | 0.800 (0.78 to 0.82) | 0.708 (0.68 to 0.74) | 0.920 (0.90 to 0.94) | 0.891 (0.85 to 0.93) | 0.719 (0.69 to 0.74) |
| Type III-IV | 596 | 71 | 0.849 (0.82 to 0.88) | 0.739 (0.69 to 0.79) | 0.930 (0.89 to 0.96) | 0.901 (0.83 to 0.96) | 0.777 (0.74 to 0.81) |
| Type V-VI | 209 | 13 | 0.833 (0.78 to 0.88) | 0.693 (0.58 to 0.80) | 0.924 (0.83 to 0.99) | 0.923 (0.75 to 1.00) | 0.811 (0.75 to 0.87) |
| **Gap: I-II minus V-VI** |  |  | -0.032 (-0.09 to 0.02) | 0.015 (-0.10 to 0.13) | -0.004 (-0.07 to 0.09) | -0.032 (-0.14 to 0.15) | -0.092 (-0.15 to -0.03) |

### Robustness: only images where both annotators agree on the group

| Skin type | Images | Malignant | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|---|
| Type I-II | 1069 | 183 | 0.799 (0.77 to 0.82) | 0.699 (0.66 to 0.74) | 0.915 (0.89 to 0.94) | 0.880 (0.83 to 0.92) | 0.714 (0.68 to 0.75) |
| Type III-IV | 451 | 51 | 0.858 (0.82 to 0.89) | 0.752 (0.69 to 0.81) | 0.933 (0.89 to 0.97) | 0.902 (0.81 to 0.98) | 0.800 (0.76 to 0.84) |
| Type V-VI | 144 | 8 | 0.833 (0.77 to 0.89) | 0.655 (0.51 to 0.81) | 0.902 (0.74 to 0.99) | 0.875 (0.56 to 1.00) | 0.860 (0.80 to 0.91) |
| **Gap: I-II minus V-VI** |  |  | -0.034 (-0.10 to 0.03) | 0.044 (-0.12 to 0.19) | 0.013 (-0.08 to 0.18) | 0.005 (-0.15 to 0.33) | -0.146 (-0.21 to -0.08) |

## By image source

| Source | Images | Accuracy | Balanced accuracy | Malignant AUC | Malignant sensitivity | Malignant specificity |
|---|---|---|---|---|---|---|
| Atlas Dermatologico | 476 | 0.889 | 0.866 | 0.983 | 0.980 | 0.772 |
| DermaAmin | 1734 | 0.791 | 0.685 | 0.897 | 0.863 | 0.733 |

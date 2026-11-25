Test-set performance by Fitzpatrick skin type group, with 95% CIs. The last column is the gap between light (I-II) and dark (V-VI) skin.

| Experiment | Training images (I-II / III-IV / V-VI) |
|---|---|
| A: all skin types | 7,770 (4,202 / 2,681 / 887) |
| B: light skin only (I-II) | 4,202 (4,202 / 0 / 0) |
| C: all skin types, same size as B | 4,202 (2,302 / 1,440 / 460) |

### Balanced accuracy

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.710 (0.67 to 0.74) | 0.750 (0.70 to 0.79) | 0.707 (0.62 to 0.80) | 0.003 (-0.11 to 0.09) |
| B: light skin only (I-II) | 0.660 (0.62 to 0.69) | 0.614 (0.57 to 0.66) | 0.480 (0.39 to 0.59) | 0.180 (0.07 to 0.28) |
| C: all skin types, same size as B | 0.690 (0.66 to 0.72) | 0.716 (0.67 to 0.76) | 0.667 (0.57 to 0.77) | 0.023 (-0.08 to 0.13) |

### Malignant AUC

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.917 (0.89 to 0.94) | 0.935 (0.90 to 0.96) | 0.911 (0.81 to 0.99) | 0.005 (-0.07 to 0.11) |
| B: light skin only (I-II) | 0.904 (0.88 to 0.93) | 0.903 (0.87 to 0.93) | 0.787 (0.68 to 0.89) | 0.118 (0.01 to 0.22) |
| C: all skin types, same size as B | 0.907 (0.88 to 0.93) | 0.904 (0.86 to 0.94) | 0.885 (0.78 to 0.97) | 0.022 (-0.06 to 0.12) |

### Malignant sensitivity

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.886 (0.84 to 0.93) | 0.922 (0.86 to 0.97) | 0.909 (0.77 to 1.00) | -0.024 (-0.14 to 0.12) |
| B: light skin only (I-II) | 0.930 (0.89 to 0.96) | 0.941 (0.89 to 0.98) | 0.773 (0.60 to 0.94) | 0.158 (-0.02 to 0.34) |
| C: all skin types, same size as B | 0.930 (0.89 to 0.96) | 0.882 (0.81 to 0.94) | 0.909 (0.78 to 1.00) | 0.021 (-0.09 to 0.15) |

### Malignant specificity

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.706 (0.68 to 0.74) | 0.765 (0.73 to 0.80) | 0.818 (0.76 to 0.87) | -0.112 (-0.17 to -0.05) |
| B: light skin only (I-II) | 0.607 (0.57 to 0.64) | 0.605 (0.57 to 0.64) | 0.565 (0.50 to 0.63) | 0.041 (-0.04 to 0.11) |
| C: all skin types, same size as B | 0.574 (0.54 to 0.60) | 0.632 (0.59 to 0.67) | 0.640 (0.58 to 0.71) | -0.066 (-0.14 to 0.00) |


# Skin type results within each image source

Test images by source and skin type group (malignant in brackets):

| Source | Type I-II | Type III-IV | Type V-VI |
|---|---|---|---|
| DermaAmin | 1,092 (166) | 509 (49) | 133 (12) |
| Atlas Dermatologico | 99 (35) | 276 (53) | 101 (10) |

Each model's referral threshold is the one set on its validation set (all sources and skin types). 95% CIs from bootstrap resampling within each group. The last column is the gap between light (I-II) and dark (V-VI) skin.

## DermaAmin

### Balanced accuracy

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.686 (0.65 to 0.72) | 0.695 (0.64 to 0.75) | 0.632 (0.51 to 0.75) | 0.054 (-0.06 to 0.18) |
| B: light skin only (I-II) | 0.642 (0.61 to 0.68) | 0.611 (0.55 to 0.67) | 0.401 (0.30 to 0.51) | 0.242 (0.13 to 0.34) |
| C: all skin types, same size as B | 0.669 (0.63 to 0.70) | 0.666 (0.61 to 0.73) | 0.614 (0.49 to 0.74) | 0.054 (-0.08 to 0.18) |

### Malignant AUC

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.902 (0.88 to 0.93) | 0.887 (0.82 to 0.94) | 0.837 (0.66 to 0.97) | 0.065 (-0.07 to 0.25) |
| B: light skin only (I-II) | 0.890 (0.86 to 0.91) | 0.872 (0.82 to 0.92) | 0.641 (0.46 to 0.80) | 0.248 (0.10 to 0.42) |
| C: all skin types, same size as B | 0.890 (0.86 to 0.92) | 0.850 (0.77 to 0.92) | 0.833 (0.65 to 0.96) | 0.057 (-0.07 to 0.25) |

### Malignant sensitivity

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.867 (0.82 to 0.91) | 0.857 (0.75 to 0.95) | 0.833 (0.60 to 1.00) | 0.034 (-0.16 to 0.27) |
| B: light skin only (I-II) | 0.916 (0.87 to 0.96) | 0.878 (0.78 to 0.96) | 0.583 (0.25 to 0.88) | 0.332 (0.05 to 0.65) |
| C: all skin types, same size as B | 0.916 (0.87 to 0.95) | 0.816 (0.69 to 0.92) | 0.917 (0.71 to 1.00) | -0.001 (-0.11 to 0.21) |

### Malignant specificity

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.710 (0.68 to 0.74) | 0.761 (0.72 to 0.80) | 0.802 (0.73 to 0.87) | -0.092 (-0.16 to -0.01) |
| B: light skin only (I-II) | 0.610 (0.58 to 0.64) | 0.628 (0.58 to 0.67) | 0.521 (0.43 to 0.61) | 0.089 (-0.00 to 0.18) |
| C: all skin types, same size as B | 0.568 (0.54 to 0.60) | 0.630 (0.59 to 0.67) | 0.620 (0.53 to 0.70) | -0.052 (-0.14 to 0.04) |

## Atlas Dermatologico

### Balanced accuracy

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.901 (0.81 to 0.97) | 0.844 (0.77 to 0.91) | 0.929 (0.84 to 0.98) | -0.028 (-0.13 to 0.09) |
| B: light skin only (I-II) | 0.746 (0.62 to 0.88) | 0.583 (0.51 to 0.65) | 0.582 (0.39 to 0.83) | 0.164 (-0.12 to 0.41) |
| C: all skin types, same size as B | 0.844 (0.72 to 0.95) | 0.780 (0.71 to 0.85) | 0.781 (0.54 to 0.95) | 0.063 (-0.15 to 0.33) |

### Malignant AUC

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.983 (0.95 to 1.00) | 0.977 (0.96 to 0.99) | 0.993 (0.98 to 1.00) | -0.011 (-0.04 to 0.01) |
| B: light skin only (I-II) | 0.975 (0.94 to 1.00) | 0.926 (0.89 to 0.96) | 0.944 (0.88 to 0.99) | 0.031 (-0.03 to 0.10) |
| C: all skin types, same size as B | 0.986 (0.97 to 1.00) | 0.948 (0.91 to 0.98) | 0.941 (0.84 to 1.00) | 0.046 (-0.02 to 0.14) |

### Malignant sensitivity

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.971 (0.90 to 1.00) | 0.981 (0.94 to 1.00) | 1.000 (1.00 to 1.00) | -0.029 (-0.10 to 0.00) |
| B: light skin only (I-II) | 1.000 (1.00 to 1.00) | 1.000 (1.00 to 1.00) | 1.000 (1.00 to 1.00) | 0.000 (0.00 to 0.00) |
| C: all skin types, same size as B | 1.000 (1.00 to 1.00) | 0.943 (0.87 to 1.00) | 0.900 (0.67 to 1.00) | 0.100 (0.00 to 0.33) |

### Malignant specificity

| Experiment | Type I-II | Type III-IV | Type V-VI | Gap I-II minus V-VI |
|---|---|---|---|---|
| A: all skin types | 0.672 (0.56 to 0.78) | 0.776 (0.73 to 0.83) | 0.835 (0.77 to 0.91) | -0.163 (-0.30 to -0.03) |
| B: light skin only (I-II) | 0.562 (0.44 to 0.68) | 0.556 (0.49 to 0.62) | 0.637 (0.54 to 0.74) | -0.075 (-0.23 to 0.08) |
| C: all skin types, same size as B | 0.672 (0.56 to 0.78) | 0.637 (0.57 to 0.70) | 0.670 (0.57 to 0.77) | 0.002 (-0.14 to 0.14) |

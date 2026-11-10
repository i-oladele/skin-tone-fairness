# Data overview

- Original Fitzpatrick17k: 16,577 images.
- Fitzpatrick17k-C (duplicates and erroneous images removed): 11,394 images (31% removed).
- With a Fitzpatrick skin type: 11,098 images.

## Skin type representation

| Skin type group | benign | malignant | non-neoplastic | total | share of images |
|---|---|---|---|---|---|
| I-II | 824 | 934 | 4,244 | 6,002 | 54.1% |
| III-IV | 514 | 559 | 2,771 | 3,844 | 34.6% |
| V-VI | 125 | 130 | 997 | 1,252 | 11.3% |

## Agreement between the two skin type annotators

Images typed by both Scale AI and Centaur Labs: 10,635.

- Same Fitzpatrick type: 48.8%
- Within one type: 91.3%
- Same group (I-II / III-IV / V-VI): 78.3%
- Quadratic-weighted Cohen's kappa: 0.78
- When they disagree, Centaur Labs gives the lighter type 79% of the time

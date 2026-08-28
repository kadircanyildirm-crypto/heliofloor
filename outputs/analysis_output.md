label mismatches vs official CSVs: validation 0, test 0

### EXPANDED VALIDATION (2011-2019)
n=739, positives=85, base rate=0.115, blocks=50, positive-containing blocks=6

| model | TP | FN | FP | TN | TSS | TSS 95% CI | HSS | F1 |
|---|---|---|---|---|---|---|---|---|
| Surya @ 0.5 | 37 | 48 | 7 | 647 | 0.425 | [0.028, 0.746] | 0.537 | 0.574 |
| Surya @ 0.1 | 69 | 16 | 121 | 533 | 0.627 | [0.257, 0.844] | 0.408 | 0.502 |
| Surya @ 0.05 | 72 | 13 | 166 | 488 | 0.593 | [0.291, 0.796] | 0.333 | 0.446 |
| persistence (t-24h) | 39 | 46 | 35 | 619 | 0.405 | [-0.019, 0.792] | 0.429 | 0.491 |

Best Surya TSS = **0.673** at threshold 0.16 (block bootstrap 95% CI [0.289, 0.886])

### Expanded — by year (threshold 0.16)
| year | n | positives | Surya TSS | persistence TSS |
|---|---|---|---|---|
| 2011 | 88 | 0 | — (no positives) | — |
| 2012 | 88 | 21 | 0.032 | -0.114 |
| 2013 | 78 | 0 | — (no positives) | — |
| 2014 | 88 | 36 | 0.558 | 0.517 |
| 2015 | 88 | 28 | 0.462 | 0.379 |
| 2016 | 77 | 0 | — (no positives) | — |
| 2017 | 80 | 0 | — (no positives) | — |
| 2018 | 76 | 0 | — (no positives) | — |
| 2019 | 76 | 0 | — (no positives) | — |

### Expanded — onset / continuation split
- positive hours: 85 (onset 46, continuation 39)
- persistence false-alarm zone (decay): 35 hours
- onset hours occupy 4 independent blocks -> rule of three upper bound 0.750
- **ONSET caught:** persistence 0/46 (structurally impossible), Surya@0.16 35/46 (in 4/4 blocks), Surya@0.5 14/46 (in 3/4 blocks)
- **CONTINUATION caught:** persistence 39/39 (structurally certain), Surya@0.16 33/39, Surya@0.5 23/39
- **DECAY (false alarms):** persistence 35/35, Surya@0.16 10/35
- hybrid (persistence OR Surya@0.16): TSS=0.705, HSS=0.471, F1=0.554

### Expanded — reliability (calibration) table

| probability bin | n | blocks | mean predicted | observed frequency |
|---|---|---|---|---|
| [0.00, 0.01) | 391 | 32 | 0.002 | 0.000 |
| [0.01, 0.05) | 110 | 20 | 0.024 | 0.118 |
| [0.05, 0.10) | 48 | 15 | 0.076 | 0.062 |
| [0.10, 0.25) | 88 | 15 | 0.172 | 0.125 |
| [0.25, 0.50) | 58 | 11 | 0.350 | 0.362 |
| [0.50, 0.75) | 18 | 4 | 0.622 | 0.667 |
| [0.75, 1.01) | 26 | 3 | 0.866 | 0.962 |

Brier score (raw Surya): 0.0571

### TEST (2020-2024)
n=407, positives=133, base rate=0.327, blocks=28, positive-containing blocks=11

| model | TP | FN | FP | TN | TSS | TSS 95% CI | HSS | F1 |
|---|---|---|---|---|---|---|---|---|
| Surya @ 0.5 | 23 | 110 | 0 | 274 | 0.173 | [0.000, 0.484] | 0.220 | 0.295 |
| Surya @ 0.1 | 94 | 39 | 57 | 217 | 0.499 | [0.222, 0.730] | 0.482 | 0.662 |
| Surya @ 0.05 | 117 | 16 | 69 | 205 | 0.628 | [0.323, 0.869] | 0.569 | 0.734 |
| persistence (t-24h) | 106 | 27 | 49 | 225 | 0.618 | [0.258, 0.889] | 0.593 | 0.736 |

Best Surya TSS = **0.632** at threshold 0.04 (block bootstrap 95% CI [0.315, 0.876])

### Test — by year (threshold 0.04)
| year | n | positives | Surya TSS | persistence TSS |
|---|---|---|---|---|
| 2020 | 77 | 0 | — (no positives) | — |
| 2021 | 80 | 14 | -0.030 | -0.197 |
| 2022 | 88 | 10 | 0.808 | 0.846 |
| 2023 | 77 | 48 | -0.021 | 0.771 |
| 2024 | 85 | 61 | 0.000 | -0.033 |

### Test — onset / continuation split
- positive hours: 133 (onset 27, continuation 106)
- persistence false-alarm zone (decay): 49 hours
- onset hours occupy 3 independent blocks -> rule of three upper bound 1.000
- **ONSET caught:** persistence 0/27 (structurally impossible), Surya@0.04 13/27 (in 2/3 blocks), Surya@0.5 0/27 (in 0/3 blocks)
- **CONTINUATION caught:** persistence 106/106 (structurally certain), Surya@0.04 105/106, Surya@0.5 23/106
- **DECAY (false alarms):** persistence 49/49, Surya@0.04 38/49
- hybrid (persistence OR Surya@0.04): TSS=0.599, HSS=0.530, F1=0.715

### Test — reliability (calibration) table

| probability bin | n | blocks | mean predicted | observed frequency |
|---|---|---|---|---|
| [0.00, 0.01) | 180 | 15 | 0.003 | 0.078 |
| [0.01, 0.05) | 41 | 8 | 0.021 | 0.049 |
| [0.05, 0.10) | 35 | 13 | 0.078 | 0.657 |
| [0.10, 0.25) | 108 | 13 | 0.170 | 0.537 |
| [0.25, 0.50) | 20 | 9 | 0.307 | 0.650 |
| [0.50, 0.75) | 1 | 1 | 0.504 | 1.000 |
| [0.75, 1.01) | 22 | 1 | 0.931 | 1.000 |

Brier score (raw Surya): 0.2076

### CALIBRATION TRANSFER (fitted on validation -> applied to test)
Platt parameters: a=0.944, b=0.145

| model | TSS@0.5 | HSS@0.5 | F1@0.5 | Brier |
|---|---|---|---|---|
| raw Surya | 0.173 | 0.220 | 0.295 | 0.2076 |
| Platt-calibrated Surya | 0.173 | 0.220 | 0.295 | 0.1975 |
| persistence | 0.618 | 0.593 | 0.736 | — |

Platt-calibrated Surya TSS@0.5 block-bootstrap 95% CI: [0.000, 0.484]

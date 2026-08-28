GOES-history logistic trained: n=74564 of 74760 (196 rows dropped as non-finite), base rate=0.1214

threshold chosen on the FULL validation split and frozen: 0.10

| split | n | base rate | model | TSS | TSS 95% CI | HSS | F1 | TP/FN/FP/TN |
|---|---|---|---|---|---|---|---|---|
| validation (full) | 3672 | 0.1089 | GOES-history logistic | **0.661** | [0.532, 0.777] | 0.375 | 0.475 | 355/45/740/2532 |
| validation (full) | 3672 | 0.1089 | persistence (t-24h) | **0.430** | [0.238, 0.621] | 0.428 | 0.491 | 197/203/206/3066 |
| validation (full) | 3672 | 0.1089 | climatology (always no) | **0.000** | — | 0.000 | 0.000 | 0/400/0/3272 |
| test (full) | 43848 | 0.2943 | GOES-history logistic | **0.554** | [0.526, 0.581] | 0.436 | 0.655 | 12387/516/12551/18394 |
| test (full) | 43848 | 0.2943 | persistence (t-24h) | **0.535** | [0.502, 0.568] | 0.536 | 0.672 | 8664/4239/4216/26729 |
| test (full) | 43848 | 0.2943 | climatology (always no) | **0.000** | — | 0.000 | 0.000 | 0/12903/0/30945 |

| year | n | base rate | GOES-logistic TSS | persistence TSS |
|---|---|---|---|---|
| 2020 | 8784 | 0.005 | 0.452 | -0.005 |
| 2021 | 8760 | 0.061 | 0.514 | 0.270 |
| 2022 | 8760 | 0.264 | 0.250 | 0.322 |
| 2023 | 8760 | 0.443 | 0.056 | 0.293 |
| 2024 | 8784 | 0.697 | 0.079 | 0.389 |

base-rate shift across the split: 0.00546 (2020) -> 0.69695 (2024) = **127.5-fold**
pooled test TSS 0.554 vs per-year range 0.056..0.514 — pooled exceeds every single year: True

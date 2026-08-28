GOES-history logistic trained: n=74564 of 74760 (196 rows dropped as non-finite), base rate=0.1214
standardised feature weights:
   ci24       +0.863
   lf48       +0.432
   lf24       +0.278
   lf72       +0.233
   ci48       +0.222
   lf7dmax    +0.136
   lf144      +0.113
   lf120      -0.090
   lf168      -0.058
   ci7dmean   +0.036
   lf96       +0.028

### VALIDATION — H3 baseline comparison (n=739, positives=85, blocks=50)
| model | input | TSS | TSS 95% CI | HSS | F1 |
|---|---|---|---|---|---|
| climatology (always 'no') | — | 0.000 | — | 0.000 | 0.000 |
| persistence (t-24h) | past 24h X-ray | 0.405 | [-0.019, 0.792] | 0.429 | 0.491 |
| GOES-history logistic @0.10 | 7 days of X-ray history | 0.685 | [0.417, 0.881] | 0.414 | 0.510 |
| Surya @0.5 (shipped) | 13-channel SDO imagery | 0.425 | [0.028, 0.746] | 0.537 | 0.574 |
| Surya @0.16 (tuned) | 13-channel SDO imagery | 0.673 | [0.289, 0.886] | 0.503 | 0.576 |
| hybrid: persistence OR Surya@0.16 | both | 0.705 | — | 0.471 | 0.554 |
| hybrid: GOES-logistic OR Surya@0.16 | both | 0.716 | — | 0.367 | 0.478 |

### TEST — H3 baseline comparison (n=407, positives=133, blocks=28)
| model | input | TSS | TSS 95% CI | HSS | F1 |
|---|---|---|---|---|---|
| climatology (always 'no') | — | 0.000 | — | 0.000 | 0.000 |
| persistence (t-24h) | past 24h X-ray | 0.618 | [0.258, 0.889] | 0.593 | 0.736 |
| GOES-history logistic @0.34 | 7 days of X-ray history | 0.738 | [0.467, 0.940] | 0.699 | 0.807 |
| Surya @0.5 (shipped) | 13-channel SDO imagery | 0.173 | [0.000, 0.484] | 0.220 | 0.295 |
| Surya @0.04 (tuned) | 13-channel SDO imagery | 0.632 | [0.315, 0.876] | 0.571 | 0.735 |
| hybrid: persistence OR Surya@0.04 | both | 0.599 | — | 0.530 | 0.715 |
| hybrid: GOES-logistic OR Surya@0.04 | both | 0.639 | — | 0.577 | 0.739 |

# Gap audit: attacking our own claims

## A. cumulative_index direction

data.csv columns: ['timestamp', 'max_goes_class', 'cumulative_index', 'label_max', 'label_cum', 'ts']

aligned hours: 128232
correlation of cumulative_index[t] with log-flux max over ...
  [t,     t+24h)  (same window as label): +nan
  [t-24h, t)      (one window back)     : +nan
  [t+24h, t+48h)  (one window forward)  : +nan
  [t-48h, t-24h)  (two back)            : +nan
  [t+48h, t+72h)  (two forward)         : +nan

Reading: if ci[t] aggregates [t, t+24h), the same-window correlation dominates
and forward/backward neighbours are roughly symmetric. A window longer than
24h would show the forward neighbour beating the backward one.

label_cum exists — testing threshold identities against cumulative_index:
  best threshold 10.0: 128328/128328 rows agree (EXACT IDENTITY)

## B. Multiplicity across the ten paired tests

| split | pair | point | tail frac (wrong side of 0) | 99.5% CI (Bonferroni m=10) |
|---|---|---|---|---|
| validation | GOES-SuryaTuned | +0.012 | 0.4572 | [-0.612, +0.763] |
| validation | SuryaTuned-Persist | +0.268 | 0.0834 | [-0.925, +0.886] |
| validation | GOES-Persist | +0.279 | 0.0486 | [-0.202, +0.880] |
| validation | Surya05-Persist | +0.019 | 0.4594 | [-0.953, +0.747] |
| validation | Hybrid-SuryaTuned | +0.032 | 0.4231 | [-0.063, +0.820] |
| test | GOES-SuryaTuned | +0.106 | 0.0055 | [+0.000, +0.382] |
| test | SuryaTuned-Persist | +0.014 | 0.4387 | [-0.318, +0.412] |
| test | GOES-Persist | +0.120 | 0.0467 | [-0.046, +0.489] |
| test | Surya05-Persist | -0.445 | 0.0070 | [-0.924, +0.070] |
| test | Hybrid-SuryaTuned | -0.033 | 0.1467 | [-0.132, +0.032] |

Reading: family alpha 0.05 over ten tests needs per-test 0.005 (99.5% CI).
A pair whose 99.5% interval still excludes zero survives Bonferroni; the tail
fraction is the bootstrap's one-sided evidence, comparable against 0.0025.

## C. Full-split intervals under longer blocks

frozen threshold 0.10 (unchanged)

| split | model | TSS | 1-day blocks | 2-day blocks | 3-day blocks |
|---|---|---|---|---|---|
| validation | GOES logistic | 0.661 | [0.535, 0.777] | [0.504, 0.800] | [0.507, 0.776] |
| validation | persistence | 0.430 | [0.251, 0.616] | [0.168, 0.681] | [0.189, 0.656] |
| test | GOES logistic | 0.554 | [0.526, 0.581] | [0.521, 0.589] | [0.512, 0.597] |
| test | persistence | 0.535 | [0.503, 0.571] | [0.493, 0.573] | [0.484, 0.578] |

Reading: what matters is whether any conclusion moves — does the validation
persistence interval still contain 0.436, and does the validation GOES interval
still exclude it — as the block length doubles and triples.

## A-addendum: fingerprint with finite masking (corrected)

The first fingerprint printed NaN. The cause was not the cumulative_index
column (it is clean float64, no NaN/inf) but the log-flux series: the four
known `A0.0` hours parse to flux 0, whose log10 is -inf, and one -inf poisons a
whole correlation. With a finite mask (n = 128,324 of 128,328):

| window of the log-flux max | corr with cumulative_index[t] |
|---|---|
| [t, t+24h)  (same window as the label) | +0.416 |
| [t-24h, t)  (one back) | +0.341 |
| [t+24h, t+48h)  (one forward) | +0.340 |
| [t-48h, t-24h)  (two back) | +0.323 |
| [t+48h, t+72h)  (two forward) | +0.322 |

The same-window correlation dominates and the backward/forward neighbours are
symmetric to three decimals (+0.341 vs +0.340) — the fingerprint of a 24h
forward aggregate, not a longer one. Together with the exact label_cum identity
above, the window question is settled twice over.

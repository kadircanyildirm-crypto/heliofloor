### Onset catch rates, with block-effective sample sizes


**validation** — 46 onset hours in **4 independent blocks** (rule-of-three upper bound on a zero count: 3/4 = 0.750)

| predictor | onsets caught | rate | 95% CI (block bootstrap) | blocks with a hit |
|---|---|---|---|---|
| Surya @0.16 (tuned) | 35/46 | 0.761 | [0.357, 1.000] | 4/4 |
| Surya @0.50 (shipped) | 14/46 | 0.304 | [0.000, 0.750] | 3/4 |
| persistence | 0/46 | 0.000 | structural, no interval | 0/4 |

**test** — 27 onset hours in **3 independent blocks** (rule-of-three upper bound on a zero count: 3/3 = 1.000)

| predictor | onsets caught | rate | 95% CI (block bootstrap) | blocks with a hit |
|---|---|---|---|---|
| Surya @0.04 (tuned) | 13/27 | 0.481 | [0.000, 1.000] | 2/3 |
| Surya @0.50 (shipped) | 0/27 | 0.000 | [0.000, 0.000]  ← degenerate, see below | 0/3 |
| persistence | 0/27 | 0.000 | structural, no interval | 0/3 |

**Reading these intervals.** Only the tuned-threshold rows carry information, and
even there the interval spans most of the unit interval. The shipped-threshold
row for the test split shows 0/27 with an interval of [0.000, 0.000]: that is the
boundary artefact described above, not a precise zero. With three onset-containing
blocks the rule of three gives an upper bound of 1.000, so no rate is estimable.
The manuscript therefore reports the zero-catch result as a description of the
three sampled episodes, never as a measured miss rate.


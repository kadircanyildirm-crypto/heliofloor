#!/usr/bin/env python3
"""Onset catch rates with block-bootstrap intervals, and the correction that
keeps section 4.4 honest.

A bootstrap interval of [0, 0] around a 0/n observation is a boundary artefact
of resampling a sample that contains no successes, not evidence of precision.
For zero events the defensible one-sided statement is the rule of three, 3/n --
and n must be the number of INDEPENDENT blocks containing onsets, not the number
of correlated onset hours. On this sample that upper bound is 1.0, i.e. the
observation constrains nothing and must be reported descriptively.

Run:  venv-quick/bin/python onset_ci.py > onset_ci_output.md
"""
import numpy as np
import pandas as pd

import heliofloor_data as H


def rate_ci(df, mask_fn, hit_fn, n_boot=4000, seed=H.SEED):
    """Interval for a rate defined on a subset, resampling whole blocks."""
    rng = np.random.default_rng(seed)
    blocks = [g for _, g in df.groupby("block")]
    vals = []
    for _ in range(n_boot):
        s = pd.concat([blocks[i] for i in rng.integers(0, len(blocks), len(blocks))],
                      ignore_index=True)
        sub = s[mask_fn(s)]
        if len(sub) >= 3:
            vals.append(hit_fn(sub).mean())
    if not vals:
        return np.nan, np.nan
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


print("### Onset catch rates, with block-effective sample sizes\n")
for split in ("validation", "test"):
    df = H.load(split)
    thr, _ = H.best_threshold(df)
    onset = df[(df["label"] == 1) & (df["persist"] == 0)]
    nb = onset["block"].nunique()
    print(f"\n**{split}** — {len(onset)} onset hours in **{nb} independent blocks** "
          f"(rule-of-three upper bound on a zero count: 3/{nb} = {3/nb:.3f})\n")
    print("| predictor | onsets caught | rate | 95% CI (block bootstrap) | blocks with a hit |")
    print("|---|---|---|---|---|")
    for label, fn in ((f"Surya @{thr:.2f} (tuned)", lambda s, t=thr: s["prob"] > t),
                      ("Surya @0.50 (shipped)", lambda s: s["prob"] > 0.5)):
        hits = int(fn(onset).sum())
        lo, hi = rate_ci(df, lambda s: (s["label"] == 1) & (s["persist"] == 0), fn)
        bh = onset[fn(onset)]["block"].nunique()
        note = "  ← degenerate, see below" if hits == 0 else ""
        print(f"| {label} | {hits}/{len(onset)} | {hits/len(onset):.3f} | "
              f"[{lo:.3f}, {hi:.3f}]{note} | {bh}/{nb} |")
    print(f"| persistence | 0/{len(onset)} | 0.000 | structural, no interval | 0/{nb} |")

print("""
**Reading these intervals.** Only the tuned-threshold rows carry information, and
even there the interval spans most of the unit interval. The shipped-threshold
row for the test split shows 0/27 with an interval of [0.000, 0.000]: that is the
boundary artefact described above, not a precise zero. With three onset-containing
blocks the rule of three gives an upper bound of 1.000, so no rate is estimable.
The manuscript therefore reports the zero-catch result as a description of the
three sampled episodes, never as a measured miss rate.
""")

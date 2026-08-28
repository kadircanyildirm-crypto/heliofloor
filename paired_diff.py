#!/usr/bin/env python3
"""Paired block-bootstrap differences between forecasting methods.

Why this exists: section 4.3 originally argued from overlapping individual
confidence intervals ("no two methods separate"). Overlapping CIs are weak
evidence about a difference -- two estimates can overlap while their paired
difference excludes zero, because the same resampled blocks move both scores
together. The defensible statement resamples blocks ONCE per draw, computes
every method's TSS on the same resample, and builds the interval of the
DIFFERENCE.

Thresholds are held fixed at their full-sample values under resampling (the
same convention as the individual intervals; re-tuning per resample would
answer a different question).

Run:  venv-quick/bin/python paired_diff.py > paired_diff_output.md
"""
import numpy as np
import pandas as pd

import heliofloor_data as H

N_BOOT = 4000


def method_preds(df, goes_thr, surya_thr):
    """Fixed-threshold binary predictions for every method, as columns."""
    out = pd.DataFrame(index=df.index)
    out["persistence"] = df["persist"].to_numpy()
    out["surya05"] = (df["prob"] > 0.5).astype(int).to_numpy()
    out["surya_tuned"] = (df["prob"] > surya_thr).astype(int).to_numpy()
    out["goes"] = (df["goes"] > goes_thr).astype(int).to_numpy()
    out["hybrid"] = ((df["prob"] > surya_thr) | (df["persist"] == 1)).astype(int).to_numpy()
    return out


PAIRS = [
    ("goes", "surya_tuned", "GOES logistic - Surya (tuned)"),
    ("surya_tuned", "persistence", "Surya (tuned) - persistence"),
    ("goes", "persistence", "GOES logistic - persistence"),
    ("surya05", "persistence", "Surya @0.5 - persistence"),
    ("hybrid", "surya_tuned", "hybrid - Surya (tuned)"),
]

w, mu, sd = H.train_goes_model(verbose=False)

print("# Paired block-bootstrap differences (Delta TSS)\n")
print(f"{N_BOOT} draws; one block resample per draw scores every method, so each")
print("difference is computed within the same resample. Thresholds fixed at their")
print("full-sample values. Seed 42 per split.\n")

for split in ("validation", "test"):
    df = H.load(split)
    df["goes"] = H.score_goes(w, mu, sd, df["ts"])
    s_thr, _ = H.best_threshold(df, "prob")
    g_thr, _ = H.best_threshold(df, "goes")
    preds = method_preds(df, g_thr, s_thr)
    y = df["label"].to_numpy()

    point = {}
    for col in preds.columns:
        point[col] = H.tss(y, preds[col].to_numpy())

    blocks_idx = [g.index.to_numpy() for _, g in df.groupby("block")]
    rng = np.random.default_rng(H.SEED)
    diffs = {name: [] for _, _, name in PAIRS}
    for _ in range(N_BOOT):
        pick = rng.integers(0, len(blocks_idx), len(blocks_idx))
        idx = np.concatenate([blocks_idx[i] for i in pick])
        yy = df["label"].to_numpy()[idx]
        t = {c: H.tss(yy, preds[c].to_numpy()[idx]) for c in preds.columns}
        for a, b, name in PAIRS:
            d = t[a] - t[b]
            if not np.isnan(d):
                diffs[name].append(d)

    print(f"\n## {split} (Surya thr {s_thr:.2f}, GOES thr {g_thr:.2f}, "
          f"{df['block'].nunique()} blocks)\n")
    print("| pair | point Delta | 95% CI | excludes zero? |")
    print("|---|---|---|---|")
    for a, b, name in PAIRS:
        pd_ = point[a] - point[b]
        lo, hi = np.percentile(diffs[name], [2.5, 97.5])
        sep = "**yes**" if (lo > 0 or hi < 0) else "no"
        print(f"| {name} | {pd_:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {sep} |")

print("""
Reading: a pair whose interval straddles zero is not separated at this sample
size; a pair whose interval excludes zero is. This is the statement section 4.3
should make, in place of reasoning from overlapping individual intervals.
""")

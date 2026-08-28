#!/usr/bin/env python3
"""How many INDEPENDENT blocks actually support each headline claim?

Hours inside a 24-hour block are strongly autocorrelated, so the unit of
evidence is the block. A finding concentrated in two or three blocks is a
description of a handful of episodes, not a rate estimate — and the manuscript
is required to say so wherever that is the case.

Run:  venv-quick/bin/python block_support.py > block_support_output.md
"""
import heliofloor_data as H

for split in ("validation", "test"):
    df = H.load(split)
    print(f"\n=== {split}: {len(df)} hours, {df['block'].nunique()} blocks, "
          f"{int(df['label'].sum())} positives ===")
    print(f"  blocks containing any positive : {df[df['label']==1]['block'].nunique()}")
    print(f"  blocks containing any onset    : "
          f"{df[(df['label']==1)&(df['persist']==0)]['block'].nunique()}")

    sizes = df.groupby("block").size()
    print(f"  block sizes: min {sizes.min()}, median {int(sizes.median())}, "
          f"max {sizes.max()}; complete-or-near (>=20 h) {int((sizes>=20).sum())}, "
          f"fragments (<20 h) {int((sizes<20).sum())}")

    # the calibration claim rests on the low-probability bins
    m = (df["prob"] >= 0.05) & (df["prob"] < 0.25)
    sub = df[m]
    print(f"  calibration claim [0.05,0.25): {len(sub)} hours, "
          f"{sub['block'].nunique()} blocks, mean predicted {sub['prob'].mean():.3f}, "
          f"observed frequency {sub['label'].mean():.3f}")
    if sub["block"].nunique() >= 2:
        per = sub.groupby("block")["label"].agg(["size", "mean"])
        cells = ", ".join(f"{r['mean']:.2f}(n={int(r['size'])})" for _, r in per.iterrows())
        print(f"    per-block observed frequency: {cells}")

#!/usr/bin/env python3
"""How much could bf16 inference noise move our reported numbers?

Our probabilities were produced under bf16 autocast. A reviewer is entitled to
ask whether fp32 would give different scores. Recomputing needs a GPU we no
longer have running, but the question can be bounded without one.

bf16 carries 8 significand bits, so its relative resolution is about 2^-8
(~0.4%). Autocast keeps accumulations in fp32 and the final sigmoid is applied
in fp32, so the perturbation reaching a probability is far smaller than that;
we nevertheless take a deliberately pessimistic view and ask: if EVERY hour
whose probability lies within epsilon of the decision threshold flipped to the
wrong side, how far could TSS move?

That is a worst case no real numerical difference could reach, so if it is small
the open item is closed by argument rather than by a GPU run.

Run:  venv-quick/bin/python precision_sensitivity.py > precision_sensitivity_output.md
"""
import numpy as np

import heliofloor_data as H

EPS = [1e-4, 1e-3, 5e-3, 1e-2]

print("# bf16 precision sensitivity (no GPU required)\n")
print("Worst case: every hour within epsilon of the threshold flips to the side")
print("that hurts TSS most. Real bf16 perturbation is far smaller than the")
print("largest epsilon shown.\n")

for split in ("validation", "test"):
    df = H.load(split)
    y = df["label"].to_numpy()
    p = df["prob"].to_numpy()
    tuned, _ = H.best_threshold(df)
    print(f"\n## {split} (n={len(df)})\n")
    print("| threshold | TSS | eps | hours within eps | worst-case TSS | max shift |")
    print("|---|---|---|---|---|---|")
    for thr in (0.5, tuned):
        base = H.tss(y, (p > thr).astype(int))
        for eps in EPS:
            near = np.abs(p - thr) <= eps
            n_near = int(near.sum())
            if n_near == 0:
                print(f"| {thr:.2f} | {base:.3f} | {eps:g} | 0 | {base:.3f} | 0.000 |")
                continue
            # adversarial flip: push every borderline hour the damaging way --
            # true positives below the threshold, true negatives above it
            adv = (p > thr).astype(int)
            adv[near & (y == 1)] = 0
            adv[near & (y == 0)] = 1
            worst = H.tss(y, adv)
            print(f"| {thr:.2f} | {base:.3f} | {eps:g} | {n_near} | {worst:.3f} | "
                  f"{abs(base - worst):.3f} |")

# ------------------------------------------------------------------ margins
print("\n## How far are the headline observations from their thresholds?\n")
test = H.load("test")
onset = test[(test["label"] == 1) & (test["persist"] == 0)]
print(f"The 0/27 zero-catch observation at the shipped 0.5 threshold: the largest")
print(f"probability among those 27 onset hours is **{onset['prob'].max():.4f}**, a")
print(f"margin of {0.5 - onset['prob'].max():.4f} below the threshold. No plausible")
print("numerical perturbation reaches that.\n")

for split in ("validation", "test"):
    df = H.load(split)
    p = df["prob"].to_numpy()
    for thr in (0.5,):
        d = np.abs(p - thr)
        print(f"- {split} @ {thr}: closest hour is {d.min():.5f} from the threshold; "
              f"{int((d <= 1e-3).sum())} hours within 1e-3, "
              f"{int((d <= 1e-2).sum())} within 1e-2")

print("\n## Verdict\n")
print("If the worst-case shifts above are small relative to the 0.46-0.81 wide")
print("confidence intervals we already report, then bf16-vs-fp32 cannot change any")
print("conclusion in the manuscript, and the open item can be stated as bounded")
print("rather than unresolved. A confirmatory fp32 run remains desirable and")
print("cheap; this analysis says what it could and could not overturn.")

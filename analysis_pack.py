#!/usr/bin/env python3
"""HELIOFLOOR analysis package: block-bootstrap intervals, calibration and its
transfer, onset-vs-continuation stratification, per-year breakdown.

All loading, metrics and bootstrapping come from heliofloor_data, so this script
cannot drift from the others on sample size or block count. No GPU, no scipy,
no sklearn.

Run:  venv-quick/bin/python analysis_pack.py > analysis_output.md
"""
import numpy as np
import pandas as pd

import heliofloor_data as H


def scoreboard(df, title):
    y = df["label"].to_numpy()
    print(f"\n### {title}")
    print(f"n={len(df)}, positives={int(y.sum())}, base rate={y.mean():.3f}, "
          f"blocks={df['block'].nunique()}, "
          f"positive-containing blocks={df[df['label']==1]['block'].nunique()}")
    print("\n| model | TP | FN | FP | TN | TSS | TSS 95% CI | HSS | F1 |")
    print("|---|---|---|---|---|---|---|---|---|")
    rows = [(f"Surya @ {t}", (df["prob"] > t).astype(int).to_numpy(), t)
            for t in (0.5, 0.1, 0.05)]
    rows.append(("persistence (t-24h)", df["persist"].to_numpy(), None))
    for name, pred, thr in rows:
        tp, fn, fp, tn = H.cm(y, pred)
        if thr is None:
            lo, hi = H.block_bootstrap(
                df, lambda s: H.tss(s["label"].to_numpy(), s["persist"].to_numpy()))
        else:
            lo, hi = H.block_bootstrap(
                df, lambda s, t=thr: H.tss(s["label"].to_numpy(),
                                           (s["prob"] > t).astype(int).to_numpy()))
        print(f"| {name} | {tp} | {fn} | {fp} | {tn} | {H.tss(y, pred):.3f} | "
              f"[{lo:.3f}, {hi:.3f}] | {H.hss(y, pred):.3f} | {H.f1(y, pred):.3f} |")

    thr, best = H.best_threshold(df)
    lo, hi = H.block_bootstrap(
        df, lambda s, t=thr: H.tss(s["label"].to_numpy(),
                                   (s["prob"] > t).astype(int).to_numpy()))
    print(f"\nBest Surya TSS = **{best:.3f}** at threshold {thr:.2f} "
          f"(block bootstrap 95% CI [{lo:.3f}, {hi:.3f}])")
    return thr


# ------------------------------------------------------------- calibration
def logit(p, eps=1e-6):
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


def fit_platt(p, y, iters=4000, lr=0.05):
    """1-D logistic recalibration sigmoid(a*logit(p)+b), plain gradient descent."""
    x, a, b = logit(p), 1.0, 0.0
    for _ in range(iters):
        e = 1 / (1 + np.exp(-(a * x + b))) - y
        a -= lr * np.mean(e * x)
        b -= lr * np.mean(e)
    return a, b


def apply_platt(p, a, b):
    return 1 / (1 + np.exp(-(a * logit(p) + b)))


def reliability(df, bins=(0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.01)):
    print("\n| probability bin | n | blocks | mean predicted | observed frequency |")
    print("|---|---|---|---|---|")
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (df["prob"] >= lo) & (df["prob"] < hi)
        if m.sum():
            print(f"| [{lo:.2f}, {hi:.2f}) | {int(m.sum())} | "
                  f"{int(df.loc[m, 'block'].nunique())} | "
                  f"{df.loc[m, 'prob'].mean():.3f} | {df.loc[m, 'label'].mean():.3f} |")


def onset_analysis(df, thr, title):
    y = df["label"].to_numpy()
    pos = df[df["label"] == 1]
    onset = pos[pos["persist"] == 0]      # persistence is structurally blind here
    contin = pos[pos["persist"] == 1]     # persistence is trivially right here
    decay = df[(df["label"] == 0) & (df["persist"] == 1)]   # and false-alarms here
    print(f"\n### {title} — onset / continuation split")
    print(f"- positive hours: {len(pos)} (onset {len(onset)}, continuation {len(contin)})")
    print(f"- persistence false-alarm zone (decay): {len(decay)} hours")
    print(f"- onset hours occupy {onset['block'].nunique()} independent blocks "
          f"-> rule of three upper bound {3/max(onset['block'].nunique(),1):.3f}")
    print(f"- **ONSET caught:** persistence 0/{len(onset)} (structurally impossible), "
          f"Surya@{thr:.2f} {int((onset['prob'] > thr).sum())}/{len(onset)} "
          f"(in {onset[onset['prob']>thr]['block'].nunique()}/{onset['block'].nunique()} blocks), "
          f"Surya@0.5 {int((onset['prob'] > 0.5).sum())}/{len(onset)} "
          f"(in {onset[onset['prob']>0.5]['block'].nunique()}/{onset['block'].nunique()} blocks)")
    print(f"- **CONTINUATION caught:** persistence {len(contin)}/{len(contin)} (structurally certain), "
          f"Surya@{thr:.2f} {int((contin['prob'] > thr).sum())}/{len(contin)}, "
          f"Surya@0.5 {int((contin['prob'] > 0.5).sum())}/{len(contin)}")
    print(f"- **DECAY (false alarms):** persistence {len(decay)}/{len(decay)}, "
          f"Surya@{thr:.2f} {int((decay['prob'] > thr).sum())}/{len(decay)}")
    hyb = ((df["prob"] > thr) | (df["persist"] == 1)).astype(int).to_numpy()
    print(f"- hybrid (persistence OR Surya@{thr:.2f}): TSS={H.tss(y, hyb):.3f}, "
          f"HSS={H.hss(y, hyb):.3f}, F1={H.f1(y, hyb):.3f}")


def per_year(df, thr, title):
    print(f"\n### {title} — by year (threshold {thr:.2f})")
    print("| year | n | positives | Surya TSS | persistence TSS |")
    print("|---|---|---|---|---|")
    for yr, g in df.groupby(df["ts"].dt.year):
        gy = g["label"].to_numpy()
        if gy.sum() == 0:
            print(f"| {yr} | {len(g)} | 0 | — (no positives) | — |")
            continue
        s = H.tss(gy, (g["prob"] > thr).astype(int).to_numpy())
        p = H.tss(gy, g["persist"].to_numpy())
        print(f"| {yr} | {len(g)} | {int(gy.sum())} | {s:.3f} | {p:.3f} |")


# -------------------------------------------------------------------- main
val = H.load("validation")
test = H.load("test")
print(f"label mismatches vs official CSVs: validation "
      f"{H.label_mismatches(val, 'validation')}, test {H.label_mismatches(test, 'test')}")

for name, df, title in (("validation", val, "EXPANDED VALIDATION (2011-2019)"),
                        ("test", test, "TEST (2020-2024)")):
    thr = scoreboard(df, title)
    per_year(df, thr, title.split()[0].title())
    onset_analysis(df, thr, title.split()[0].title())
    print(f"\n### {title.split()[0].title()} — reliability (calibration) table")
    reliability(df)
    print(f"\nBrier score (raw Surya): "
          f"{H.brier(df['prob'].to_numpy(), df['label'].to_numpy()):.4f}")

# ---- cross-split calibration transfer: fit on validation, apply to test
yv = val["label"].to_numpy()
yt = test["label"].to_numpy()
a, b = fit_platt(val["prob"].to_numpy(), yv.astype(float))
cal_p = apply_platt(test["prob"].to_numpy(), a, b)
print("\n### CALIBRATION TRANSFER (fitted on validation -> applied to test)")
print(f"Platt parameters: a={a:.3f}, b={b:.3f}")
print("\n| model | TSS@0.5 | HSS@0.5 | F1@0.5 | Brier |")
print("|---|---|---|---|---|")
raw = (test["prob"] > 0.5).astype(int).to_numpy()
cal = (cal_p > 0.5).astype(int)
print(f"| raw Surya | {H.tss(yt, raw):.3f} | {H.hss(yt, raw):.3f} | {H.f1(yt, raw):.3f} | "
      f"{H.brier(test['prob'].to_numpy(), yt):.4f} |")
print(f"| Platt-calibrated Surya | {H.tss(yt, cal):.3f} | {H.hss(yt, cal):.3f} | "
      f"{H.f1(yt, cal):.3f} | {H.brier(cal_p, yt):.4f} |")
pt = test["persist"].to_numpy()
print(f"| persistence | {H.tss(yt, pt):.3f} | {H.hss(yt, pt):.3f} | {H.f1(yt, pt):.3f} | — |")
lo, hi = H.block_bootstrap(
    test, lambda s: H.tss(s["label"].to_numpy(),
                          (apply_platt(s["prob"].to_numpy(), a, b) > 0.5).astype(int)))
print(f"\nPlatt-calibrated Surya TSS@0.5 block-bootstrap 95% CI: [{lo:.3f}, {hi:.3f}]")

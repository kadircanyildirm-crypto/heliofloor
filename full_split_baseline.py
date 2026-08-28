#!/usr/bin/env python3
"""H3, strong form: the cheap GOES-history baseline on the COMPLETE official
splits — every hour, not our stratified sample.

Protocol, fixed in advance so nothing is cherry-picked:
  * weights fitted on the official TRAIN split (Feb 15 - Dec 31, 2010-2019)
  * ONE decision threshold chosen on the FULL VALIDATION split
  * that threshold frozen and applied to the FULL TEST split (2020-2024)
Persistence and climatology are scored on the same hours for reference.

The resulting numbers are NOT matched to our model measurements: the baseline
runs on every hour, the model on our sample. They corroborate the matched
comparison in goes_baseline.py; they do not replace it.

Run:  venv-quick/bin/python full_split_baseline.py > full_split_output.md
"""
import numpy as np

import heliofloor_data as H

w, mu, sd = H.train_goes_model()

# ------------------------------------------- pick ONE threshold on validation
va = H.load_official("validation")
va["p"] = H.score_goes(w, mu, sd, va["ts"])
yv = va["label_max"].to_numpy()
THR = H.best_threshold(va.rename(columns={"label_max": "label"}), "p")[0]
print(f"\nthreshold chosen on the FULL validation split and frozen: {THR:.2f}")

te = H.load_official("test")
te["p"] = H.score_goes(w, mu, sd, te["ts"])

print("\n| split | n | base rate | model | TSS | TSS 95% CI | HSS | F1 | TP/FN/FP/TN |")
print("|---|---|---|---|---|---|---|---|---|")
for name, df in (("validation (full)", va), ("test (full)", te)):
    y = df["label_max"].to_numpy()
    # the complete splits are contiguous, so block on calendar days: the same
    # 24-hour unit used for the sampled hours, and the shortest defensible one
    # given that the label window is itself 24 hours long
    df = df.assign(label=y, block=df["ts"].dt.floor("D"))
    for label, pred, col in (
            ("GOES-history logistic", (df["p"] > THR).astype(int).to_numpy(), "p"),
            ("persistence (t-24h)", df["persist"].to_numpy(), "persist"),
            ("climatology (always no)", np.zeros(len(y), int), None)):
        tp, fn, fp, tn = H.cm(y, pred)
        if col == "p":
            lo, hi = H.block_bootstrap(
                df, lambda s: H.tss(s["label"].to_numpy(),
                                    (s["p"] > THR).astype(int).to_numpy()), n_boot=500)
            ci = f"[{lo:.3f}, {hi:.3f}]"
        elif col == "persist":
            lo, hi = H.block_bootstrap(
                df, lambda s: H.tss(s["label"].to_numpy(), s["persist"].to_numpy()),
                n_boot=500)
            ci = f"[{lo:.3f}, {hi:.3f}]"
        else:
            ci = "—"
        print(f"| {name} | {len(df)} | {y.mean():.4f} | {label} | "
              f"**{H.tss(y, pred):.3f}** | {ci} | {H.hss(y, pred):.3f} | "
              f"{H.f1(y, pred):.3f} | {tp}/{fn}/{fp}/{tn} |")

# ------------------------------------- per-year test split: non-stationarity
print("\n| year | n | base rate | GOES-logistic TSS | persistence TSS |")
print("|---|---|---|---|---|")
rates = {}
for yr, g in te.groupby(te["ts"].dt.year):
    y = g["label_max"].to_numpy()
    a = H.tss(y, (g["p"] > THR).astype(int).to_numpy())
    b = H.tss(y, g["persist"].to_numpy())
    rates[int(yr)] = (float(y.mean()), a)
    print(f"| {yr} | {len(g)} | {y.mean():.3f} | {a:.3f} | {b:.3f} |")

lo_yr, hi_yr = min(rates, key=lambda k: rates[k][0]), max(rates, key=lambda k: rates[k][0])
fold = rates[hi_yr][0] / rates[lo_yr][0]
pooled = H.tss(te["label_max"].to_numpy(), (te["p"] > THR).astype(int).to_numpy())
peryear = [v[1] for v in rates.values()]
print(f"\nbase-rate shift across the split: {rates[lo_yr][0]:.5f} ({lo_yr}) -> "
      f"{rates[hi_yr][0]:.5f} ({hi_yr}) = **{fold:.1f}-fold**")
print(f"pooled test TSS {pooled:.3f} vs per-year range "
      f"{min(peryear):.3f}..{max(peryear):.3f} — pooled exceeds every single year: "
      f"{pooled > max(peryear)}")

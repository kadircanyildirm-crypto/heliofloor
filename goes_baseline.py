#!/usr/bin/env python3
"""H3: can a logistic model that sees ONLY past GOES X-ray flux match Surya,
which sees 13 channels of full-disk SDO imagery?

Evaluated on exactly the hours we scored with the model, so the comparison is
matched hour for hour.

Leakage guard: in SuryaBench, max_goes_class[t] is the maximum class over
[t, t+24h) -- verified label_max == (max_goes_class >= M1.0) on 128,328 of
128,328 rows -- so that column is FORWARD-looking and unusable at time t. Every
feature here is read at t-24h or earlier.

Run:  venv-quick/bin/python goes_baseline.py > goes_baseline_output.md
"""
import numpy as np

import heliofloor_data as H

w, mu, sd = H.train_goes_model()
print("standardised feature weights:")
for f, ww in sorted(zip(H.FEATS, w[:-1]), key=lambda x: -abs(x[1])):
    print(f"   {f:10s} {ww:+.3f}")


def evaluate(split):
    df = H.load(split)
    df["goes"] = H.score_goes(w, mu, sd, df["ts"])
    y = df["label"].to_numpy()

    bs_thr, bs_tss = H.best_threshold(df, "prob")
    bg_thr, bg_tss = H.best_threshold(df, "goes")

    print(f"\n### {split.upper()} — H3 baseline comparison "
          f"(n={len(df)}, positives={int(y.sum())}, blocks={df['block'].nunique()})")
    print("| model | input | TSS | TSS 95% CI | HSS | F1 |")
    print("|---|---|---|---|---|---|")
    rows = [
        ("climatology (always 'no')", "—", np.zeros(len(y), int), None),
        ("persistence (t-24h)", "past 24h X-ray", df["persist"].to_numpy(), "persist"),
        (f"GOES-history logistic @{bg_thr:.2f}", "7 days of X-ray history",
         (df["goes"] > bg_thr).astype(int).to_numpy(), ("goes", bg_thr)),
        ("Surya @0.5 (shipped)", "13-channel SDO imagery",
         (df["prob"] > 0.5).astype(int).to_numpy(), ("prob", 0.5)),
        (f"Surya @{bs_thr:.2f} (tuned)", "13-channel SDO imagery",
         (df["prob"] > bs_thr).astype(int).to_numpy(), ("prob", bs_thr)),
        (f"hybrid: persistence OR Surya@{bs_thr:.2f}", "both",
         ((df["prob"] > bs_thr) | (df["persist"] == 1)).astype(int).to_numpy(), None),
        (f"hybrid: GOES-logistic OR Surya@{bs_thr:.2f}", "both",
         ((df["prob"] > bs_thr) | (df["goes"] > bg_thr)).astype(int).to_numpy(), None),
    ]
    for name, inp, pred, boot in rows:
        ci = "—"
        if boot == "persist":
            lo, hi = H.block_bootstrap(
                df, lambda s: H.tss(s["label"].to_numpy(), s["persist"].to_numpy()))
            ci = f"[{lo:.3f}, {hi:.3f}]"
        elif boot:
            col, thr = boot
            lo, hi = H.block_bootstrap(
                df, lambda s, c=col, t=thr: H.tss(s["label"].to_numpy(),
                                                  (s[c] > t).astype(int).to_numpy()))
            ci = f"[{lo:.3f}, {hi:.3f}]"
        print(f"| {name} | {inp} | {H.tss(y, pred):.3f} | {ci} | "
              f"{H.hss(y, pred):.3f} | {H.f1(y, pred):.3f} |")
    return df


for s in ("validation", "test"):
    evaluate(s)

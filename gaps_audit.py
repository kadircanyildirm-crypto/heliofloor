#!/usr/bin/env python3
"""Three targeted attacks on our own paper, before a referee mounts them.

GAP A — is `cumulative_index` forward-looking over exactly 24 h?
    We verified the direction of `max_goes_class` (it sources label_max over
    [t, t+24h)) but silently assumed the same window for `cumulative_index`,
    whose lag-24 value is the GOES model's strongest feature (+0.863). If its
    window were longer than 24 h, ci at t-24h would leak into the label window
    and the headline baseline would be invalid. Tests:
      1. if a label_cum column exists, look for an exact identity with a
         threshold on cumulative_index (mirroring the label_max identity);
      2. lag correlation: a 24h-forward aggregate correlates most with
         max_goes_class[t] (same window), and no more with fx[t+24] than
         with fx[t-24]. A 48h-forward aggregate would love fx[t+24].

GAP B — multiplicity. We run ten simultaneous paired tests at 95%. Report each
    pair's tail fraction (share of draws on the wrong side of zero) and, for
    the two zero-excluders, the Bonferroni-corrected 99.5% interval
    (family alpha 0.05 over m=10).

GAP C — the full-split intervals use calendar-day blocks, but flare episodes
    span days, so adjacent day-blocks are correlated and 1-day blocks may be
    too narrow. Recompute the section 4.1/4.2 intervals with 2-day and 3-day
    blocks and see whether any conclusion moves.

Run:  venv-quick/bin/python gaps_audit.py > gaps_audit_output.md
"""
import numpy as np
import pandas as pd

import heliofloor_data as H

print("# Gap audit: attacking our own claims\n")

# ================================================================= GAP A
print("## A. cumulative_index direction\n")
full = pd.read_csv(f"{H.D}/data.csv")
full["ts"] = pd.to_datetime(full["timestamp"])
print(f"data.csv columns: {list(full.columns)}\n")

full["fx"] = full["max_goes_class"].map(H.flux)
# finite masking matters here: the four A0.0 hours parse to flux 0, whose log10
# is -inf, and a single -inf poisons a whole correlation into NaN
full = full.sort_values("ts").reset_index(drop=True)
lg = np.log10(full.set_index("ts")["fx"])
cis = full.set_index("ts")["cumulative_index"]
idx = cis.index


def corr_at(hours):
    other = lg.reindex(idx + pd.Timedelta(hours=hours)).to_numpy()
    a = cis.to_numpy(float)
    m = np.isfinite(a) & np.isfinite(other)
    return float(np.corrcoef(a[m], other[m])[0, 1]), int(m.sum())


print("correlation of cumulative_index[t] with log-flux max over ...")
for label, h in [("[t,     t+24h)  (same window as label)", 0),
                 ("[t-24h, t)      (one window back)     ", -24),
                 ("[t+24h, t+48h)  (one window forward)  ", 24),
                 ("[t-48h, t-24h)  (two back)            ", -48),
                 ("[t+48h, t+72h)  (two forward)         ", 48)]:
    c, n = corr_at(h)
    print(f"  {label}: {c:+.3f}  (n={n})")
print("""
Reading: if ci[t] aggregates [t, t+24h), the same-window correlation dominates
and forward/backward neighbours are roughly symmetric. A window longer than
24h would show the forward neighbour beating the backward one.""")

if "label_cum" in full.columns:
    print("\nlabel_cum exists — testing threshold identities against cumulative_index:")
    best = None
    for thr in sorted(full["cumulative_index"].unique()):
        agree = int(((full["cumulative_index"] >= thr).astype(int) == full["label_cum"]).sum())
        if best is None or agree > best[1]:
            best = (thr, agree)
    print(f"  best threshold {best[0]}: {best[1]}/{len(full)} rows agree "
          f"({'EXACT IDENTITY' if best[1] == len(full) else 'not exact'})")
else:
    print("\nlabel_cum not in data.csv; relying on the correlation fingerprint.")

# ================================================================= GAP B
print("\n## B. Multiplicity across the ten paired tests\n")
w, mu, sd = H.train_goes_model(verbose=False)
PAIRS = [("goes", "surya_tuned", "GOES-SuryaTuned"),
         ("surya_tuned", "persistence", "SuryaTuned-Persist"),
         ("goes", "persistence", "GOES-Persist"),
         ("surya05", "persistence", "Surya05-Persist"),
         ("hybrid", "surya_tuned", "Hybrid-SuryaTuned")]

print("| split | pair | point | tail frac (wrong side of 0) | 99.5% CI (Bonferroni m=10) |")
print("|---|---|---|---|---|")
for split in ("validation", "test"):
    df = H.load(split)
    df["goes"] = H.score_goes(w, mu, sd, df["ts"])
    s_thr, _ = H.best_threshold(df, "prob")
    g_thr, _ = H.best_threshold(df, "goes")
    preds = {
        "persistence": df["persist"].to_numpy(),
        "surya05": (df["prob"] > 0.5).astype(int).to_numpy(),
        "surya_tuned": (df["prob"] > s_thr).astype(int).to_numpy(),
        "goes": (df["goes"] > g_thr).astype(int).to_numpy(),
        "hybrid": ((df["prob"] > s_thr) | (df["persist"] == 1)).astype(int).to_numpy(),
    }
    y = df["label"].to_numpy()
    blocks_idx = [g.index.to_numpy() for _, g in df.groupby("block")]
    rng = np.random.default_rng(H.SEED)
    draws = {t: [] for _, _, t in PAIRS}
    for _ in range(4000):
        pick = rng.integers(0, len(blocks_idx), len(blocks_idx))
        idx = np.concatenate([blocks_idx[i] for i in pick])
        yy = y[idx]
        t_ = {c: H.tss(yy, preds[c][idx]) for c in preds}
        for a, b, tag in PAIRS:
            d = t_[a] - t_[b]
            if not np.isnan(d):
                draws[tag].append(d)
    for a, b, tag in PAIRS:
        arr = np.asarray(draws[tag])
        point = H.tss(y, preds[a]) - H.tss(y, preds[b])
        tail = float((arr <= 0).mean() if point > 0 else (arr >= 0).mean())
        lo995, hi995 = np.percentile(arr, [0.25, 99.75])
        print(f"| {split} | {tag} | {point:+.3f} | {tail:.4f} | "
              f"[{lo995:+.3f}, {hi995:+.3f}] |")

print("""
Reading: family alpha 0.05 over ten tests needs per-test 0.005 (99.5% CI).
A pair whose 99.5% interval still excludes zero survives Bonferroni; the tail
fraction is the bootstrap's one-sided evidence, comparable against 0.0025.""")

# ================================================================= GAP C
print("\n## C. Full-split intervals under longer blocks\n")
va = H.load_official("validation")
va["p"] = H.score_goes(w, mu, sd, va["ts"])
THR = H.best_threshold(va.rename(columns={"label_max": "label"}), "p")[0]
te = H.load_official("test")
te["p"] = H.score_goes(w, mu, sd, te["ts"])

print(f"frozen threshold {THR:.2f} (unchanged)\n")
print("| split | model | TSS | 1-day blocks | 2-day blocks | 3-day blocks |")
print("|---|---|---|---|---|---|")
for name, d in (("validation", va), ("test", te)):
    y = d["label_max"].to_numpy()
    for label, predcol in (("GOES logistic", (d["p"] > THR).astype(int)),
                           ("persistence", d["persist"])):
        point = H.tss(y, predcol.to_numpy())
        cells = []
        for k in (1, 2, 3):
            dd = d.assign(label=y,
                          block=(d["ts"].dt.dayofyear - 1) // k
                                + d["ts"].dt.year * 1000)
            pr = predcol.to_numpy()
            dd = dd.assign(_pred=pr)
            lo, hi = H.block_bootstrap(
                dd, lambda s: H.tss(s["label"].to_numpy(), s["_pred"].to_numpy()),
                n_boot=400)
            cells.append(f"[{lo:.3f}, {hi:.3f}]")
        print(f"| {name} | {label} | {point:.3f} | {' | '.join(cells)} |")

print("""
Reading: what matters is whether any conclusion moves — does the validation
persistence interval still contain 0.436, and does the validation GOES interval
still exclude it — as the block length doubles and triples.""")

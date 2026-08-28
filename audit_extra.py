#!/usr/bin/env python3
"""Second audit pass: the quantities the manuscript states in prose rather than
in a table, and which the claim-checker in verify_paper.py cannot reach.

Answers, with numbers:
  1. why the sampler's 36+20 planned blocks become 50+28 recovered ones
  2. how many hours the archive gaps actually cost
  3. how many distinct netCDF files the study streamed (the "~700 GB" claim)
  4. the onset catch-rate intervals, so section 4.4 stops contradicting itself
  5. the flux-parser edge cases that produce non-finite features
"""
import numpy as np
import pandas as pd

import os as _os

BASE = _os.environ.get("HELIOFLOOR_DIR",
                       _os.path.dirname(_os.path.abspath(__file__)))
D = _os.environ.get("SURYABENCH_FLARE_DIR", _os.path.join(BASE, "data", "flare"))


def flux(c):
    c = str(c).strip()
    if not c or c in ("FQ", "nan"):
        return 1e-9
    mult = {"A": 1e-8, "B": 1e-7, "C": 1e-6, "M": 1e-5, "X": 1e-4}.get(c[0])
    if mult is None:
        return 1e-9
    try:
        return mult * float(c[1:])
    except ValueError:
        return mult


full = pd.read_csv(f"{D}/data.csv")
full["ts"] = pd.to_datetime(full["timestamp"])
full["fx"] = full["max_goes_class"].map(flux)
FX = dict(zip(full["ts"], full["fx"]))


def load(files):
    df = pd.concat([pd.read_csv(f"{BASE}/{f}") for f in files], ignore_index=True)
    df["ts"] = pd.to_datetime(df["timestamp"])
    df = df.drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    df["persist"] = [1 if FX.get(t - pd.Timedelta(hours=24), 0.0) >= 1e-5 else 0
                     for t in df["ts"]]
    df["block"] = (df["ts"].diff() > pd.Timedelta(hours=3)).cumsum()
    return df


val = load(["probs_validation_full.csv", "probs_validation_ek.csv"])
test = load(["probs_test_full.csv"])

print("=" * 92)
print("1-2. BLOCK STRUCTURE: planned 24h windows vs recovered contiguous runs")
print("=" * 92)
for name, df, planned in (("validation", val, 36), ("test", test, 20)):
    sizes = df.groupby("block").size()
    # a planned window = a calendar day that contains any scored hour
    days = df["ts"].dt.floor("D").nunique()
    print(f"\n{name}: {len(df)} scored hours, {df['block'].nunique()} recovered blocks, "
          f"{days} distinct calendar days")
    print(f"  planned windows (from plan_blocks.py): {planned} x 24h = {planned*24} hours")
    print(f"  actually scored                      : {len(df)} hours "
          f"({planned*24 - len(df)} short)")
    print(f"  recovered-block sizes: min {sizes.min()}, median {int(sizes.median())}, "
          f"max {sizes.max()}")
    print(f"  size histogram: {dict(sorted(sizes.value_counts().items()))}")
    # how many recovered blocks are fragments (< 20 h) vs near-complete
    print(f"  blocks with >=20 h: {(sizes >= 20).sum()};  fragments (<20 h): {(sizes < 20).sum()}")

print()
print("=" * 92)
print("3. netCDF FILES STREAMED  (input is two timesteps: t-60min and t)")
print("=" * 92)
tot = 0
for name, df in (("validation", val), ("test", test)):
    need = set()
    for t in df["ts"]:
        need.add(t)
        need.add(t - pd.Timedelta(hours=1))
    tot += len(need)
    print(f"  {name}: {len(df)} forecast hours -> {len(need)} distinct timesteps")
print(f"  TOTAL distinct timesteps: {tot}")
print(f"  at ~586 MB per timestep  : {tot*586/1024:.0f} GB")

print()
print("=" * 92)
print("4. ONSET CATCH RATES with block-bootstrap intervals (section 4.4)")
print("=" * 92)


def rate_ci(df, mask_fn, hit_fn, n=4000, seed=42):
    rng = np.random.default_rng(seed)
    blocks = [g for _, g in df.groupby("block")]
    vals = []
    for _ in range(n):
        s = pd.concat([blocks[i] for i in rng.integers(0, len(blocks), len(blocks))],
                      ignore_index=True)
        sub = s[mask_fn(s)]
        if len(sub) >= 3:
            vals.append(hit_fn(sub).mean())
    return (np.percentile(vals, 2.5), np.percentile(vals, 97.5)) if vals else (np.nan, np.nan)


for name, df, thr in (("validation", val, 0.16), ("test", test, 0.04)):
    onset = df[(df["label"] == 1) & (df["persist"] == 0)]
    nb = onset["block"].nunique()
    print(f"\n{name}: {len(onset)} onset hours in {nb} independent blocks")
    for lbl, fn in ((f"Surya @{thr:.2f} (tuned)", lambda s, t=thr: s["prob"] > t),
                    ("Surya @0.50 (shipped)", lambda s: s["prob"] > 0.5)):
        hits = int(fn(onset).sum())
        lo, hi = rate_ci(df, lambda s: (s["label"] == 1) & (s["persist"] == 0), fn)
        blocks_hit = onset[fn(onset)]["block"].nunique()
        print(f"  {lbl:24s}: {hits:2d}/{len(onset)} = {hits/len(onset):.3f}  "
              f"95% CI [{lo:.3f}, {hi:.3f}]  (hits in {blocks_hit}/{nb} blocks)")
    print(f"  {'persistence':24s}:  0/{len(onset)} = 0.000  structural, no interval")
    print(f"  rule of three on block-effective n: 3/{nb} = {3/nb:.3f}")

print()
print("=" * 92)
print("5. FLUX-PARSER EDGE CASES (why some feature rows are non-finite)")
print("=" * 92)
zero = full[full["fx"] <= 0]
print(f"  rows where parsed flux == 0 (log10 -> -inf): {len(zero)}")
if len(zero):
    print(f"  the classes responsible: {sorted(zero['max_goes_class'].astype(str).unique())[:12]}")
blank = full["max_goes_class"].isna().sum()
print(f"  rows with missing max_goes_class          : {blank}")
print(f"  total rows in data.csv                    : {len(full)}")
print(f"  distinct class prefixes                   : "
      f"{sorted({str(c)[0] for c in full['max_goes_class'].dropna().unique()})}")

print()
print("=" * 92)
print("6. SPLIT DEFINITIONS as they appear in the released CSVs")
print("=" * 92)
for s in ("train", "validation", "leaky_validation", "test"):
    d = pd.read_csv(f"{D}/{s}.csv")
    d["ts"] = pd.to_datetime(d["timestamp"])
    yrs = sorted(d["ts"].dt.year.unique())
    md = sorted({f"{m:02d}-{dd:02d}" for m, dd in zip(d["ts"].dt.month, d["ts"].dt.day)})
    print(f"  {s:18s} n={len(d):6d}  years {yrs[0]}-{yrs[-1]} ({len(yrs)} yrs)  "
          f"base={d['label_max'].mean():.4f}")
    print(f"  {'':18s} calendar span: {md[0]} .. {md[-1]}  ({len(md)} distinct month-days)")

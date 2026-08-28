#!/usr/bin/env python3
"""HELIOFLOOR: stratified contiguous-block sampling plan for the Colab run.

Validation (2011-2019, Jan15-31): 2 x 24h blocks/year, gap-checked against
valid_index_surya_1_0.csv. Test (2020-2024): 4 x 24h blocks/year (presence
verified at download time). Seed 42, fully deterministic.
"""
import json
import os
import random

import pandas as pd

# Paths are environment-driven so the plan regenerates on any machine.
A = os.environ.get(
    "SURYA_ASSETS_DIR",
    "Surya/downstream_examples/solar_flare_forcasting/assets")
D = os.environ.get("SURYABENCH_FLARE_DIR",
                   os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "data", "flare"))
OUT = os.environ.get("HELIOFLOOR_OUT", "colab_pkg")
os.makedirs(OUT, exist_ok=True)

rng = random.Random(42)

vidx = pd.read_csv(f"{A}/valid_index_surya_1_0.csv")
vidx["ts"] = pd.to_datetime(vidx["timestep"])
hourly = vidx[(vidx["ts"].dt.minute == 0)].set_index("ts")
present = hourly["present"].to_dict()

def key_for(ts):
    return f"{ts.year}/{ts.month:02d}/{ts:%Y%m%d_%H%M}.nc"

blocks = []

# --- validation blocks ---
for year in range(2011, 2020):
    # block = 24 samples at hours start..start+23h; needs instants start-1h..start+23h
    lo = pd.Timestamp(f"{year}-01-15 01:00")
    hi = pd.Timestamp(f"{year}-01-31 00:00") - pd.Timedelta(hours=23)
    candidates = pd.date_range(lo, hi, freq="h")
    scored = []
    for s in candidates:
        sample_hours = pd.date_range(s, s + pd.Timedelta(hours=23), freq="h")
        usable = sum(
            1 for t in sample_hours
            if present.get(t, 0) == 1 and present.get(t - pd.Timedelta(hours=1), 0) == 1
        )
        if usable >= 18:
            scored.append((usable, rng.random(), s))
    scored.sort(reverse=True)
    chosen = []
    for usable, _, s in scored:
        if all(abs((s - c).total_seconds()) >= 25 * 3600 for c in chosen):
            chosen.append(s)
        if len(chosen) == 2:
            break
    if len(chosen) < 2:
        print(f"WARN {year}: only {len(chosen)} feasible validation blocks")
    for s in sorted(chosen):
        needed = pd.date_range(s - pd.Timedelta(hours=1), s + pd.Timedelta(hours=23), freq="h")
        keys = [key_for(t) for t in needed if present.get(t, 0) == 1]
        blocks.append({
            "split": "validation", "year": year, "start": str(s), "hours": 24,
            "s3_keys": keys,
        })

# --- test blocks ---
for year in range(2020, 2025):
    lo = pd.Timestamp(f"{year}-01-02 01:00")
    hi = pd.Timestamp(f"{year}-12-30 01:00")
    days = pd.date_range(lo, hi, freq="D")
    picked = []
    day_list = list(days)
    rng.shuffle(day_list)
    for d in day_list:
        if all(abs((d - p).days) >= 2 for p in picked):
            picked.append(d)
        if len(picked) == 4:
            break
    for s in sorted(picked):
        needed = pd.date_range(s - pd.Timedelta(hours=1), s + pd.Timedelta(hours=23), freq="h")
        blocks.append({
            "split": "test", "year": year, "start": str(s), "hours": 24,
            "s3_keys": [key_for(t) for t in needed],
        })

with open(f"{OUT}/blocks.json", "w") as f:
    json.dump(blocks, f, indent=1)

# --- flare-CSV subsets for the chosen hours ---
for split, csvname in (("validation", "validation"), ("test", "test")):
    flare = pd.read_csv(os.path.join(D, f"{csvname}.csv"))
    flare["ts"] = pd.to_datetime(flare["timestamp"])
    hours = set()
    for b in blocks:
        if b["split"] != split:
            continue
        s = pd.Timestamp(b["start"])
        hours.update(pd.date_range(s, s + pd.Timedelta(hours=23), freq="h"))
    sub = flare[flare["ts"].isin(hours)].drop(columns=["ts"])
    sub.to_csv(f"{OUT}/sample_{split}.csv", index=False)
    print(f"{split}: {len([b for b in blocks if b['split']==split])} blocks, "
          f"{len(sub)} samples, base_rate={sub['label_max'].mean():.4f}")

nkeys = sum(len(b["s3_keys"]) for b in blocks)
print(f"total blocks={len(blocks)}, s3 files={nkeys}, ~{nkeys*0.586:.0f} GB streamed")

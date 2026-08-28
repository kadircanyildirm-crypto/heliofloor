#!/usr/bin/env python3
"""HELIOFLOOR Colab runner — evaluate the released solar_flares_surya checkpoint
on a stratified, seeded (42) sample of the SuryaBench flare splits, streaming
SDO inputs from S3 (download -> infer -> delete).

Usage on Colab (GPU runtime, T4 or better):
    1. (Recommended) Runtime with GPU; optionally mount Drive for resume:
         from google.colab import drive; drive.mount('/content/drive')
    2. Upload this file, then:  !python heliofloor_colab.py
       or paste the whole file into a cell and run.

Output: probs_validation.csv / probs_test.csv (timestamp,label,prob) in OUT_DIR.
Re-running resumes: finished samples are skipped, finished blocks skip download.
"""
import json
import os
import random
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# ----------------------------- CONFIG ---------------------------------------
SPLITS = ["validation", "test"]   # run both; reorder or trim as needed
WORKERS = 1                        # dataloader workers (RAM!)
DTYPE = "bfloat16"
S3 = "https://nasa-surya-bench.s3.amazonaws.com"
DRIVE = "/content/drive/MyDrive"
OUT_DIR = os.path.join(DRIVE, "heliofloor") if os.path.isdir(DRIVE) else "/content/heliofloor"
WORK = "/content/hf_work"
REPO = "/content/Surya"
FLARE_DIR = os.path.join(REPO, "downstream_examples", "solar_flare_forcasting")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(WORK, exist_ok=True)
print(f"output dir: {OUT_DIR}")

# ----------------------------- SETUP ----------------------------------------
def sh(cmd):
    print("+", cmd)
    subprocess.run(cmd, shell=True, check=True)

if not os.path.isdir(REPO):
    sh(f"git clone --depth 1 https://github.com/NASA-IMPACT/Surya.git {REPO}")
    sh(f"pip -q install -e {REPO}")
    sh("pip -q install h5netcdf hf_transfer")

from huggingface_hub import hf_hub_download  # noqa: E402

def hf_get(repo_id, repo_type, filename):
    return hf_hub_download(repo_id=repo_id, repo_type=repo_type, filename=filename,
                           local_dir=WORK)

CKPT = hf_get("nasa-ibm-ai4science/solar_flares_surya", "model", "solar_flare_weights.pth")
BACKBONE = hf_get("nasa-ibm-ai4science/Surya-1.0", "model", "surya.366m.v1.pt")
SCALERS = hf_get("nasa-ibm-ai4science/Surya-1.0", "model", "scalers.yaml")
VALID_INDEX = hf_get("nasa-ibm-ai4science/core-sdo", "dataset", "valid_index_surya_1_0.csv")
FLARE_CSV = {
    s: hf_get("nasa-ibm-ai4science/surya-bench-flare-forecasting", "dataset", f"{s}.csv")
    for s in ("validation", "test")
}

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import requests  # noqa: E402
import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402
import yaml  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

# ------------------------- BLOCK PLAN (seed 42) ------------------------------
# Identical logic to the local planner — regenerates the same blocks.
def key_for(ts):
    return f"{ts.year}/{ts.month:02d}/{ts:%Y%m%d_%H%M}.nc"

def make_blocks():
    rng = random.Random(42)
    vidx = pd.read_csv(VALID_INDEX)
    vidx["ts"] = pd.to_datetime(vidx["timestep"])
    hourly = vidx[vidx["ts"].dt.minute == 0].set_index("ts")
    present = hourly["present"].to_dict()
    blocks = []
    for year in range(2011, 2020):
        lo = pd.Timestamp(f"{year}-01-15 01:00")
        hi = pd.Timestamp(f"{year}-01-31 00:00") - pd.Timedelta(hours=23)
        scored = []
        for s in pd.date_range(lo, hi, freq="h"):
            sample_hours = pd.date_range(s, s + pd.Timedelta(hours=23), freq="h")
            usable = sum(1 for t in sample_hours
                         if present.get(t, 0) == 1
                         and present.get(t - pd.Timedelta(hours=1), 0) == 1)
            if usable >= 18:
                scored.append((usable, rng.random(), s))
        scored.sort(reverse=True)
        chosen = []
        for usable, _, s in scored:
            if all(abs((s - c).total_seconds()) >= 25 * 3600 for c in chosen):
                chosen.append(s)
            if len(chosen) == 2:
                break
        for s in sorted(chosen):
            needed = pd.date_range(s - pd.Timedelta(hours=1), s + pd.Timedelta(hours=23), freq="h")
            keys = [key_for(t) for t in needed if present.get(t, 0) == 1]
            blocks.append({"split": "validation", "year": year, "start": str(s), "s3_keys": keys})
    for year in range(2020, 2025):
        days = list(pd.date_range(f"{year}-01-02 01:00", f"{year}-12-30 01:00", freq="D"))
        rng.shuffle(days)
        picked = []
        for d in days:
            if all(abs((d - p).days) >= 2 for p in picked):
                picked.append(d)
            if len(picked) == 4:
                break
        for s in sorted(picked):
            needed = pd.date_range(s - pd.Timedelta(hours=1), s + pd.Timedelta(hours=23), freq="h")
            blocks.append({"split": "test", "year": year, "start": str(s),
                           "s3_keys": [key_for(t) for t in needed]})
    return blocks

BLOCKS = make_blocks()
for s in SPLITS:
    n = sum(1 for b in BLOCKS if b["split"] == s)
    print(f"{s}: {n} blocks")

# --------------------------- MODEL (load once) -------------------------------
sys.path.insert(0, FLARE_DIR)
os.chdir(FLARE_DIR)
from dataset import SolarFlareDataset  # noqa: E402
from finetune import custom_collate_fn  # noqa: E402
from infer import load_model  # noqa: E402
from surya.utils.data import build_scalers  # noqa: E402

with open(os.path.join(FLARE_DIR, "config_infer.yaml")) as f:
    CONFIG = yaml.safe_load(f)
with open(SCALERS) as f:
    CONFIG["data"]["scalers"] = yaml.safe_load(f)
CONFIG["pretrained_path"] = BACKBONE
SCALER_OBJS = build_scalers(info=CONFIG["data"]["scalers"])
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL = load_model(CONFIG, CKPT, DEVICE)
TORCH_DTYPE = getattr(torch, DTYPE)
print(f"model on {DEVICE} ({torch.cuda.get_device_name(0) if DEVICE=='cuda' else 'cpu'})")

# --------------------------- STREAMING EVAL ----------------------------------
def fetch(key, dest):
    path = os.path.join(dest, os.path.basename(key))
    if os.path.exists(path):
        return key, True
    try:
        r = requests.get(f"{S3}/{key}", stream=True, timeout=120)
        if r.status_code != 200:
            return key, False
        with open(path + ".part", "wb") as f:
            for chunk in r.iter_content(1 << 22):
                f.write(chunk)
        os.rename(path + ".part", path)
        return key, True
    except Exception as e:
        print(f"  fetch fail {key}: {e}")
        return key, False

def run_block(block, out_csv, done):
    tag = f"{block['split']}/{block['start'][:10]}"
    bdir = os.path.join(WORK, "block")
    os.makedirs(bdir, exist_ok=True)
    t0 = time.time()
    with ThreadPoolExecutor(4) as ex:
        results = list(ex.map(lambda k: fetch(k, bdir), block["s3_keys"]))
    ok = [k for k, good in results if good]
    print(f"[{tag}] downloaded {len(ok)}/{len(block['s3_keys'])} files "
          f"in {time.time()-t0:.0f}s")
    idx = pd.DataFrame({
        "path": [os.path.basename(k) for k in ok],
        "timestep": [pd.Timestamp(f"{os.path.basename(k)[:4]}-{os.path.basename(k)[4:6]}-"
                                  f"{os.path.basename(k)[6:8]} {os.path.basename(k)[9:11]}:"
                                  f"{os.path.basename(k)[11:13]}:00") for k in ok],
        "present": 1,
    })
    idx_path = os.path.join(bdir, "index.csv")
    idx.to_csv(idx_path)

    flare = pd.read_csv(FLARE_CSV[block["split"]])
    flare["ts"] = pd.to_datetime(flare["timestamp"])
    s = pd.Timestamp(block["start"])
    hours = pd.date_range(s, s + pd.Timedelta(hours=23), freq="h")
    # exclude already-done hours BEFORE building the dataset — the loader loads
    # each sample's netCDF pair even when the eval loop would skip it
    hours_new = [h for h in hours
                 if np.datetime_as_string(np.datetime64(h), unit="m") not in done]
    sub = flare[flare["ts"].isin(hours_new)].drop(columns=["ts"])
    sub_path = os.path.join(bdir, "flare.csv")
    sub.to_csv(sub_path, index=False)

    ds = SolarFlareDataset(
        sdo_data_root_path=bdir, index_path=idx_path, flare_index_path=sub_path,
        time_delta_input_minutes=CONFIG["data"]["time_delta_input_minutes"],
        time_delta_target_minutes=CONFIG["data"]["time_delta_target_minutes"],
        n_input_timestamps=CONFIG["data"]["n_input_timestamps"],
        rollout_steps=CONFIG["rollout_steps"], scalers=SCALER_OBJS,
        channels=CONFIG["data"]["channels"], phase="valid",
        pooling=CONFIG["data"]["pooling"], random_vert_flip=False,
    )
    loader = DataLoader(ds, batch_size=1, num_workers=WORKERS, pin_memory=True,
                        shuffle=False, collate_fn=custom_collate_fn)
    n, t1 = 0, time.time()
    with torch.no_grad(), open(out_csv, "a") as f:
        for batch, metadata in loader:
            ts = np.datetime_as_string(
                np.array(metadata["timestamps_input"])[..., -1].ravel()[0], unit="m")
            if ts in done:
                continue
            label = int(batch["label"].item())
            batch = {k: v.to(DEVICE) for k, v in batch.items()}
            with torch.amp.autocast(device_type="cuda" if DEVICE == "cuda" else "cpu",
                                    dtype=TORCH_DTYPE):
                prob = float(F.sigmoid(MODEL(batch)).item())
            f.write(f"{ts},{label},{prob:.6f}\n")
            f.flush()
            done.add(ts)
            n += 1
    if n:
        print(f"[{tag}] {n} samples, {(time.time()-t1)/n:.0f} s/sample")
    shutil.rmtree(bdir)

for split in SPLITS:
    out_csv = os.path.join(OUT_DIR, f"probs_{split}.csv")
    done = set()
    if os.path.exists(out_csv):
        done = set(pd.read_csv(out_csv)["timestamp"].astype(str))
        print(f"{split}: resuming, {len(done)} samples already done")
    else:
        with open(out_csv, "w") as f:
            f.write("timestamp,label,prob\n")
    for block in [b for b in BLOCKS if b["split"] == split]:
        s = pd.Timestamp(block["start"])
        hours = [np.datetime_as_string(np.datetime64(h), unit="m")
                 for h in pd.date_range(s, s + pd.Timedelta(hours=23), freq="h")]
        # >=18 done counts as complete: data gaps mean a block rarely yields all
        # 24 hours, and re-downloading it would produce nothing new.
        if sum(h in done for h in hours) >= 18:
            continue
        run_block(block, out_csv, done)

# --------------------------- QUICK SUMMARY -----------------------------------
def tss_at(df, thr):
    p = (df["prob"] > thr).astype(int)
    tp = ((df.label == 1) & (p == 1)).sum(); fn = ((df.label == 1) & (p == 0)).sum()
    fp = ((df.label == 0) & (p == 1)).sum(); tn = ((df.label == 0) & (p == 0)).sum()
    pod = tp / (tp + fn) if tp + fn else float("nan")
    pofd = fp / (fp + tn) if fp + tn else float("nan")
    return pod - pofd

for split in SPLITS:
    out_csv = os.path.join(OUT_DIR, f"probs_{split}.csv")
    df = pd.read_csv(out_csv)
    if not len(df):
        continue
    best = max(((t, tss_at(df, t)) for t in np.arange(0.05, 0.96, 0.05)), key=lambda x: x[1])
    print(f"\n== {split}: n={len(df)}, base={df.label.mean():.3f} | "
          f"TSS@0.5={tss_at(df, 0.5):.3f} | best TSS={best[1]:.3f} @ thr={best[0]:.2f}")
print("\nDONE — download the probs_*.csv files for the full analysis.")

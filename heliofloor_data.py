#!/usr/bin/env python3
"""Canonical data loading and metrics for every HELIOFLOOR analysis script.

This module exists because two earlier scripts disagreed about the sample size
(739 vs 736 validation hours, 50 vs 49 blocks). The cause was the persistence
reference: one script looked up t-24h in the *split* file and dropped the three
hours whose reference falls in a neighbouring split, the other looked it up in
the complete hourly record and kept them. Every script now imports from here, so
the disagreement cannot recur.

Conventions fixed here
----------------------
persistence reference
    Read from `data.csv`, the complete hourly record. `max_goes_class[t]` is the
    maximum class over [t, t+24h), so `max_goes_class[t-24h]` covers [t-24h, t)
    -- strictly past, hence admissible at forecast time. Using the complete
    record avoids dropping hours merely because the reference hour is filed
    under a different split. Threshold M1.0 = 1e-5 W/m^2.

blocks
    A gap of more than 3 hours between consecutive scored hours starts a new
    block. Computed once, on the full scored set, before any filtering.

bootstrap
    Every interval reseeds its own generator (default 42), so a printed interval
    is reproducible on its own rather than depending on how many intervals were
    drawn before it.
"""
import os

import numpy as np
import pandas as pd

# Portable by default: the scored CSVs live next to this file, and the official
# SuryaBench flare CSVs are pointed at by an environment variable. Override
# either with HELIOFLOOR_DIR / SURYABENCH_FLARE_DIR.
BASE = os.environ.get("HELIOFLOOR_DIR",
                      os.path.dirname(os.path.abspath(__file__)))
D = os.environ.get("SURYABENCH_FLARE_DIR", os.path.join(BASE, "data", "flare"))
SEED = 42

MISSING_DATA = """\
SuryaBench flare CSVs not found at: {d}

Download validation.csv, test.csv, train.csv, leaky_validation.csv and data.csv
from the Hugging Face dataset

    nasa-ibm-ai4science/surya-bench-flare-forecasting

then point SURYABENCH_FLARE_DIR at the folder holding them:

    SURYABENCH_FLARE_DIR=/path/to/flare python {script}

The scored probabilities (probs_*.csv) are already in this repository, so no GPU
and no re-inference are needed once the CSVs are in place."""


def require_data(script="verify_paper.py"):
    """Fail with an actionable message rather than a bare FileNotFoundError."""
    if not os.path.isdir(D):
        raise SystemExit(MISSING_DATA.format(d=os.path.abspath(D), script=script))


require_data()

M1 = 1e-5          # W m^-2, the event threshold
BLOCK_GAP_H = 3    # a gap longer than this starts a new block

SPLIT_FILES = {
    "validation": ["probs_validation_full.csv", "probs_validation_ek.csv"],
    "test": ["probs_test_full.csv"],
}


def flux(c):
    """GOES class string -> peak flux in W m^-2. 'FQ'/unparseable -> quiet."""
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


_full = pd.read_csv(f"{D}/data.csv")
_full["ts"] = pd.to_datetime(_full["timestamp"])
_full["fx"] = _full["max_goes_class"].map(flux)
FX = dict(zip(_full["ts"], _full["fx"]))
CI = dict(zip(_full["ts"], _full["cumulative_index"]))
FULL = _full


def persistence_at(t):
    """The 24-hour persistence reference for forecast hour t (0/1)."""
    return 1 if FX.get(t - pd.Timedelta(hours=24), 0.0) >= M1 else 0


def load(split):
    """Scored hours for one split, with persistence reference and block index."""
    files = SPLIT_FILES[split]
    df = pd.concat([pd.read_csv(f"{BASE}/{f}") for f in files], ignore_index=True)
    df["ts"] = pd.to_datetime(df["timestamp"])
    df = df.drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    df["persist"] = [persistence_at(t) for t in df["ts"]]
    df["block"] = (df["ts"].diff() > pd.Timedelta(hours=BLOCK_GAP_H)).cumsum()
    return df


def load_official(split):
    """One complete official split with the persistence reference attached."""
    d = pd.read_csv(f"{D}/{split}.csv")
    d["ts"] = pd.to_datetime(d["timestamp"])
    d["persist"] = [persistence_at(t) for t in d["ts"]]
    return d


def label_mismatches(df, split):
    """How many of our scored labels disagree with the official split file."""
    t = pd.read_csv(f"{D}/{split}.csv")
    t["ts"] = pd.to_datetime(t["timestamp"])
    look = dict(zip(t["ts"], t["label_max"]))
    return sum(1 for ts, l in zip(df["ts"], df["label"])
               if look.get(ts) is not None and look.get(ts) != l)


# --------------------------------------------------------------------- metrics
def cm(y, p):
    return (int(((y == 1) & (p == 1)).sum()), int(((y == 1) & (p == 0)).sum()),
            int(((y == 0) & (p == 1)).sum()), int(((y == 0) & (p == 0)).sum()))


def tss(y, p):
    tp, fn, fp, tn = cm(y, p)
    return ((tp / (tp + fn) if tp + fn else np.nan)
            - (fp / (fp + tn) if fp + tn else np.nan))


def hss(y, p):
    tp, fn, fp, tn = cm(y, p)
    den = (tp + fn) * (fn + tn) + (tp + fp) * (fp + tn)
    return 2 * (tp * tn - fn * fp) / den if den else np.nan


def f1(y, p):
    tp, fn, fp, _ = cm(y, p)
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return 2 * pr * rc / (pr + rc) if pr + rc else 0.0


def brier(p, y):
    return float(np.mean((p - y) ** 2))


def block_bootstrap(df, score_fn, n_boot=2000, seed=SEED):
    """Resample whole blocks; hours inside a block are strongly autocorrelated.

    Reseeds per call, so each printed interval reproduces independently.
    """
    rng = np.random.default_rng(seed)
    blocks = [g for _, g in df.groupby("block")]
    vals = []
    for _ in range(n_boot):
        s = pd.concat([blocks[i] for i in rng.integers(0, len(blocks), len(blocks))],
                      ignore_index=True)
        v = score_fn(s)
        if not np.isnan(v):
            vals.append(v)
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def best_threshold(df, col="prob", grid=None):
    """Threshold maximising TSS, and that TSS."""
    grid = np.arange(0.01, 0.96, 0.01) if grid is None else grid
    y = df["label"].to_numpy()
    return max(((float(t), tss(y, (df[col] > t).astype(int).to_numpy())) for t in grid),
               key=lambda x: x[1])


# ------------------------------------------------- GOES-history logistic model
LAGS = [24, 48, 72, 96, 120, 144, 168]      # hours back; all >= 24h, so strictly past
FEATS = [f"lf{h}" for h in LAGS] + ["lf7dmax", "ci24", "ci48", "ci7dmean"]
_LF = {t: np.log10(f) if f > 0 else -np.inf for t, f in FX.items()}


def features(ts_list):
    rows = []
    for t in ts_list:
        lfs = [_LF.get(t - pd.Timedelta(hours=h), np.nan) for h in LAGS]
        cis = [CI.get(t - pd.Timedelta(hours=h), np.nan) for h in LAGS]
        # cumulative_index spans 0..1913 (std 73); log1p keeps z-scores sane
        rows.append(lfs + [np.nanmax(lfs), np.log1p(cis[0]), np.log1p(cis[1]),
                           np.log1p(np.nanmean(cis))])
    return pd.DataFrame(rows, columns=FEATS)


def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))


def fit_logreg(X, y, iters=8000, lr=0.1, l2=1e-3):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = np.hstack([np.clip((X - mu) / sd, -10, 10), np.ones((len(X), 1))])
    w = np.zeros(Z.shape[1])
    for _ in range(iters):
        w -= lr * (Z.T @ (sigmoid(Z @ w) - y) / len(y) + l2 * np.r_[w[:-1], 0.0])
    return w, mu, sd


def predict(w, mu, sd, X):
    Z = np.hstack([np.clip((X - mu) / sd, -10, 10), np.ones((len(X), 1))])
    return sigmoid(Z @ w)


def train_goes_model(verbose=True):
    """Fit the 11-feature logistic model on the official train split."""
    tr = pd.read_csv(f"{D}/train.csv")
    tr["ts"] = pd.to_datetime(tr["timestamp"])
    X = features(tr["ts"]).to_numpy()
    ok = np.isfinite(X).all(1)      # catches NaN and +-inf alike
    y = tr["label_max"].to_numpy()[ok].astype(float)
    w, mu, sd = fit_logreg(X[ok], y)
    if verbose:
        print(f"GOES-history logistic trained: n={int(ok.sum())} of {len(tr)} "
              f"({len(tr)-int(ok.sum())} rows dropped as non-finite), "
              f"base rate={y.mean():.4f}")
    return w, mu, sd


def score_goes(w, mu, sd, ts_list):
    X = features(ts_list).replace([np.inf, -np.inf], np.nan)
    return predict(w, mu, sd, X.fillna(X.median()).to_numpy())

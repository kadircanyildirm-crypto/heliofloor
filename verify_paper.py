#!/usr/bin/env python3
"""Claim-by-claim audit of PAPER_DRAFT.md.

Every numeric claim in the manuscript is recomputed here from the committed
probability CSVs and the official SuryaBench flare CSVs, then compared against
the value asserted in the text. Any disagreement is printed as FAIL.

Canonical conventions fixed by this script (and adopted by the paper):
  * The persistence reference at time t is read from `data.csv`, the complete
    hourly record, not from the split file. `max_goes_class[t-24h]` is the max
    class over [t-24h, t) -- strictly past, hence admissible -- and using the
    complete record avoids dropping hours merely because their reference hour is
    filed under a different split.
  * A block boundary is a gap of more than 3 hours between consecutive scored
    hours; blocks are computed once, on the full scored set.

Run:  venv-quick/bin/python verify_paper.py
"""
import numpy as np
import pandas as pd

import os as _os

BASE = _os.environ.get("HELIOFLOOR_DIR",
                       _os.path.dirname(_os.path.abspath(__file__)))
D = _os.environ.get("SURYABENCH_FLARE_DIR", _os.path.join(BASE, "data", "flare"))
RNG_SEED = 42

# Deliberately not imported from heliofloor_data: this script stays independent
# of the loader so a bug cannot propagate into both.
if not _os.path.isdir(D):
    raise SystemExit(
        f"SuryaBench flare CSVs not found at: {_os.path.abspath(D)}\n\n"
        "Download validation.csv, test.csv, train.csv, leaky_validation.csv and\n"
        "data.csv from the Hugging Face dataset\n\n"
        "    nasa-ibm-ai4science/surya-bench-flare-forecasting\n\n"
        "then point SURYABENCH_FLARE_DIR at the folder holding them:\n\n"
        "    SURYABENCH_FLARE_DIR=/path/to/flare python verify_paper.py\n\n"
        "The scored probabilities (probs_*.csv) are already in this repository,\n"
        "so no GPU and no re-inference are needed once the CSVs are in place.")

FAILS, CHECKS = [], []


def check(tag, claimed, computed, tol=0.0005, note=""):
    """Record one claim-vs-computation comparison."""
    if isinstance(claimed, (int, np.integer)) and isinstance(computed, (int, np.integer)):
        ok = int(claimed) == int(computed)
        shown = f"claimed {claimed}  computed {computed}"
    else:
        ok = abs(float(claimed) - float(computed)) <= tol
        shown = f"claimed {float(claimed):.4f}  computed {float(computed):.4f}"
    CHECKS.append((ok, tag, shown, note))
    if not ok:
        FAILS.append((tag, shown, note))
    print(f"  [{'OK  ' if ok else 'FAIL'}] {tag:<52s} {shown}  {note}")


# --------------------------------------------------------------- flux parsing
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


# ------------------------------------------------------------ canonical load
def load(split, files):
    df = pd.concat([pd.read_csv(f"{BASE}/{f}") for f in files], ignore_index=True)
    df["ts"] = pd.to_datetime(df["timestamp"])
    df = df.drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    # persistence reference from the complete record: M1.0 = 1e-5 W/m^2
    df["persist"] = [1 if FX.get(t - pd.Timedelta(hours=24), 0.0) >= 1e-5 else 0
                     for t in df["ts"]]
    df["block"] = (df["ts"].diff() > pd.Timedelta(hours=3)).cumsum()
    # label cross-check against the official split file
    t = pd.read_csv(f"{D}/{split}.csv")
    t["ts"] = pd.to_datetime(t["timestamp"])
    look = dict(zip(t["ts"], t["label_max"]))
    df["official"] = [look.get(x, np.nan) for x in df["ts"]]
    return df


# ------------------------------------------------------------------- metrics
def cm(y, p):
    return (int(((y == 1) & (p == 1)).sum()), int(((y == 1) & (p == 0)).sum()),
            int(((y == 0) & (p == 1)).sum()), int(((y == 0) & (p == 0)).sum()))


def tss(y, p):
    tp, fn, fp, tn = cm(y, p)
    return (tp / (tp + fn) if tp + fn else np.nan) - (fp / (fp + tn) if fp + tn else np.nan)


def hss(y, p):
    tp, fn, fp, tn = cm(y, p)
    den = (tp + fn) * (fn + tn) + (tp + fp) * (fp + tn)
    return 2 * (tp * tn - fn * fp) / den if den else np.nan


def f1(y, p):
    tp, fn, fp, _ = cm(y, p)
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return 2 * pr * rc / (pr + rc) if pr + rc else 0.0


def boot_ci(df, fn, n=2000, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    blocks = [g for _, g in df.groupby("block")]
    v = [fn(pd.concat([blocks[i] for i in rng.integers(0, len(blocks), len(blocks))],
                      ignore_index=True)) for _ in range(n)]
    v = [x for x in v if not np.isnan(x)]
    return tuple(np.percentile(v, [2.5, 97.5]))


def best_thr(df, col):
    grid = np.arange(0.01, 0.96, 0.01)
    y = df["label"].to_numpy()
    return max(((t, tss(y, (df[col] > t).astype(int).to_numpy())) for t in grid),
               key=lambda x: x[1])


val = load("validation", ["probs_validation_full.csv", "probs_validation_ek.csv"])
test = load("test", ["probs_test_full.csv"])

print("=" * 100)
print("SECTION: sample sizes  (Abstract, section 3.2, section 4.2, section 4.3)")
print("=" * 100)
check("validation scored hours", 739, len(val))
check("test scored hours", 407, len(test))
check("total scored hours (abstract '1,146')", 1146, len(val) + len(test))
check("total positives (abstract '218')", 218,
      int(val["label"].sum() + test["label"].sum()))
check("validation positives", 85, int(val["label"].sum()))
check("test positives", 133, int(test["label"].sum()))
check("validation blocks", 50, int(val["block"].nunique()))
check("test blocks", 28, int(test["block"].nunique()))
check("validation base rate", 0.115, float(val["label"].mean()), tol=0.001)
check("test base rate", 0.327, float(test["label"].mean()), tol=0.001)

# label agreement with the official split CSVs
for name, df in (("validation", val), ("test", test)):
    m = df.dropna(subset=["official"])
    check(f"{name} label mismatches vs official CSV", 0,
          int((m["label"] != m["official"]).sum()),
          note=f"({len(m)} of {len(df)} hours present in split file)")

print()
print("=" * 100)
print("SECTION: block support  (Abstract, section 4.3, section 7)")
print("=" * 100)
for name, df, cl_pos in (("validation", val, 6), ("test", test, 11)):
    pos_blocks = df[df["label"] == 1]["block"].nunique()
    check(f"{name} positive-containing blocks", cl_pos, int(pos_blocks))

print()
print("=" * 100)
print("SECTION: matched-hours scoreboard  (Abstract, section 4.2, section 4.3)")
print("=" * 100)
vb = best_thr(val, "prob")
tb = best_thr(test, "prob")
check("validation Surya tuned threshold", 0.16, vb[0], tol=0.005)
check("validation Surya tuned TSS", 0.673, vb[1])
check("test Surya tuned threshold", 0.04, tb[0], tol=0.005)
check("test Surya tuned TSS", 0.632, tb[1])

yv, yt = val["label"].to_numpy(), test["label"].to_numpy()
pv05 = (val["prob"] > 0.5).astype(int).to_numpy()
pt05 = (test["prob"] > 0.5).astype(int).to_numpy()
check("validation Surya @0.5 TSS", 0.425, tss(yv, pv05))
check("test Surya @0.5 TSS", 0.173, tss(yt, pt05))
check("validation persistence TSS", 0.405, tss(yv, val["persist"].to_numpy()))
check("test persistence TSS", 0.618, tss(yt, test["persist"].to_numpy()))

pvT = (val["prob"] > vb[0]).astype(int).to_numpy()
ptT = (test["prob"] > tb[0]).astype(int).to_numpy()
check("test Surya tuned HSS", 0.571, hss(yt, ptT))
check("test Surya tuned F1", 0.735, f1(yt, ptT))

hyb = ((val["prob"] > vb[0]) | (val["persist"] == 1)).astype(int).to_numpy()
check("validation hybrid (persist OR Surya) TSS", 0.705, tss(yv, hyb))

print()
print("=" * 100)
print("SECTION: block-bootstrap intervals  (section 4.3)")
print("=" * 100)
# These reproduce exactly: heliofloor_data.block_bootstrap reseeds per call with
# the same seed and draw count used here, so an interval does not depend on how
# many intervals were drawn before it.
for tag, df, y, col, thr, claim in [
        ("validation Surya @0.5", val, yv, "prob", 0.5, (0.028, 0.746)),
        ("validation Surya tuned", val, yv, "prob", vb[0], (0.289, 0.886)),
        ("test Surya @0.5", test, yt, "prob", 0.5, (0.000, 0.484)),
        ("test Surya tuned", test, yt, "prob", tb[0], (0.315, 0.876))]:
    lo, hi = boot_ci(df, lambda s, c=col, t=thr: tss(s["label"].to_numpy(),
                                                     (s[c] > t).astype(int).to_numpy()))
    check(f"{tag} CI low", claim[0], lo, tol=0.001)
    check(f"{tag} CI high", claim[1], hi, tol=0.001)
for tag, df, claim in [("validation persistence", val, (-0.019, 0.792)),
                       ("test persistence", test, (0.258, 0.889))]:
    lo, hi = boot_ci(df, lambda s: tss(s["label"].to_numpy(), s["persist"].to_numpy()))
    check(f"{tag} CI low", claim[0], lo, tol=0.001)
    check(f"{tag} CI high", claim[1], hi, tol=0.001)

print()
print("=" * 100)
print("SECTION: calibration  (Abstract, section 4.5)")
print("=" * 100)


def brier(p, y):
    return float(np.mean((p - y) ** 2))


check("validation Brier", 0.057, brier(val["prob"].to_numpy(), yv), tol=0.001)
check("test Brier", 0.208, brier(test["prob"].to_numpy(), yt), tol=0.001)

BINS = [0, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 1.01]
print("\n  reliability table (recomputed):")
for name, df in (("validation", val), ("test", test)):
    print(f"    {name}:")
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        m = (df["prob"] >= lo) & (df["prob"] < hi)
        if m.sum():
            print(f"      [{lo:.2f},{hi:.2f})  n={int(m.sum()):4d}  "
                  f"pred {df.loc[m,'prob'].mean():.3f}  obs {df.loc[m,'label'].mean():.3f}  "
                  f"blocks {df.loc[m,'block'].nunique()}")

for name, df, n_cl, blk_cl, obs_cl in (("validation", val, 136, 17, 0.103),
                                       ("test", test, 143, 15, 0.566)):
    m = (df["prob"] >= 0.05) & (df["prob"] < 0.25)
    check(f"{name} bin [0.05,0.25) hours", n_cl, int(m.sum()))
    check(f"{name} bin [0.05,0.25) blocks", blk_cl, int(df.loc[m, "block"].nunique()))
    check(f"{name} bin [0.05,0.25) observed rate", obs_cl,
          float(df.loc[m, "label"].mean()), tol=0.002)
    if name == "test":
        pm = float(df.loc[m, "prob"].mean())
        check("test bin [0.05,0.25) mean predicted", 0.148, pm, tol=0.001)


def logit(p, eps=1e-6):
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


def fit_platt(p, y, iters=4000, lr=0.05):
    x, a, b = logit(p), 1.0, 0.0
    for _ in range(iters):
        q = 1 / (1 + np.exp(-(a * x + b)))
        e = q - y
        a -= lr * np.mean(e * x)
        b -= lr * np.mean(e)
    return a, b


a, b = fit_platt(val["prob"].to_numpy(), yv.astype(float))
check("Platt a", 0.944, a, tol=0.002)
check("Platt b", 0.145, b, tol=0.002)
cal = (1 / (1 + np.exp(-(a * logit(test["prob"].to_numpy()) + b))) > 0.5).astype(int)
check("test TSS after Platt (claim: unchanged 0.173)", 0.173, tss(yt, cal))

print()
print("=" * 100)
print("SECTION: onset / continuation  (section 4.4, Figure 4)")
print("=" * 100)
for name, df, thr, cl in (("validation", val, vb[0],
                           dict(onset=46, cont=39, decay=35, tuned=35, at05=14, blocks=4)),
                          ("test", test, tb[0],
                           dict(onset=27, cont=106, decay=49, tuned=13, at05=0, blocks=3))):
    pos = df[df["label"] == 1]
    onset = pos[pos["persist"] == 0]
    cont = pos[pos["persist"] == 1]
    decay = df[(df["label"] == 0) & (df["persist"] == 1)]
    check(f"{name} onset positives", cl["onset"], len(onset))
    check(f"{name} continuation positives", cl["cont"], len(cont))
    check(f"{name} decay hours", cl["decay"], len(decay))
    check(f"{name} onsets caught, Surya tuned", cl["tuned"], int((onset["prob"] > thr).sum()))
    check(f"{name} onsets caught, Surya @0.5", cl["at05"], int((onset["prob"] > 0.5).sum()))
    check(f"{name} onset-containing blocks", cl["blocks"], int(onset["block"].nunique()))
    print(f"       rule of three on block-effective n: 3/{onset['block'].nunique()} = "
          f"{3/onset['block'].nunique():.3f}")

print()
print("=" * 100)
print("SECTION: full official splits  (section 4.1, 4.2, 4.6)")
print("=" * 100)
LAGS = [24, 48, 72, 96, 120, 144, 168]
FEATS = [f"lf{h}" for h in LAGS] + ["lf7dmax", "ci24", "ci48", "ci7dmean"]
full["lf"] = np.log10(full["fx"])
LF = dict(zip(full["ts"], full["lf"]))
CI = dict(zip(full["ts"], full["cumulative_index"]))


def features(ts_list):
    rows = []
    for t in ts_list:
        lfs = [LF.get(t - pd.Timedelta(hours=h), np.nan) for h in LAGS]
        cis = [CI.get(t - pd.Timedelta(hours=h), np.nan) for h in LAGS]
        rows.append(lfs + [np.nanmax(lfs), np.log1p(cis[0]), np.log1p(cis[1]),
                           np.log1p(np.nanmean(cis))])
    return pd.DataFrame(rows, columns=FEATS)


def sig(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))


def fit_lr(X, y, iters=8000, lr=0.1, l2=1e-3):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = np.hstack([np.clip((X - mu) / sd, -10, 10), np.ones((len(X), 1))])
    w = np.zeros(Z.shape[1])
    for _ in range(iters):
        w -= lr * (Z.T @ (sig(Z @ w) - y) / len(y) + l2 * np.r_[w[:-1], 0.0])
    return w, mu, sd


def pred(w, mu, sd, X):
    Z = np.hstack([np.clip((X - mu) / sd, -10, 10), np.ones((len(X), 1))])
    return sig(Z @ w)


tr = pd.read_csv(f"{D}/train.csv")
tr["ts"] = pd.to_datetime(tr["timestamp"])
Xtr = features(tr["ts"]).to_numpy()
ok = np.isfinite(Xtr).all(1)
check("train rows used (section 3.3 claims 74,564)", 74564, int(ok.sum()),
      note=f"(of {len(tr)} train rows; {len(tr)-int(ok.sum())} dropped as non-finite)")
w, mu, sd = fit_lr(Xtr[ok], tr["label_max"].to_numpy()[ok].astype(float))

splits = {}
for nm in ("validation", "test"):
    d = pd.read_csv(f"{D}/{nm}.csv")
    d["ts"] = pd.to_datetime(d["timestamp"])
    X = features(d["ts"]).replace([np.inf, -np.inf], np.nan)
    d["goes"] = pred(w, mu, sd, X.fillna(X.median()).to_numpy())
    d["persist"] = [1 if FX.get(t - pd.Timedelta(hours=24), 0.0) >= 1e-5 else 0 for t in d["ts"]]
    splits[nm] = d

check("full validation hours", 3672, len(splits["validation"]))
check("full test hours", 43848, len(splits["test"]))
check("full validation base rate", 0.109, float(splits["validation"]["label_max"].mean()), tol=0.001)
check("full test base rate", 0.294, float(splits["test"]["label_max"].mean()), tol=0.001)

THR = 0.10  # frozen: chosen on the full validation split
for nm, cl_g, cl_p, cl_gh, cl_gf, cl_ph, cl_pf in [
        ("validation", 0.661, 0.430, 0.375, 0.475, 0.428, 0.491),
        ("test", 0.554, 0.535, 0.436, 0.655, 0.536, 0.672)]:
    d = splits[nm]
    y = d["label_max"].to_numpy()
    g = (d["goes"] > THR).astype(int).to_numpy()
    p = d["persist"].to_numpy()
    check(f"full {nm} GOES logistic TSS", cl_g, tss(y, g))
    check(f"full {nm} GOES logistic HSS", cl_gh, hss(y, g))
    check(f"full {nm} GOES logistic F1", cl_gf, f1(y, g))
    check(f"full {nm} persistence TSS", cl_p, tss(y, p))
    check(f"full {nm} persistence HSS", cl_ph, hss(y, p))
    check(f"full {nm} persistence F1", cl_pf, f1(y, p))

print("\n  per-year test table (recomputed):")
d = splits["test"]
peryear = {}
for yr, g in d.groupby(d["ts"].dt.year):
    y = g["label_max"].to_numpy()
    gg = (g["goes"] > THR).astype(int).to_numpy()
    peryear[int(yr)] = (len(g), float(y.mean()), tss(y, gg), tss(y, g["persist"].to_numpy()))
    print(f"    {yr}  n={len(g)}  base={y.mean():.5f}  GOES TSS={tss(y,gg):+.3f}  "
          f"persist TSS={tss(y,g['persist'].to_numpy()):+.3f}")

for yr, (n_cl, b_cl, g_cl, p_cl) in {2020: (8784, 0.005, 0.452, -0.005),
                                     2021: (8760, 0.061, 0.514, 0.270),
                                     2022: (8760, 0.264, 0.250, 0.322),
                                     2023: (8760, 0.443, 0.056, 0.293),
                                     2024: (8784, 0.697, 0.079, 0.389)}.items():
    n, br, gt, pt = peryear[yr]
    check(f"{yr} hours", n_cl, n)
    check(f"{yr} base rate", b_cl, br, tol=0.001)
    check(f"{yr} GOES TSS", g_cl, gt)
    check(f"{yr} persistence TSS", p_cl, pt)

fold = peryear[2024][1] / peryear[2020][1]
print(f"\n  EXACT base-rate ratio 2024/2020 = {peryear[2024][1]:.6f} / "
      f"{peryear[2020][1]:.6f} = {fold:.1f}x")
check("base-rate fold change (paper says 128-fold)", 128.0, fold, tol=1.0,
      note="computed from unrounded rates, not 0.697/0.005")

pooled = tss(d["label_max"].to_numpy(), (d["goes"] > THR).astype(int).to_numpy())
peryr_vals = [peryear[y][2] for y in sorted(peryear)]
print(f"  pooled test GOES TSS = {pooled:.3f}; per-year range "
      f"{min(peryr_vals):.3f}..{max(peryr_vals):.3f}")
check("pooled exceeds every per-year value (Simpson)", 1,
      int(pooled > max(peryr_vals)), note="1 = claim holds")

print()
print("=" * 100)
print("SECTION: leakage identity  (section 2.4)")
print("=" * 100)
lab = pd.concat([pd.read_csv(f"{D}/{s}.csv")[["timestamp", "label_max"]]
                 for s in ("train", "validation", "leaky_validation", "test")],
                ignore_index=True)
lab["ts"] = pd.to_datetime(lab["timestamp"])
mg = full.set_index("ts")["fx"]
j = lab.join(mg, on="ts").dropna(subset=["fx"])
agree = int(((j["fx"] >= 1e-5).astype(int) == j["label_max"]).sum())
check("leakage identity rows checked", 128328, len(j))
check("leakage identity rows agreeing", 128328, agree)

# cumulative_index is forward-looking over the same 24h window (section 2.4):
# the card-stated identity label_cum == (cumulative_index >= 10) must be exact.
cum_agree = int(((full["cumulative_index"] >= 10).astype(int)
                 == full["label_cum"]).sum())
check("label_cum identity rows checked", 128328, len(full))
check("label_cum == (cumulative_index >= 10) agreeing", 128328, cum_agree)

print()
print("=" * 100)
print("SECTION: split table and sampling arithmetic  (section 2.2, section 3.2)")
print("=" * 100)
tr_all = pd.read_csv(f"{D}/train.csv")
lk = pd.read_csv(f"{D}/leaky_validation.csv")
check("train hours (table 2.2)", 74760, len(tr_all))
check("train base rate (table 2.2)", 0.1211, float(tr_all["label_max"].mean()), tol=0.0005)
check("leaky_validation hours", 6048, len(lk))
check("leaky_validation base rate", 0.1490, float(lk["label_max"].mean()), tol=0.0005)
check("validation hours lost to archive gaps (125 of 864)", 125, 36 * 24 - len(val))
check("test hours lost to archive gaps (73 of 480)", 73, 20 * 24 - len(test))

need = set()
for df in (val, test):
    for t in df["ts"]:
        need.add(t)
        need.add(t - pd.Timedelta(hours=1))
check("distinct netCDF timesteps streamed", 1224, len(need))

vs = val.groupby("block").size()
ts_ = test.groupby("block").size()
check("validation blocks >= 20 h", 20, int((vs >= 20).sum()))
check("validation fragments < 20 h", 30, int((vs < 20).sum()))
check("test blocks >= 20 h", 14, int((ts_ >= 20).sum()))
check("test fragments < 20 h", 14, int((ts_ < 20).sum()))

print()
print("=" * 100)
print("SECTION: GOES logistic on the matched hours  (section 4.2, section 4.3)")
print("=" * 100)
for df in (val, test):
    X = features(df["ts"]).replace([np.inf, -np.inf], np.nan)
    df["goes"] = pred(w, mu, sd, X.fillna(X.median()).to_numpy())

gv = best_thr(val, "goes")
gt = best_thr(test, "goes")
check("validation GOES tuned threshold", 0.10, gv[0], tol=0.005)
check("validation GOES matched TSS", 0.685, gv[1])
check("test GOES tuned threshold", 0.34, gt[0], tol=0.005)
check("test GOES matched TSS", 0.738, gt[1])
ptG = (test["goes"] > gt[0]).astype(int).to_numpy()
check("test GOES matched HSS", 0.699, hss(yt, ptG))
check("test GOES matched F1", 0.807, f1(yt, ptG))
for tag, df, thr, claim in [("validation GOES", val, gv[0], (0.417, 0.881)),
                            ("test GOES", test, gt[0], (0.467, 0.940))]:
    lo, hi = boot_ci(df, lambda s, t=thr: tss(s["label"].to_numpy(),
                                              (s["goes"] > t).astype(int).to_numpy()))
    check(f"{tag} CI low", claim[0], lo, tol=0.001)
    check(f"{tag} CI high", claim[1], hi, tol=0.001)

print()
print("=" * 100)
print("SECTION: paired block-bootstrap differences  (section 4.3, section 4.4)")
print("=" * 100)
# Replicates paired_diff.py exactly (same seed, same draw structure), so the
# committed intervals must reproduce to three decimals.
PAIRS = [("goes_p", "surya_tuned", "GOES-SuryaTuned"),
         ("surya_tuned", "persistence", "SuryaTuned-Persist"),
         ("goes_p", "persistence", "GOES-Persist"),
         ("surya05", "persistence", "Surya05-Persist"),
         ("hybrid", "surya_tuned", "Hybrid-SuryaTuned")]
PAIRED_CLAIMS = {
    "validation": {"GOES-SuryaTuned": (0.012, -0.325, 0.473),
                   "SuryaTuned-Persist": (0.268, -0.153, 0.658),
                   "GOES-Persist": (0.279, -0.058, 0.681),
                   "Surya05-Persist": (0.019, -0.398, 0.427),
                   "Hybrid-SuryaTuned": (0.032, -0.044, 0.241)},
    "test": {"GOES-SuryaTuned": (0.106, 0.009, 0.280),
             "SuryaTuned-Persist": (0.014, -0.210, 0.253),
             "GOES-Persist": (0.120, -0.009, 0.330),
             "Surya05-Persist": (-0.445, -0.825, -0.086),
             "Hybrid-SuryaTuned": (-0.033, -0.098, 0.015)},
}
for name, df, s_thr, g_thr in [("validation", val, vb[0], gv[0]),
                               ("test", test, tb[0], gt[0])]:
    preds = {
        "persistence": df["persist"].to_numpy(),
        "surya05": (df["prob"] > 0.5).astype(int).to_numpy(),
        "surya_tuned": (df["prob"] > s_thr).astype(int).to_numpy(),
        "goes_p": (df["goes"] > g_thr).astype(int).to_numpy(),
        "hybrid": ((df["prob"] > s_thr) | (df["persist"] == 1)).astype(int).to_numpy(),
    }
    y = df["label"].to_numpy()
    for a, b, tagp in PAIRS:
        pt_, lo_, hi_ = PAIRED_CLAIMS[name][tagp]
        check(f"{name} paired point {tagp}", pt_,
              tss(y, preds[a]) - tss(y, preds[b]), tol=0.0006)
    blocks_idx = [g.index.to_numpy() for _, g in df.groupby("block")]
    rng = np.random.default_rng(RNG_SEED)
    diffs = {tagp: [] for _, _, tagp in PAIRS}
    for _ in range(4000):
        pick = rng.integers(0, len(blocks_idx), len(blocks_idx))
        idx = np.concatenate([blocks_idx[i] for i in pick])
        yy = y[idx]
        t_ = {c: tss(yy, preds[c][idx]) for c in preds}
        for a, b, tagp in PAIRS:
            d_ = t_[a] - t_[b]
            if not np.isnan(d_):
                diffs[tagp].append(d_)
    for a, b, tagp in PAIRS:
        _, lo_c, hi_c = PAIRED_CLAIMS[name][tagp]
        lo_, hi_ = np.percentile(diffs[tagp], [2.5, 97.5])
        check(f"{name} paired CI low {tagp}", lo_c, lo_, tol=0.0006)
        check(f"{name} paired CI high {tagp}", hi_c, hi_, tol=0.0006)
    if name == "test":
        # section 4.3's multiplicity numbers: tail fractions and the
        # Bonferroni-corrected 99.5% intervals for the two 95% exclusions
        arr_g = np.asarray(diffs["GOES-SuryaTuned"])
        arr_s = np.asarray(diffs["Surya05-Persist"])
        check("test tail fraction GOES-SuryaTuned (0.55%)",
              0.0055, float((arr_g <= 0).mean()), tol=0.00006)
        check("test tail fraction Surya05-Persist (0.70%)",
              0.0070, float((arr_s >= 0).mean()), tol=0.00006)
        g995 = np.percentile(arr_g, [0.25, 99.75])
        s995 = np.percentile(arr_s, [0.25, 99.75])
        check("test 99.5% low GOES-SuryaTuned", 0.000, g995[0], tol=0.0006)
        check("test 99.5% high GOES-SuryaTuned", 0.382, g995[1], tol=0.0006)
        check("test 99.5% low Surya05-Persist", -0.924, s995[0], tol=0.0006)
        check("test 99.5% high Surya05-Persist", 0.070, s995[1], tol=0.0006)

print()
print("=" * 100)
n_ok = sum(1 for c in CHECKS if c[0])
print(f"RESULT: {n_ok}/{len(CHECKS)} checks passed, {len(FAILS)} FAILED")
print("=" * 100)
if FAILS:
    print("\nFAILURES REQUIRING A TEXT CHANGE:\n")
    for tag, shown, note in FAILS:
        print(f"  * {tag}\n      {shown}  {note}")

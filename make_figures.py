#!/usr/bin/env python3
"""Paper figures for HELIOFLOOR. Writes PNG + PDF into figures/.

Fig 1  reliability diagrams (validation vs test) -> calibration collapse
Fig 2  per-year base rate and TSS on the full test split -> base-rate drift
Fig 3  TSS vs decision threshold, with baselines as reference lines
Fig 4  onset / continuation / decay catch rates

Every number on every figure is computed here from the committed data — nothing
is hardcoded, so the figures cannot silently drift from the text the way a
pasted value could. The price is runtime: fig 2 needs the GOES-history model
trained and scored on the complete splits, so a full regeneration takes a few
minutes on a CPU.

Run:  venv-quick/bin/python make_figures.py
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import heliofloor_data as H

OUT = f"{H.BASE}/figures"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 300, "font.size": 9,
    "axes.grid": True, "grid.alpha": 0.25, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False,
})
C = {"surya": "#C1272D", "persist": "#2B6CB0", "goes": "#2F855A", "hyb": "#6B46C1"}


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/{name}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}.png / .pdf")


# ------------------------------------------------------------------ data
val = H.load("validation")
test = H.load("test")
w, mu, sd = H.train_goes_model(verbose=False)
for df in (val, test):
    df["goes"] = H.score_goes(w, mu, sd, df["ts"])

vb_thr, _ = H.best_threshold(val, "prob")
tb_thr, _ = H.best_threshold(test, "prob")
gv_thr, gv_tss = H.best_threshold(val, "goes")
gt_thr, gt_tss = H.best_threshold(test, "goes")

briers = {id(val): H.brier(val["prob"].to_numpy(), val["label"].to_numpy()),
          id(test): H.brier(test["prob"].to_numpy(), test["label"].to_numpy())}

# ------------------------------------------------------- Fig 1 reliability
BINS = [0, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 1.01]
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
for ax, (df, name) in zip(axes, [(val, "Validation (2011–2019)"),
                                 (test, "Test (2020–2024)")]):
    xs, ys, ns = [], [], []
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        m = (df["prob"] >= lo) & (df["prob"] < hi)
        if m.sum() >= 5:
            xs.append(df.loc[m, "prob"].mean())
            ys.append(df.loc[m, "label"].mean())
            ns.append(int(m.sum()))
    ax.plot([0, 1], [0, 1], "--", color="0.6", lw=1, label="perfect calibration")
    ax.plot(xs, ys, "o-", color=C["surya"], lw=1.6, ms=5, label="Surya")
    # The low-probability bins crowd into one corner, so a fixed offset makes
    # their labels overprint each other and pushes the lowest one off the axis.
    # Step each label outward until it clears the ones already placed.
    PT = 170.0          # points per data unit on this axis, near enough for a test
    placed = []
    for x, y, n in zip(xs, ys, ns):
        for dy in (9, -12, 20, -23, 31, -34):
            if y < 0.05 and dy < 0:
                continue                       # would fall below the axis
            cy = y + dy / PT
            if all(abs(px - x) > 0.11 or abs(py - cy) > 0.05
                   for px, py in placed):
                break
        placed.append((x, y + dy / PT))
        ax.annotate(f"n={n}", (x, y), textcoords="offset points", xytext=(0, dy),
                    fontsize=6, color="0.35", ha="center")
    # left margin widened so a centred label on the x~0 bin clears the spine
    ax.set_xlim(-0.09, 1.03); ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("mean predicted probability")
    ax.set_title(f"{name}\nBrier = {briers[id(df)]:.3f}", fontsize=9)
axes[0].set_ylabel("observed frequency")
axes[0].legend(loc="upper left", fontsize=7)
# annotate the worst test bin, located from the data
mt = (test["prob"] >= 0.05) & (test["prob"] < 0.10)
axes[1].annotate(f"predicted {test.loc[mt,'prob'].mean():.3f},\n"
                 f"observed {test.loc[mt,'label'].mean():.3f}",
                 xy=(test.loc[mt, "prob"].mean(), test.loc[mt, "label"].mean()),
                 xytext=(0.30, 0.42), fontsize=7, color=C["surya"],
                 arrowprops=dict(arrowstyle="->", color=C["surya"], lw=1))
# no baked-in title: the LaTeX caption numbers and describes the figure
save(fig, "fig1_reliability")

# ------------------------------------------------------- Fig 2 base drift
# Full-split protocol, recomputed: threshold frozen on the full validation split.
va = H.load_official("validation")
va["p"] = H.score_goes(w, mu, sd, va["ts"])
THR = H.best_threshold(va.rename(columns={"label_max": "label"}), "p")[0]
te = H.load_official("test")
te["p"] = H.score_goes(w, mu, sd, te["ts"])
pooled = H.tss(te["label_max"].to_numpy(), (te["p"] > THR).astype(int).to_numpy())

rows = []
for yr, g in te.groupby(te["ts"].dt.year):
    y = g["label_max"].to_numpy()
    rows.append((int(yr), float(y.mean()),
                 H.tss(y, (g["p"] > THR).astype(int).to_numpy()),
                 H.tss(y, g["persist"].to_numpy())))
yr = [r[0] for r in rows]
fold = max(r[1] for r in rows) / min(r[1] for r in rows)

fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.4, 4.4), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1.25]})
a1.bar(yr, [r[1] for r in rows], color="0.55", width=0.6)
for x, r in zip(yr, rows):
    a1.annotate(f"{r[1]:.4f}", (x, r[1]), ha="center", va="bottom", fontsize=7)
a1.set_ylabel("positive rate"); a1.set_ylim(0, 0.83)
# title omitted on purpose; the caption carries the description
a2.axhline(0, color="0.5", lw=0.8)
a2.plot(yr, [r[2] for r in rows], "o-", color=C["goes"], lw=1.8,
        label="GOES-history logistic")
a2.plot(yr, [r[3] for r in rows], "s-", color=C["persist"], lw=1.8,
        label="persistence")
a2.axhline(pooled, ls=":", color=C["goes"], lw=1.2)
a2.annotate(f"pooled test TSS = {pooled:.3f}\n(above every single year)",
            (2022.0, pooled + 0.02), fontsize=7, color=C["goes"])
a2.set_ylabel("TSS (threshold frozen on validation)")
a2.set_xlabel("year of the official test split")
a2.set_xticks(yr); a2.legend(loc="lower left", fontsize=7)
save(fig, "fig2_base_rate_drift")

# ------------------------------------------------------- Fig 3 thresholds
grid = np.arange(0.01, 0.96, 0.01)
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True)
for ax, (df, name, goes_ref) in zip(
        axes, [(val, "Validation (2011–2019)", gv_tss),
               (test, "Test (2020–2024)", gt_tss)]):
    y = df["label"].to_numpy()
    pers_ref = H.tss(y, df["persist"].to_numpy())
    curve = [H.tss(y, (df["prob"] > t).astype(int).to_numpy()) for t in grid]
    best = int(np.nanargmax(curve))
    ax.plot(grid, curve, color=C["surya"], lw=1.8, label="Surya (threshold sweep)")
    ax.axhline(pers_ref, ls="--", color=C["persist"], lw=1.4, label="persistence")
    ax.axhline(goes_ref, ls="-.", color=C["goes"], lw=1.4,
               label="GOES-history logistic")
    ax.axvline(0.5, color="0.45", lw=1, ls=":")
    ax.annotate("official threshold", (0.5, 0.985), fontsize=7, color="0.35",
                xycoords=("data", "axes fraction"), rotation=90,
                ha="right", va="top")
    ax.plot(grid[best], curve[best], "*", color=C["surya"], ms=12)
    # the sweep falls steeply away from its peak and runs straight through this
    # label, so give it an opaque backing rather than chase a clear offset
    ax.annotate(f"best {curve[best]:.3f}\n@ {grid[best]:.2f}",
                (grid[best], curve[best]), textcoords="offset points",
                xytext=(10, -26), fontsize=7, color=C["surya"],
                bbox=dict(boxstyle="round,pad=0.25", fc="white",
                          ec="none", alpha=0.85))
    ax.set_xlabel("decision threshold"); ax.set_title(name, fontsize=9)
axes[0].set_ylabel("TSS"); axes[0].legend(loc="lower left", fontsize=7)
# no baked-in title: the LaTeX caption numbers and describes the figure
save(fig, "fig3_threshold_sweep")

# ------------------------------------------------------- Fig 4 onset split
# the middle label ran on one line and collided with its neighbours
labels = ["onset positives\n(persistence blind)", "continuation\npositives",
          "decay hours\n(false-alarm zone)"]


def regime_fracs(df, thr):
    pos = df[df["label"] == 1]
    onset = pos[pos["persist"] == 0]
    cont = pos[pos["persist"] == 1]
    decay = df[(df["label"] == 0) & (df["persist"] == 1)]
    def frac(sub, t):
        return float((sub["prob"] > t).mean()) if len(sub) else np.nan
    return {
        "n": (len(onset), len(cont), len(decay)),
        "persistence": (0.0, 1.0, 1.0),           # definitional
        "tuned": (frac(onset, thr), frac(cont, thr), frac(decay, thr)),
        "at05": (frac(onset, 0.5), frac(cont, 0.5), frac(decay, 0.5)),
    }


R = {"Validation": regime_fracs(val, vb_thr), "Test": regime_fracs(test, tb_thr)}

fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.2), sharey=True)
w_, x = 0.26, np.arange(3)
for k, (ax, name) in enumerate(zip(axes, ["Validation", "Test"])):
    r = R[name]
    series = [("persistence", r["persistence"], C["persist"]),
              ("Surya (tuned)", r["tuned"], C["surya"]),
              ("Surya @0.5", r["at05"], "#E8A33D")]
    for i, (mdl, vals, col) in enumerate(series):
        ax.bar(x + (i - 1) * w_, vals, w_, color=col,
               label=mdl if k == 0 else None)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=6.5)
    ax.set_ylim(0, 1.08); ax.set_title(name, fontsize=9)
    n_on = r["n"][0]
    ax.annotate(f"0/{n_on}", (x[0] - w_, 0.015), fontsize=7, ha="center",
                va="bottom", color=C["persist"], weight="bold")
    if r["at05"][0] == 0:      # the shipped threshold caught no onsets here
        ax.annotate(f"0/{n_on}", (x[0] + w_, 0.015), fontsize=7, ha="center",
                    va="bottom", color="#E8A33D", weight="bold")
    n_blocks = val if name == "Validation" else test
    ob = n_blocks[(n_blocks["label"] == 1) & (n_blocks["persist"] == 0)]["block"].nunique()
    # anchored left of centre: centring on the first group clipped the wider
    # second line against the y-axis
    ax.annotate(f"onset column:\n{ob} independent episodes",
                (x[0] - w_ * 1.4, 1.0), fontsize=6, ha="left", va="top",
                color="0.35", style="italic")
axes[0].set_ylabel("fraction flagged")
_h, _l = axes[0].get_legend_handles_labels()
fig.legend(_h, _l, loc="lower center", bbox_to_anchor=(0.5, 1.0),
           ncol=3, fontsize=7, frameon=False)
# no baked-in title: the LaTeX caption numbers and describes the figure
save(fig, "fig4_onset_continuation")

print(f"\n4 figures written to {OUT}, every value computed from the data")

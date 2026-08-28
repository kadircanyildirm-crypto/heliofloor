# HELIOFLOOR — an independent evaluation of Surya's solar-flare head

Surya is the 366M-parameter heliophysics foundation model released by NASA and
IBM in August 2025. Its paper reports a solar-flare forecasting score of **TSS
0.436** against two deep image baselines (AlexNet, ResNet50). This repository
contains, to our knowledge, the first independent evaluation of the released
`solar_flares_surya` checkpoint, together with the cheap baselines the benchmark
does not report.

The manuscript is `paper.pdf`. `PAPER_DRAFT.md` is the same text in
Markdown, and `PAPER_TR.md` is a full Turkish translation.

## What we did

We ran the released checkpoint with the authors' own inference code on **1,146
forecast hours** sampled from 2011–2024 (218 positive), streaming 1,224 raw SDO
netCDF files from the official archive — roughly 700 GB. Because non-imagery
baselines need no GPU, we additionally scored them on the **complete** official
splits (3,672 validation and 43,848 test hours).

Every number in the manuscript is recomputed from the committed data by
`verify_paper.py`, which prints a pass/fail line per claim — including exact
reproduction of every bootstrap interval. It currently reports **161/161**.

## Headline findings

1. **The benchmark's effective sample is far smaller than it appears.** Hours
   inside a 24-hour block are autocorrelated, so the block is the unit of
   evidence: 739 validation hours occupy 50 blocks of which only **6 contain any
   positive**; 407 test hours occupy 28 blocks of which 11 do. Block-bootstrap
   95% intervals are 0.46–0.81 TSS wide; paired differences straddle zero for
   eight of ten method pairs, the strongest separation is the shipped 0.5
   threshold scoring below persistence on test (ΔTSS −0.445), and no pair
   survives a ten-way family-wise correction.
2. **Calibration is regime-dependent and does not transfer.** Brier 0.057 on
   validation vs 0.208 on test; test hours assigned 0.05–0.25 are followed by a
   flare 56.6% of the time against a mean predicted 0.148. A Platt rescaling
   fitted on validation is a near-identity map and changes nothing.
3. **An 11-feature logistic regression over past GOES X-ray flux — seconds to
   train on a CPU — ties the foundation model on identical validation hours
   (0.685 vs 0.673) and beats it on identical test hours (0.738 vs 0.632).**
4. **The benchmark reports no cheap baseline at all.** A 24-hour persistence rule
   reaches TSS 0.430 on the full validation split, with a 95% interval of
   [0.238, 0.621] that contains the reported 0.436.
5. **Skill appears regime-split, but only its structural half is estimable.**
   Persistence is definitionally blind to flare-episode onsets and false-alarms
   on every decay hour. The model's onset behaviour rests on only 4 and 3
   independent episodes, so we report it descriptively and quote no rate.

The common cause of 2 and 5 is base-rate drift: the positive rate in the official
test split rises from 0.0055 (2020) to 0.697 (2024) — **128-fold** — as solar
cycle 25 climbs. Pooled test TSS (0.554) exceeds every per-year value
(0.056–0.514): a Simpson's paradox.

**What this does not claim.** Eight of the ten paired differences straddle zero,
and neither of the two exclusions survives a family-wise correction. That is the
point rather than a caveat: at 50 and 28 blocks the protocol resolves almost
nothing, so these results should be read as showing the benchmark cannot rank
methods as published — not as a demonstration that any one method is better.

## The reported 0.436 cannot be located

While verifying our own citations we found that the released artifacts give
**three mutually incompatible split definitions**, and Table 4 of the model paper
names none of them — so the headline score is not attributable to any specific
evaluation period. Worse, the two companion papers report irreconcilable numbers
for the same baselines on the same task: ResNet50's TSS is 0.018 in the Surya
paper and 0.261 in SuryaBench, a factor of fourteen. Details and sources in §2.3
of the manuscript.

## A leakage trap worth knowing about

In the released flare CSVs, `max_goes_class[t]` is the maximum class over
[t, t+24h) — it is the **source of the label**, not a past observation. We
verified `label_max == (max_goes_class ≥ M1.0)` on 128,328 of 128,328 rows. Any
baseline reading that column at time *t* is trivially perfect and meaningless.
All features here are read at t−24h or earlier.

This check also resolves a documentation conflict: SuryaBench's text states the
threshold as 10⁻⁴ W m⁻² (X1.0) while calling it M1.0. The released labels follow
M1.0 (10⁻⁵ W m⁻²).

## Reproducing

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python goes_baseline.py        # matched-hours baseline comparison    (CPU, ~1 min)
python full_split_baseline.py  # complete-split baselines             (CPU, ~5 min)
python analysis_pack.py        # bootstrap, calibration, regime split (CPU, ~2 min)
python block_support.py        # independent-block support per claim  (CPU, seconds)
python onset_ci.py             # onset catch-rate intervals           (CPU, ~1 min)
python paired_diff.py          # paired method differences            (CPU, ~4 min)
python gaps_audit.py           # multiplicity and block-length checks (CPU, ~3 min)
python audit_extra.py          # the quantities stated in prose       (CPU, ~1 min)
python precision_sensitivity.py  # bf16 worst-case bound              (CPU, ~1 min)
python make_figures.py         # writes figures/*.png|pdf
python verify_paper.py         # recomputes every manuscript claim, pass/fail
```

Building the PDF needs a LaTeX toolchain:

```bash
latexmk -pdf paper.tex         # figures/ must contain the PDF versions
```

**Nothing needs downloading.** The scored probabilities are committed, and so is
the exact snapshot of the official SuryaBench flare CSVs the results were
computed from (`data/flare/`, 8.4 MB, CC BY 4.0 — see
`data/flare/PROVENANCE.md` for the upstream revision and checksums). So
**no GPU, no re-inference and no external fetch** are required to reproduce
every number in the paper; a clone and `pip install -r requirements.txt` is the
whole setup.

The snapshot is pinned deliberately. Sections 2.3 and 2.4 document a
label-leakage trap and three incompatible split definitions in the released
artifacts; if those are corrected upstream, a reader running against corrected
data would not reproduce our numbers and could not tell why. Set
`SURYABENCH_FLARE_DIR` to point at a different copy if you want to check our
results against a newer revision.

`heliofloor_colab.py` regenerates the probabilities from scratch (GPU + ~700 GB
of streamed SDO data); the block plan is deterministic from seed 42.

## Files

| file | what it is |
|---|---|
| `paper.pdf` | the manuscript |
| `paper.tex` | its LaTeX source |
| `PAPER_DRAFT.md` | the same manuscript in Markdown |
| `PAPER_TR.md` | full Turkish translation |
| `heliofloor_data.py` | **canonical loader, metrics, block bootstrap — imported by every script** |
| `verify_paper.py` | recomputes every manuscript claim and prints pass/fail |
| `goes_baseline.py` | GOES-history logistic vs Surya on identical hours |
| `full_split_baseline.py` | the same baseline on every official hour |
| `analysis_pack.py` | block bootstrap, reliability, calibration transfer, regime split |
| `block_support.py` | how many independent blocks support each claim |
| `onset_ci.py` | onset catch rates and the rule-of-three correction |
| `paired_diff.py` | paired block-bootstrap differences between methods |
| `gaps_audit.py` | self-attacks: label direction, multiplicity, block-length robustness |
| `precision_sensitivity.py` | bounds what bf16-vs-fp32 could change, without a GPU |
| `audit_extra.py` | prose-level quantities: block structure, archive gaps, files streamed |
| `plan_blocks.py` | seeded stratified block sampler |
| `make_figures.py` → `figures/` | the four paper figures |
| `heliofloor_colab.py` | inference runner (GPU) |
| `texcheck.py`, `md_tex_parity.py` | manuscript structure and Markdown/LaTeX agreement checks |
| `probs_validation_full.csv`, `probs_validation_ek.csv`, `probs_test_full.csv` | 1,146 scored hours: timestamp, label, model probability |
| `data/flare/` | pinned snapshot of the official SuryaBench flare CSVs (CC BY 4.0), with `PROVENANCE.md` giving the upstream revision and checksums |
| `outputs/` | committed output of every script, so numbers can be diffed without re-running |

## Data licensing

Code is Apache-2.0 (see `LICENSE`). Two things here are not ours and carry the
CC BY 4.0 attribution requirement of the SuryaBench flare dataset
(`nasa-ibm-ai4science/surya-bench-flare-forecasting`, Roy et al. 2026): the
label column in `probs_*.csv`, and the redistributed snapshot in `data/flare/`,
which is unmodified and documented in `data/flare/PROVENANCE.md`. The model
probabilities are our own output.

## Citing

A preprint is in preparation. Until it is posted, please cite this repository by
commit hash. This README will carry the DOI once the preprint is live.

## AI usage disclosure

Analysis code, experiment orchestration, and draft prose were produced with
assistance from an AI coding assistant (Claude). Every reported number is
computed by the committed scripts from the committed data and is checked
mechanically by `verify_paper.py`. The label-leakage check, the split
definitions, the bibliography, and the comparison figures quoted from the model
paper were verified against primary sources.

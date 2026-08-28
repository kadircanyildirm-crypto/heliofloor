# Paired block-bootstrap differences (Delta TSS)

4000 draws; one block resample per draw scores every method, so each
difference is computed within the same resample. Thresholds fixed at their
full-sample values. Seed 42 per split.


## validation (Surya thr 0.16, GOES thr 0.10, 50 blocks)

| pair | point Delta | 95% CI | excludes zero? |
|---|---|---|---|
| GOES logistic - Surya (tuned) | +0.012 | [-0.325, +0.473] | no |
| Surya (tuned) - persistence | +0.268 | [-0.153, +0.658] | no |
| GOES logistic - persistence | +0.279 | [-0.058, +0.681] | no |
| Surya @0.5 - persistence | +0.019 | [-0.398, +0.427] | no |
| hybrid - Surya (tuned) | +0.032 | [-0.044, +0.241] | no |

## test (Surya thr 0.04, GOES thr 0.34, 28 blocks)

| pair | point Delta | 95% CI | excludes zero? |
|---|---|---|---|
| GOES logistic - Surya (tuned) | +0.106 | [+0.009, +0.280] | **yes** |
| Surya (tuned) - persistence | +0.014 | [-0.210, +0.253] | no |
| GOES logistic - persistence | +0.120 | [-0.009, +0.330] | no |
| Surya @0.5 - persistence | -0.445 | [-0.825, -0.086] | **yes** |
| hybrid - Surya (tuned) | -0.033 | [-0.098, +0.015] | no |

Reading: a pair whose interval straddles zero is not separated at this sample
size; a pair whose interval excludes zero is. This is the statement section 4.3
should make, in place of reasoning from overlapping individual intervals.


# bf16 precision sensitivity (no GPU required)

Worst case: every hour within epsilon of the threshold flips to the side
that hurts TSS most. Real bf16 perturbation is far smaller than the
largest epsilon shown.


## validation (n=739)

| threshold | TSS | eps | hours within eps | worst-case TSS | max shift |
|---|---|---|---|---|---|
| 0.50 | 0.425 | 0.0001 | 0 | 0.425 | 0.000 |
| 0.50 | 0.425 | 0.001 | 0 | 0.425 | 0.000 |
| 0.50 | 0.425 | 0.005 | 0 | 0.425 | 0.000 |
| 0.50 | 0.425 | 0.01 | 1 | 0.423 | 0.002 |
| 0.16 | 0.673 | 0.0001 | 0 | 0.673 | 0.000 |
| 0.16 | 0.673 | 0.001 | 0 | 0.673 | 0.000 |
| 0.16 | 0.673 | 0.005 | 8 | 0.657 | 0.016 |
| 0.16 | 0.673 | 0.01 | 14 | 0.640 | 0.033 |

## test (n=407)

| threshold | TSS | eps | hours within eps | worst-case TSS | max shift |
|---|---|---|---|---|---|
| 0.50 | 0.173 | 0.0001 | 0 | 0.173 | 0.000 |
| 0.50 | 0.173 | 0.001 | 0 | 0.173 | 0.000 |
| 0.50 | 0.173 | 0.005 | 1 | 0.165 | 0.008 |
| 0.50 | 0.173 | 0.01 | 1 | 0.165 | 0.008 |
| 0.04 | 0.632 | 0.0001 | 0 | 0.632 | 0.000 |
| 0.04 | 0.632 | 0.001 | 1 | 0.632 | 0.000 |
| 0.04 | 0.632 | 0.005 | 7 | 0.606 | 0.026 |
| 0.04 | 0.632 | 0.01 | 8 | 0.606 | 0.026 |

## How far are the headline observations from their thresholds?

The 0/27 zero-catch observation at the shipped 0.5 threshold: the largest
probability among those 27 onset hours is **0.3320**, a
margin of 0.1680 below the threshold. No plausible
numerical perturbation reaches that.

- validation @ 0.5: closest hour is 0.00586 from the threshold; 0 hours within 1e-3, 1 within 1e-2
- test @ 0.5: closest hour is 0.00391 from the threshold; 0 hours within 1e-3, 1 within 1e-2

## Verdict

If the worst-case shifts above are small relative to the 0.46-0.81 wide
confidence intervals we already report, then bf16-vs-fp32 cannot change any
conclusion in the manuscript, and the open item can be stated as bounded
rather than unresolved. A confirmatory fp32 run remains desirable and
cheap; this analysis says what it could and could not overturn.

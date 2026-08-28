# Provenance of the SuryaBench flare CSVs in this folder

These files are **not our work**. They are redistributed here, unmodified,
so that every number in the manuscript reproduces from a fresh clone with no
external download step, and so that the exact snapshot our results rest on is
pinned rather than left to drift.

| field | value |
|---|---|
| source | Hugging Face dataset `nasa-ibm-ai4science/surya-bench-flare-forecasting` |
| revision | `bf474bc1e7752bd529e9707650f9310db8693763` |
| retrieved | 2026-08-24 (UTC) |
| license | CC BY 4.0 |
| attribution | Roy, S., Hegde, D. V., Schmude, J., et al. 2026, *SuryaBench*, Scientific Data 13(1), 712 |

Reuse of these files carries the CC BY 4.0 attribution requirement above.
The upstream dataset card is kept as `UPSTREAM_README.md`.

## Checksums as retrieved

```
593560599946bc806270f8a69709d02ddb0737befb3de6af20c557a1deac1bba  data.csv
2f3a40b2074ac8984593d53df4f81434ec91f34bb7629066252f3e0bcd8e37b7  train.csv
b4e29566e786c45693a5d78eef73c1f05f6e19fb87f6e2f255dbfa5b81cb256d  validation.csv
158901e21da5a87720b5db1200dbd4765b7ad7dc692157f9bf87f2e8eeefdf58  test.csv
dfe13927a3afc0780831100e5810ae29f750acbe7e951338dada3ecef3da68a6  leaky_validation.csv
```

## Why a pinned copy matters here

Section 2.4 of the manuscript documents a label-leakage trap and Section 2.3 a
set of mutually incompatible split definitions in the released artifacts. If
those are corrected upstream, a later reader running against the corrected data
would not reproduce our numbers and could not tell why. This snapshot removes
that ambiguity: it is the data the results were computed from.

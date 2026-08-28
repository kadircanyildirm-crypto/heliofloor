# audit_extra.py output

The prose-level quantities the claim-checker in verify_paper.py cannot
reach: block structure, archive gaps, files streamed, onset intervals,
flux-parser edge cases, and the split definitions as released.

```
============================================================================================
1-2. BLOCK STRUCTURE: planned 24h windows vs recovered contiguous runs
============================================================================================

validation: 739 scored hours, 50 recovered blocks, 65 distinct calendar days
  planned windows (from plan_blocks.py): 36 x 24h = 864 hours
  actually scored                      : 739 hours (125 short)
  recovered-block sizes: min 2, median 15, max 22
  size histogram: {2: 2, 3: 1, 4: 1, 5: 2, 6: 1, 7: 4, 8: 3, 11: 3, 12: 4, 13: 1, 14: 2, 15: 1, 16: 1, 17: 2, 19: 2, 20: 1, 21: 3, 22: 16}
  blocks with >=20 h: 20;  fragments (<20 h): 30

test: 407 scored hours, 28 recovered blocks, 20 distinct calendar days
  planned windows (from plan_blocks.py): 20 x 24h = 480 hours
  actually scored                      : 407 hours (73 short)
  recovered-block sizes: min 1, median 20, max 22
  size histogram: {1: 2, 3: 2, 4: 2, 5: 2, 8: 1, 9: 1, 11: 1, 13: 1, 14: 1, 18: 1, 22: 14}
  blocks with >=20 h: 14;  fragments (<20 h): 14

============================================================================================
3. netCDF FILES STREAMED  (input is two timesteps: t-60min and t)
============================================================================================
  validation: 739 forecast hours -> 789 distinct timesteps
  test: 407 forecast hours -> 435 distinct timesteps
  TOTAL distinct timesteps: 1224
  at ~586 MB per timestep  : 700 GB

============================================================================================
4. ONSET CATCH RATES with block-bootstrap intervals (section 4.4)
============================================================================================

validation: 46 onset hours in 4 independent blocks
  Surya @0.16 (tuned)     : 35/46 = 0.761  95% CI [0.357, 1.000]  (hits in 4/4 blocks)
  Surya @0.50 (shipped)   : 14/46 = 0.304  95% CI [0.000, 0.750]  (hits in 3/4 blocks)
  persistence             :  0/46 = 0.000  structural, no interval
  rule of three on block-effective n: 3/4 = 0.750

test: 27 onset hours in 3 independent blocks
  Surya @0.04 (tuned)     : 13/27 = 0.481  95% CI [0.000, 1.000]  (hits in 2/3 blocks)
  Surya @0.50 (shipped)   :  0/27 = 0.000  95% CI [0.000, 0.000]  (hits in 0/3 blocks)
  persistence             :  0/27 = 0.000  structural, no interval
  rule of three on block-effective n: 3/3 = 1.000

============================================================================================
5. FLUX-PARSER EDGE CASES (why some feature rows are non-finite)
============================================================================================
  rows where parsed flux == 0 (log10 -> -inf): 4
  the classes responsible: ['A0.0']
  rows with missing max_goes_class          : 0
  total rows in data.csv                    : 128328
  distinct class prefixes                   : ['A', 'B', 'C', 'F', 'M', 'X']

============================================================================================
6. SPLIT DEFINITIONS as they appear in the released CSVs
============================================================================================
  train              n= 74760  years 2010-2019 (10 yrs)  base=0.1211
                     calendar span: 02-15 .. 12-31  (321 distinct month-days)
  validation         n=  3672  years 2011-2019 (9 yrs)  base=0.1089
                     calendar span: 01-15 .. 01-31  (17 distinct month-days)
  leaky_validation   n=  6048  years 2011-2019 (9 yrs)  base=0.1490
                     calendar span: 01-01 .. 02-14  (28 distinct month-days)
  test               n= 43848  years 2020-2024 (5 yrs)  base=0.2943
                     calendar span: 01-01 .. 12-31  (366 distinct month-days)
```

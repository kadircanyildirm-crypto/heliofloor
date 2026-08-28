====================================================================================================
SECTION: sample sizes  (Abstract, section 3.2, section 4.2, section 4.3)
====================================================================================================
  [OK  ] validation scored hours                              claimed 739  computed 739  
  [OK  ] test scored hours                                    claimed 407  computed 407  
  [OK  ] total scored hours (abstract '1,146')                claimed 1146  computed 1146  
  [OK  ] total positives (abstract '218')                     claimed 218  computed 218  
  [OK  ] validation positives                                 claimed 85  computed 85  
  [OK  ] test positives                                       claimed 133  computed 133  
  [OK  ] validation blocks                                    claimed 50  computed 50  
  [OK  ] test blocks                                          claimed 28  computed 28  
  [OK  ] validation base rate                                 claimed 0.1150  computed 0.1150  
  [OK  ] test base rate                                       claimed 0.3270  computed 0.3268  
  [OK  ] validation label mismatches vs official CSV          claimed 0  computed 0  (739 of 739 hours present in split file)
  [OK  ] test label mismatches vs official CSV                claimed 0  computed 0  (407 of 407 hours present in split file)

====================================================================================================
SECTION: block support  (Abstract, section 4.3, section 7)
====================================================================================================
  [OK  ] validation positive-containing blocks                claimed 6  computed 6  
  [OK  ] test positive-containing blocks                      claimed 11  computed 11  

====================================================================================================
SECTION: matched-hours scoreboard  (Abstract, section 4.2, section 4.3)
====================================================================================================
  [OK  ] validation Surya tuned threshold                     claimed 0.1600  computed 0.1600  
  [OK  ] validation Surya tuned TSS                           claimed 0.6730  computed 0.6731  
  [OK  ] test Surya tuned threshold                           claimed 0.0400  computed 0.0400  
  [OK  ] test Surya tuned TSS                                 claimed 0.6320  computed 0.6317  
  [OK  ] validation Surya @0.5 TSS                            claimed 0.4250  computed 0.4246  
  [OK  ] test Surya @0.5 TSS                                  claimed 0.1730  computed 0.1729  
  [OK  ] validation persistence TSS                           claimed 0.4050  computed 0.4053  
  [OK  ] test persistence TSS                                 claimed 0.6180  computed 0.6182  
  [OK  ] test Surya tuned HSS                                 claimed 0.5710  computed 0.5710  
  [OK  ] test Surya tuned F1                                  claimed 0.7350  computed 0.7352  
  [OK  ] validation hybrid (persist OR Surya) TSS             claimed 0.7050  computed 0.7055  

====================================================================================================
SECTION: block-bootstrap intervals  (section 4.3)
====================================================================================================
  [OK  ] validation Surya @0.5 CI low                         claimed 0.0280  computed 0.0282  
  [OK  ] validation Surya @0.5 CI high                        claimed 0.7460  computed 0.7457  
  [OK  ] validation Surya tuned CI low                        claimed 0.2890  computed 0.2886  
  [OK  ] validation Surya tuned CI high                       claimed 0.8860  computed 0.8858  
  [OK  ] test Surya @0.5 CI low                               claimed 0.0000  computed 0.0000  
  [OK  ] test Surya @0.5 CI high                              claimed 0.4840  computed 0.4842  
  [OK  ] test Surya tuned CI low                              claimed 0.3150  computed 0.3149  
  [OK  ] test Surya tuned CI high                             claimed 0.8760  computed 0.8758  
  [OK  ] validation persistence CI low                        claimed -0.0190  computed -0.0185  
  [OK  ] validation persistence CI high                       claimed 0.7920  computed 0.7918  
  [OK  ] test persistence CI low                              claimed 0.2580  computed 0.2580  
  [OK  ] test persistence CI high                             claimed 0.8890  computed 0.8885  

====================================================================================================
SECTION: calibration  (Abstract, section 4.5)
====================================================================================================
  [OK  ] validation Brier                                     claimed 0.0570  computed 0.0571  
  [OK  ] test Brier                                           claimed 0.2080  computed 0.2076  

  reliability table (recomputed):
    validation:
      [0.00,0.01)  n= 391  pred 0.002  obs 0.000  blocks 32
      [0.01,0.05)  n= 110  pred 0.024  obs 0.118  blocks 20
      [0.05,0.10)  n=  48  pred 0.076  obs 0.062  blocks 15
      [0.10,0.25)  n=  88  pred 0.172  obs 0.125  blocks 15
      [0.25,0.50)  n=  58  pred 0.350  obs 0.362  blocks 11
      [0.50,0.75)  n=  18  pred 0.622  obs 0.667  blocks 4
      [0.75,1.01)  n=  26  pred 0.866  obs 0.962  blocks 3
    test:
      [0.00,0.01)  n= 180  pred 0.003  obs 0.078  blocks 15
      [0.01,0.05)  n=  41  pred 0.021  obs 0.049  blocks 8
      [0.05,0.10)  n=  35  pred 0.078  obs 0.657  blocks 13
      [0.10,0.25)  n= 108  pred 0.170  obs 0.537  blocks 13
      [0.25,0.50)  n=  20  pred 0.307  obs 0.650  blocks 9
      [0.50,0.75)  n=   1  pred 0.504  obs 1.000  blocks 1
      [0.75,1.01)  n=  22  pred 0.931  obs 1.000  blocks 1
  [OK  ] validation bin [0.05,0.25) hours                     claimed 136  computed 136  
  [OK  ] validation bin [0.05,0.25) blocks                    claimed 17  computed 17  
  [OK  ] validation bin [0.05,0.25) observed rate             claimed 0.1030  computed 0.1029  
  [OK  ] test bin [0.05,0.25) hours                           claimed 143  computed 143  
  [OK  ] test bin [0.05,0.25) blocks                          claimed 15  computed 15  
  [OK  ] test bin [0.05,0.25) observed rate                   claimed 0.5660  computed 0.5664  
  [OK  ] test bin [0.05,0.25) mean predicted                  claimed 0.1480  computed 0.1477  
  [OK  ] Platt a                                              claimed 0.9440  computed 0.9437  
  [OK  ] Platt b                                              claimed 0.1450  computed 0.1447  
  [OK  ] test TSS after Platt (claim: unchanged 0.173)        claimed 0.1730  computed 0.1729  

====================================================================================================
SECTION: onset / continuation  (section 4.4, Figure 4)
====================================================================================================
  [OK  ] validation onset positives                           claimed 46  computed 46  
  [OK  ] validation continuation positives                    claimed 39  computed 39  
  [OK  ] validation decay hours                               claimed 35  computed 35  
  [OK  ] validation onsets caught, Surya tuned                claimed 35  computed 35  
  [OK  ] validation onsets caught, Surya @0.5                 claimed 14  computed 14  
  [OK  ] validation onset-containing blocks                   claimed 4  computed 4  
       rule of three on block-effective n: 3/4 = 0.750
  [OK  ] test onset positives                                 claimed 27  computed 27  
  [OK  ] test continuation positives                          claimed 106  computed 106  
  [OK  ] test decay hours                                     claimed 49  computed 49  
  [OK  ] test onsets caught, Surya tuned                      claimed 13  computed 13  
  [OK  ] test onsets caught, Surya @0.5                       claimed 0  computed 0  
  [OK  ] test onset-containing blocks                         claimed 3  computed 3  
       rule of three on block-effective n: 3/3 = 1.000

====================================================================================================
SECTION: full official splits  (section 4.1, 4.2, 4.6)
====================================================================================================
  [OK  ] train rows used (section 3.3 claims 74,564)          claimed 74564  computed 74564  (of 74760 train rows; 196 dropped as non-finite)
  [OK  ] full validation hours                                claimed 3672  computed 3672  
  [OK  ] full test hours                                      claimed 43848  computed 43848  
  [OK  ] full validation base rate                            claimed 0.1090  computed 0.1089  
  [OK  ] full test base rate                                  claimed 0.2940  computed 0.2943  
  [OK  ] full validation GOES logistic TSS                    claimed 0.6610  computed 0.6613  
  [OK  ] full validation GOES logistic HSS                    claimed 0.3750  computed 0.3752  
  [OK  ] full validation GOES logistic F1                     claimed 0.4750  computed 0.4749  
  [OK  ] full validation persistence TSS                      claimed 0.4300  computed 0.4295  
  [OK  ] full validation persistence HSS                      claimed 0.4280  computed 0.4281  
  [OK  ] full validation persistence F1                       claimed 0.4910  computed 0.4907  
  [OK  ] full test GOES logistic TSS                          claimed 0.5540  computed 0.5544  
  [OK  ] full test GOES logistic HSS                          claimed 0.4360  computed 0.4359  
  [OK  ] full test GOES logistic F1                           claimed 0.6550  computed 0.6547  
  [OK  ] full test persistence TSS                            claimed 0.5350  computed 0.5352  
  [OK  ] full test persistence HSS                            claimed 0.5360  computed 0.5355  
  [OK  ] full test persistence F1                             claimed 0.6720  computed 0.6721  

  per-year test table (recomputed):
    2020  n=8784  base=0.00546  GOES TSS=+0.452  persist TSS=-0.005
    2021  n=8760  base=0.06130  GOES TSS=+0.514  persist TSS=+0.270
    2022  n=8760  base=0.26381  GOES TSS=+0.250  persist TSS=+0.322
    2023  n=8760  base=0.44349  GOES TSS=+0.056  persist TSS=+0.293
    2024  n=8784  base=0.69695  GOES TSS=+0.079  persist TSS=+0.389
  [OK  ] 2020 hours                                           claimed 8784  computed 8784  
  [OK  ] 2020 base rate                                       claimed 0.0050  computed 0.0055  
  [OK  ] 2020 GOES TSS                                        claimed 0.4520  computed 0.4516  
  [OK  ] 2020 persistence TSS                                 claimed -0.0050  computed -0.0055  
  [OK  ] 2021 hours                                           claimed 8760  computed 8760  
  [OK  ] 2021 base rate                                       claimed 0.0610  computed 0.0613  
  [OK  ] 2021 GOES TSS                                        claimed 0.5140  computed 0.5135  
  [OK  ] 2021 persistence TSS                                 claimed 0.2700  computed 0.2699  
  [OK  ] 2022 hours                                           claimed 8760  computed 8760  
  [OK  ] 2022 base rate                                       claimed 0.2640  computed 0.2638  
  [OK  ] 2022 GOES TSS                                        claimed 0.2500  computed 0.2502  
  [OK  ] 2022 persistence TSS                                 claimed 0.3220  computed 0.3222  
  [OK  ] 2023 hours                                           claimed 8760  computed 8760  
  [OK  ] 2023 base rate                                       claimed 0.4430  computed 0.4435  
  [OK  ] 2023 GOES TSS                                        claimed 0.0560  computed 0.0559  
  [OK  ] 2023 persistence TSS                                 claimed 0.2930  computed 0.2926  
  [OK  ] 2024 hours                                           claimed 8784  computed 8784  
  [OK  ] 2024 base rate                                       claimed 0.6970  computed 0.6969  
  [OK  ] 2024 GOES TSS                                        claimed 0.0790  computed 0.0795  
  [OK  ] 2024 persistence TSS                                 claimed 0.3890  computed 0.3889  

  EXACT base-rate ratio 2024/2020 = 0.696949 / 0.005464 = 127.5x
  [OK  ] base-rate fold change (paper says 128-fold)          claimed 128.0000  computed 127.5417  computed from unrounded rates, not 0.697/0.005
  pooled test GOES TSS = 0.554; per-year range 0.056..0.514
  [OK  ] pooled exceeds every per-year value (Simpson)        claimed 1  computed 1  1 = claim holds

====================================================================================================
SECTION: leakage identity  (section 2.4)
====================================================================================================
  [OK  ] leakage identity rows checked                        claimed 128328  computed 128328  
  [OK  ] leakage identity rows agreeing                       claimed 128328  computed 128328  
  [OK  ] label_cum identity rows checked                      claimed 128328  computed 128328  
  [OK  ] label_cum == (cumulative_index >= 10) agreeing       claimed 128328  computed 128328  

====================================================================================================
SECTION: split table and sampling arithmetic  (section 2.2, section 3.2)
====================================================================================================
  [OK  ] train hours (table 2.2)                              claimed 74760  computed 74760  
  [OK  ] train base rate (table 2.2)                          claimed 0.1211  computed 0.1211  
  [OK  ] leaky_validation hours                               claimed 6048  computed 6048  
  [OK  ] leaky_validation base rate                           claimed 0.1490  computed 0.1490  
  [OK  ] validation hours lost to archive gaps (125 of 864)   claimed 125  computed 125  
  [OK  ] test hours lost to archive gaps (73 of 480)          claimed 73  computed 73  
  [OK  ] distinct netCDF timesteps streamed                   claimed 1224  computed 1224  
  [OK  ] validation blocks >= 20 h                            claimed 20  computed 20  
  [OK  ] validation fragments < 20 h                          claimed 30  computed 30  
  [OK  ] test blocks >= 20 h                                  claimed 14  computed 14  
  [OK  ] test fragments < 20 h                                claimed 14  computed 14  

====================================================================================================
SECTION: GOES logistic on the matched hours  (section 4.2, section 4.3)
====================================================================================================
  [OK  ] validation GOES tuned threshold                      claimed 0.1000  computed 0.1000  
  [OK  ] validation GOES matched TSS                          claimed 0.6850  computed 0.6846  
  [OK  ] test GOES tuned threshold                            claimed 0.3400  computed 0.3400  
  [OK  ] test GOES matched TSS                                claimed 0.7380  computed 0.7378  
  [OK  ] test GOES matched HSS                                claimed 0.6990  computed 0.6986  
  [OK  ] test GOES matched F1                                 claimed 0.8070  computed 0.8068  
  [OK  ] validation GOES CI low                               claimed 0.4170  computed 0.4168  
  [OK  ] validation GOES CI high                              claimed 0.8810  computed 0.8808  
  [OK  ] test GOES CI low                                     claimed 0.4670  computed 0.4671  
  [OK  ] test GOES CI high                                    claimed 0.9400  computed 0.9402  

====================================================================================================
SECTION: paired block-bootstrap differences  (section 4.3, section 4.4)
====================================================================================================
  [OK  ] validation paired point GOES-SuryaTuned              claimed 0.0120  computed 0.0115  
  [OK  ] validation paired point SuryaTuned-Persist           claimed 0.2680  computed 0.2678  
  [OK  ] validation paired point GOES-Persist                 claimed 0.2790  computed 0.2793  
  [OK  ] validation paired point Surya05-Persist              claimed 0.0190  computed 0.0193  
  [OK  ] validation paired point Hybrid-SuryaTuned            claimed 0.0320  computed 0.0324  
  [OK  ] validation paired CI low GOES-SuryaTuned             claimed -0.3250  computed -0.3245  
  [OK  ] validation paired CI high GOES-SuryaTuned            claimed 0.4730  computed 0.4726  
  [OK  ] validation paired CI low SuryaTuned-Persist          claimed -0.1530  computed -0.1530  
  [OK  ] validation paired CI high SuryaTuned-Persist         claimed 0.6580  computed 0.6576  
  [OK  ] validation paired CI low GOES-Persist                claimed -0.0580  computed -0.0585  
  [OK  ] validation paired CI high GOES-Persist               claimed 0.6810  computed 0.6809  
  [OK  ] validation paired CI low Surya05-Persist             claimed -0.3980  computed -0.3982  
  [OK  ] validation paired CI high Surya05-Persist            claimed 0.4270  computed 0.4275  
  [OK  ] validation paired CI low Hybrid-SuryaTuned           claimed -0.0440  computed -0.0443  
  [OK  ] validation paired CI high Hybrid-SuryaTuned          claimed 0.2410  computed 0.2413  
  [OK  ] test paired point GOES-SuryaTuned                    claimed 0.1060  computed 0.1061  
  [OK  ] test paired point SuryaTuned-Persist                 claimed 0.0140  computed 0.0136  
  [OK  ] test paired point GOES-Persist                       claimed 0.1200  computed 0.1196  
  [OK  ] test paired point Surya05-Persist                    claimed -0.4450  computed -0.4452  
  [OK  ] test paired point Hybrid-SuryaTuned                  claimed -0.0330  computed -0.0326  
  [OK  ] test paired CI low GOES-SuryaTuned                   claimed 0.0090  computed 0.0091  
  [OK  ] test paired CI high GOES-SuryaTuned                  claimed 0.2800  computed 0.2805  
  [OK  ] test paired CI low SuryaTuned-Persist                claimed -0.2100  computed -0.2097  
  [OK  ] test paired CI high SuryaTuned-Persist               claimed 0.2530  computed 0.2526  
  [OK  ] test paired CI low GOES-Persist                      claimed -0.0090  computed -0.0088  
  [OK  ] test paired CI high GOES-Persist                     claimed 0.3300  computed 0.3304  
  [OK  ] test paired CI low Surya05-Persist                   claimed -0.8250  computed -0.8249  
  [OK  ] test paired CI high Surya05-Persist                  claimed -0.0860  computed -0.0856  
  [OK  ] test paired CI low Hybrid-SuryaTuned                 claimed -0.0980  computed -0.0983  
  [OK  ] test paired CI high Hybrid-SuryaTuned                claimed 0.0150  computed 0.0153  
  [OK  ] test tail fraction GOES-SuryaTuned (0.55%)           claimed 0.0055  computed 0.0055  
  [OK  ] test tail fraction Surya05-Persist (0.70%)           claimed 0.0070  computed 0.0070  
  [OK  ] test 99.5% low GOES-SuryaTuned                       claimed 0.0000  computed 0.0000  
  [OK  ] test 99.5% high GOES-SuryaTuned                      claimed 0.3820  computed 0.3816  
  [OK  ] test 99.5% low Surya05-Persist                       claimed -0.9240  computed -0.9236  
  [OK  ] test 99.5% high Surya05-Persist                      claimed 0.0700  computed 0.0698  

====================================================================================================
RESULT: 161/161 checks passed, 0 FAILED
====================================================================================================

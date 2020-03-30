# Stop combination

## Renaming of 2l:

L1prefire -> L1prefireSyst
Lumi -> LumiSyst
SFb_2016 -> bTagEffHF16Syst
SFl_2016 -> bTagEffLF16Syst
JEC_2016 -> jes16Syst
leptonSF -> lepSFSyst
PU_2016 -> pileup16Syst
trigger -> TrigSyst (should this be correlated, or 2l CR)

## ToDo:
- [ ] combination of 1l and 2l analysis
```

```
- [ ] check rate parameters / discrepancy of observed limit in ttHinv


## Commands

```
combineCards.py dc_1l=datacard_std_ttHtoInv.txt dc_2l=datacard_2l_ttHtoInv.txt > datacard_combined_ttHtoInv.txt
combine --saveWorkspace -M AsymptoticLimits --rMin -1 --rMax 100 datacard_combined_ttHtoInv.txt
```


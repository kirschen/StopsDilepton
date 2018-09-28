#!/bin/bash
Masspoints="T2tt_850_0 T2tt_900_50 T2tt_850_100 T2tt_900_150 T2tt_600_300 T2tt_750_350"
#Masspoints="T8bbllnunu_XCha0p5_XSlep0p05_1100_0 T8bbllnunu_XCha0p5_XSlep0p05_1000_25 T8bbllnunu_XCha0p5_XSlep0p05_900_50 T8bbllnunu_XCha0p5_XSlep0p05_800_50"
#Masspoints="T8bbllnunu_XCha0p5_XSlep0p5_1200_0 T8bbllnunu_XCha0p5_XSlep0p5_1252_200 T8bbllnunu_XCha0p5_XSlep0p5_1252_400 T8bbllnunu_XCha0p5_XSlep0p5_1152_600 T8bbllnunu_XCha0p5_XSlep0p5_1000_650 T8bbllnunu_XCha0p5_XSlep0p5_800_550"
#Masspoints="T8bbllnunu_XCha0p5_XSlep0p95_1300_0 T8bbllnunu_XCha0p5_XSlep0p95_1300_200 T8bbllnunu_XCha0p5_XSlep0p95_1300_400 T8bbllnunu_XCha0p5_XSlep0p95_1200_800 T8bbllnunu_XCha0p5_XSlep0p95_1000_800"

MVAs="MVA_T2tt_dM350_smaller_TTLep_pow MVA_T2tt_dM350_TTLep_pow MVA_T2tt_dM350_TTZtoLLNuNu MVA_T8bbllnunu_XCha0p5_XSlep0p05_dM350_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p5_dM350_smaller_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p5_dM350_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p95_dM350_smaller_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p95_dM350_TTLep_pow"
 
for i in 0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 0.925 0.95 0.975 0.05 0.15 0.25 0.35 0.45 0.55 0.65 0.75 0.85
do
    for MVA in $MVAs
    do
        for j in $Masspoints
        do
            python run_limit.py --signal T2tt --only $j --expected --MVAselection $MVA --MVAcut $i
        done
    done
done

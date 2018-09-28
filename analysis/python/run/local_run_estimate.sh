#!/bin/bash
Estimators="TTJets DY TTZ multiBoson other"
MVAs="MVA_T2tt_dM350_smaller_TTLep_pow MVA_T2tt_dM350_TTLep_pow MVA_T2tt_dM350_TTZtoLLNuNu MVA_T8bbllnunu_XCha0p5_XSlep0p05_dM350_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p5_dM350_smaller_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p5_dM350_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p95_dM350_smaller_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p95_dM350_TTLep_pow"
 
for i in 0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 0.925 0.95 0.975 0.05 0.15 0.25 0.35 0.45 0.55 0.65 0.75 0.85
do
    for j in $Estimators
    do
        for MVA in $MVAs
        do
            python run_estimate.py --selectEstimator $j --MVAselection $MVA --MVAcut $i
        done
    done
done

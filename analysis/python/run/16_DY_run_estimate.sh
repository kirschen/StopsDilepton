#!/bin/bash

for i in 0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9
do 
    for MVA in MVA_T2tt_dM350_smaller_TTLep_pow MVA_T2tt_dM350_TTLep_pow MVA_T2tt_dM350_TTZtoLLNuNu MVA_T8bbllnunu_XCha0p5_XSlep0p05_dM350_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p5_dM350_smaller_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p5_dM350_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p95_dM350_smaller_TTLep_pow MVA_T8bbllnunu_XCha0p5_XSlep0p95_dM350_TTLep_pow
    do    
        for k in {0..13..1}
        do 
            submitBatch.py "python run_estimate.py --selectEstimator DY --MVAselection $MVA --MVAcut $i --selectRegion $k --noMultiThreading"
        done
    done
done

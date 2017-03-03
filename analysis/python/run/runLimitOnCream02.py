#!/usr/bin/env python
import os
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed       import signals_T2tt
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed    import signals_TTbarDM
from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05, signals_T8bbllnunu_XCha0p5_XSlep0p5
signalEstimators  = [(s.name, 'T2tt') for s in signals_T2tt]
#signalEstimators += [(s.name, 'TTbarDM') for s in signals_TTbarDM]
signalEstimators += [(s.name, 'T8bbllnunu_XCha0p5_XSlep0p05') for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
signalEstimators += [(s.name, 'T8bbllnunu_XCha0p5_XSlep0p5') for s in signals_T8bbllnunu_XCha0p5_XSlep0p5]

import time


for i, (estimator, signal) in enumerate(signalEstimators):
  logfile    = "log/limit_" + estimator + ".log"
  logfileErr = "log/limit_" + estimator + "_err.log"
  os.system("qsub -v command=\"./run_limit.py               --only=" + str(i) + " --signal=" + signal + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfileErr + " -l walltime=8:00:00 runOnCream02.sh")
  os.system("qsub -v command=\"./run_limit.py --controlDYVV --only=" + str(i) + " --signal=" + signal + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfileErr + " -l walltime=8:00:00 runOnCream02.sh")
  os.system("qsub -v command=\"./run_limit.py --controlTTZ  --only=" + str(i) + " --signal=" + signal + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfileErr + " -l walltime=8:00:00 runOnCream02.sh")
  os.system("qsub -v command=\"./run_limit.py --fitAll      --only=" + str(i) + " --signal=" + signal + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfileErr + " -l walltime=8:00:00 runOnCream02.sh")
  time.sleep(10)

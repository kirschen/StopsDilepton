#!/usr/bin/env python
import os
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM
signalEstimators = [s.name for s in signals_T2tt]
#signalEstimators = [s.name for s in signals_TTbarDM]

import time


for i, estimator in enumerate(signalEstimators):
  logfile    = "log/limit_" + estimator + ".log"
  logfileErr = "log/limit_" + estimator + "_err.log"
  os.system("qsub -v command=\"./run_limit.py               --only=" + str(i) + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfileErr + " -l walltime=8:00:00 runEstimatesOnCream02.sh")
  os.system("qsub -v command=\"./run_limit.py --controlDYVV --only=" + str(i) + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfileErr + " -l walltime=8:00:00 runEstimatesOnCream02.sh")
  os.system("qsub -v command=\"./run_limit.py --controlTTZ  --only=" + str(i) + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfileErr + " -l walltime=8:00:00 runEstimatesOnCream02.sh")
  os.system("qsub -v command=\"./run_limit.py --fitAll      --only=" + str(i) + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfileErr + " -l walltime=8:00:00 runEstimatesOnCream02.sh")
  time.sleep(10)

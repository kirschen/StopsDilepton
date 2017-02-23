#!/usr/bin/env python
import os
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05, signals_T8bbllnunu_XCha0p5_XSlep0p5, signals_T8bbllnunu_XCha0p5_XSlep0p95
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM

#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p5]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p95]
signalEstimators = [s.name for s in signals_T2tt]
#signalEstimators = [s.name for s in signals_TTbarDM]

import time

#cmd = "submitBatch.py --title='Limit'"
cmd = "echo"

for i, estimator in enumerate(signalEstimators):
  #logfile    = "log/limit_" + estimator + ".log"
  #logfileErr = "log/limit_" + estimator + "_err.log"
  #os.system("submitBatch.py --title='Limit' 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p95               --only=%s'"%(str(i)))
  #if "1300_1" in estimator:
  #  print i
  #  print estimator
  if i%20==0: print
  os.system(cmd+" 'python run_limit.py --signal T2tt              --only=%s'"%str(i))
#  os.system(cmd+" 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p5--controlDYVV --only=%s'"%str(i))
#  os.system(cmd+" 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p5--controlTTZ  --only=%s'"%str(i))
#  os.system(cmd+" 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p5--fitAll      --only=%s'"%str(i))
#  time.sleep(1)


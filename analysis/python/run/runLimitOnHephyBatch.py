#!/usr/bin/env python
import os
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05, signals_T8bbllnunu_XCha0p5_XSlep0p5, signals_T8bbllnunu_XCha0p5_XSlep0p95
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM

#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05 if s.mStop>650]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p95]

#signalEstimators = [s.name for s in signals_T2tt]
#signalEstimators = [s.name for s in signals_TTbarDM]

import time


for i, estimator in enumerate(signalEstimators):
  #logfile    = "log/limit_" + estimator + ".log"
  #logfileErr = "log/limit_" + estimator + "_err.log"
  os.system("submitBatch.py --title='Limit' 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p95               --only=%s'"%(str(i)))
  #os.system("submitBatch.py --title='Limit' 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p05 --regions=O               --only=%s'"%(str(i)))
  #os.system("submitBatch.py --title='Limit' 'python run_limit.py --signal T2tt --regions=O --controlDYVV --only=%s'"%(str(i))
  time.sleep(0.1)


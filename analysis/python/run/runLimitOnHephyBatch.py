#!/usr/bin/env python
import os
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM
signalEstimators = [s.name for s in signals_T2tt]
#signalEstimators = [s.name for s in signals_TTbarDM]

import time


for i, estimator in enumerate(signalEstimators):
  #logfile    = "log/limit_" + estimator + ".log"
  #logfileErr = "log/limit_" + estimator + "_err.log"
  os.system("submitBatch.py --title='Limit' 'python run_limit.py --signal T2tt --regions=O               --only=%s'"%(str(i)))
  #os.system("submitBatch.py --title='Limit' 'python run_limit.py --signal T2tt --regions=O --controlDYVV --only=%s'"%(str(i))
  time.sleep(1)


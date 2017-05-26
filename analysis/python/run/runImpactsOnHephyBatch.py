#!/usr/bin/env python
import os
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM

#signalEstimators = [s.name for s in signals_T2tt]
signalEstimators = [s.name for s in signals_TTbarDM]

import time

cmd = "submitBatch.py --title='Impacts'"
#cmd = "echo"

for i, estimator in enumerate(signalEstimators):
  #print i, estimator
  #Use only 1 core to not overload the workers!
  os.system(cmd+" 'python run_impacts.py --signal TTbarDM --cores 1 --only=%s'"%str(i))

#!/usr/bin/env python
import os
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
from StopsDilepton.samples.cmgTuples_FastSimT2bX_mAODv2_25ns_postProcessed import signals_T2bt, signals_T2bW

from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05, signals_T8bbllnunu_XCha0p5_XSlep0p09, signals_T8bbllnunu_XCha0p5_XSlep0p5, signals_T8bbllnunu_XCha0p5_XSlep0p95
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM

#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p09]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p5]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p95]
#signalEstimators = [s.name for s in signals_T2tt]
#signalEstimators = [s.name for s in signals_T2bt]
#signalEstimators = [s.name for s in signals_T2bW]
signalEstimators = [s.name for s in signals_TTbarDM]

import time

#cmd = "submitBatch.py --title='Limit'"
cmd = "echo"

for i, estimator in enumerate(signalEstimators):
  #if estimator == "T2tt_500_200":
  print i, estimator
  os.system(cmd+" 'python run_limit.py --signal TTbarDM --fitAll  --extension _preAppFix_flat_regionsDM7_noSysV2          --only=%s'"%str(i))
#  os.system(cmd+" 'python run_limit.py --signal T2tt --fitAll            --only=%s'"%str(i))
#  os.system(cmd+" 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p5--controlDYVV --only=%s'"%str(i))
#  os.system(cmd+" 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p5--controlTTZ  --only=%s'"%str(i))
#  os.system(cmd+" 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p5--fitAll      --only=%s'"%str(i))
#  time.sleep(5)

# 4,5,21,22 for popping
#for i in range(3):
#  os.system('python run_limit.py --signal TTbarDM --fitAll --only 22 --aggregate --popFromSR=%s'%str(i))


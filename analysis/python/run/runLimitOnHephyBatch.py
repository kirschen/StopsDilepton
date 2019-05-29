#!/usr/bin/env python
import os

data_directory              = '/afs/hephy.at/data/dspitzbart03/nanoTuples/'
postProcessing_directory    = 'stops_2017_nano_v0p7/dilep/'
from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt


signalEstimators = [s.name for s in signals_T2tt]

import time

#cmd = "submitBatch.py --title='Limit'"
cmd = "echo"

for i, estimator in enumerate(signalEstimators):
    os.system(cmd+" 'python run_limit.py --signal T2tt --expected --year 2017 --skipFitDiagnostics --only=%s'"%str(i))


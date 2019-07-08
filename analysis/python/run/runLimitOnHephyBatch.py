#!/usr/bin/env python
import os

data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
postProcessing_directory    = 'stops_2016_nano_v0p13/dilep/'
from StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed import signals_T2tt

#data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
#postProcessing_directory    = 'stops_2017_nano_v0p13/dilep/'
#from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt

#data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
#postProcessing_directory    = 'stops_2018_nano_v0p13/dilep/'
#from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T2tt


signalEstimators = [s.name for s in signals_T2tt]

import time

cmd = "submitBatch.py --title='Limit2016'"
#cmd = "echo"

for i, estimator in enumerate(signalEstimators):
    os.system(cmd+" 'python run_limit.py --signal T2tt --expected --year 2016 --skipFitDiagnostics --only=%s'"%str(i))


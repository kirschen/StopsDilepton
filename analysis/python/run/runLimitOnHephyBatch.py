#!/usr/bin/env python
import os

#data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
#postProcessing_directory    = 'stops_2016_nano_v0p19/dilep/'
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2tt
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2bW
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5  
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 

#data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
#postProcessing_directory    = 'stops_2017_nano_v0p19/dilep/'
#from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt
#from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2bW
#from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 
#from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5  
#from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 

data_directory              = '/afs/hephy.at/data/cms07/nanoTuples/'
postProcessing_directory    = 'stops_2018_nano_v0p21/dilep/'
from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T2tt
#from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T2bW
#from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05
#from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 
#from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95


signalEstimators = [s.name for s in signals_T2tt]
#signalEstimators = [s.name for s in signals_T2bW]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p5]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p95]

import time

cmd = "submitBatch.py --title='limit'"
#cmd = "echo"

print len(signalEstimators)
for i, estimator in enumerate(signalEstimators):
    os.system(cmd+" 'python run_limit.py --signal T2tt --unblind --fitAll  --year 2018 --skipFitDiagnostics --only=%s'"%str(i))

#for i, estimator in enumerate(signalEstimators):
#    if estimator.startswith('T2tt_35') or estimator.startswith('T2tt_36') or estimator.startswith('T2tt_37') or estimator.startswith('T2tt_38') or estimator.startswith('T2tt_39') or estimator.startswith('T2tt_400'):
#        os.system(cmd+" 'python run_combination.py --signal T2tt --controlRegions fitAll --overwrite --only=%s'"%str(i))


##cmd = "submitBatch.py --title='scale'"
#cmd = "echo"
#
#print len(signalEstimators)
#for i, estimator in enumerate(signalEstimators):
#    os.system(cmd+" 'python runPDFandScale.py --signal T2tt --year 2018 --combine --only=%s'"%str(i))


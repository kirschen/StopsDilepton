#!/usr/bin/env python
import os

data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
postProcessing_directory    = 'stops_2016_nano_v0p16/dilep/'
from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2tt
from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2bW
from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 
from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 
from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 


#data_directory              = '/afs/hephy.at/data/dspitzbart03/nanoTuples/'
#postProcessing_directory    = 'stops_2017_nano_v0p7/dilep/'
#from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt


#signalEstimators = [s.name for s in signals_T2tt]
#signalEstimators = [s.name for s in signals_T2bW]
signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p5]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p95]

import time

#cmd = "submitBatch.py --title='combLimit'"
cmd = "echo"

for i, estimator in enumerate(signalEstimators):
    #os.system(cmd+" 'python run_combination.py --expected --controlRegions signalOnly  --only=%s'"%str(i)) 
    #os.system(cmd+" 'python run_combination.py --expected --controlRegions fitAll  --only=%s'"%str(i)) 
    #os.system(cmd+" 'python run_combination.py --expected --controlRegions fitAll  --only=%s'"%str(i)) 
    
    #os.system(cmd+" 'python run_combination.py --expected --controlRegions fitAll --signal T2tt --only=%s'"%str(i))
    #os.system(cmd+" 'python run_combination.py --expected --controlRegions fitAll --signal T2bW --only=%s'"%str(i))
    os.system(cmd+" 'python run_combination.py --expected --controlRegions fitAll --signal T8bbllnunu_XCha0p5_XSlep0p05 --only=%s'"%str(i))
    #os.system(cmd+" 'python run_combination.py --expected --controlRegions fitAll --signal T8bbllnunu_XCha0p5_XSlep0p5 --only=%s'"%str(i))
    #os.system(cmd+" 'python run_combination.py --expected --controlRegions fitAll --signal T8bbllnunu_XCha0p5_XSlep0p95 --only=%s'"%str(i))


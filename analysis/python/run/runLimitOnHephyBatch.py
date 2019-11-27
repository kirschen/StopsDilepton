#!/usr/bin/env python
import os

#data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
#postProcessing_directory    = 'stops_2016_nano_v0p16/dilep/'
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2tt
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2bW
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5  
#from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 

data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
postProcessing_directory    = 'stops_2017_nano_v0p19/dilep/'
from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt
from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2bW
from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 
from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5  
from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 

#data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
#postProcessing_directory    = 'stops_2018_nano_v0p19/dilep/'
#from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T2tt
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

#cmd = "submitBatch.py --title='limit17'"
cmd = "echo"

print len(signalEstimators)
for i, estimator in enumerate(signalEstimators):
    #os.system(cmd+" 'python run_limit.py --signal T2tt --expected --year 2018 --skipFitDiagnostics --only=%s'"%str(i))
    #os.system(cmd+" 'python run_limit.py --signal T2bW --expected --year 2018 --skipFitDiagnostics --only=%s'"%str(i))
    # fitAll
    os.system(cmd+" 'python run_limit.py --signal T2tt --unblind --fitAll  --year 2017 --skipFitDiagnostics --only=%s'"%str(i))
    #os.system(cmd+" 'python run_limit.py --signal T2bW --expected --fitAll  --year 2018 --skipFitDiagnostics --only=%s'"%str(i))
    #os.system(cmd+" 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p05 --expected --fitAll  --year 2016 --skipFitDiagnostics --only=%s'"%str(i))
    #os.system(cmd+" 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p5 --unblind --fitAll  --year 2018 --skipFitDiagnostics --only=%s'"%str(i))
    #os.system(cmd+" 'python run_limit.py --signal T8bbllnunu_XCha0p5_XSlep0p95 --expected --fitAll  --year 2017 --skipFitDiagnostics --only=%s'"%str(i))

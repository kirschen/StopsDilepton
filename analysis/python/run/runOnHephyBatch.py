#!/usr/bin/env python
import os
import time
postProcessing_directory = "stops_2016_nano_v2/dilep"
from StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed import signals_T2tt


# Here, all the estimators are defined
estimators = ["TTJets",
              "DY",
              "TTZ",
              "multiBoson",
              "other",
             ]

submitCMD = "submitBatch.py "
#submitCMD = "echo "

from StopsDilepton.analysis.regions import regionsO, regions80X, regionsDM, reducedRegionsNew, superRegion, superRegion140, regions80X_2D, regionsAgg, regionsDM1, regionsDM2, regionsDM3, regionsDM4, regionsDM5, regionsDM6, regionsDM7
allRegions = regionsO
signalEstimators = ['T2tt_850_0', 'T2tt_800_200', '700_350', '600_300']


option = ' --MVAselection MVA_T2tt_default --MVAcut 0.2'

for control in [None]:#, 'DYVV']:#, 'TTZ1', 'TTZ2', 'TTZ3', 'TTZ4', 'TTZ5']:
    controlString = '' if not control else (' --control=' + control)
    for i, estimator in enumerate(estimators):
        title = " --title='Est_%s' "%estimator if submitCMD.count('submit') else ""
        if 'DD' in estimator and control: continue
        for j, region in enumerate(allRegions):
            os.system(submitCMD+title+"'python run_estimate.py --noMultiThreading --selectEstimator=" + estimator + controlString + option + " --selectRegion=%s'"%str(j))
            if submitCMD.count('submit'): time.sleep(2)



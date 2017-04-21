#!/usr/bin/env python
import os
postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
#from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05, signals_T8bbllnunu_XCha0p5_XSlep0p5, signals_T8bbllnunu_XCha0p5_XSlep0p95


# Here, all the estimators are defined
estimators = ["TTJets",
              "TTJets-DD",
              "DY",
              "TTZ",
              "multiBoson",
              "other",
             ]

#submitCMD = "submitBatch.py --title='Estimate' "
submitCMD = "echo "

from StopsDilepton.analysis.regions import regionsO, regions80X, regionsDM, reducedRegionsNew, superRegion, superRegion140, regions80X_2D, regionsAgg
#allRegions = regions80X + superRegion + superRegion140 + regions80X_2D
#allRegions = regionsO
#allRegions = regionsAgg
allRegions = regionsDM
#signalEstimators = [s.name for s in signals_T2tt]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p5]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p95]
signalEstimators = []

#estimators = []

option = ' --DMsync'
#option = ' --aggregate'
#option = ''

for control in [None, 'DYVV']:#, 'TTZ1', 'TTZ2', 'TTZ3', 'TTZ4', 'TTZ5']:
#for control in ['TTZ1', 'TTZ2', 'TTZ3', 'TTZ4', 'TTZ5']:
  controlString = '' if not control else (' --control=' + control)
  for i, estimator in enumerate(estimators):
    if 'DD' in estimator and control: continue
    for j, region in enumerate(allRegions):
      os.system(submitCMD+"'python run_estimate.py --selectEstimator=" + estimator + controlString + option + " --selectRegion=%s'"%str(j))

  # For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
  for i, estimator in enumerate(signalEstimators):
    os.system(submitCMD+"'python run_estimate.py --selectEstimator=" + estimator + controlString + option +"'")

for control in ['TTZ1', 'TTZ2', 'TTZ3', 'TTZ4', 'TTZ5']:
  controlString = '' if not control else (' --control=' + control)
  for i, estimator in enumerate(estimators):
    if 'DD' in estimator and control: continue
    os.system(submitCMD+"'python run_estimate.py --selectEstimator=" + estimator + controlString + option +"'")

  ## For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
  for i, estimator in enumerate(signalEstimators):
    os.system(submitCMD+"'python run_estimate.py --selectEstimator=" + estimator + controlString + option +"'")

###Group 1
#for i, estimator in enumerate(estimators):
#  for j, region in enumerate(allRegions):
#    # print "./submit.sh 'python run_estimate.py --selectEstimator=" + estimator + " --selectRegion=%i'"%j 
#    os.system( "%s 'python run_estimate.py --selectEstimator=%s --selectRegion=%i'"%(submitCMD, estimator, j) )

## Group 2
#from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
#signalEstimators = [s.name for s in signals_T2tt]
## For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
#for i, estimator in enumerate(signalEstimators):
#    os.system("%s 'python run_estimate.py --selectEstimator=%s'"%(submitCMD, estimator))
#
## Group 3
#from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM
#signalEstimators = [s.name for s in signals_TTbarDM]
## For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
#for i, estimator in enumerate(signalEstimators):
#    os.system("%s 'python run_estimate.py --selectEstimator=%s'"%(submitCMD, estimator))

#from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
## For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
#for i, estimator in enumerate(signalEstimators):
#    os.system("%s 'python run_estimate.py --selectEstimator=%s'"%(submitCMD, estimator))
#
#from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p5]
## For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
#for i, estimator in enumerate(signalEstimators):
#    os.system("%s 'python run_estimate.py --selectEstimator=%s'"%(submitCMD, estimator))
#
#from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p95]
## For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
#for i, estimator in enumerate(signalEstimators):
#    os.system("%s 'python run_estimate.py --selectEstimator=%s'"%(submitCMD, estimator))

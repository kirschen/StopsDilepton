#!/usr/bin/env python
import os

# Here, all the estimators are defined
estimators = [
#              "TTJets-DD",
#              "DY-DD",
              "TTXNoZ",
#              "TTZ-DD-Top16009",
#              "multiBoson-DD",
              "multiBoson",
              "other",
              "TTJets",
              "DY",
              "TTZ",
              "singleTop",
#              "TTZ-DD",
             ]

#submitCMD = "submitBatch.py"
submitCMD = "echo"

from StopsDilepton.analysis.regions import regionsO, regions80X, reducedRegionsNew, superRegion, superRegion140, regions80X_2D
#allRegions = regions80X + superRegion + superRegion140 + regions80X_2D
allRegions = regionsO

#Group 1
for i, estimator in enumerate(estimators):
  for j, region in enumerate(allRegions):
    # print "./submit.sh 'python run_estimate.py --selectEstimator=" + estimator + " --selectRegion=%i'"%j 
    os.system( "%s 'python run_estimate.py --selectEstimator=%s --selectRegion=%i'"%(submitCMD, estimator, j) )

# Group 2
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
signalEstimators = [s.name for s in signals_T2tt]
# For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
for i, estimator in enumerate(signalEstimators):
    os.system("%s 'python run_estimate.py --selectEstimator=%s'"%(submitCMD, estimator))

# Group 3
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM
signalEstimators = [s.name for s in signals_TTbarDM]
# For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
for i, estimator in enumerate(signalEstimators):
    os.system("%s 'python run_estimate.py --selectEstimator=%s'"%(submitCMD, estimator))

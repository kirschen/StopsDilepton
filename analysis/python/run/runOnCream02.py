#!/usr/bin/env python
import os
estimators = ["TTJets",
              "TTJets-DD",
              "DY",
              "DY-DD",
              "singleTop",
              "TTXNoZ",
              "TTZ",
              "TTZ-DD",
              "TTZ-DD-Top16009",
              "multiBoson",
              "multiBoson-DD",
              "other",
             ]

#from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
#signalEstimators = [s.name for s in signals_T2tt]

from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
signalEstimators = [s.name for s in signals_TTbarDM]

from StopsDilepton.analysis.regions import regions80X, reducedRegionsNew, superRegion, superRegion140, regionsA, regionsB, regionsC, regionsD, regionsE, regionsF, regionsG, regionsH, regionsI, regionsJ, regionsK, regionsL, regionsM, regionsN

allRegions = regions80X + superRegion + superRegion140 #Cannot be a set! A set has no order and you enumerate below
allRegions += regionsA + regionsB + regionsC + regionsD + regionsE + regionsF + regionsG + regionsH + regionsI + regionsJ + regionsK + regionsL + regionsM + regionsN

for i, estimator in enumerate(estimators):
  for j, region in enumerate(allRegions):
    if j < 100: continue
    logfile = "log/" + estimator + "_" + str(j) + ".log"
    os.system("qsub -v command=\"./run_estimate.py --selectEstimator=" + estimator + " --selectRegion=" + str(j) +"\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runEstimatesOnCream02.sh")

# For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
for i, estimator in enumerate(signalEstimators):
  logfile = "log/" + estimator + ".log"
  os.system("qsub -v command=\"./run_estimate.py --selectEstimator=" + estimator + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runEstimatesOnCream02.sh")

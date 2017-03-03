#!/usr/bin/env python
import os,time
estimators = ["TTJets",
              "TTJets-DD",
              "DY",
              "TTZ",
              "multiBoson",
              "other",
             ]


from StopsDilepton.analysis.regions import regionsO, noRegions

allRegions = regionsO

for control in [None, 'DYVV', 'TTZ1', 'TTZ2', 'TTZ3', 'TTZ4', 'TTZ5']:
  controlString = '' if not control else (' --control=' + control)
  for i, estimator in enumerate(estimators):
    if 'DD' in estimator and control: continue
    allRegions = regionsO if not control or not control.count('TTZ') else noRegions
    for j, region in enumerate(allRegions):
      logfile = "log/" + estimator + "_" + str(j) + ('_' + control if control else '') + ".log"
      if not control or not control.count('TTZ'): os.system("qsub -v command=\"./run_estimate.py                    --selectEstimator=" + estimator + controlString + " --selectRegion=" + str(j) +"\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runOnCream02multiCore.sh")
      else:                                       os.system("qsub -v command=\"./run_estimate.py --noMultiThreading --selectEstimator=" + estimator + controlString + " --selectRegion=" + str(j) +"\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runOnCream02.sh")

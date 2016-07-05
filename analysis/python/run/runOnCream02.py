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
              "EWK",
             ]

from StopsDilepton.analysis.regions import regions80X, reducedRegionsNew, superRegion, superRegion140
allRegions = set(regions80X + reducedRegionsNew + superRegion + superRegion140)

for i, estimator in enumerate(estimators):
  for j, region in enumerate(allRegions):
    logfile = "log/" + estimator + "_" + str(j) + ".log"
    os.system("qsub -v command=\"./run_all_estimates.py --selectEstimator=" + estimator + " --selectRegion=" + str(j) +"\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runEstimatesOnCream02.sh")

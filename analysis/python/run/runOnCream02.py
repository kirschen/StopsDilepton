#!/usr/bin/env python
import os
estimators = ["TTJets",
              "TTJets-DD",
              "DY",
              "TTZ",
              "multiBoson",
              "other",
             ]


from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import signals_T2tt
signalEstimators = [s.name for s in signals_T2tt]

from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import signals_TTbarDM
signalEstimators += [s.name for s in signals_TTbarDM]

from StopsDilepton.analysis.regions import regions80X, reducedRegionsNew, superRegion, superRegion140, regionsO

allRegions = regionsO

for i, estimator in enumerate(estimators):
  for j, region in enumerate(allRegions):
    logfile = "log/" + estimator + "_" + str(j) + ".log"
    os.system("qsub -v command=\"./run_estimate.py --selectEstimator=" + estimator + "                --selectRegion=" + str(j) +"\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runEstimatesOnCream02.sh")
    if 'DD' in estimator: continue
    os.system("qsub -v command=\"./run_estimate.py --selectEstimator=" + estimator + " --control=DYVV --selectRegion=" + str(j) +"\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runEstimatesOnCream02.sh")

# For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
for i, estimator in enumerate(signalEstimators):
  logfile = "log/" + estimator + ".log"
  os.system("qsub -v command=\"./run_estimate.py --selectEstimator=" + estimator + "               \" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runEstimatesOnCream02.sh")
  os.system("qsub -v command=\"./run_estimate.py --selectEstimator=" + estimator + " --control=DYVV\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runEstimatesOnCream02.sh")

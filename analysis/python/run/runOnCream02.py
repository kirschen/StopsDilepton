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

#for control in [None, 'DYVV', 'TTZ1', 'TTZ2', 'TTZ3', 'TTZ4', 'TTZ5']:
for control in ['TTZ1', 'TTZ2', 'TTZ3', 'TTZ4', 'TTZ5']:
  controlString = '' if not control else (' --control=' + control)
  for i, estimator in enumerate(estimators):
    if 'DD' in estimator and control: continue
    for j, region in enumerate(allRegions):
      logfile = "log/" + estimator + "_" + str(j) + ('_' + control if control else '') + ".log"
      os.system("qsub -v command=\"./run_estimate.py --selectEstimator=" + estimator + controlString + " --selectRegion=" + str(j) +"\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runEstimatesOnCream02.sh")

  # For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
  for i, estimator in enumerate(signalEstimators):
    logfile = "log/" + estimator + ('_' + control if control else '') + ".log"
    os.system("qsub -v command=\"./run_estimate.py --selectEstimator=" + estimator + controlString + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runEstimatesOnCream02.sh")

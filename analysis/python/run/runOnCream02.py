#!/usr/bin/env python
import os,time
estimators = ["TTJets",
              "TTJets-DD",
              "DY",
              "TTZ",
              "multiBoson",
              "other",
             ]


from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed       import signals_T2tt
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed    import signals_TTbarDM
from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05, signals_T8bbllnunu_XCha0p5_XSlep0p5
signalEstimators  = [s.name for s in signals_T2tt]
signalEstimators += [s.name for s in signals_TTbarDM]
signalEstimators += [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
signalEstimators += [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p5]

from StopsDilepton.analysis.regions import regionsO, noRegions

allRegions = regionsO

for control in [None, 'DYVV', 'TTZ1', 'TTZ2', 'TTZ3', 'TTZ4', 'TTZ5']:
  controlString = '' if not control else (' --control=' + control)
  for i, estimator in enumerate(estimators):
    continue
    if 'DD' in estimator and control: continue
    allRegions = regionsO if not control or not control.count('TTZ') else noRegions
    for j, region in enumerate(allRegions):
      logfile = "log/" + estimator + "_" + str(j) + ('_' + control if control else '') + ".log"
      if control.count('TTZ'): os.system("qsub -v command=\"./run_estimate.py                    --selectEstimator=" + estimator + controlString + " --selectRegion=" + str(j) +"\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runOnCream02multiCore.sh")
      else:                    os.system("qsub -v command=\"./run_estimate.py --noMultiThreading --selectEstimator=" + estimator + controlString + " --selectRegion=" + str(j) +"\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runOnCream02.sh")
      time.sleep(30)

  # For signals, do not split up in regions, because otherwise you easily reach the maximum of allowed jobs, they are fast anyway
  for i, estimator in enumerate(signalEstimators):
    logfile = "log/" + estimator + ('_' + control if control else '') + ".log"
    os.system("qsub -v command=\"./run_estimate.py --noMultiThreading --selectEstimator=" + estimator + controlString + "\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=8:00:00 runOnCream02.sh")
    time.sleep(30)

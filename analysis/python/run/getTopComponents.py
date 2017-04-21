#!/usr/bin/env python
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--onlyStat",       action='store_true', default=False,          help="show only stat errors?")
args = argParser.parse_args()

from StopsDilepton.analysis.SetupHelpers    import allChannels, channels
from StopsDilepton.analysis.estimators      import setup, constructEstimatorList, MCBasedEstimate
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.SumEstimate     import SumEstimate
from StopsDilepton.analysis.regions         import regionsO as regions
from StopsDilepton.analysis.Cache           import Cache

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )

setup.verbose = False

estimators     = constructEstimatorList(["TTJets","Top_gaussian", "Top_nongaussian", "Top_fakes"])
for e in estimators: e.initCache(setup.defaultCacheDir())


from StopsDilepton.analysis.u_float                                           import u_float
from math                                                                     import sqrt



texdir  = os.path.join(setup.analysis_results, setup.prefix(), 'tables')
try:    os.makedirs(texdir)
except: pass

allChannels = ["SF","EMu","all"]
for channel in allChannels:
  try:    os.makedirs(os.path.join(texdir, channel))
  except: pass

  yieldTexfile = os.path.join(texdir, channel, "topComponents.tex")
  print "Writing to " + yieldTexfile
  with open(yieldTexfile, "w") as yieldTable:
    yieldTable.write("\\begin{tabular}{c|" + "|cc"*3 + "} \n")
    yieldTable.write("  signal region & gaussian & \\% & non-gaussian & \\% & fakes & \\% \\\\ \n")
    yieldTable.write("  \\hline \n")
                 
    for i, r in enumerate(regions[1:]):
      yieldTable.write(" $" + str(i) + "$ ")
      
      totalTop = estimators[0].cachedEstimate(r, channel, setup).val 
      for e in estimators[1:]:
        expected = e.cachedEstimate(r, channel, setup).val
        yieldTable.write(" &  %.2f & %.2f " % (expected, expected/totalTop*100))
      yieldTable.write(" \\\\ \n")

    yieldTable.write("\\end{tabular} \n")

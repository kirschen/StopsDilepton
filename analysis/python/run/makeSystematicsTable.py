#!/usr/bin/env python
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--metSigMin",      action='store', default=5,                   type=int,                                                                                                         help="metSigMin?")
argParser.add_argument("--metMin",         action='store', default=80,                  type=int,                                                                                                         help="metMin?")
argParser.add_argument("--estimateDY",     action='store', default='DY',                nargs='?', choices=["DY","DY-DD"],                                                                                help="which DY estimate?")
argParser.add_argument("--estimateTTZ",    action='store', default='TTZ',               nargs='?', choices=["TTZ","TTZ-DD","TTZ-DD-Top16009"],                                                            help="which TTZ estimate?")
argParser.add_argument("--estimateTTJets", action='store', default='TTJets',            nargs='?', choices=["TTZJets","TTJets-DD"],                                                                       help="which TTJets estimate?")
argParser.add_argument("--regions",        action='store', default='reducedRegionsNew', nargs='?', choices=["defaultRegions","superRegion","superRegion140"],                                             help="which regions setup?")
argParser.add_argument("--signal",         action='store', default='T2tt',              nargs='?', choices=["T2tt","DM"],                                                                                 help="which signal?")
args = argParser.parse_args()

from StopsDilepton.analysis.SetupHelpers import allChannels
from StopsDilepton.analysis.estimators   import setup, constructEstimatorList, MCBasedEstimate, DataDrivenTTZEstimate, DataDrivenDYEstimate, DataDrivenTTJetsEstimate
from StopsDilepton.analysis.regions      import reducedRegionsNew, superRegion, superRegion140
from StopsDilepton.analysis.Cache        import Cache

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )

setup.verbose = False
setup.parameters['metMin']    = args.metMin
setup.parameters['metSigMin'] = args.metSigMin

if args.regions == "defaultRegions":      regions = defaultRegions
elif args.regions == "reducedRegionsA":   regions = reducedRegionsA
elif args.regions == "reducedRegionsB":   regions = reducedRegionsB
elif args.regions == "reducedRegionsAB":  regions = reducedRegionsAB
elif args.regions == "reducedRegionsNew": regions = reducedRegionsNew
elif args.regions == "reducedRegionsC":   regions = reducedRegionsC
elif args.regions == "superRegion":       regions = superRegion
elif args.regions == "superRegion140":    regions = superRegion140
else: raise Exception("Unknown regions setup")

estimators = constructEstimatorList([args.estimateTTJets, 'other-detailed', args.estimateDY, args.estimateTTZ])
for e in estimators:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.analysis.u_float                                           import u_float
from math                                                                     import sqrt


texdir      = os.path.join(setup.analysis_results, setup.prefix(), 'tables', args.signal, args.regions)

try:
  os.makedirs(texdir)
except:
  pass 

def displaySysValue(val):
  roundedVal = int(100*val+0.99)/100.    # round to next 0.0x
  if roundedVal <= 0: return "-"
  return str(roundedVal)


# Make a separate table for each of regions
for channel in ["EE","MuMu","EMu","all"]:
  try:
    os.makedirs(os.path.join(texdir, channel))
  except:
    pass 

  SR = 0
  for r in regions[1:]:
    texfile = os.path.join(texdir, channel, "signalRegion" + str(SR) + ".tex")
    print "Writing to " + texfile
    with open(texfile, "w") as f:
      columns = ["expected","stat","PU","JEC","JER","top \\pt","b-tag SFb", "b-tag SFl"]
      f.write("\\begin{tabular}{l|" + "c"*len(columns) + "} \n")
      f.write("  estimator & " + "&".join(columns) + " \\\\ \n")
      f.write("  \\hline \n")
      
      # One row for each estimator
      for e in estimators:
	f.write("  " + e.name)
	expected = int(100*e.cachedEstimate(       r, channel, setup).val+0.5)/100.
	f.write(" & " + str(expected))
        if expected <= 0:
          f.write(" & -"*(len(columns)-1))
        else:
	  f.write(" & " + displaySysValue(e.cachedEstimate(       r, channel, setup).sigma))
	  f.write(" & " + displaySysValue(e.PUSystematic(         r, channel, setup).val))
	  f.write(" & " + displaySysValue(e.JECSystematic(        r, channel, setup).val))
	  f.write(" & " + displaySysValue(e.JERSystematic(        r, channel, setup).val))
	  f.write(" & " + displaySysValue(e.topPtSystematic(      r, channel, setup).val))
	  f.write(" & " + displaySysValue(e.btaggingSFbSystematic(r, channel, setup).val))
	  f.write(" & " + displaySysValue(e.btaggingSFlSystematic(r, channel, setup).val)) 
	f.write(" \\\\ \n")
      f.write("\\end{tabular} \n")
      f.write("\\caption{Yields and uncertainties for each background in the signal region $" + r.texString(useRootLatex = False) + "$ in channel " + channel + "} \n")
    SR = SR+1

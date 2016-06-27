#!/usr/bin/env python
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--metSigMin",      action='store', default=5,                   type=int,                                                                                                         help="metSigMin?")
argParser.add_argument("--metMin",         action='store', default=80,                  type=int,                                                                                                         help="metMin?")
argParser.add_argument("--regions",        action='store', default='reducedRegionsNew', nargs='?', choices=["defaultRegions","superRegion","superRegion140"],                                             help="which regions setup?")
argParser.add_argument("--signal",         action='store', default='T2tt',              nargs='?', choices=["T2tt","DM"],                                                                                 help="which signal?")
argParser.add_argument("--estimates",      action='store', default='mc',                nargs='?', choices=["mc","dd"],                                                                                   help="mc estimators or data-driven estimators?")
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

if   args.estimates == "mc": estimators = constructEstimatorList(["TTJets","TTZ","DY", 'other-detailed'])
elif args.estimates == "dd": estimators = constructEstimatorList(["TTJets","TTJets-DD","TTZ","TTZ-DD","TTZ-DD-Top16009","DY","DY-DD"])

for e in estimators:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.analysis.u_float                                           import u_float
from math                                                                     import sqrt


texdir      = os.path.join(setup.analysis_results, setup.prefix(), 'tables' + ("_dd" if args.estimates == "dd" else ""), args.signal, args.regions)

try:
  os.makedirs(texdir)
except:
  pass 

def displaySysValue(val):
  roundedVal = int(100*val+0.99)/100.    # round to next 0.0x
  if roundedVal <= 0.: return "-"
  return "%0.2f" % roundedVal


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
        try:
          name = e.sample[channel].texName
        except:
          try:
            texNames = [e.sample[c].texName for c in ['MuMu','EMu','EE']]		# If all, only take texName if it is the same for all channels
	    if texNames.count(texNames[0]) == len(texNames):
	      name = texNames[0]
            else:
	      name = e.name
          except:
	    name = e.name
        name = name.replace('#','\\') # Make it tex format

	f.write(" $" + name + "$ ")
	expected = int(100*e.cachedEstimate(       r, channel, setup).val+0.5)/100.
	f.write(" & " + str(expected))
#        if expected <= 0:
#          f.write(" & -"*(len(columns)-1))
#        else:
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

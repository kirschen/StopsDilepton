#!/usr/bin/env python
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--metSigMin",      action='store', default=5,                   type=int,                                                                                                         help="metSigMin?")
argParser.add_argument("--metMin",         action='store', default=80,                  type=int,                                                                                                         help="metMin?")
argParser.add_argument("--regions",        action='store', default='regions80X', nargs='?', choices=["defaultRegions","superRegion","superRegion140"],                                             help="which regions setup?")
argParser.add_argument("--signal",         action='store', default='T2tt',              nargs='?', choices=["T2tt","DM"],                                                                                 help="which signal?")
argParser.add_argument("--estimates",      action='store', default='mc',                nargs='?', choices=["mc","dd"],                                                                                   help="mc estimators or data-driven estimators?")
argParser.add_argument("--relativeError",  action='store_true', default=False,          help="show relative errors?")
args = argParser.parse_args()

from StopsDilepton.analysis.SetupHelpers    import allChannels, channels
from StopsDilepton.analysis.estimators      import setup, constructEstimatorList
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.SumEstimate     import SumEstimate
from StopsDilepton.analysis.regions         import regions80X, superRegion, superRegion140
from StopsDilepton.analysis.Cache           import Cache

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )

setup.verbose = False
setup.parameters['metMin']    = args.metMin
setup.parameters['metSigMin'] = args.metSigMin

if   args.regions == "regions80X":        regions = regions80X
elif args.regions == "superRegion":       regions = superRegion
elif args.regions == "superRegion140":    regions = superRegion140
else: raise Exception("Unknown regions setup")

if   args.estimates == "mc": estimators = constructEstimatorList(["TTJets","TTZ","DY", 'other-detailed'])
elif args.estimates == "dd": estimators = constructEstimatorList(["TTJets","TTJets-DD","TTZ","TTZ-DD","TTZ-DD-Top16009","DY","DY-DD"])
summedEstimate = SumEstimate(name="sum")

DYestimators = constructEstimatorList(["DY", "DY-DD"])
observation = DataObservation(name='Data', sample=setup.sample['Data'])

for e in estimators + [summedEstimate, observation]:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.analysis.u_float                                           import u_float
from math                                                                     import sqrt


texdir      = os.path.join(setup.analysis_results, setup.prefix(), 'tables' + ("_dd" if args.estimates == "dd" else "") + ("_rel" if args.relativeError else ""), args.signal, args.regions)

try:
  os.makedirs(texdir)
except:
  pass 

def displaySysValue(val, expected):
   if args.relativeError:
     if val <=0 or expected <= 0: return "-"
     return "%.0f" % (val/expected*100+0.5) + " \\%" # round off to next percent
   else:
     roundedVal = int(100*val+0.99)/100.    # round to next 0.0x
     if roundedVal <= 0.: return "-"
     return "%.2f" % roundedVal


# Make a separate table for each of regions
for channel in allChannels:
  try:
    os.makedirs(os.path.join(texdir, channel))
  except:
    pass 

  columns = ["expected","stat","PU","JEC","top \\pt","b-tag SFb", "b-tag SFl","top norm.","ttZ norm","DY norm"]

  overviewTexfile = os.path.join(texdir, channel, "overview.tex")
  print "Writing to " + overviewTexfile
  with open(overviewTexfile, "w") as overviewTable:
    overviewTable.write("\\begin{tabular}{l|c" + "c"*len(columns) + "} \n")
    overviewTable.write("  signal region & observed & " + "&".join(columns) + " \\\\ \n")
    overviewTable.write("  \\hline \n")

    SR = 0
    for r in regions[1:]:
      texfile = os.path.join(texdir, channel, "signalRegion" + str(SR) + ".tex")
      print "Writing to " + texfile
      with open(texfile, "w") as f:
	f.write("\\begin{tabular}{l|" + "c"*len(columns) + "} \n")
	f.write("  estimator & " + "&".join(columns) + " \\\\ \n")
	f.write("  \\hline \n")

        topNorm = 0
        ttZNorm = 0
	
	# One row for each estimator
	for e in estimators:
	  try:
	    name = e.sample[channel].texName
	  except:
	    try:
	      texNames = [e.sample[c].texName for c in channels]		# If all, only take texName if it is the same for all channels
	      if texNames.count(texNames[0]) == len(texNames):
		name = texNames[0]
	      else:
		name = e.name
	    except:
	      name = e.name
	  name = name.replace('#','\\') # Make it tex format

	  f.write(" $" + name + "$ ")
	  expected = int(100*e.cachedEstimate(r, channel, setup).val+0.5)/100.

          if e.name == "TTJets": topNorm = ("%.2f" % (0.3*expected if SR < 6 else 0.2*expected if SR < 12 else expected)) if expected > 0 else " - "
          if e.name == "TTZ":    ttZNorm = ("%.2f" % (0.2*expected)) if expected > 0 else " - "
          if e.name == "DY":     
	     mc = int(100*DYestimators[0].cachedEstimate(r, channel, setup).val+0.5)/100.
	     dd = int(100*DYestimators[1].cachedEstimate(r, channel, setup).val+0.5)/100.
             dyScale = dd/mc if mc > 0 else 0
             print "Scale of DY:" + str(dyScale)
             dyNorm  = ("%.2f" % abs(mc-dd)) if abs(mc-dd) > 0 else " - "

	  f.write(" & %.2f" % expected)
	  f.write(" & " + displaySysValue(e.cachedEstimate(       r, channel, setup).sigma, expected))
	  f.write(" & " + displaySysValue(e.PUSystematic(         r, channel, setup).val,   expected))
	  f.write(" & " + displaySysValue(e.JECSystematic(        r, channel, setup).val,   expected))
  #	f.write(" & " + displaySysValue(e.JERSystematic(        r, channel, setup).val,   expected))
	  f.write(" & " + displaySysValue(e.topPtSystematic(      r, channel, setup).val,   expected))
	  f.write(" & " + displaySysValue(e.btaggingSFbSystematic(r, channel, setup).val,   expected))
	  f.write(" & " + displaySysValue(e.btaggingSFlSystematic(r, channel, setup).val,   expected))
	  f.write(" & " + (topNorm if e.name=="TTJets" else " - "))
	  f.write(" & " + (ttZNorm if e.name=="TTZ"    else " - "))
	  f.write(" & " + (dyNorm  if e.name=="DY"     else " - "))
	  f.write(" \\\\ \n")
	f.write("\\end{tabular} \n")
	f.write("\\caption{Yields and uncertainties for each background in the signal region $" + r.texString(useRootLatex = False) + "$ in channel " + channel + "} \n")

        e = summedEstimate
	overviewTable.write(" $" + str(SR) + "$ ")
	expected = int(100*e.cachedEstimate(r, channel, setup).val+0.5)/100.
	observed = observation.cachedObservation(r, channel, setup).val
#	overviewTable.write(" & xxxx")
	overviewTable.write(" & %.2f" % observed)
	overviewTable.write(" & %.2f" % expected)
	overviewTable.write(" & " + displaySysValue(e.cachedEstimate(       r, channel, setup).sigma, expected))
	overviewTable.write(" & " + displaySysValue(e.PUSystematic(         r, channel, setup).val,   expected))
	overviewTable.write(" & " + displaySysValue(e.JECSystematic(        r, channel, setup).val,   expected))
#	overviewTable.write(" & " + displaySysValue(e.JERSystematic(        r, channel, setup).val,   expected))
	overviewTable.write(" & " + displaySysValue(e.topPtSystematic(      r, channel, setup).val,   expected))
	overviewTable.write(" & " + displaySysValue(e.btaggingSFbSystematic(r, channel, setup).val,   expected))
	overviewTable.write(" & " + displaySysValue(e.btaggingSFlSystematic(r, channel, setup).val,   expected))
	overviewTable.write(" & " + topNorm)
	overviewTable.write(" & " + ttZNorm)
	overviewTable.write(" & " + dyNorm)
	overviewTable.write(" \\\\ \n")

      SR = SR+1

    overviewTable.write("\\end{tabular} \n")
    overviewTable.write("\\caption{Yields and uncertainties for the total background in each of the signal regions for channel" + channel + "} \n")

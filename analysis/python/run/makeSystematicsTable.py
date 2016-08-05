#!/usr/bin/env python
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--regions",        action='store', default='regions80X', nargs='?', choices=["defaultRegions","superRegion","superRegion140"],                                             help="which regions setup?")
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

if   args.regions == "regions80X":        regions = regions80X
elif args.regions == "superRegion":       regions = superRegion
elif args.regions == "superRegion140":    regions = superRegion140
else: raise Exception("Unknown regions setup")

if   args.estimates == "mc": estimators = constructEstimatorList(["TTJets","TTZ","DY", 'other-detailed'])
elif args.estimates == "dd": estimators = constructEstimatorList(["TTJets-DD","TTZ-DD-Top16009","DY-DD", 'other-detailed'])
summedEstimate = SumEstimate(name="sum_dd" if args.estimates == "dd" else "sum")

DYestimators = constructEstimatorList(["DY", "DY-DD"])
observation = DataObservation(name='Data', sample=setup.sample['Data'])

for e in estimators + [summedEstimate, observation] + DYestimators:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.analysis.u_float                                           import u_float
from math                                                                     import sqrt


texdir = os.path.join(setup.analysis_results, setup.prefix(), 'tables' + ("_dd" if args.estimates == "dd" else "") + ("_rel" if args.relativeError else ""), args.regions)

try:    os.makedirs(texdir)
except: pass

def displayRelSysValue(val):
     if val <=0: return "0 \\%"
     return "%.0f" % (val*100) + " \\%"

def displayAbsSysValue(val):
     roundedVal = int(100*val+0.99)/100.    # round to next 0.0x
     if roundedVal <= 0.: return "-"
     return "%.2f" % roundedVal

# Evaluate absolute and relative errors
def evaluateEstimate(e, SR, estimators=None):
     expected            = e.cachedEstimate(r, channel, setup).val

     e.rel               = {}
     e.abs               = {}
     e.displayRel        = {}
     e.displayAbs        = {}

     e.abs["stat"]       = e.cachedEstimate(       r, channel, setup).sigma
     e.rel["PU"]         = e.PUSystematic(         r, channel, setup).val
     e.rel["JEC"]        = e.JECSystematic(        r, channel, setup).val
     e.rel["JER"]        = e.JERSystematic(        r, channel, setup).val
     e.rel["top-\\pt"]   = e.topPtSystematic(      r, channel, setup).val
     e.rel["b-tag SF-b"] = e.btaggingSFbSystematic(r, channel, setup).val
     e.rel["b-tag SF-l"] = e.btaggingSFlSystematic(r, channel, setup).val
     e.rel["TTJets"]     = 0 if not e.name.count("TTJets")     else 0.3 if SR < 6 else 0.2 if SR < 12 else 1
     e.rel["TTZ"]        = 0 if not e.name.count("TTZ")        else 0.2
     e.rel["multiBoson"] = 0 if not e.name.count("multiBoson") else 0.25
     e.rel["TTXNoZ"]     = 0 if not e.name.count("TTXNoZ")     else 0.25
     e.rel["DY"]         = 0 if not e.name.count("DY")         else 0.5

#    if e.name.count("DY"):
#      mc = DYestimators[0].cachedEstimate(r, channel, setup).val
#      dd = DYestimators[1].cachedEstimate(r, channel, setup).val
#      e.abs["DY"] = abs(mc-dd)

     # For sum assume the individual estimators are already evaluated such that we can pick their corresponding absolute error
     if e.name.count("sum"):
       for i in ['TTJets','DY','TTXNoZ','TTZ','multiBoson']:
         summedEstimate.abs[i] = next(e for e in estimators if e.name.count(i)).abs[i]

     for i in e.abs: e.rel[i] = e.abs[i]/expected if expected > 0 else 0
     for i in e.rel: e.abs[i] = e.rel[i]*expected
     for i in e.abs: e.displayRel[i] = displayRelSysValue(e.rel[i])
     for i in e.rel: e.displayAbs[i] = displayAbsSysValue(e.abs[i])

     e.expected = int(100*expected+0.5)/100.



# Make a separate table for each of regions
for channel in allChannels:
  try:    os.makedirs(os.path.join(texdir, channel))
  except: pass

  sysColumns = ["stat","PU","JEC","top-\\pt","b-tag SF-b", "b-tag SF-l", "TTJets", "TTZ", "multiBoson", "TTXNoZ", "DY"]
  columns    = ["expected"] + sysColumns

  minima = {}
  maxima = {}
  for i in sysColumns:
    minima[i]  = 9999
    maxima[i]  = 0


  overviewTexfile = os.path.join(texdir, channel, "overview.tex")
  print "Writing to " + overviewTexfile
  with open(overviewTexfile, "w") as overviewTable:
    overviewTable.write("\\begin{tabular}{l|c" + "c"*len(columns) + "} \n")
    overviewTable.write("  signal region & observed & " + "&".join(columns) + " \\\\ \n")
    overviewTable.write("  \\hline \n")

    for SR,r in enumerate(regions[1:]):
      texfile = os.path.join(texdir, channel, "signalRegion" + str(SR) + ".tex")
      print "Writing to " + texfile
      with open(texfile, "w") as f:
	f.write("\\begin{tabular}{l|" + "c"*len(columns) + "} \n")
	f.write("  estimator & " + "&".join(columns) + " \\\\ \n")
	f.write("  \\hline \n")

	# One row for each estimator
	for e in estimators:
          evaluateEstimate(e, SR)
 
	  f.write(" $" + e.getTexName(channel, rootTex=False) + "$ ")
	  f.write(" & %.2f" % e.expected)
          for i in sysColumns:
            f.write(" & " + e.displayAbs[i])
	  f.write(" \\\\ \n")

	f.write("\\end{tabular} \n")
	f.write("\\caption{Yields and uncertainties for each background in the signal region $" + r.texString(useRootLatex = False) + "$ in channel " + channel + "} \n")

        evaluateEstimate(summedEstimate, SR, estimators)

	overviewTable.write(" $" + str(SR) + "$ ")
	overviewTable.write(" & %d" % observation.cachedObservation(r, channel, setup).val)
	overviewTable.write(" & %.2f" % summedEstimate.expected)

	for i in sysColumns:
	  overviewTable.write(" & " + summedEstimate.displayAbs[i])
        overviewTable.write(" \\\\ \n")

        for i in sysColumns:
          minima[i] = min(e.rel[i], minima[i])
          maxima[i] = max(e.rel[i], maxima[i])

    overviewTable.write("\\end{tabular} \n")
    overviewTable.write("\\caption{Yields and uncertainties for the total background in each of the signal regions for channel" + channel + "} \n")

    minmaxFile = os.path.join(texdir, channel, "minmax.tex")
    print "Writing to " + minmaxFile
    with open(minmaxFile, "w") as minmaxTable:
      minmaxTable.write("\\begin{tabular}{l|c} \n")
      minmaxTable.write("  systematic & min-max of signal regions \\\\ \n")
      minmaxTable.write("  \\hline \n")
      longNames = {"stat":        "statistical",
                   "PU":          "pile-up",
                   "TTJets" :     "top background",
                   "TTZ":         "$t\\bar{t}Z$ background",
                   "TTXNoZ" :     "$t\\bar{t}X$ (excl. $t\\bar{t}Z$) background",
                   "DY" :         "DY background",
                   "multiBoson" : "multiboson background"}

      for i in sysColumns:
        name = longNames[i] if i in longNames else i
        if minima[i] > 0:  minmaxTable.write(name + " & " + displayRelSysValue(minima[i]) + " - " + displayRelSysValue(maxima[i]) + " \\\\ \n")
        else:              minmaxTable.write(name + " & $<$ " + displayRelSysValue(maxima[i]) + " \\\\ \n")
      minmaxTable.write("\\end{tabular} \n")

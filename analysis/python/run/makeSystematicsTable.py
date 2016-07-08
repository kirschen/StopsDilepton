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
elif args.estimates == "dd": estimators = constructEstimatorList(["TTJets-DD","TTZ-DD-Top16009","DY-DD", 'other-detailed'])
summedEstimate = SumEstimate(name="sum")

DYestimators = constructEstimatorList(["DY", "DY-DD"])
observation = DataObservation(name='Data', sample=setup.sample['Data'])

for e in estimators + [summedEstimate, observation] + DYestimators:
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
     if val <=0 or expected <= 0: return "0 \\%"
     return "%.0f" % (val*100) + " \\%"
   else:
     roundedVal = int(100*(val*expected)+0.99)/100.    # round to next 0.0x
     if roundedVal <= 0.: return "-"
     return "%.2f" % roundedVal

def min((x, y), (xx, yy)):
     if   isinstance(x, str): return (xx,yy)
     elif isinstance(xx, str):return (x,y)
     elif not y or y == 0:   return (xx,yy)
     elif not yy or yy == 0: return (x,y)
     elif abs(x) < abs(xx):       return (x,y)
     else:                   return (xx,yy)

def max((x, y), (xx, yy)):
     if   isinstance(x, str): return (xx,yy)
     elif isinstance(xx, str):return (x,y)
     if   not y or y == 0:   return (xx,yy)
     elif not yy or yy == 0: return (x,y)
     elif abs(x) > abs(xx):       return (x,y)
     else:                   return (xx,yy)




# Make a separate table for each of regions
for channel in allChannels:
  try:
    os.makedirs(os.path.join(texdir, channel))
  except:
    pass 

  columns = ["expected","stat","PU","JEC","top-\\pt","b-tag SFb", "b-tag SFl","TTJets","TTZ","DY","TTXNoZ","multiBoson"]

  minima = {}
  maxima = {}

  minima["stat"]  = (999999,None)
  minima["PU"]    = (999999,None) 
  minima["JEC"]   = (999999,None) 
  minima["topPt"] = (999999,None)
  minima["SFb"]   = (999999,None) 
  minima["SFl"]   = (999999,None) 
  minima["top"]   = (999999,None) 
  minima["ttz"]   = (999999,None) 
  minima["dy"]    = (999999,None) 
  minima["ttx"]   = (999999,None) 
  minima["multi"] = (999999,None) 

  maxima["stat"]  = (0,None) 
  maxima["PU"]    = (0,None) 
  maxima["JEC"]   = (0,None) 
  maxima["topPt"] = (0,None) 
  maxima["SFb"]   = (0,None) 
  maxima["SFl"]   = (0,None) 
  maxima["top"]   = (0,None) 
  maxima["ttz"]   = (0,None) 
  maxima["dy"]    = (0,None) 
  maxima["ttx"]   = (0,None) 
  maxima["multi"] = (0,None)


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

        topErr        = None
        ttzErr        = None
        dyErr         = None
        multiBosonErr = None
        ttxErr        = None
	
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

          if e.name.count("TTJets"): topErr = 0.3 if SR < 6 else 0.2 if SR < 12 else 1
          if e.name.count("TTZ"):    ttzErr = 0.2
          if e.name.count("DY"):
	     mc = int(100*DYestimators[0].cachedEstimate(r, channel, setup).val+0.5)/100.
	     dd = int(100*DYestimators[1].cachedEstimate(r, channel, setup).val+0.5)/100.
             dyScale = dd/mc if mc > 0 else 0
             print "Scale of DY:" + str(dyScale)
          #   dyNorm  = ("%.2f" % abs(mc-dd))*(1/expected if args.relError else 1) if (abs(mc-dd) > 0 and expected > 0) else " - "
             dyErr    = 0.5
	  if e.name.count("multiBoson"): multiBosonErr = 0.25
          if e.name.count("TTXNoZ"):     ttxErr        = 0.25


	  f.write(" & %.2f" % expected)
	  f.write(" & " + displaySysValue(e.cachedEstimate(       r, channel, setup).sigma, expected))
	  f.write(" & " + displaySysValue(e.PUSystematic(         r, channel, setup).val,   expected))
	  f.write(" & " + displaySysValue(e.JECSystematic(        r, channel, setup).val,   expected))
  #	f.write(" & " + displaySysValue(e.JERSystematic(        r, channel, setup).val,   expected))
	  f.write(" & " + displaySysValue(e.topPtSystematic(      r, channel, setup).val,   expected))
	  f.write(" & " + displaySysValue(e.btaggingSFbSystematic(r, channel, setup).val,   expected))
	  f.write(" & " + displaySysValue(e.btaggingSFlSystematic(r, channel, setup).val,   expected))
	  f.write(" & " + (displaySysValue(topErr                                        ,   expected) if e.name.count("TTJets")     else " - "))
	  f.write(" & " + (displaySysValue(ttzErr                                        ,   expected) if e.name.count("TTZ")        else " - "))
	  f.write(" & " + (displaySysValue(dyErr                                         ,   expected) if e.name.count("DY")         else " - "))
	  f.write(" & " + (displaySysValue(ttxErr                                        ,   expected) if e.name.count("TTXNoZ")     else " - "))
          f.write(" & " + (displaySysValue(multiBosonErr                                 ,   expected) if e.name.count("multiBoson") else " - "))
	  f.write(" \\\\ \n")
 
          # Convert to absolute
          if e.name.count("TTJets"): topErr *= expected
          if e.name.count("TTZ"): ttzErr *= expected
          if e.name.count("DY"):  dyErr  *= expected
          if e.name.count("TTXNoZ"):  ttxErr *= expected
          if e.name.count("multiBoson"): multiBosonErr *= expected


	f.write("\\end{tabular} \n")
	f.write("\\caption{Yields and uncertainties for each background in the signal region $" + r.texString(useRootLatex = False) + "$ in channel " + channel + "} \n")

        e = summedEstimate
	overviewTable.write(" $" + str(SR) + "$ ")
	expected = int(100*e.cachedEstimate(r, channel, setup).val+0.5)/100.
	observed = observation.cachedObservation(r, channel, setup).val
	overviewTable.write(" & %d" % observed)
	overviewTable.write(" & %.2f" % expected)

        # Convert back to relative
	topErr = topErr/expected if expected > 0 else 0
	ttzErr = ttzErr/expected if expected > 0 else 0
	dyErr  = dyErr/expected if expected > 0 else 0
	ttxErr = ttxErr/expected if expected > 0 else 0
	multiBosonErr = multiBosonErr/expected if expected > 0 else 0


	overviewTable.write(" & " + displaySysValue(e.cachedEstimate(       r, channel, setup).sigma, expected))
	overviewTable.write(" & " + displaySysValue(e.PUSystematic(         r, channel, setup).val,   expected))
	overviewTable.write(" & " + displaySysValue(e.JECSystematic(        r, channel, setup).val,   expected))
#	overviewTable.write(" & " + displaySysValue(e.JERSystematic(        r, channel, setup).val,   expected))
	overviewTable.write(" & " + displaySysValue(e.topPtSystematic(      r, channel, setup).val,   expected))
	overviewTable.write(" & " + displaySysValue(e.btaggingSFbSystematic(r, channel, setup).val,   expected))
	overviewTable.write(" & " + displaySysValue(e.btaggingSFlSystematic(r, channel, setup).val,   expected))
	overviewTable.write(" & " + displaySysValue(topErr, expected))
	overviewTable.write(" & " + displaySysValue(ttzErr, expected))
	overviewTable.write(" & " + displaySysValue(dyErr, expected))
	overviewTable.write(" & " + displaySysValue(ttxErr, expected))
	overviewTable.write(" & " + displaySysValue(multiBosonErr, expected))
        overviewTable.write(" \\\\ \n")

        temp1 = minima["stat"]
        temp2 = maxima["stat"]

        minima["stat"]  = min((e.cachedEstimate(       r, channel, setup).sigma, expected), minima["stat"])
        minima["PU"]    = min((e.PUSystematic(         r, channel, setup).val,   expected), minima["PU"])
        minima["JEC"]   = min((e.JECSystematic(        r, channel, setup).val,   expected), minima["JEC"])
        minima["topPt"] = min((e.topPtSystematic(      r, channel, setup).val,   expected), minima["topPt"])
        minima["SFb"]   = min((e.btaggingSFbSystematic(r, channel, setup).val,   expected), minima["SFb"])
        minima["SFl"]   = min((e.btaggingSFlSystematic(r, channel, setup).val,   expected), minima["SFl"])
        minima["top"]   = min((topErr,                                           expected), minima["top"])
        minima["ttz"]   = min((ttzErr,                                           expected), minima["ttz"])
        minima["dy"]    = min((dyErr,                                            expected), minima["dy"])
        minima["ttx"]   = min((ttxErr,                                           expected), minima["ttx"])
        minima["multi"] = min((multiBosonErr,                                    expected), minima["multi"])

        maxima["stat"]  = max((e.cachedEstimate(       r, channel, setup).sigma, expected), maxima["stat"])
        maxima["PU"]    = max((e.PUSystematic(         r, channel, setup).val,   expected), maxima["PU"])
        maxima["JEC"]   = max((e.JECSystematic(        r, channel, setup).val,   expected), maxima["JEC"])
        maxima["topPt"] = max((e.topPtSystematic(      r, channel, setup).val,   expected), maxima["topPt"])
        maxima["SFb"]   = max((e.btaggingSFbSystematic(r, channel, setup).val,   expected), maxima["SFb"])
        maxima["SFl"]   = max((e.btaggingSFlSystematic(r, channel, setup).val,   expected), maxima["SFl"])
        maxima["top"]   = max((topErr,                                           expected), maxima["top"])
        maxima["ttz"]   = max((ttzErr,                                           expected), maxima["ttz"])
        maxima["dy"]    = max((dyErr,                                            expected), maxima["dy"])
        maxima["ttx"]   = max((ttxErr,                                           expected), maxima['ttx']) 
        maxima["multi"] = max((multiBosonErr,                                    expected), maxima["multi"])

    overviewTable.write("\\end{tabular} \n")
    overviewTable.write("\\caption{Yields and uncertainties for the total background in each of the signal regions for channel" + channel + "} \n")

    temp = args.relativeError
    args.relativeError = True # Following table always relative
    minmaxFile = os.path.join(texdir, channel, "minmax.tex")
    print "Writing to " + minmaxFile
    with open(minmaxFile, "w") as minmaxTable:
      minmaxTable.write("\\begin{tabular}{l|c} \n")
      minmaxTable.write("  systematic & min-max of signal regions \\\\ \n")
      minmaxTable.write("  \\hline \n")
      systematics = {"statistical"           : "stat",
                     "pile-up"               : "PU",
                     "JEC"                   : "JEC",
                     "top-\\pt"              : "topPt",
                     "b-tag SF-b"            : "SFb",
                     "b-tag SF-l"            : "SFl",
                     "top background"        : "ttz",
                     "ttZ background"        : "dy",
                     "ttXNoZ background"     : "ttx",
                     "top background"        : "top",
                     "DY background"         : "dy",
                     "multiboson background" : "multi"}
      for i,j in systematics.iteritems():
        if minima[j][0] > 0:  minmaxTable.write(i + " & " + displaySysValue(*minima[j]) + " - " + displaySysValue(*maxima[j]) + " \\\\ \n")
        else:                 minmaxTable.write(i + " & $<$ " + displaySysValue(*maxima[j]) + " \\\\ \n")
      minmaxTable.write("\\end{tabular} \n")
    args.relativeError = temp



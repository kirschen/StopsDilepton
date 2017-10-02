#!/usr/bin/env python
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--signal",        action='store',      default='T2tt', nargs='?', choices=["T2tt","TTbarDM","T8bbllnunu_XCha0p5_XSlep0p05", "T8bbllnunu_XCha0p5_XSlep0p5"], help="which signal to plot?")
argParser.add_argument("--relativeError", action='store_true', default=False,  help="show relative errors?")
args = argParser.parse_args()

from StopsDilepton.analysis.SetupHelpers    import allChannels, channels
from StopsDilepton.analysis.estimators      import setup, constructEstimatorList
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.SumEstimate     import SumEstimate
from StopsDilepton.analysis.regions         import regionsO as regions
from StopsDilepton.analysis.Cache           import Cache
from math import sqrt

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )

scale = 1.
if args.signal == "TTbarDM":
  setup.blinding = "(evt%15==0)"
  scale = 1./15.
#elif args.signal == "T2tt" or args.signal.count('T8'):
#  setup.blinding = "(run<=276811||(run>=277820&&run<=279931))"
#  scale = 17.3/36.4


estimators     = constructEstimatorList(["TTJets-DD","TTZ","DY", 'multiBoson', 'other'])
summedEstimate = SumEstimate(name="sum")
observation    = DataObservation(name='Data', sample=setup.sample['Data'])

for e in estimators + [summedEstimate, observation]:
    e.initCache(setup.defaultCacheDir())

texdir = os.path.join(setup.analysis_results, setup.prefix(), 'tables' + ("_rel" if args.relativeError else ""))

try:    os.makedirs(texdir)
except: pass

def displayRelSysValue(val):
     if val <=0: return "0" # \\%"
     return "%.0f" % (val*100+1) # + " \\%"   # Round to next percent

def displayAbsSysValue(val):
     roundedVal = int(100*val+0.99)/100.    # round to next 0.0x
     if roundedVal <= 0.: return "0.00"
     return "%.2f" % roundedVal

from StopsDilepton.analysis.infoFromCards import getPreFitUncFromCard, getPostFitUncFromCard

def getSampleUncertainty(cardFile, res, var, estimate, binName, i):
    if   estimate.name.count('TTZ'):    uncName = 'ttZ'
    elif estimate.name.count('TTJets'): uncName = 'top'
    else:                               uncName = estimate.name
    estimateName = estimate.name.split('-')[0]

    if var and var.count(estimateName):
      unc = getPreFitUncFromCard(cardFile,  estimateName, uncName, binName);

      if estimate.name.count("TTZ"):        unc = sqrt(0.2**2+0.15**2)
      if estimate.name.count("DY"):         unc = 0.19
      if estimate.name.count("multiBoson"): unc = 0.17
      if estimate.name.count("other"):      unc = 0.25
      if estimate.name.count('TTJets'):
        unc1 = (0.25 if i < 6 else 0.55)*0.15
        unc2 = (0.50 if i < 6 else 0.44)*0.30
        unc3 = (0.25 if i < 6 else 0.01)*0.50
        unc  = sqrt(unc1**2+unc2**2+unc3**2)

    return unc



cardFile = '/user/tomc/StopsDilepton/results_80X_v30/controlDYVV/cardFiles/T2tt/T2tt_750_1.txt'

# Evaluate absolute and relative errors
def evaluateEstimate(e, SR, binName, estimators=None):
     expected            = e.cachedEstimate(r, channel, setup).val*scale
     if e.name.count('DY'):         expected = expected*1.31
     if e.name.count('multiBoson'): expected = expected*1.19

     e.rel               = {}
     e.abs               = {}
     e.displayRel        = {}
     e.displayAbs        = {}
     e.displayYieldAbs   = {}

     e.abs["MC stat"]    = e.cachedEstimate(       r, channel, setup).sigma*scale
     if e.name.count('DY'):         e.abs["MC stat"] = e.abs["MC stat"]*1.31
     if e.name.count('multiBoson'): e.abs["MC stat"] = e.abs["MC stat"]*1.19
     e.rel["PU"]         = e.PUSystematic(         r, channel, setup).val
     e.rel["JEC"]        = e.JECSystematic(        r, channel, setup).val
     e.rel["unclEn"]     = e.unclusteredSystematic(r, channel, setup).val
     e.rel["JER"]        = e.JERSystematic(        r, channel, setup).val
     e.rel["top-\\pt"]   = e.topPtSystematic(      r, channel, setup).val
     e.rel["b-tag SF-b"] = e.btaggingSFbSystematic(r, channel, setup).val
     e.rel["b-tag SF-l"] = e.btaggingSFlSystematic(r, channel, setup).val
     e.rel["trigger"]    = e.triggerSystematic(    r, channel, setup).val
     e.rel["lepton SF"]  = e.leptonSFSystematic(   r, channel, setup).val
     e.rel["TTJets"]     = 0 if not e.name.count("TTJets")     else getSampleUncertainty(cardFile, expected, 'TTJets',     e, binName, SR)
     e.rel["TTZ"]        = 0 if not e.name.count("TTZ")        else getSampleUncertainty(cardFile, expected, 'TTZ',        e, binName, SR)
     e.rel["multiBoson"] = 0 if not e.name.count("multiBoson") else getSampleUncertainty(cardFile, expected, 'multiBoson', e, binName, SR)
     e.rel["other"]      = 0 if not e.name.count("other")      else getSampleUncertainty(cardFile, expected, 'other',      e, binName, SR)
     e.rel["DY"]         = 0 if not e.name.count("DY")         else getSampleUncertainty(cardFile, expected, 'DY',         e, binName, SR)

     # For sum assume the individual estimators are already evaluated such that we can pick their corresponding absolute error
     if e.name.count("sum"):
       for i in ['TTJets','DY','other','TTZ','multiBoson']:
         summedEstimate.abs[i]             = next(e for e in estimators if e.name.count(i)).abs[i]
         summedEstimate.displayYieldAbs[i] = next(e for e in estimators if e.name.count(i)).displayYieldAbs[i]

     for i in e.abs: e.rel[i] = e.abs[i]/expected if expected > 0 else 0
     for i in e.rel: e.abs[i] = e.rel[i]*expected
     for i in e.abs: e.displayRel[i] = displayRelSysValue(e.rel[i])
     for i in e.rel: e.displayAbs[i] = displayAbsSysValue(e.abs[i])

     e.expected = int(100*expected+0.5)/100.
     for i in e.displayAbs:
       if not e.name.count("sum"):
         e.displayYieldAbs[i] = str(e.expected) + " $\pm$ " + e.displayAbs[i]

def rotate(tex):
    return "\\rotatebox[origin=c]{50}{"+tex+"}"


# Make a separate table for each of regions
for channel in allChannels:
  try:    os.makedirs(os.path.join(texdir, channel))
  except: pass

  sysColumnsA = ["MC stat","PU","JEC","unclEn","top-\\pt","trigger","lepton SF","b-tag SF-b", "b-tag SF-l"]
 # sysColumnsA = ["MC stat","PU","JEC","unclEn","top-\\pt","trigger","lepton SF"]
  sysColumnsB = ["TTJets", "TTZ", "multiBoson", "other", "DY"]
  columns     = ["expected"] + sysColumnsA + sysColumnsB

  minima = {}
  maxima = {}
  for i in columns[1:]:
    minima[i]  = 9999
    maxima[i]  = 0


  overviewTexfile = os.path.join(texdir, channel, "overview.tex")
  print "Writing to " + overviewTexfile
  with open(overviewTexfile, "w") as overviewTable:
    overviewTable.write("\\begin{tabular}{l|cc|" + "c"*len(sysColumnsA) + "|" + "c"*len(sysColumnsB) + "} \n")
    overviewTable.write("  " + rotate("signal region") + " & " + rotate("observed") + " & " + "&".join([rotate(c) for c in columns]) + " \\\\ \n")
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
          binName = ' '.join(['SF' if channel not in ["SF","Emu"] else channel, r.__str__()])
          evaluateEstimate(e, SR, binName)
 
          f.write(" " + e.getTexName(channel, rootTex=False) + " ")
          f.write(" & %.2f" % e.expected)
          for i in columns[1:]:
            f.write(" & " + e.displayAbs[i])
          f.write(" \\\\ \n")

        f.write("\\end{tabular} \n")
        f.write("\\caption{Yields and uncertainties for each background in the signal region $" + r.texString(useRootLatex = False) + "$ in channel " + channel + "} \n")

        evaluateEstimate(summedEstimate, SR, binName, estimators)

        overviewTable.write(" $" + str(SR) + "$ ")
        overviewTable.write(" & %d" % observation.cachedObservation(r, channel, setup).val)
        overviewTable.write(" & %.2f" % summedEstimate.expected)

        for i in sysColumnsA:
          overviewTable.write(" & " + summedEstimate.displayAbs[i])
        for i in sysColumnsB:
          overviewTable.write(" & " + summedEstimate.displayYieldAbs[i])  # For those we display yield +- error
        overviewTable.write(" \\\\ \n")

        for i in columns[1:]:
          minima[i] = min(summedEstimate.rel[i], minima[i])
          maxima[i] = max(summedEstimate.rel[i], maxima[i])

    overviewTable.write("\\end{tabular} \n")

    minmaxFile = os.path.join(texdir, channel, "minmax.tex")
    print "Writing to " + minmaxFile
    with open(minmaxFile, "w") as minmaxTable:
      minmaxTable.write("\\begin{tabular}{l|c} \n")
      minmaxTable.write("  systematic & min-max of signal regions (\\%) \\\\ \n")
      minmaxTable.write("  \\hline \n")
      longNames = {"MC stat":     "MC statistics",
                   "PU":          "pile-up modelling",
                   "JEC":         "jet energy uncertainty",
                   "unclEn":      "modelling of unclustered energy",
                   "b-tag SF-l" : "b-tagging (light flavour)",
                   "b-tag SF-b" : "b-tagging (heavy flavour)",
                   "top-\\pt" :   "top-\\pt modelling",
                   "trigger" :    "trigger efficiency",
                   "TTJets":      "top background normalization",
                   "TTZ":         "$t\\bar{t}Z$ background normalization",
                   "other" :      "$t\\bar{t}X$ (excl. $t\\bar{t}Z$) background normalization",
                   "DY" :         "DY background normalization",
                   "multiBoson" : "multiboson background normalization"}

      for i in columns[1:]:
        name = longNames[i] if i in longNames else i
        minmaxTable.write(name + " & " + displayRelSysValue(minima[i]) + " - " + displayRelSysValue(maxima[i]) + " \\\\ \n")
        #if minima[i] > 0.0099:       minmaxTable.write(name + " & " + displayRelSysValue(minima[i]) + " - " + displayRelSysValue(maxima[i]) + " \\\\ \n")
        #elif minima[i] == maxima[i]: minmaxTable.write(name + " & " + displayRelSysValue(minima[i]) + " \\\\ \n")
        #else:                        minmaxTable.write(name + " & $<$ " + displayRelSysValue(maxima[i]) + " \\\\ \n")
      minmaxTable.write("\\end{tabular} \n")

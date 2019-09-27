#!/usr/bin/env python

""" 
Get a signal region plot from the cardfiles
"""

# Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)
import os
import sys
import pickle
import math

# Analysis
from Analysis.Tools.u_float           import u_float
from Analysis.Tools.getPostFit        import *
from Analysis.Tools.cardFileHelpers   import *

from StopsDilepton.tools.user            import plot_directory, analysis_results
from StopsDilepton.samples.color         import color

from RootTools.core.standard          import *

# Arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--small",                action="store_true",                            help="small?")
argParser.add_argument("--logLevel",             action="store",                default="INFO",  help="log level?", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"])
argParser.add_argument("--overwrite",            action="store_true",                            help="Overwrite existing output files, bool flag set to True  if used")
argParser.add_argument("--bkgOnly",              action="store_true",                            help="fix r to 0?")
argParser.add_argument("--preliminary",          action="store_true",                            help="Run expected?")
argParser.add_argument("--restrict",             action="store_true",                            help="Remove stat unc and r?")
argParser.add_argument("--year",                 action="store",                default='2016',    help="Which year?")
argParser.add_argument("--carddir",              action='store',                default='2016/limits/cardFiles/defaultSetup/observed',      help="which cardfile directory?")
argParser.add_argument("--cardfile",             action='store',                default='',      help="which cardfile?")
args = argParser.parse_args()

args.preliminary = True # fix label (change later)

# logger
import Analysis.Tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(    args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger( args.logLevel, logFile = None )

if args.year == '2016':   lumi_scale = 35.92
elif args.year == '2017': lumi_scale = 41.86
elif args.year == '2018': lumi_scale = 58.83
elif args.year =='COMBINED': lumi_scale = 138.4

cardFile = os.path.join( analysis_results, args.year, args.carddir, args.cardfile+".txt" )
logger.info("Plotting from cardfile %s"%cardFile)

# get the results
postFitResults = getFitObject( cardFile.replace(".txt","_shapeCard_FD.root") )

if args.bkgOnly:
    hist  = postFitResults["fit_b"].correlationHist()
    coeff = postFitResults["fit_b"].floatParsFinal()
else:
    hist  = postFitResults["fit_s"].correlationHist()
    coeff = postFitResults["fit_s"].floatParsFinal()

hist.LabelsOption("v","X")

coeffs = []
iter = coeff.createIterator()
var = iter.Next()
while var:
    coeffs.append(var.GetName())
    var = iter.Next()

for coeff in coeffs:
    print coeff

sysIndices = []
sysTitle = []

if args.restrict:
    allCoeffs = copy.copy(coeffs)
    for i, item in enumerate(coeffs):
        if not ("prop" in item or "Stat" in item):
            sysIndices.append(i+1)
            sysTitle.append(item)

    sysCorrelations = ROOT.TH2F("corr", "corr", len(sysIndices), 0, len(sysIndices), len(sysIndices), 0, len(sysIndices))
    for x,i in enumerate(sysIndices):
        sysCorrelations.GetXaxis().SetBinLabel(x+1, sysTitle[x])
        sysCorrelations.GetYaxis().SetBinLabel(len(sysIndices)-x, sysTitle[x])
        for y,j in enumerate(sysIndices):
            sysCorrelations.SetBinContent(x+1,len(sysIndices)-y,hist.GetBinContent(i,len(coeffs)-j+1))
    
    sysCorrelations.LabelsOption("v","X")
    hist = sysCorrelations


def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.03)
    tex.SetTextAlign(11) # align right
    addon = "bkg only" if args.bkgOnly else "float"
    if "incl" in args.cardfile: addon += ", inclusive"
    lines = [
      ( (0.2, 0.945, "CMS (%s)"%addon) if not args.preliminary else (0.2, 0.945, "CMS #bf{#it{Preliminary}} #bf{(%s)}"%addon)),
      (0.7 if len(coeffs)>25 else 0.7, 0.945, "#bf{%3.1f fb^{-1} (13 TeV)}"%lumi_scale )
    ]
    return [tex.DrawLatex(*l) for l in lines]

drawObjects = drawObjects( lumi_scale=lumi_scale )

plotName = "_".join( [ item for item in args.cardfile.split("_") if item not in ["addDYSF", "addMisIDSF", "misIDPOI"] ] )
add      = "_".join( [ item for item in args.cardfile.split("_") if item in ["addDYSF", "addMisIDSF", "misIDPOI"] ] )
if args.restrict: add += "_sysOnly"
fit      = "bkgOnly" if args.bkgOnly else "float"
if add: fit += "_"+add

for log in [False, True]:
    hist.GetZaxis().SetRangeUser(-1,1)
    plotting.draw2D(
        Plot2D.fromHisto(plotName,
            [[hist]],
            texX = "",
            texY = "",
        ),
        plot_directory = os.path.join(plot_directory, "corrNuisance", str(args.year), fit, "log" if log else "lin"),
        logX = False, logY = False, logZ = log, 
        widths = {"x_width":800 if len(coeffs)>25 else 800, "y_width":800 if len(coeffs)>25 else 800},
        zRange = (-1,1),
        drawObjects = drawObjects,
        histModifications = [lambda h: h.GetYaxis().SetLabelSize(12), lambda h: h.GetXaxis().SetLabelSize(12), lambda h: h.GetZaxis().SetLabelSize(0.03)],
        canvasModifications = [ lambda c : c.SetLeftMargin(0.2), lambda c: c.SetBottomMargin(0.2) ],
        copyIndexPHP = True,
    )


#!/usr/bin/env python
#Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)

from math import sqrt, cos, sin, pi, acos
import itertools

#RootTools
from RootTools.core.standard import *

from StopsDilepton.analysis.mcAnalysis import setup, bkgEstimators_detailed
from StopsDilepton.analysis.regions import defaultRegions, reducedRegionsA, reducedRegionsB, reducedRegionsAB
import StopsDilepton.tools.user as user
from StopsDilepton.samples.color import color

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate

from StopsDilepton.analysis.SetupHelpers import channels, allChannels

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store', default='INFO',           nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],      help="Log level for logging")
argParser.add_argument("--regions",        action='store', default='defaultRegions', nargs='?', choices=["defaultRegions","reducedRegionsA","reducedRegionsB","reducedRegionsAB"], help="which regions setup?")
argParser.add_argument('--plot_directory', action='store', default='png25ns_3rdLep')
args = argParser.parse_args()


if   args.regions == "defaultRegions":   regions = defaultRegions
elif args.regions == "reducedRegionsA":  regions = reducedRegionsA
elif args.regions == "reducedRegionsB":  regions = reducedRegionsB
elif args.regions == "reducedRegionsAB": regions = reducedRegionsAB
else: raise Exception("Unknown regions setup")

signalSetup = setup.sysClone(parameters={'useTriggers':False})

for estimator in bkgEstimators_detailed:
    estimator.style = styles.fillStyle( getattr( color, estimator.name ) )

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
signalEstimators = [ MCBasedEstimate(name=s.name,  sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in [T2tt_450_0] ]
for estimator in signalEstimators:
    estimator.style = styles.lineStyle( getattr( color, estimator.name ) )
 
estimators = bkgEstimators_detailed + signalEstimators
for e in estimators:
    e.initCache(setup.defaultCacheDir())


# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

def getRegionHisto(estimate, regions, channel, setup):

    h = ROOT.TH1F(estimate.name + channel, estimate.name, len(regions), 0, len(regions))
    h.legendText = estimate.name 
    for i, r in enumerate(regions):
        res = estimate.cachedEstimate(r, channel, setup, save=False)
        h.SetBinContent(i+1, res.val)
        h.SetBinError(i+1, res.sigma)
    h.style = estimate.style
    return h

def drawObjects( regions ):
    tex = ROOT.TLatex()
#    tex.SetNDC()
    tex.SetTextSize(0.015)
    tex.SetTextAngle(90)
    tex.SetTextAlign(12) # align right
#    lines = [(i+1-0.3, 10**4, r.texString()) for i, r in enumerate(regions)]
    lines =  [(i+1-0.3, 10**-6.5,  r.texStringForVar('dl_mt2ll'))   for i, r in enumerate(regions)]
    lines += [(i+1-0.3, 10**-5.5,  r.texStringForVar('dl_mt2blbl')) for i, r in enumerate(regions)]
    lines += [(i+1-0.3, 10**-4.5,  r.texStringForVar('dl_mt2bb'))   for i, r in enumerate(regions)]
    return [tex.DrawLatex(*l) for l in lines] 

for channel in allChannels:

    regions_ = regions[1:]
    # regions_ = filter(lambda r: r.vals['dl_mt2ll'][0]>0, regions)

    bkg_histos = [ getRegionHisto(e, regions=regions_, channel=channel, setup = setup) for e in bkgEstimators_detailed ]
    sig_histos = [ [getRegionHisto(e, regions=regions_, channel=channel, setup = signalSetup)] for e in signalEstimators ]

    region_plot = Plot.fromHisto(name = channel+"_bkgs", histos = [ bkg_histos ] + sig_histos, texX = "SR number", texY = "Events" )
    plotting.draw( region_plot, \
        plot_directory = os.path.join(user.plot_directory, args.regions), 
        logX = False, logY = True, 
        # sorting = True , 
        yRange = (10**-3, 10**4), 
        widths = {'x_width':1000, 'y_width':2000},
        drawObjects = drawObjects(regions_), 
        legend = (0.7,0.93-0.025*(len(bkg_histos) + len(sig_histos)), 0.95, 0.93),
        canvasModifications = [lambda c: c.SetWindowSize(c.GetWw(), int(c.GetWh()*1.5)), lambda c : c.GetPad(0).SetBottomMargin(0.33)] # Keep some space for the labels
    )

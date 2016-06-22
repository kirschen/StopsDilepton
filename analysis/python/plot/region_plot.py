#!/usr/bin/env python
#Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)

from math import sqrt, cos, sin, pi, acos
import itertools

#RootTools
from RootTools.core.standard import *

from StopsDilepton.analysis.estimators import setup, constructEstimatorList, MCBasedEstimate
from StopsDilepton.analysis.regions import defaultRegions, reducedRegionsA, reducedRegionsB, reducedRegionsAB, reducedRegionsNew
import StopsDilepton.tools.user as user
from StopsDilepton.samples.color import color

from StopsDilepton.analysis.SetupHelpers import channels, allChannels

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store', default='INFO',              nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],                          help="Log level for logging")
argParser.add_argument("--regions",        action='store', default='reducedRegionsNew', nargs='?', choices=["defaultRegions","reducedRegionsA","reducedRegionsB","reducedRegionsAB","reducedRegionsNew"], help="which regions setup?")
argParser.add_argument("--signal",         action='store', default='T2tt',              nargs='?', choices=["T2tt","DM"],                                                                                 help="which signal to plot?")
argParser.add_argument("--estimateDY",     action='store', default='DY',                nargs='?', choices=["DY","DY-DD"],                                                                                help="which DY estimate?")
argParser.add_argument("--estimateTTZ",    action='store', default='TTZ',               nargs='?', choices=["TTZ","TTZ-DD","TTZ-DD-Top16009"],                                                            help="which TTZ estimate?")
argParser.add_argument("--estimateTTJets", action='store', default='TTJets',            nargs='?', choices=["TTJets","TTJets-DD"],                                                                        help="which TTJets estimate?")
argParser.add_argument("--log",            action='store_true', default=False,          help="plot logarithmic y-axis?")
argParser.add_argument("--labels",         action='store_true', default=False,          help="plot labels?")
args = argParser.parse_args()


if   args.regions == "defaultRegions":    regions = defaultRegions
elif args.regions == "reducedRegionsA":   regions = reducedRegionsA
elif args.regions == "reducedRegionsB":   regions = reducedRegionsB
elif args.regions == "reducedRegionsAB":  regions = reducedRegionsAB
elif args.regions == "reducedRegionsNew": regions = reducedRegionsNew
else: raise Exception("Unknown regions setup")

detailedEstimators = constructEstimatorList([args.estimateTTJets,'other-detailed', args.estimateDY, args.estimateTTZ])
signalSetup = setup.sysClone(parameters={'useTriggers':False})

for estimator in detailedEstimators:
    estimatorColor = getattr( color, estimator.name.split('-')[0] ) 
    estimator.style = styles.fillStyle(estimatorColor, lineColor = estimatorColor )

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
signalEstimators = [ MCBasedEstimate(name=s.name,  sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in ([T2tt_450_0] if args.signal == "T2tt" else [TTbarDMJets_scalar_Mchi1_Mphi100])]
for estimator in signalEstimators:
    estimator.style = styles.lineStyle( getattr(color, estimator.name ), width=2 )
 
estimators = detailedEstimators + signalEstimators
for e in estimators:
    e.initCache(setup.defaultCacheDir())


# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

def getRegionHisto(estimate, regions, channel, setup):

    h = ROOT.TH1F(estimate.name + channel, estimate.name, len(regions), 0, len(regions))
    try:
      h.legendText = estimate.sample[channel].texName
    except:
      try:
	texNames = [estimate.sample[c].texName for c in ['MuMu','EMu','EE']]		# If all, only take texName if it is the same for all channels
	if texNames.count(texNames[0]) == len(texNames):
	  h.legendText = texNames[0]
	else:
	  h.legendText = estimate.name
      except:
	h.legendText = estimate.name
    for i, r in enumerate(regions):
        res = estimate.cachedEstimate(r, channel, setup, save=False)
        h.SetBinContent(i+1, res.val)
        h.SetBinError(i+1, res.sigma)
    h.style = estimate.style
    return h

def drawObjects( regions ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.015)
    tex.SetTextAngle(90)
    tex.SetTextAlign(12) # align right
    min = 0.15
    max = 0.95
    diff = (max-min) / len(regions)
    lines =  [(min+(i+0.5)*diff, 0.005,  r.texStringForVar('dl_mt2ll'))   for i, r in enumerate(regions)]
    lines += [(min+(i+0.5)*diff, 0.145,  r.texStringForVar('dl_mt2blbl')) for i, r in enumerate(regions)]
    lines += [(min+(i+0.5)*diff, 0.285,  r.texStringForVar('dl_mt2bb'))   for i, r in enumerate(regions)]
    return [tex.DrawLatex(*l) for l in lines] 

for channel in allChannels:

    regions_ = regions[1:]

    bkg_histos = [  getRegionHisto(e, regions=regions_, channel=channel, setup = setup) for e in detailedEstimators ]
    sig_histos = [ [getRegionHisto(e, regions=regions_, channel=channel, setup = signalSetup)] for e in signalEstimators ]

    region_plot = Plot.fromHisto(name = channel+"_bkgs", histos = [ bkg_histos ] + sig_histos, texX = "SR number", texY = "Events" )
    plotting.draw( region_plot, \
        plot_directory = os.path.join(user.plot_directory, args.regions, args.estimateDY, args.estimateTTZ, args.estimateTTJets),
        logX = False, logY = args.log, 
        sorting = True,
        yRange = (10**-2.4, "auto"),
        widths = {'x_width':500, 'y_width':600},
        drawObjects = drawObjects(regions_) if args.labels else [], 
        legend = (0.7,0.93-0.02*(len(bkg_histos) + len(sig_histos)), 0.95, 0.93),
        canvasModifications = [lambda c: c.SetWindowSize(c.GetWw(), int(c.GetWh()*2)), lambda c : c.GetPad(0).SetBottomMargin(0.5)] if args.labels else []# Keep some space for the labels
    )

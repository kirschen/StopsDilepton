#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools

#RootTools
from RootTools.core.standard import *

from StopsDilepton.analysis.mcAnalysis import setup, regions, bkgEstimators_detailed
import StopsDilepton.tools.user as user
from StopsDilepton.samples.color import color
#from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_2l_postProcessed import *

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate

from StopsDilepton.analysis.SetupHelpers import channels, allChannels

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='INFO',
      help="Log level for logging"
)

argParser.add_argument('--plot_directory',
    default='png25ns_3rdLep',
    action='store',
)

setup.analysis_results='/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test6_noPU'
signalSetup = setup.sysClone(parameters={'useTriggers':False})

for estimator in bkgEstimators_detailed:
    estimator.style = styles.fillStyle( getattr( color, estimator.name ) )

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_2l_postProcessed import *
signalEstimators = [ MCBasedEstimate(name=s.name,    sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in [T2tt_450_0] ]
for estimator in signalEstimators:
    estimator.style = styles.lineStyle( getattr( color, estimator.name ) )
 
estimators = bkgEstimators_detailed + signalEstimators
for e in estimators:
    e.initCache(setup.defaultCacheDir())

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

def getRegionHisto(estimate, regions, channel, setup):

    h = ROOT.TH1F(estimate.name, estimate.name, len(regions), 0, len(regions))
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
    tex.SetTextSize(0.02)
    tex.SetTextAngle(90)
    tex.SetTextAlign(11) # align right
    lines = [(i+1-0.3, 10**4, r.texString()) for i, r in enumerate(regions)]
    return [tex.DrawLatex(*l) for l in lines] 

for channel in allChannels:

    regions_ = regions
    # regions_ = filter(lambda r: r.vals['dl_mt2ll'][0]>0, regions)

    bkg_histos = [ getRegionHisto(e, regions=regions_, channel=channel, setup = setup) for e in bkgEstimators_detailed ]
    sig_histos = [ [getRegionHisto(e, regions=regions_, channel=channel, setup = signalSetup)] for e in signalEstimators ]

    region_plot = Plot.fromHisto(name = channel+"_bkgs", histos = [ bkg_histos ] + sig_histos, texX = "SR number", texY = "Events" )
    plotting.draw( region_plot, \
        plot_directory = user.plot_directory+'/etc/', 
        logX = False, logY = True, 
        # sorting = True , 
        yRange = (10**-3, 10**12), 
        widths = {'x_width':1000, 'y_width':2000},
        drawObjects = drawObjects(regions_), 
        legend = (0.7,0.93-0.025*(len(bkg_histos) + len(sig_histos)), 0.95, 0.93)
    )

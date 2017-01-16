#!/usr/bin/env python
#Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)

from math import sqrt, cos, sin, pi, acos
import itertools
import os

#RootTools
from RootTools.core.standard import *

from StopsDilepton.analysis.estimators import setup, constructEstimatorList, MCBasedEstimate
from StopsDilepton.analysis.regions import regionsO as regions
import StopsDilepton.tools.user as user
from StopsDilepton.samples.color import color

from StopsDilepton.analysis.SetupHelpers import channels, allChannels

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store', default='INFO',              nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],                          help="Log level for logging")
argParser.add_argument('--sample',         action='store', default='DY',                nargs='?', choices=['DY','multiBoson'],                                                                           help="Which sample?")
argParser.add_argument("--labels",         action='store_true', default=False,          help="plot labels?")
argParser.add_argument("--noData",         action='store_true', default=False,          help="do not plot data?")
args = argParser.parse_args()

setup = setup.sysClone(parameters={'nBTags':(0,0 ), 'dPhi': False, 'dPhiInv': False, 'zWindow': 'onZ'})

preEstimate        = MCBasedEstimate(name=args.sample, sample=setup.sample[args.sample])
estimatorColor     = getattr( color, preEstimate.name.split('-')[0].split('_')[0] ) 
preEstimate.style = styles.fillStyle(estimatorColor, lineColor = estimatorColor )

postEstimate       = MCBasedEstimate(name=args.sample, sample=setup.sample[args.sample])
postEstimate.style = styles.errorStyle( ROOT.kBlack, markerSize = 1.5 )

for e in [preEstimate, postEstimate]:
    e.initCache(setup.defaultCacheDir())

from RootTools.core.standard import *

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )


from StopsDilepton.analysis.infoFromCards import getUncFromCard, applyNuisance
cardFile = '/user/tomc/StopsDilepton/results_80X_v24/isOS-nJets2p-nbtag0-met80-metSig5-mll20-looseLeptonVeto-relIso0.12/DY/TTZ/TTJets/multiBoson/cardFiles/TTbarDM/regionsO/TTbarDMJets_pseudoscalar_Mchi_50_Mphi_200.txt'

def getRegionHisto(estimate, regions, channel, setup):
    h = ROOT.TH1F(estimate.name + channel, estimate.name, len(regions), 0, len(regions))

    # Legend text
    h.legendText = estimate.getTexName(channel) + (' (pre-fit)' if estimate == preEstimate else ' (post-fit)')

    for i, r in enumerate(regions):
        res = estimate.cachedEstimate(r, channel, setup, save=True)
        if estimate == postEstimate: res = applyNuisance(cardFile, estimate, res, i)
        h.SetBinContent(i+1, res.val)
        h.SetBinError(i+1, res.sigma)

    h.style = estimate.style
    h.GetXaxis().SetLabelOffset(99)
    h.GetXaxis().SetTitleOffset(1.5)
    h.GetXaxis().SetTitleSize(2)
    h.GetYaxis().SetTitleSize(2)
    h.GetYaxis().SetLabelSize(0.7)

    return h

def drawLabels( regions ):
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

def drawSR( regions ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(23) # align right
    min = 0.15
    max = 0.95
    diff = (max-min) / len(regions)
    lines = [(min+(i+0.5)*diff, .12,  str(i)) for i, r in enumerate(regions)]

    tex2 = tex.Clone()
    tex2.SetTextSize(0.03)
    tex2.SetTextColor(38)

    lines2  = [(min+3*diff,  .9, '100 GeV < M_{T2}(ll) < 140 GeV')]
    lines2 += [(min+9*diff, .9, '140 GeV < M_{T2}(ll) < 240 GeV')]

    tex3= tex2.Clone()
    tex3.SetTextAngle(90)
    tex3.SetTextAlign(31)
    lines3  = [(min+12.5*diff, .9, 'M_{T2}(ll) > 240 GeV')]

    line = ROOT.TLine()
    line.SetLineColor(38)
    line.SetLineWidth(2)
    line.SetLineStyle(3)
    line1 = (min+6*diff,  0.13, min+6*diff, 0.93);
    line2 = (min+12*diff, 0.13, min+12*diff, 0.93);
    return [tex.DrawLatex(*l) for l in lines] + [line.DrawLineNDC(*l) for l in [line1, line2]] + [tex2.DrawLatex(*l) for l in lines2] + [tex3.DrawLatex(*l) for l in lines3]


def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'),
      (0.71, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % (lumi_scale/1000.))
    ]
    return [tex.DrawLatex(*l) for l in lines]

for channel in ['all','SF','EE','EMu','MuMu']:

    regions_ = regions[1:]

    preHisto  = getRegionHisto(preEstimate, regions=regions_, channel=channel, setup = setup)
    postHisto = getRegionHisto(postEstimate, regions=regions_, channel=channel, setup = setup)

    region_plot = Plot.fromHisto(name = channel, histos = [ [preHisto], [postHisto] ], texX = "signal region number", texY = "Events" )

    plotting.draw( region_plot, \
        plot_directory = os.path.join(user.plot_directory, 'regionsO', 'preAndPostFit', args.sample),
        logX = False, logY = True,
        sorting = False,
        ratio = {'yRange':(0.1,1.9)},
        extensions = ["pdf", "png", "root","C"],
        yRange = (0.006, 2000000),
        widths = {'x_width':1000, 'y_width':700},
        drawObjects = (drawLabels(regions_) if args.labels else drawSR(regions_)) + drawObjects( setup.dataLumi[channel] if channel in ['EE','MuMu','EMu'] else setup.dataLumi['EE'] ),
        legend = (0.55,0.5, 0.9, 0.85),
        canvasModifications = [lambda c: c.SetWindowSize(c.GetWw(), int(c.GetWh()*2)), lambda c : c.GetPad(0).SetBottomMargin(0.5)] if args.labels else []# Keep some space for th labels
    )

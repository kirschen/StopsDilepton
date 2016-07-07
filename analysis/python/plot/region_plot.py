#!/usr/bin/env python
#Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)

from math import sqrt, cos, sin, pi, acos
import itertools

#RootTools
from RootTools.core.standard import *

from StopsDilepton.analysis.estimators import setup, constructEstimatorList, MCBasedEstimate
from StopsDilepton.analysis.regions import regions80X, reducedRegionsNew
import StopsDilepton.tools.user as user
from StopsDilepton.samples.color import color

from StopsDilepton.analysis.SetupHelpers import channels, allChannels

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store', default='INFO',              nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],                          help="Log level for logging")
argParser.add_argument("--regions",        action='store', default='regions80X',        nargs='?', choices=["reducedRegionsNew", "regions80X"],                                                           help="which regions setup?")
argParser.add_argument("--signal",         action='store', default='T2tt',              nargs='?', choices=["T2tt","DM"],                                                                                 help="which signal to plot?")
argParser.add_argument("--estimateDY",     action='store', default='DY',                nargs='?', choices=["DY","DY-DD"],                                                                                help="which DY estimate?")
argParser.add_argument("--estimateTTZ",    action='store', default='TTZ',               nargs='?', choices=["TTZ","TTZ-DD","TTZ-DD-Top16009"],                                                            help="which TTZ estimate?")
argParser.add_argument("--estimateTTJets", action='store', default='TTJets',            nargs='?', choices=["TTJets","TTJets-DD"],                                                                        help="which TTJets estimate?")
argParser.add_argument("--labels",         action='store_true', default=False,          help="plot labels?")
args = argParser.parse_args()


if   args.regions == "reducedRegionsNew": regions = reducedRegionsNew
elif args.regions == "regions80X":        regions = regions80X
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
    estimator.applyFilterCut=False
 
estimators = detailedEstimators + signalEstimators
for e in estimators:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.analysis.DataObservation import DataObservation
from RootTools.core.standard import *
observation = DataObservation(name='Data', sample=setup.sample['Data'])
observation.style = styles.errorStyle( ROOT.kBlack )

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

systematics = { 'JEC' :      ['JECVUp', 'JECVDown'],
       #         'JER' :      ['JERUp', 'JERDown'],
                'PU' :       ['reweightPUUp', 'reweightPUDown'],
                'stat' :     ['statLow', 'statHigh'],
                'topPt' :    ['reweightTopPt', None],
       #         'b-tag-b' :  ['reweightBTag_SF_b_Up','reweightBTag_SF_b_Down'],
       #         'b-tag-l' :  ['reweightBTag_SF_l_Up','reweightBTag_SF_l_Down'] 
}

sysVariations = [None]
for var in systematics.values():
  sysVariations += var

def getRegionHisto(estimate, regions, channel, setup, variations = [None]):

    h = {}
    for var in variations:
      h[var] = ROOT.TH1F(estimate.name + channel + (var if var else ""), estimate.name, len(regions), 0, len(regions))


    # Legend text
    try:
      h[None].legendText = estimate.sample[channel].texName
    except:
      try:
	texNames = [estimate.sample[c].texName for c in ['MuMu','EMu','EE']]		# If all, only take texName if it is the same for all channels
	if texNames.count(texNames[0]) == len(texNames):
	  h[None].legendText = texNames[0]
	else:
	  h[None].legendText = estimate.name
      except:
	h[None].legendText = estimate.name

    for i, r in enumerate(regions):
      for var in variations:
        if var == 'statLow' or var == 'statHigh': continue
        setup_ = setup if not var else setup.sysClone({'selectionModifier': var}) if var.count('JE') else setup.sysClone({'reweight':[var]})
        res = estimate.cachedEstimate(r, channel, setup_, save=True)
        h[var].SetBinContent(i+1, res.val)
        h[var].SetBinError(i+1, res.sigma)
        if not var and ('statLow' in variations or 'statHigh' in variations):
          h['statLow'].SetBinContent(i+1,  res.val-res.sigma)
          h['statHigh'].SetBinContent(i+1, res.val+res.sigma)

    h[None].style = estimate.style

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

def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'),
      (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV)'% ( int(lumi_scale*100)/100.) )
    ]
    return [tex.DrawLatex(*l) for l in lines]

for channel in ['all']:

    regions_ = regions[1:]

    bkg_histos = {}
    for e in detailedEstimators:
      histos = getRegionHisto(e, regions=regions_, channel=channel, setup = setup, variations = sysVariations)
      for k in set(sysVariations):
        if k in bkg_histos: bkg_histos[k].append(histos[k])
        else:               bkg_histos[k] = [histos[k]]

    # Get summed histos for the systematics
    histos_summed = {k: bkg_histos[k][0].Clone() for k in set(sysVariations)}
    for k in set(sysVariations):
      for i in range(1, len(bkg_histos[k])):
        histos_summed[k].Add(bkg_histos[k][i])

    # Get up-down for each of the systematics
    h_sys = {}
    for sys, vars in systematics.iteritems():
        h_sys[sys] = histos_summed[vars[0]].Clone()
        h_sys[sys].Scale(-1)
        h_sys[sys].Add(histos_summed[vars[1] if len(vars) > 1 else None])

    h_rel_err = histos_summed[None].Clone()
    h_rel_err.Reset()

    # Adding the systematics in quadrature
    for k in h_sys.keys():
        for ib in range( 1 + h_rel_err.GetNbinsX() ):
            h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + h_sys[k].GetBinContent(ib)**2 )

    for ib in range( 1 + h_rel_err.GetNbinsX() ):
        h_rel_err.SetBinContent(ib, sqrt( h_rel_err.GetBinContent(ib) ) )

    # Divide by the summed hist to get relative errors
    h_rel_err.Divide(histos_summed[None])


    # For signal histos we don't need the systematics, so only access the "None"
    sig_histos = [ [getRegionHisto(e, regions=regions_, channel=channel, setup = signalSetup)[None]] for e in signalEstimators ]

    data_histo = [ [getRegionHisto(observation, regions=regions_, channel=channel, setup=setup)[None]]]
 
    region_plot = Plot.fromHisto(name = channel+"_bkgs", histos = [ bkg_histos[None] ] + sig_histos + data_histo, texX = "signal region number", texY = "Events" )

    boxes = []
    ratio_boxes = []
    for ib in range(1, 1 + h_rel_err.GetNbinsX() ):
        val = histos_summed[None].GetBinContent(ib)
        if val<0: continue
        sys = h_rel_err.GetBinContent(ib)
        box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max([0.0015, (1-sys)*val]), h_rel_err.GetXaxis().GetBinUpEdge(ib), max([0.0015, (1+sys)*val]) )
        box.SetLineColor(ROOT.kBlack)
        box.SetFillStyle(3444)
        box.SetFillColor(ROOT.kBlack)
        r_box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max(0.1, 1-sys), h_rel_err.GetXaxis().GetBinUpEdge(ib), min(1.9, 1+sys) )
        r_box.SetLineColor(ROOT.kBlack)
        r_box.SetFillStyle(3444)
        r_box.SetFillColor(ROOT.kBlack)

        boxes.append( box )
   #     ratio_boxes.append( r_box )



    plotting.draw( region_plot, \
        plot_directory = os.path.join(user.plot_directory, args.regions, args.estimateDY, args.estimateTTZ, args.estimateTTJets),
        logX = False, logY = True,
        sorting = True,
        yRange = (0.0015, "auto"),
        widths = {'x_width':1000, 'y_width':700},
        drawObjects = (drawLabels(regions_) if args.labels else []) + boxes + drawObjects( 3.997 ),
        legend = (0.6,0.9-0.02*(len(bkg_histos) + len(sig_histos)), 0.95, 0.9),
        canvasModifications = [lambda c: c.SetWindowSize(c.GetWw(), int(c.GetWh()*2)), lambda c : c.GetPad(0).SetBottomMargin(0.5)] if args.labels else []# Keep some space for the labels
    )

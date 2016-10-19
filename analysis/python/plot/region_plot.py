#!/usr/bin/env python
#Standard imports
import ROOT
ROOT.gROOT.SetBatch(True)

from math import sqrt, cos, sin, pi, acos
import itertools

#RootTools
from RootTools.core.standard import *

from StopsDilepton.analysis.estimators import setup, constructEstimatorList, MCBasedEstimate
from StopsDilepton.analysis.regions import regions80X as regions
import StopsDilepton.tools.user as user
from StopsDilepton.samples.color import color

from StopsDilepton.analysis.SetupHelpers import channels, allChannels

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store', default='INFO',              nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],                          help="Log level for logging")
argParser.add_argument("--signal",         action='store', default='T2tt',              nargs='?', choices=["T2tt","TTbarDM"],                                                                                 help="which signal to plot?")
argParser.add_argument("--estimateDY",     action='store', default='DY-DD',             nargs='?', choices=["DY","DY-DD"],                                                                                help="which DY estimate?")
argParser.add_argument("--estimateTTZ",    action='store', default='TTZ-DD-Top16009',   nargs='?', choices=["TTZ","TTZ-DD","TTZ-DD-Top16009"],                                                            help="which TTZ estimate?")
argParser.add_argument("--estimateTTJets", action='store', default='TTJets-DD',         nargs='?', choices=["TTJets","TTJets-DD"],                                                                        help="which TTJets estimate?")
argParser.add_argument("--estimateMB",     action='store', default='multiBoson-DD',     nargs='?', choices=["multiBoson","multiBoson-DD"],                                                                help="which multiBoson estimate?")
argParser.add_argument("--labels",         action='store_true', default=False,          help="plot labels?")
args = argParser.parse_args()

detailedEstimators = constructEstimatorList([args.estimateTTJets,  args.estimateDY, args.estimateTTZ, args.estimateMB, 'TTXNoZ'])
if args.signal=='T2tt':
    signalSetup = setup.sysClone(sys = {'reweight':['reweightLeptonFastSimSF']})
else:
    signalSetup = setup

for estimator in detailedEstimators:
    estimatorColor = getattr( color, estimator.name.split('-')[0] ) 
    estimator.style = styles.fillStyle(estimatorColor, lineColor = estimatorColor )

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *


if args.signal == "T2tt":
    signals = [T2tt_650_1, T2tt_450_1]
    postfix = "regions_80X"
elif args.signal == "TTbarDM":
    #postfix = "regions_80X_scalar"
    #signals = [TTbarDMJets_scalar_Mchi_1_Mphi_10, TTbarDMJets_scalar_Mchi_1_Mphi_20, TTbarDMJets_scalar_Mchi_1_Mphi_50]
    postfix = "regions_80X_pseudoscalar"
    signals = [TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10, TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20, TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50]

signalEstimators = [ MCBasedEstimate(name=s.name,  sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in signals]

for i, estimator in enumerate(signalEstimators):
    estimator.style = styles.lineStyle( ROOT.kBlack, width=2, dotted=(i==1), dashed=(i==2), errors = True)
    estimator.isSignal=True
 
estimators = detailedEstimators + signalEstimators
for e in estimators:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.analysis.DataObservation import DataObservation
from RootTools.core.standard import *
observation = DataObservation(name='Data', sample=setup.sample['Data'])
observation.style = styles.errorStyle( ROOT.kBlack, markerSize = 1.5 )

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

systematics = { 'JEC' :      ['JECUp', 'JECDown'],
       #         'JER' :      ['JERUp', 'JERDown'],
                'PU' :       ['reweightPU12fbUp', 'reweightPU12fbDown'],
                'stat' :     ['statLow', 'statHigh'],
                'topPt' :    ['reweightTopPt', None],
                'b-tag-b' :  ['reweightBTag_SF_b_Up','reweightBTag_SF_b_Down'],
                'b-tag-l' :  ['reweightBTag_SF_l_Up','reweightBTag_SF_l_Down'],
                'trigger' :  ['reweightDilepTriggerBackupUp', 'reweightDilepTriggerBackupDown'],
                'leptonSF' : ['reweightLeptonSFUp','reweightLeptonSFDown'],
                'TTJets' :   ['shape-TTJetsUp', 'shape-TTJetsDown'],
                'TTZ' :      ['shape-TTZUp', 'shape-TTZDown'],
                'TTX' :      ['shape-TTXUp', 'shape-TTXDown'],
                'MB' :       ['shape-MBUp', 'shape-MBDown'],
                'DY' :       ['shape-DYUp', 'shape-DYDown'],
}

sysVariations = [None]
for var in systematics.values():
  sysVariations += var


def getRegionHisto(estimate, regions, channel, setup, variations = [None]):

    h = {}
    for var in variations:
      h[var] = ROOT.TH1F(estimate.name + channel + (var if var else ""), estimate.name, len(regions), 0, len(regions))


    # Legend text
    if estimate.name == "Data":
      if channel == "all":  h[None].legendText = "Data"
      if channel == "EE":   h[None].legendText = "Data (2e)"
      if channel == "MuMu": h[None].legendText = "Data (2#mu)"
      if channel == "EMu":  h[None].legendText = "Data (1e, 1#mu)"
      if channel == "SF":   h[None].legendText = "Data (SF)"
    else:
      h[None].legendText = estimate.getTexName(channel)

    for i, r in enumerate(regions):
      for var in variations:
        if var in ['statLow', 'statHigh']: continue

        setup_ = setup if not var or var.count('shape') else setup.sysClone({'selectionModifier': var}) if var.count('JE') else setup.sysClone({'reweight':[var]})
        res = estimate.cachedEstimate(r, channel, setup_, save=True)
        if var and var.count('TTJetsUp') and estimate.name.count('TTJets'):   res *= 1.5
        if var and var.count('TTJetsDown') and estimate.name.count('TTJets'): res *= 0.5
        if var and var.count('TTZUp') and estimate.name.count('TTZ'):         res *= 1.2
        if var and var.count('TTZDown') and estimate.name.count('TTZ'):       res *= 0.8
        if var and var.count('TTXUp') and estimate.name.count('TTX'):         res *= 1.25
        if var and var.count('TTXDown') and estimate.name.count('TTX'):       res *= 0.75
        if var and var.count('MBUp') and estimate.name.count('multiBoson'):   res *= 1.25
        if var and var.count('MBDown') and estimate.name.count('multiBoson'): res *= 0.75
        if var and var.count('DYUp') and estimate.name.count('DYBoson'):      res *= 1.25
        if var and var.count('DYDown') and estimate.name.count('DYBoson'):    res *= 0.75
        h[var].SetBinContent(i+1, res.val)
        h[var].SetBinError(i+1, res.sigma)

        if not var and ('statLow' in variations or 'statHigh' in variations):
          h['statLow'].SetBinContent(i+1,  res.val-res.sigma)
          h['statHigh'].SetBinContent(i+1, res.val+res.sigma)

    h[None].style = estimate.style
    h[None].GetXaxis().SetLabelOffset(99)
    h[None].GetXaxis().SetTitleOffset(1.5)
    h[None].GetXaxis().SetTitleSize(2)
    h[None].GetYaxis().SetTitleSize(2)
    h[None].GetYaxis().SetLabelSize(0.7)
 
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
    tex2.SetTextColor(12)

    lines2  = [(min+3*diff,  .9, '100 GeV < M_{T2}(ll) < 140 GeV')]
    lines2 += [(min+9*diff, .9, '140 GeV < M_{T2}(ll) < 240 GeV')]

    tex3= tex2.Clone()
    tex3.SetTextAngle(90)
    tex3.SetTextAlign(31)
    lines3  = [(min+12.5*diff, .9, 'M_{T2}(ll) > 240 GeV')]

    line = ROOT.TLine()
    line.SetLineColor(12)
    line.SetLineWidth(2)
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
      (0.71, 0.95, 'L=12.9 fb{}^{-1} (13 TeV)')
    ]
    return [tex.DrawLatex(*l) for l in lines]

for channel in ['all','SF','EE','EMu','MuMu']:

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
            h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + (h_sys[k].GetBinContent(ib)/2)**2 )

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
        box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max([0.006, (1-sys)*val]), h_rel_err.GetXaxis().GetBinUpEdge(ib), max([0.06, (1+sys)*val]) )
        box.SetLineColor(ROOT.kBlack)
        box.SetFillStyle(3444)
        box.SetFillColor(ROOT.kBlack)
        r_box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max(0.1, 1-sys), h_rel_err.GetXaxis().GetBinUpEdge(ib), min(1.9, 1+sys) )
        r_box.SetLineColor(ROOT.kBlack)
        r_box.SetFillStyle(3444)
        r_box.SetFillColor(ROOT.kBlack)

        boxes.append( box )
   #     ratio_boxes.append( r_box )


    if args.signal == "T2tt":
        legend = (0.55,0.85-0.013*(len(bkg_histos) + len(sig_histos)), 0.9, 0.85)
    elif args.signal == "TTbarDM":
        legend = (0.55,0.85-0.010*(len(bkg_histos) + len(sig_histos)), 0.9, 0.85)
    plotting.draw( region_plot, \
        plot_directory = os.path.join(user.plot_directory, postfix, args.estimateDY, args.estimateTTZ, args.estimateTTJets, args.estimateMB),
        logX = False, logY = True,
        sorting = True,
        yRange = (0.006, "auto"),
        widths = {'x_width':1000, 'y_width':700},
        drawObjects = (drawLabels(regions_) if args.labels else drawSR(regions_)) + boxes + drawObjects( setup.dataLumi[channel] if channel in ['EE','MuMu','EMu'] else setup.dataLumi['EE'] ),
        legend = legend,
        canvasModifications = [lambda c: c.SetWindowSize(c.GetWw(), int(c.GetWh()*2)), lambda c : c.GetPad(0).SetBottomMargin(0.5)] if args.labels else []# Keep some space for the labels
    )

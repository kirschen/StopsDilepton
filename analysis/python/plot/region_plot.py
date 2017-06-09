#!/usr/bin/env python
#Standard imports
import ROOT, os
ROOT.gROOT.SetBatch(True)

from math                                   import sqrt
from RootTools.core.standard                import *
from StopsDilepton.analysis.estimators      import setup, constructEstimatorList, MCBasedEstimate
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.regions         import regionsO as regions
from StopsDilepton.analysis.regions         import noRegions
from StopsDilepton.tools.user               import plot_directory
from StopsDilepton.samples.color            import color
from StopsDilepton.analysis.SetupHelpers    import channels, allChannels, trilepChannels

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', action='store',      default='INFO', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument("--signal",   action='store',      default='T2tt', nargs='?', choices=["T2tt","TTbarDM","T8"],                                              help="Which signal to plot?")
argParser.add_argument("--control",  action='store',      default=None,   nargs='?', choices=[None, "DY", "VV", "DYVV","TTZ"],                                     help="For CR region?")
argParser.add_argument("--scale",    action='store_true', default=False,  help="Scale CR using pulls from nuisance table?")
argParser.add_argument("--splitTop", action='store_true', default=False,  help="Split top in gaussian, non-gaussian and fake contribution")
argParser.add_argument("--labels",   action='store_true', default=False,  help="Plot labels?")
argParser.add_argument("--ratio",    action='store_true', default=True,   help="Plot ratio?")
argParser.add_argument("--blinded",  action='store_true', default=False,  help="Blind for DM?")
argParser.add_argument("--noData",   action='store_true', default=False,  help="Do not plot data?")
args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
import RootTools.core.logger      as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None )
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

channels = ['all','SF','EE','EMu','MuMu']

# alternative setups for control region
if args.control:
  if   args.control == "DY":   setup = setup.sysClone(parameters={'nBTags':(0,0 ), 'dPhi': False, 'dPhiInv': True,  'zWindow': 'onZ'}) 
  elif args.control == "VV":   setup = setup.sysClone(parameters={'nBTags':(0,0 ), 'dPhi': True,  'dPhiInv': False, 'zWindow': 'onZ'})
  elif args.control == "DYVV": setup = setup.sysClone(parameters={'nBTags':(0,0 ), 'dPhi': False, 'dPhiInv': False, 'zWindow': 'onZ'})
  elif args.control == "TTZ":
    setups   = [setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(2,2),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False}),
                setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False}),
                setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(3,3),  'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False}),
                setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(1,1),  'dPhi': False, 'dPhiInv': False}),
                setup.sysClone(parameters={'triLep': True, 'zWindow' : 'onZ', 'mllMin': 0, 'metMin' : 0, 'metSigMin' : 0, 'nJets':(4,-1), 'nBTags':(2,-1), 'dPhi': False, 'dPhiInv': False})]
    channels = ['all'] # only make plot in channel all for TTZ CR

# define order of estimators
if not args.control:         detailedEstimators = constructEstimatorList(['TTJets-DD', 'TTZ', 'multiBoson', 'other', 'DY'])  # use DD Top prediction when we are in SR
elif args.control == "DY":   detailedEstimators = constructEstimatorList(['DY', 'multiBoson', 'TTJets', 'TTZ', 'other'])
elif args.control == "VV":   detailedEstimators = constructEstimatorList(['multiBoson', 'DY', 'TTJets', 'TTZ', 'other'])
elif args.control == "DYVV": detailedEstimators = constructEstimatorList(['DY', 'multiBoson', 'TTJets', 'TTZ', 'other'])
elif args.control == "TTZ":  detailedEstimators = constructEstimatorList(['TTZ', 'TTJets', 'multiBoson', 'DY', 'other'])

if args.splitTop:            detailedEstimators = constructEstimatorList(['Top_gaussian','Top_nongaussian','Top_fakes', 'TTZ', 'multiBoson', 'other','DY'])

for estimator in detailedEstimators:
    estimatorColor = getattr( color, estimator.name.split('-')[0] ) 
    estimator.style = styles.fillStyle(estimatorColor, lineColor = estimatorColor )


if args.control: postfix = 'controlRegions_' + args.control + ('_scaled' if args.scale else '')
else:            postfix = 'signalRegions'

if args.control: args.signal = None

# signals and blindings
scale = 1.
if args.signal == "T2tt":
  from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import T2tt_750_1, T2tt_600_300
  signals        = [T2tt_750_1, T2tt_600_300]
  signalSetup    = setup.sysClone(sys = {'reweight':['reweightLeptonFastSimSF']})
elif args.signal == "T8":
  from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import T8bbllnunu_XCha0p5_XSlep0p05_800_1, T8bbllnunu_XCha0p5_XSlep0p5_800_1, T8bbllnunu_XCha0p5_XSlep0p95_800_1
  signals        = [T8bbllnunu_XCha0p5_XSlep0p05_800_1, T8bbllnunu_XCha0p5_XSlep0p5_800_1, T8bbllnunu_XCha0p5_XSlep0p95_800_1]
  signalSetup    = setup.sysClone(sys = {'reweight':['reweightLeptonFastSimSF']})
  postfix       += "_T8bbllnunu"
elif args.signal == "TTbarDM":
  from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10, TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10
  signals        = [TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10, TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10] #   setup.blinding = "(evt%15==0)"
  if args.blinded:
    setup.blinding = "(evt%15==0)"
    postfix       += "_blinded"
    scale          = 1./15.
  signalSetup    = setup
  postfix       += "_DM"
else:
  signals = []

if args.noData: 
  postfix += '_noData'
  args.ratio = False 

if args.splitTop:
  postfix += '_splitTop'

# signals style
signalEstimators = [ MCBasedEstimate(name=s.name,  sample={channel:s for channel in allChannels+trilepChannels}, cacheDir=setup.defaultCacheDir() ) for s in signals]
for i, estimator in enumerate(signalEstimators):
  if args.signal != "TTbarDM":  estimator.style = styles.lineStyle( ROOT.kBlack, width=2, dotted=(i==1), dashed=(i==2))
  else:                         estimator.style = styles.lineStyle( ROOT.kBlack if i==0 else 28, width=3)
  estimator.isSignal=True
 
estimators = detailedEstimators + signalEstimators
for e in estimators: e.initCache(setup.defaultCacheDir())

# data
observation       = DataObservation(name='Data', sample=setup.sample['Data'], cacheDir=setup.defaultCacheDir())
observation.style = styles.errorStyle( ROOT.kBlack, markerSize = 1.9 )

# define the systemativ variations
systematics = { 'JEC' :        ['JECUp', 'JECDown'],
       #         'JER' :        ['JERUp', 'JERDown'],
                'PU' :         ['reweightPU36fbUp', 'reweightPU36fbDown'],
                'stat' :       ['statLow', 'statHigh'],
                'topPt' :      ['reweightTopPt', None],
                'b-tag-b' :    ['reweightBTag_SF_b_Up','reweightBTag_SF_b_Down'],
                'b-tag-l' :    ['reweightBTag_SF_l_Up','reweightBTag_SF_l_Down'],
                'trigger' :    ['reweightDilepTriggerBackupUp', 'reweightDilepTriggerBackupDown'],
                'leptonSF' :   ['reweightLeptonSFUp','reweightLeptonSFDown'],
                'TTJetsG' :    ['shape-TTJetsGUp', 'shape-TTJetsGDown'],
                'TTJetsNG' :   ['shape-TTJetsNGUp', 'shape-TTJetsNGDown'],
                'TTJetsF' :    ['shape-TTJetsFUp', 'shape-TTJetsFDown'],
                'TTZ' :        ['shape-TTZUp', 'shape-TTZDown'],
                'other' :      ['shape-otherUp', 'shape-otherDown'],
                'multiBoson' : ['shape-multiBosonUp', 'shape-multiBosonDown'],
                'DY' :         ['shape-DYUp', 'shape-DYDown'],
}

sysVariations = [None]
for var in systematics.values():
  sysVariations += var

# Function to get the sample uncertainty from the card and nuisance files
from StopsDilepton.analysis.infoFromCards import getPreFitUncFromCard, getPostFitUncFromCard, applyNuisance, getBinNumber

cardFile = '/user/tomc/StopsDilepton/results_80X_v30/controlDYVV/cardFiles/T2tt/T2tt_750_1.txt'
if args.control:
  if args.control == "TTZ":  cardFile = '/user/tomc/StopsDilepton/results_80X_v35/controlTTZ/cardFiles/T8bbllnunu_XCha0p5_XSlep0p05/T8bbllnunu_XCha0p5_XSlep0p05_1250_350.txt'  # Warning: need to have a card where there is at least a little bit of signal, otherwise the nuisance file is not derived correctly
  if args.control == "DYVV": cardFile = '/user/tomc/StopsDilepton/results_80X_v35/controlDYVV/cardFiles/T2tt/T2tt_600_300.txt'

def getSampleUncertainty(cardFile, res, var, estimate, binName, i):
    if   estimate.name.count('TTZ'):    uncName = 'ttZ'
    elif estimate.name.count('TTJets'): uncName = 'top'
    else:                               uncName = estimate.name
    estimateName = estimate.name.split('-')[0]

    if var and var.count(estimateName):
      if   args.scale and args.control == "DYVV" and estimate.name in ["DY","multiBoson"]: unc = getPostFitUncFromCard(cardFile, estimateName, uncName, binName);
      elif args.scale and args.control == "TTZ"  and estimate.name in ["TTZ"]:             unc = getPostFitUncFromCard(cardFile, estimateName, uncName, binName);
      else:                                                                                unc = getPreFitUncFromCard(cardFile,  estimateName, uncName, binName);

      if estimate.name.count('TTJets'):
        if   var.count('TTJetsG'):  unc = (0.25 if i < 6 else 0.55)*0.15
        elif var.count('TTJetsNG'): unc = (0.50 if i < 6 else 0.44)*0.30
        elif var.count('TTJetsF'):  unc = (0.25 if i < 6 else 0.01)*0.50

        print var, estimateName, unc

      if   var.count('Up'):   return res*(1.+unc)
      elif var.count('Down'): return res*(1.-unc)
    return res

# Histogram style
def applyStyle(hist, estimate):
    if estimate.name == "Data":
      if channel == "all":  hist.legendText = "Data"
      if channel == "EE":   hist.legendText = "Data (2e)"
      if channel == "MuMu": hist.legendText = "Data (2#mu)"
      if channel == "EMu":  hist.legendText = "Data (1e, 1#mu)"
      if channel == "SF":   hist.legendText = "Data (SF)"
    else:
      hist.legendText = estimate.getTexName(channel)
    hist.style = estimate.style


# For TTZ CR we work with setups instead of regions
def getRegionHistoTTZ(estimate, channel, setups, variations = [None]):
    h = {}
    for var in variations:
      h[var] = ROOT.TH1F(estimate.name + channel + (var if var else ""), estimate.name, len(setups), 0, len(setups))

    for i, s in enumerate(setups):
      binName = ' '.join([channel, noRegions[0].__str__()]) + "_controlTTZ" + str(i+1)

      estimate.initCache(s.defaultCacheDir())
      for var in variations:
        if var in ['statLow', 'statHigh']: continue

        setup_ = s if not var or var.count('shape') else s.sysClone({'selectionModifier': var}) if var.count('JE') else s.sysClone({'reweight':[var]})
        res = estimate.cachedEstimate(noRegions[0], channel, setup_, save=True)
        if args.control == 'TTZ' and estimate.name == "TTZ" and args.scale: res = applyNuisance(cardFile, estimate, res, binName)
        res = getSampleUncertainty(cardFile, res, var, estimate, binName, i)
        h[var].SetBinContent(i+1, res.val)
        h[var].SetBinError(i+1, res.sigma)

        if not var and ('statLow' in variations or 'statHigh' in variations):
          h['statLow'].SetBinContent(i+1,  res.val-res.sigma)
          h['statHigh'].SetBinContent(i+1, res.val+res.sigma)

    applyStyle(h[None], estimate)

    if not estimate.name == "Data":
      for hh in h.values(): hh.Scale(scale)
    return h


def getRegionHisto(estimate, regions, channel, setup, variations = [None]):
    if args.control and args.control == "TTZ": return getRegionHistoTTZ(estimate, channel=channel, setups = setups, variations = variations)

    h = {}
    for var in variations:
      h[var] = ROOT.TH1F(estimate.name + channel + (var if var else ""), estimate.name, len(regions), 0, len(regions))

    for i, r in enumerate(regions):
      binName = ' '.join(['SF', r.__str__()]) + ("_controlDYVV" if args.control and args.control=="DYVV" else "") #always take SF here (that's allways available for DYVV)
      for var in variations:
        if var in ['statLow', 'statHigh']: continue

        setup_ = setup if not var or var.count('shape') else setup.sysClone({'selectionModifier': var}) if var.count('JE') else setup.sysClone({'reweight':[var]})
        res = estimate.cachedEstimate(r, channel, setup_, save=True)
        if args.control == 'DYVV' and estimate.name in ['DY', 'multiBoson'] and args.scale: res = applyNuisance(cardFile, estimate, res, binName)
        if not args.control:
          if estimate.name == 'DY':         res = res*1.31  # Warning currently coded by hand when applied for SR
          if estimate.name == 'multiBoson': res = res*1.19
        res = getSampleUncertainty(cardFile, res, var, estimate, binName, i)
        h[var].SetBinContent(i+1, res.val)
        h[var].SetBinError(i+1, res.sigma)

        if not var and ('statLow' in variations or 'statHigh' in variations):
          h['statLow'].SetBinContent(i+1,  res.val-res.sigma)
          h['statHigh'].SetBinContent(i+1, res.val+res.sigma)

    applyStyle(h[None], estimate)

    if not estimate.name == "Data":
      for hh in h.values(): hh.Scale(scale)
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

def drawBinNumbers(numberOfBins):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.13 if args.ratio else 0.04)
    tex.SetTextAlign(23) # align right
    min = 0.15
    max = 0.95
    diff = (max-min) / numberOfBins
    lines = [(min+(i+0.5)*diff, 0.35 if args.ratio else .12,  str(i)) for i in range(numberOfBins)]
    return [tex.DrawLatex(*l) for l in lines]

def drawTTZLabels():
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.2 if args.ratio else 0.04)
    tex.SetTextAlign(23) # align right
    min = 0.15
    max = 0.95
    diff = (max-min) / 5
    labels = ["=2j,#geq2b","=3j,=1b","=3j,#geq2b","#geq4j,=1b","#geq4j,#geq2b"]
    lines = [(min+(i+0.5)*diff, 0.25 if args.ratio else .12,  labels[i]) for i in range(5)]
    return [tex.DrawLatex(*l) for l in lines]


def drawDivisions(regions):
    if args.control and args.control=="TTZ": return []
    min = 0.15
    max = 0.95
    diff = (max-min) / len(regions)
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(23) # align right
    tex.SetTextSize(0.03)
    tex.SetTextColor(38)

    lines  = [(min+3*diff,  .9, '100 GeV < M_{T2}(ll) < 140 GeV')]
    lines += [(min+9*diff, .9, '140 GeV < M_{T2}(ll) < 240 GeV')]

    tex2= tex.Clone()
    tex2.SetTextAngle(90)
    tex2.SetTextAlign(31)
    lines2 = [(min+12.5*diff, .9, 'M_{T2}(ll) > 240 GeV')]

    line = ROOT.TLine()
    line.SetLineColor(38)
    line.SetLineWidth(2)
    line.SetLineStyle(3)
    line1 = (min+6*diff,  0.13, min+6*diff, 0.93);
    line2 = (min+12*diff, 0.13, min+12*diff, 0.93);
    return [line.DrawLineNDC(*l) for l in [line1, line2]] + [tex.DrawLatex(*l) for l in lines] + [tex2.DrawLatex(*l) for l in lines2]


def drawLumi( lumi_scale ):
    lumi_scale = 36*1000
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS'),
      (0.73, 0.95, 'L=%3.0f fb{}^{-1} (13 TeV)' % (lumi_scale/1000.*scale))
    ]
    return [tex.DrawLatex(*l) for l in lines]



# Main code
for channel in channels:

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
    data_histo = [ [getRegionHisto(observation, regions=regions_, channel=channel, setup=setup)[None]]] if not args.noData else []

    if not args.noData:
      data_histo[0][0].Sumw2(ROOT.kFALSE)
      data_histo[0][0].SetBinErrorOption(ROOT.TH1.kPoisson) # Set poissonian errors

    region_plot = Plot.fromHisto(name = channel, histos = [ bkg_histos[None] ] + data_histo + sig_histos, texX = "" if (args.control and args.control=="TTZ") else (("control" if args.control else "signal") + " region number"), texY = "Events" )

    boxes = []
    ratio_boxes = []
    for ib in range(1, 1 + h_rel_err.GetNbinsX() ):
        val = histos_summed[None].GetBinContent(ib)
        if val<0: continue
        sys = h_rel_err.GetBinContent(ib)
        box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max([0.006, (1-sys)*val]), h_rel_err.GetXaxis().GetBinUpEdge(ib), max([0.006, (1+sys)*val]) )
        box.SetLineColor(ROOT.kBlack)
        box.SetFillStyle(3444)
        box.SetFillColor(ROOT.kBlack)
        r_box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max(0.1, 1-sys), h_rel_err.GetXaxis().GetBinUpEdge(ib), min(1.9, 1+sys) )
        r_box.SetLineColor(ROOT.kBlack)
        r_box.SetFillStyle(3444)
        r_box.SetFillColor(ROOT.kBlack)

        if not args.splitTop:
          boxes.append( box )
          ratio_boxes.append( r_box )


    if args.signal == "T2tt" or args.signal == "T8": legend = (0.55,0.85-0.013*(len(bkg_histos) + len(sig_histos)), 0.9, 0.85)
    elif args.signal == "TTbarDM":                   legend = (0.55,0.85-0.010*(len(bkg_histos) + len(sig_histos)), 0.9, 0.85)
    else:                                            legend = (0.55,0.85-0.010*(len(bkg_histos) + len(sig_histos)), 0.9, 0.85)
    if args.control == "TTZ":                        legend = ((0.35,0.7, 0.9, 0.85), 2)

    def setRatioBorder(c, y_border):
      topPad = c.GetPad(1)
      topPad.SetPad(topPad.GetX1(), y_border, topPad.GetX2(), topPad.GetY2())
      bottomPad = c.GetPad(2)
      bottomPad.SetPad(bottomPad.GetX1(), bottomPad.GetY1(), bottomPad.GetX2(), y_border)

    canvasModifications = []
    if args.labels: canvasModifications = [lambda c: c.SetWindowSize(c.GetWw(), int(c.GetWh()*2)), lambda c : c.GetPad(0).SetBottomMargin(0.5)]
    if args.ratio:  canvasModifications = [lambda c: setRatioBorder(c, 0.23), lambda c : c.GetPad(2).SetBottomMargin(0.4)]

    if args.control and args.control=="TTZ": numberOfBins = len(setups)
    else:                                    numberOfBins = len(regions_)

    drawObjects = boxes + drawLumi(setup.dataLumi[channel] if channel in ['EE','MuMu','EMu'] else setup.dataLumi['EE'])
    if not (args.control and args.control=="TTZ"): drawObjects += drawDivisions(regions_)

    if args.ratio:
      ratio = {'yRange':(0.1,1.9), 'drawObjects': ratio_boxes + (drawTTZLabels() if (args.control and args.control=="TTZ") else drawBinNumbers(numberOfBins))}
    else:
      drawObjects += drawLabels(regions_) if args.labels else drawBinNumbers(numberOfBins)
      drawObjects += drawBinNumbers(numberOfBins)
      ratio = None

    if not args.control:       yRange = (0.006, 'auto')
    elif args.control=='DYVV': yRange = (0.006, 2000000)
    elif args.control=='TTZ':  yRange = (2.6, 500)

    plotting.draw( region_plot, \
        plot_directory = os.path.join(plot_directory, postfix),
        logX = False, logY = True,
        sorting = False,
        ratio = ratio,
        extensions = ["pdf", "png", "root","C"],
        yRange = yRange,
        widths = {'x_width':1000, 'y_width':700},
        drawObjects = drawObjects,
        legend = legend,
        copyIndexPHP = True,
        canvasModifications = canvasModifications,
        histModifications = [lambda h: h.GetYaxis().SetTitleSize(32), lambda h: h.GetYaxis().SetLabelSize(26)] + ([lambda h: h.GetYaxis().SetNoExponent()] if (args.control and args.control=="TTZ") else []),
        ratioModifications = [lambda h: h.GetYaxis().SetTitleSize(32), lambda h: h.GetYaxis().SetLabelSize(26), lambda h: h.GetXaxis().SetTitleOffset(5), lambda h: h.GetXaxis().SetTitleSize(30), lambda h: h.GetXaxis().SetLabelSize(0)],
    )

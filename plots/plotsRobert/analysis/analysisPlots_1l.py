#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)
import itertools
import copy
import array
import operator

from math                                import sqrt, cos, sin, pi, atan2, cosh
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi, deltaR
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.mt2Calculator   import mt2Calculator
from Analysis.Tools.puProfileCache import *

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',             action='store',      default=None,            nargs='?', choices=[None, "T2tt"], help="Add signal to plot")
argParser.add_argument('--noData',             action='store_true', default=False,           help='also plot data?')
argParser.add_argument('--small',                                 action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--sorting',                               action='store', default=None, choices=[None, "forDYMB"],  help='Sort histos?', )
argParser.add_argument('--dpm',                                   action='store_true',     help='Use dpm?', )
argParser.add_argument('--dataMCScaling',      action='store_true',     help='Data MC scaling?', )
argParser.add_argument('--plot_directory',     action='store',      default='v0p3')
argParser.add_argument('--era',                action='store', type=str,      default="2016")
argParser.add_argument('--selection',          action='store',      default='lep1Sel-njet4p-btag1-dPhiJet0-dPhiJet1')
argParser.add_argument('--unblinded',          action='store_true', default=False)
argParser.add_argument('--blinded',            action='store_true', default=False)
argParser.add_argument('--reweightPU',         action='store', default='Central', choices=['VDown', 'Down', 'Central', 'Up', 'VUp', 'VVUp'])
argParser.add_argument('--isr',                action='store_true', default=False)
argParser.add_argument('--plotUPara',          action='store_true',     help='Plot u_para?', )
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"
if args.noData:                       args.plot_directory += "_noData"
if args.signal == "DM":               args.plot_directory += "_DM"
if args.reweightPU:                   args.plot_directory += "_%s"%args.reweightPU
#
# Make samples, will be searched for in the postProcessing directory
#
from Analysis.Tools.puReweighting import getReweightingFunction

if "2016" in args.era:
    year = 2016
elif "2017" in args.era:
    year = 2017
elif "2018" in args.era:
    year = 2018

logger.info( "Working in year %i", year )

# Load from DPM?
if args.dpm:
    data_directory = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

if year == 2016:
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_HT_LO_16, WW_16, Top_pow_1l_16]

elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_HT_LO_17, WW_17, Top_pow_1l_17]

elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    mc             = [Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_HT_LO_18, WW_18, Top_pow_1l_18]


#if args.sorting == "forDYMB":
#    mc = [ mc[4], mc[3], mc[0], mc[2], mc[1] ]

try:
  data_sample = eval(args.era)
except Exception as e:
  logger.error( "Didn't find %s", args.era )
  raise e

lumi_scale                 = data_sample.lumi/1000
data_sample.scale          = 1.
for sample in mc:
    sample.scale          = lumi_scale

if args.small:
    for sample in mc + [data_sample]:
        sample.normalization = 1.
        #sample.reduceFiles( factor = 40 )
        sample.reduceFiles( to=1)
        sample.scale /= sample.normalization

#from Analysis.Tools.RecoilCorrector import RecoilCorrector
#recoilCorrector = RecoilCorrector( os.path.join( "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/", "recoil_v0p10_fine", "%s_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"%args.era ) )

def get_quantiles( histo, quantiles = [1-0.9545, 1-0.6826, 0.5, 0.6826, 0.9545]):
    thresholds = array.array('d', [ROOT.Double()] * len(quantiles) )
    histo.GetQuantiles( len(quantiles), thresholds, array.array('d', quantiles) )
    return thresholds 

signals = []
if args.signal == "T2tt":
    # Load 2017 signal
    data_directory           = "/afs/hephy.at/data/dspitzbart03/nanoTuples/"
    postProcessing_directory = "stops_2017_nano_v0p7/dilep"
    from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import *
    T2tt                    = T2tt_650_0
    T2tt2                   = T2tt_500_250
    T2tt2.style             = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
    T2tt.style              = styles.lineStyle( ROOT.kBlack, width=3 )
    signals = [ T2tt, T2tt2]
#
# Text on the plots
#
tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

def drawObjects( plotData, dataMCScale, lumi_scale ):
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'), 
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    if "mt2ll100" in args.selection and args.noData: lines += [(0.55, 0.5, 'M_{T2}(ll) > 100 GeV')] # Manually put the mt2ll > 100 GeV label
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlots(plots, mode, dataMCScale):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, args.era, mode + ("_log" if log else ""), args.selection)
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      if not args.noData: 
        if mode == "all": plot.histos[1][0].legendText = "Data"
        if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"

      _drawObjects = []

      if ("u_para" in plot.name or "u_perp" in plot.name) and not args.noData:
          h_mc   = plot.histos_added[0][0].Clone()
          h_data = plot.histos_added[1][0].Clone()
          if h_mc.Integral()>0:
              h_mc.Scale(h_data.Integral()/h_mc.Integral())
          q_mc   = tuple(get_quantiles( h_mc ))
          q_data = tuple(get_quantiles( h_data ))
          median_shift = q_data[2]-q_mc[2]
          sigma1_ratio = (q_data[3]-q_data[1])/(q_mc[3]-q_mc[1]) if q_mc[3]-q_mc[1]!=0 else 0
          sigma2_ratio = (q_data[4]-q_data[0])/(q_mc[4]-q_mc[0]) if q_mc[4]-q_mc[0]!=0 else 0

          _drawObjects.append( tex.DrawLatex(0.22, 0.62, '#Delta(med): %+3.1f   1#sigma: %4.3f  2#sigma  %4.3f' % ( median_shift, sigma1_ratio, sigma2_ratio) ) )

      if isinstance( plot, Plot):
          plotting.draw(plot,
            plot_directory = plot_directory_,
            ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
            logX = False, logY = log, sorting = True,
            yRange = (0.03, "auto") if log else (0.001, "auto"),
            scaling = {0:1} if args.dataMCScaling else {},
            legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
            copyIndexPHP = True, extensions = ["png", "pdf"],
          )
      elif isinstance( plot, Plot2D ):

          p_mc = Plot2D.fromHisto( plot.name+'_mc', plot.histos[:1], texX = plot.texX, texY = plot.texY )
          plotting.draw2D(p_mc,
            plot_directory = plot_directory_,
            #ratio = {'yRange':(0.1,1.9)},
            logX = False, logY = False, logZ = log, #sorting = True,
            #yRange = (0.03, "auto") if log else (0.001, "auto"),
            #scaling = {},
            #legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88),
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ),
            copyIndexPHP = True, extensions = ["png", "pdf"], 
          )
          p_data = Plot2D.fromHisto( plot.name+'_data', plot.histos[1:], texX = plot.texX, texY = plot.texY )
          plotting.draw2D(p_data,
            plot_directory = plot_directory_,
            #ratio = {'yRange':(0.1,1.9)},
            logX = False, logY = False, logZ = log, #sorting = True,
            #yRange = (0.03, "auto") if log else (0.001, "auto"),
            #scaling = {},
            #legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88),
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ),
            copyIndexPHP = True, extensions = ["png", "pdf"], 
          )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I", "RawMET_pt/F", "RawMET_phi/F"]
read_variables+= ["event/l", "luminosityBlock/I", "run/I"]
if "2017" in args.era:
    read_variables.append( "MET_pt_min/F" ) 

sequence = []

from StopsDilepton.tools.objectSelection    import muonSelector, eleSelector, getGoodMuons, getGoodElectrons, getGoodJets, getAllJets, isBJet
ele_selector = eleSelector( "tightMiniIso02", year = year )
mu_selector = muonSelector( "tightMiniIso02", year = year )

jetVars         = ['pt/F', 'chEmEF/F', 'chHEF/F', 'neEmEF/F', 'neHEF/F', 'rawFactor/F', 'eta/F', 'phi/F', 'jetId/I', 'btagDeepB/F', 'btagCSVV2/F', 'area/F', 'pt_nom/F'] 
jetVarNames     = map( lambda s:s.split('/')[0], jetVars)
read_variables += [\
    TreeVariable.fromString('nElectron/I'),
    VectorTreeVariable.fromString('Electron[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,phi/F,pt/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,pdgId/I,tightCharge/I,lostHits/b,vidNestedWPBitmap/I]'),
    TreeVariable.fromString('nMuon/I'),
    VectorTreeVariable.fromString('Muon[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,cleanmask/b]'),
    TreeVariable.fromString('nJet/I'),
    VectorTreeVariable.fromString('Jet[%s]'% ( ','.join(jetVars) ) ),
]

def make_all_jets( event, sample ):

    electrons_pt10  = getGoodElectrons(event, ele_selector = ele_selector)
    muons_pt10      = getGoodMuons(event, mu_selector = mu_selector )
    for e in electrons_pt10:
        e['pdgId']      = int( -11*e['charge'] )
    for m in muons_pt10:
        m['pdgId']      = int( -13*m['charge'] )
    leptons_pt10 = electrons_pt10+muons_pt10
    leptons_pt10.sort(key = lambda p:-p['pt'])

    leptons      = filter(lambda l:l['pt']>20, leptons_pt10)
    leptons.sort(key = lambda p:-p['pt'])
    event.jets  = getAllJets(event, leptons, ptCut=30, absEtaCut=99, jetVars=jetVarNames, jetCollections=["Jet"], idVar='jetId')     
    event.nJet_EE = len(filter(lambda j:abs(j['eta'])>2.6 and abs(j['eta'])<3.1, event.jets))
    event.nJet_EE_pt30To50 = len(filter(lambda j:abs(j['eta'])>2.6 and abs(j['eta'])<3.1 and j['pt']>30 and j['pt']<50, event.jets))
    event.nJet_EE_ptTo50 = len(filter(lambda j:abs(j['eta'])>2.6 and abs(j['eta'])<3.1 and j['pt']<50, event.jets))
    event.nJet_EE_ptTo40 = len(filter(lambda j:abs(j['eta'])>2.6 and abs(j['eta'])<3.1 and j['pt']<40, event.jets))
    event.nJet_EE_ptTo30 = len(filter(lambda j:abs(j['eta'])>2.6 and abs(j['eta'])<3.1 and j['pt']<30, event.jets))
    event.nJet_EE_pt30 = len(filter(lambda j:abs(j['eta'])>2.6 and abs(j['eta'])<3.1 and j['pt']>30, event.jets))
    event.nJet_EE_pt40 = len(filter(lambda j:abs(j['eta'])>2.6 and abs(j['eta'])<3.1 and j['pt']>40, event.jets))
    event.nJet_EE_pt50 = len(filter(lambda j:abs(j['eta'])>2.6 and abs(j['eta'])<3.1 and j['pt']>50, event.jets))

    event.badJetE  = sum( [ j['pt']*j['neEmEF']*cosh(j['eta']) for j in event.jets if abs(j['eta'])>2.6 and abs(j['eta'])<3.1], 0. )
    event.badJetPt = sum( [ j['pt']*j['neEmEF'] for j in event.jets if abs(j['eta'])>2.6 and abs(j['eta'])<3.1], 0. )

    bJets        = filter(lambda j:isBJet(j, tagger="DeepCSV", year=year) and abs(j['eta'])<=2.4    , event.jets)
    nonBJets     = filter(lambda j:not ( isBJet(j, tagger="DeepCSV", year=year) and abs(j['eta'])<=2.4 ), event.jets)

    event.bj0, event.bj1 = None, None
    if len(bJets)+len(nonBJets)>=2:
        event.bj0, event.bj1  = (bJets+nonBJets)[:2]
        event.mt2blbl_bj_dR   = deltaR  ( event.bj0, event.bj1 ) 
        event.mt2blbl_bj_dPhi = deltaPhi( event.bj0['phi'], event.bj1['phi'] ) 
        event.mt2blbl_bj_dEta = event.bj0['eta'] - event.bj1['eta']
        event.mt2blbl_bj_mass = sqrt(2.*event.bj0['pt']*event.bj1['pt']*(cosh(event.bj0['eta']-event.bj1['eta'])-cos(event.bj0['phi']-event.bj1['phi']))) 
    else:
        event.mt2blbl_bj_dR   = float('nan') 
        event.mt2blbl_bj_dPhi = float('nan') 
        event.mt2blbl_bj_dEta = float('nan') 
        event.mt2blbl_bj_mass = float('nan') 

sequence.append( make_all_jets )

# 2nd lepton
ele_selector_noIso   = eleSelector(  'tightNoIso', year )
mu_selector_noIso    = muonSelector( 'tightNoIso', year )

def make_noIso(event, sample):

    noIsoMu  = getGoodMuons(event, mu_selector = mu_selector_noIso)
    noIsoEle = getGoodElectrons(event, ele_selector = ele_selector_noIso)

    isoMu  = filter( mu_selector, noIsoMu) 
    isoEle = filter( ele_selector, noIsoEle)

    isoLep = isoMu+isoEle
    isoLep.sort( key = lambda l: -l['pt'] )
    
    noIsoLep = noIsoMu+noIsoEle
    noIsoLep.sort( key = lambda l: -l['pt'] )

    event.trailing_ele_iso = -1
    event.trailing_mu_iso  = -1
    # should have a hard isolated lepton
    #if len(isoLep)>0:
    #    for lep in noIsoLep:
    if len( noIsoLep )>1 and noIsoLep[1]['pt']<event.l1_pt:
        lep = noIsoLep[1]
#           if lep!=isoLep[0]:
        if abs(lep['pdgId'])==11:
            event.trailing_ele_iso = lep['miniPFRelIso_all']
        elif abs(lep['pdgId'])==13:
            event.trailing_mu_iso = lep['miniPFRelIso_all']
        
sequence.append( make_noIso )


#
def getLeptonSelection( mode ):
  if   mode=="mu":    return "nGoodMuons>=1" 
  elif mode=="e":     return "nGoodElectrons>=1"
  elif mode=="all":   return "nGoodMuons+nGoodElectrons>=1"

#
# Loop over channels
#
yields     = {}
allPlots   = {}
allModes   = ['mu','e']
for index, mode in enumerate(allModes):
  yields[mode] = {}

  data_sample.setSelectionString([getFilterCut(isData=True, year=year), getLeptonSelection(mode)])
  data_sample.name           = "data"
  data_sample.read_variables = ["event/I","run/I", "reweightHEM/F"]
  data_sample.style          = styles.errorStyle(ROOT.kBlack)
  weight_ = lambda event, sample: event.weight*event.reweightHEM

  for sample in mc + signals:
    sample.read_variables = ['reweightPU/F', 'reweightL1Prefire/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F', 'reweightHEM/F']
    # Need individual pu reweighting functions for each sample in 2017, so nTrueInt_puRW is only defined here

    sample.read_variables.append( 'reweightPU/F' if args.reweightPU=='Central' else 'reweightPU%s/F'%args.reweightPU )

    pu_getter = operator.attrgetter( 'reweightPU' if args.reweightPU=='Central' else 'reweightPU%s'%args.reweightPU )
    sample.weight         = lambda event, sample: pu_getter(event) * event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF*event.reweightL1Prefire

    sample.setSelectionString([getFilterCut(isData=False, year=year), getLeptonSelection(mode)])

  mc_ = mc 

  for sample in mc_: sample.style = styles.fillStyle(sample.color)

  if not args.noData:
    stack = Stack(mc_, data_sample)#, data_sample_filtered)
  else:
    stack = Stack(mc_)

  stack.extend( [ [s] for s in signals ] )

  # Use some defaults
  Plot  .setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
  Plot2D.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), histo_class=ROOT.TH2D)
  
  plots   = []
  plots2D = []
  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    attribute = lambda event, sample: 0.5 + index,
    binning=[2, 0, 2],
  ))

  plots.append(Plot(
    name = 'PV_npvsGood', texX = 'N_{PV} (good)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
    binning=[100,0,100],
  ))
    
  plots.append(Plot(
    name = 'PV_npvs', texX = 'N_{PV} (total)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "PV_npvs/I" ),
    binning=[100,0,100],
  ))

  plots.append(Plot(
      texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "met_pt/F" ),
      binning=[400/20,0,400],
  ))

  plots2D.append(Plot2D(
    name = 'allJets_occupancy_pt30',
    stack = stack,
    attribute = (
      lambda event, sample: [ j['eta'] for j in event.jets if j['pt']>30 ],
      lambda event, sample: [ j['phi'] for j in event.jets if j['pt']>30 ],
    ),
    texX = '#eta (all jets)', texY = '#phi',
    binning=[52, -5.2, 5.2, 32, -pi, pi],
  ))

  plots.append(Plot(
    name = 'allJets_eta_pt30',
    stack = stack,
    attribute = lambda event, sample: [ j['eta'] for j in event.jets if j['pt']>30 ],
    texX = '#eta (all jets)', 
    binning=[52, -5.2, 5.2],
  ))

  plots.append(Plot(
    name = 'allJets_eta_pt50',
    stack = stack,
    attribute = lambda event, sample: [ j['eta'] for j in event.jets if j['pt']>50 ],
    texX = '#eta (all jets)', 
    binning=[52, -5.2, 5.2],
  ))

  plots.append(Plot(
    name = 'allJets_eta_pt100',
    stack = stack,
    attribute =  lambda event, sample: [ j['eta'] for j in event.jets if j['pt']>100 ],
    texX = '#eta (all jets)', 
    binning=[52, -5.2, 5.2],
  ))


  if "2017" in args.era:
    plots.append(Plot(
        texX = 'min E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "MET_pt_min/F" ),
        binning=[400/20,0,400],
    ))
    plots.append(Plot(name = "MET_pt_min_delta",
        texX = '#Delta min E_{T}^{miss} (GeV)', texY = 'Number of Events / 10 GeV',
        attribute = lambda event, sample: event.met_pt - event.MET_pt_min,
        binning=[200/10,0,200],
    ))

#Sum$(abs(Jet_eta)>2.6&&abs(Jet_eta)<3.1&&Jet_pt<50)==0

  #plots.append(Plot( name = "met_pt_raw",
  #    texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
  #    attribute = TreeVariable.fromString( "RawMET_pt/F" ),
  #    binning=[400/20,0,400],
  #))

  plots.append(Plot(
      texX = 'E_{T}^{miss} significance', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "MET_significance/F" ),
      binning=[34,0,102],
  ))

  plots.append(Plot(
      texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "met_phi/F" ),
      binning=[10,-pi,pi],
  ))

  #plots.append(Plot( name = "met_phi_corr",
  #    texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
  #    attribute = lambda event, sample: event.met_phi_corr,
  #    binning=[10,-pi,pi],
  #))

  #plots.append(Plot( name = "met_phi_raw",
  #    texX = 'raw #phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
  #    attribute = TreeVariable.fromString( "RawMET_phi/F" ),
  #    binning=[10,-pi,pi],
  #))

  #plots.append(Plot( name = "met_phi_raw_corr",
  #    texX = 'raw #phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
  #    attribute = lambda event, sample: event.RawMET_phi_corr,
  #    binning=[10,-pi,pi],
  #))

  #plots.append(Plot(
  #  texX = 'E_{T}^{miss}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events',
  #  attribute = TreeVariable.fromString('metSig/F'),
  #  binning= [80,20,100] if args.selection.count('metSig20') else ([25,5,30] if args.selection.count('metSig') else [30,0,30]),
  #))

  plots.append(Plot(
    texX = 'number of jets', texY = 'Number of Events',
    attribute = TreeVariable.fromString('nJetGood/I'),
    binning=[14,0,14],
  ))
  if "2017" in args.era:  
    plots.append(Plot( name = "nJet_EE",
      texX = 'number of jets', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJet_EE,
      binning=[14,0,14],
    ))
    plots.append(Plot( name = "nJet_EE_pt30To50",
      texX = 'number of jets', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJet_EE_pt30To50,
      binning=[14,0,14],
    ))
    plots.append(Plot( name = "nJet_EE_ptTo50",
      texX = 'number of jets', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJet_EE_ptTo50,
      binning=[14,0,14],
    ))
    plots.append(Plot( name = "nJet_EE_ptTo40",
      texX = 'number of jets', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJet_EE_ptTo40,
      binning=[14,0,14],
    ))
    plots.append(Plot( name = "nJet_EE_ptTo30",
      texX = 'number of jets', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJet_EE_ptTo30,
      binning=[14,0,14],
    ))
    plots.append(Plot( name = "nJet_EE_pt50",
      texX = 'number of jets', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJet_EE_pt50,
      binning=[14,0,14],
    ))
    plots.append(Plot( name = "nJet_EE_pt40",
      texX = 'number of jets', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJet_EE_pt40,
      binning=[14,0,14],
    ))
    plots.append(Plot( name = "nJet_EE_pt30",
      texX = 'number of jets', texY = 'Number of Events',
      attribute = lambda event, sample: event.nJet_EE_pt30,
      binning=[14,0,14],
    ))
    plots.append(Plot( name = "badJetE",
      texX = 'badEEJetEnergy', texY = 'Number of Events',
      attribute = lambda event, sample: event.badJetE,
      binning=[40,0,400],
    ))
    plots.append(Plot( name = "badJetPt",
      texX = 'badEEJetPt', texY = 'Number of Events',
      attribute = lambda event, sample: event.badJetPt,
      binning=[40,0,200],
    ))

  plots.append(Plot(
    texX = 'number of medium b-tags (CSVM)', texY = 'Number of Events',
    attribute = TreeVariable.fromString('nBTag/I'),
    binning=[8,0,8],
  ))

  plots.append(Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 25 GeV',
    attribute = TreeVariable.fromString( "ht/F" ),
    binning=[500/25,0,600],
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "l1_pt/F" ),
    binning=[20,0,300],
  ))

  plots.append(Plot(
    texX = '#eta(l_{1})', texY = 'Number of Events',
    name = 'l1_eta', attribute = lambda event, sample: abs(event.l1_eta), read_variables = ['l1_eta/F'],
    binning=[15,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(l_{1})', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "l1_phi/F" ),
    binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    texX = 'I_{mini}(l_{1})', texY = 'Number of Events',
    name = 'l1_miniRelIso', attribute = lambda event, sample: event.l1_miniRelIso, read_variables = ['l1_miniRelIso/F'],
    binning=[20,0,.5],
  ))

  plots.append(Plot(
    texX = 'pdgId(l1)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "l1_pdgId/I" ),
    binning=[30,-15,15],
  ))

  plots.append(Plot(
    texX = 'I_{mini}(trailing #mu)', texY = 'Number of Events',
    name = 'l_trailing_mu_miniIso', attribute = lambda event, sample: event.trailing_mu_iso, 
    binning=[40,0,1],
  ))

  plots.append(Plot(
    texX = 'I_{mini}(trailing e)', texY = 'Number of Events',
    name = 'l_trailing_ele_miniIso', attribute = lambda event, sample: event.trailing_ele_iso, 
    binning=[40,0,1],
  ))

#  plots.append(Plot(
#    texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 15 GeV',
#    attribute = TreeVariable.fromString( "l2_pt/F" ),
#    binning=[20,0,300],
#  ))
#
#  plots.append(Plot(
#    texX = '#eta(l_{2})', texY = 'Number of Events',
#    name = 'l2_eta', attribute = lambda event, sample: abs(event.l2_eta), read_variables = ['l2_eta/F'],
#    binning=[15,0,3],
#  ))
#
#  plots.append(Plot(
#    texX = '#phi(l_{2})', texY = 'Number of Events',
#    attribute = TreeVariable.fromString( "l2_phi/F" ),
#    binning=[10,-pi,pi],
#  ))
#  
#  plots.append(Plot(
#    texX = 'I_{mini}(l_{2})', texY = 'Number of Events',
#    name = 'l2_miniRelIso', attribute = lambda event, sample: event.l2_miniRelIso, read_variables = ['l2_miniRelIso/F'],
#    binning=[20,0,.5],
#  ))
#
#  plots.append(Plot(
#    texX = 'pdgId(l2)', texY = 'Number of Events',
#    attribute = TreeVariable.fromString( "l2_pdgId/I" ),
#    binning=[30,-15,15],
#  ))

  # Plots only when at least one jet:
  if args.selection.count('njet2') or args.selection.count('njet1') or args.selection.count('njet01'):

    plots2D.append(Plot2D(
      name = 'leading_jet_occ',
      stack = stack,
      attribute = (
        lambda event, sample: event.JetGood_eta[0],
        lambda event, sample: event.JetGood_phi[0],
      ),
      texX = '#eta(leading jet) (GeV)', texY = '#phi(leading jet) (GeV)',
      binning=[16, -3.0, 3.0, 10, -pi, pi],
    ))

    plots.append(Plot(
      texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet1_pt', attribute = lambda event, sample: event.JetGood_pt[0],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet1_eta', attribute = lambda event, sample: event.JetGood_eta[0],
      binning=[20,-3,3],
    ))

    plots.append(Plot(
      texX = '#phi(leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet1_phi', attribute = lambda event, sample: event.JetGood_phi[0],
      binning=[20,-pi,pi],
    ))

    plots.append(Plot(
      name = 'cosMetJet1phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0]), 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet1phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

#  # Plots only when at least two jets:
  if args.selection.count('njet2'):
    plots.append(Plot(
      texX = 'p_{T}(2nd leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet2_pt', attribute = lambda event, sample: event.JetGood_pt[1],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(2nd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet2_eta', attribute = lambda event, sample: event.JetGood_eta[1],
      binning=[20,-3,3],
    ))

    plots.append(Plot(
      texX = '#phi(2nd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet2_phi', attribute = lambda event, sample: event.JetGood_phi[1],
      binning=[20,-pi,pi],
    ))

    plots.append(Plot(
      name = 'cosMetJet2phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet2phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))


    plots.append(Plot(
      name = 'cosJet1Jet2phi',
      texX = 'Cos(#Delta#phi(leading jet, 2nd leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.JetGood_phi[1] - event.JetGood_phi[0] ) ,
      read_variables =  ["JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

  plotting.fill(plots + plots2D, read_variables = read_variables, sequence = sequence)

  # Get normalization yields from yield histogram
  for plot in plots:
    if plot.name == "yield":
      for i, l in enumerate(plot.histos):
        for j, h in enumerate(l):
          yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
          h.GetXaxis().SetBinLabel(1, "#mu")
          h.GetXaxis().SetBinLabel(2, "e")
  if args.noData: yields[mode]["data"] = 0

  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc_)
  dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

  drawPlots(plots + plots2D, mode, dataMCScale)
  allPlots[mode] = plots + plots2D

# Add the different channels into SF and all
for mode in ["all"]:
  yields[mode] = {}
  for y in yields[allModes[0]]:
    try:    yields[mode][y] = sum(yields[c][y] for c in ['e','mu'])
    except: yields[mode][y] = 0
  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

  for plot in allPlots['mu']:
    for plot2 in (p for p in allPlots['e'] if p.name == plot.name):  #For SF add EE, second round add EMu for all
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
        for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
         if i==k:
           j.Add(l)

  drawPlots(allPlots['mu'], mode, dataMCScale)


logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )


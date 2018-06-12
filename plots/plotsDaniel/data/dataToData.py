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

from math                         import sqrt, cos, sin, pi
from RootTools.core.standard      import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaR, deltaPhi, getObjDict, getVarValue
from StopsDilepton.tools.objectSelection import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='StopsDilepton_dataVsData_v1')
argParser.add_argument('--selection',          action='store',      default='lepSel-OS-looseLeptonVeto-njet2p-relIso0.12-mll20')
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"
#
# Make samples, will be searched for in the postProcessing directory
#

data_directory           = "/afs/hephy.at/data/dspitzbart01/nanoTuples"


postProcessing_directory = "2016_nano_v1/dilep"
from StopsDilepton.samples.nanoTuples_Run2016_05Feb2018 import *

postProcessing_directory = "2017_nano_v1/dilep/"
from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018 import *

postProcessing_directory = "2018_nano_v1/dilep/"
from StopsDilepton.samples.nanoTuples_Run2018_PromptReco import *


# define 2l selections
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0"
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2"
  elif mode=='all':  return "nGoodMuons+nGoodElectrons==2"

# Read variables and sequences
#
read_variables =    ["weight/F",
                    "JetGood[pt/F,eta/F,phi/F,btagCSVV2/F,btagDeepB/F]", "nJetGood/I",
                    "l1[pt/F,eta/F,eta/F,phi/F,pdgId/I,miniRelIso/F,relIso03/F,dxy/F,dz/F]",
                    "l2[pt/F,eta/F,eta/F,phi/F,pdgId/I,miniRelIso/F,relIso03/F,dxy/F,dz/F]",
                    "MET_pt/F", "MET_phi/F", "metSig/F", "ht/F", "nBTag/I", 
                    ]
sequence = []

#
# Text on the plots
#
def drawObjects( lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary' ), 
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)'% lumi_scale )
    ]
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlots(plots, mode, lumi_scale):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'data_to_data', args.plot_directory, mode + ("_log" if log else ""), args.selection)
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      if mode == "all": 
        for s in plot.stack:
            s[0].texName = s[0].texName.replace('(2#mu)', '(all)')

      #if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"

      l  = len(plot.histos)
      #scaling = {2*i+1:2*i for i in range(l/2)} 
      scaling = {1:0, 2:0} 
      #ratio_histos = [ (2*i,2*i+1) for i in range(l/2) ] 
      ratio_histos = [(0,2),(1,2) ]
      plotting.draw(plot,
        plot_directory = plot_directory_,
        ratio = {'yRange':(0.1,1.9), 'histos':ratio_histos, 'texY': '201X / 2016'},
        logX = False, logY = log, sorting = True,
        yRange = (0.03, "auto") if log else (0.001, "auto"),
        scaling = scaling,
        legend = [ (0.15,0.9-0.03*sum(map(len, plot.histos)),0.9,0.9), 2],
        drawObjects = drawObjects( lumi_scale ),
        copyIndexPHP = True
      )

def get_nVtx_reweight( histo ):
    def get_histo_reweight( event, sample) :
        return histo.GetBinContent(sample.nVert_histo.FindBin( event.PV_npvsGood ))/sample.nVert_histo.GetBinContent(sample.nVert_histo.FindBin( event.PV_npvsGood ) )
    return get_histo_reweight

colors = [ROOT.kBlue, ROOT.kMagenta, ROOT.kGreen, ]

#
# Loop over channels
#
yields     = {}
allPlots   = {}
#allModes   = ['mumu','mue','ee']
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
    yields[mode] = {}
    if mode == "mumu":
        data_2016_sample            = DoubleMuon_Run2016 
        data_2016_sample.texName    = "data 2016 (2#mu)"
        data_2016_sample.setSelectionString(["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"])
        data_2017_sample            = DoubleMuon_Run2017 
        data_2017_sample.setSelectionString(["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"])
        data_2017_sample.texName    = "data 2017 (2#mu)"
        data_2018_sample            = DoubleMuon_Run2018
        data_2018_sample.setSelectionString(["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ"])
        data_2018_sample.texName    = "data 2018 (2#mu)"
        data_2017_samples           = [data_2017_sample]#, DoubleMuon_Run2017D, data_2017EF_sample]
        data_2018_samples           = [data_2018_sample]
        data_2016_samples           = [copy.deepcopy(data_2016_sample) for x in data_2017_samples]
    elif mode == "ee":
        data_2016_sample            = DoubleEG_Run2016
        data_2016_sample.texName    = "data 2016 (2e)"
        data_2016_sample.setSelectionString(["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2017_sample            = DoubleEG_Run2017 
        data_2017_sample.texName    = "data 2017 (2e)"
        data_2017_sample.setSelectionString(["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2018_sample            = EGamma_Run2018
        data_2018_sample.texName    = "data 2018 (2e)"
        data_2018_sample.setSelectionString(["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2018_samples           = [data_2018_sample]
        data_2017_samples           = [data_2017_sample]#, data_2017D_sample, DoubleEG_Run2017EF]
        data_2016_samples           = [copy.deepcopy(data_2016_sample) for x in data_2017_samples]
    elif mode == 'mue':
        data_2016_sample            = MuonEG_Run2016
        data_2016_sample.texName    = "data 2016 (1#mu, 1e)"
        data_2016_sample.setSelectionString(["HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL||HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL"])
        data_2017_sample            = MuonEG_Run2017 
        data_2017_sample.texName    = "data 2017 (1#mu, 1e)"
        data_2017_sample.setSelectionString(["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ||HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2018_sample            = MuonEG_Run2018
        data_2018_sample.texName    = "data 2018 (1#mu, 1e)"
        data_2018_sample.setSelectionString(["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ||HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"])
        data_2018_samples           = [data_2018_sample]
        data_2017_samples           = [data_2017_sample]#, data_2017Cv2D_sample, data_2017EF_sample]
        data_2016_samples           = [copy.deepcopy(data_2016_sample) for x in data_2017_samples]
    else: raise ValueError    

    for i_s, data_2017_sample in enumerate(data_2017_samples):
        data_2017_sample.addSelectionString([getFilterCut(isData=True, year=2017), getLeptonSelection(mode)])
        data_2017_sample.read_variables = ["event/I","run/I"]
        data_2017_sample.style          = styles.errorStyle(colors[i_s])
        lumi_2017_scale                 = data_2017_sample.lumi/1000

    for i_s, data_2016_sample in enumerate(data_2016_samples):
        data_2016_sample.addSelectionString([getFilterCut(isData=True, year=2016), getLeptonSelection(mode)])
        data_2016_sample.read_variables = ["event/I","run/I"]
        data_2016_sample.style          = styles.lineStyle(colors[i_s]+1, errors=True)
        lumi_2016_scale                 = data_2016_sample.lumi/1000

    colors2018 = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+1]
    for i_s, data_2018_sample in enumerate(data_2018_samples):
        data_2018_sample.addSelectionString([getFilterCut(isData=True, year=2018), getLeptonSelection(mode)])
        data_2018_sample.read_variables = ["event/I","run/I"]
        data_2018_sample.style          = styles.lineStyle(colors2018[i_s]+1, errors=True)
        lumi_2018_scale                 = data_2018_sample.lumi/1000

    weight_ = lambda event, sample: event.weight
    stack_samples = []
    for i in range(len(data_2017_samples)):
        stack_samples.append( [data_2018_samples[i]] )
        stack_samples.append( [data_2017_samples[i]] )
        stack_samples.append( [data_2016_samples[i]] )

    stack = Stack( *stack_samples )

    if args.small:
        for sample in stack.samples:
            sample.reduceFiles( to = 3 )

    reweight_binning = [3*i for i in range(10)]+[30,35,40,50,100]
    for i_s, data_2017_sample in enumerate(data_2017_samples):

        logger.info('nVert Histo for %s', data_2018_sample.name)
        data_2018_sample.nVert_histo     = data_2018_sample.get1DHistoFromDraw("PV_npvsGood", reweight_binning, binningIsExplicit = True)
        data_2018_sample.nVert_histo.Scale(1./data_2018_sample.nVert_histo.Integral())
        
        logger.info('nVert Histo for %s', data_2017_sample.name)
        data_2017_sample.nVert_histo     = data_2017_sample.get1DHistoFromDraw("PV_npvsGood", reweight_binning, binningIsExplicit = True)
        data_2017_sample.nVert_histo.Scale(1./data_2017_sample.nVert_histo.Integral())
    
        data_2016_sample = data_2016_samples[i_s]
        logger.info('nVert Histo for %s', data_2016_sample.name)
        data_2016_sample.nVert_histo     = data_2016_sample.get1DHistoFromDraw("PV_npvsGood", reweight_binning, binningIsExplicit = True)
        data_2016_sample.nVert_histo.Scale(1./data_2016_sample.nVert_histo.Integral())

        #data_2016_sample.weight         = lambda event, sample: data_2017_samples[i_s].nVert_histo.GetBinContent(sample.nVert_histo.FindBin( event.nVert ))/sample.nVert_histo.GetBinContent(sample.nVert_histo.FindBin( event.nVert ) )
        data_2016_sample.weight = get_nVtx_reweight(data_2018_samples[i_s].nVert_histo)
        data_2017_sample.weight = get_nVtx_reweight(data_2018_samples[i_s].nVert_histo)

    # Use some defaults
    Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin=None)

    plots = []
    
    plots.append(Plot(
      name = 'yield', texX = 'yield', texY = 'Number of Events',
      attribute = lambda event, sample: 0.5 + index,
      binning=[3, 0, 3],
    ))
    
    plots.append(Plot(
      name = 'PV_npvsGood', texX = 'number of good PVs', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "PV_npvsGood/I" ),
      binning=[80,0,80],
      addOverFlowBin='upper',
    ))
    
    plots.append(Plot(
        texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "MET_pt/F" ),
        binning=[400/20,0,400],
      addOverFlowBin='upper',
    ))
    
    plots.append(Plot(
        texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
        attribute = TreeVariable.fromString( "MET_phi/F" ),
        binning=[10,-pi,pi],
    ))
    
    plots.append(Plot(
        texX = 'M(ll) (GeV)', texY = 'Number of Events / 10 GeV',
        attribute = TreeVariable.fromString( "dl_mass/F" ),
        binning=[30,0,300],
    ))

    #plots.append(Plot(name = "Z_mass_EE",
    #    texX = 'M(ll) (GeV)', texY = 'Number of Events / 10 GeV',
    #    attribute = lambda event, sample: event.dl_mass if ( abs(event.l1_eta)>1.479 and abs(event.l2_eta)>1.479) else float('nan'),
    #    binning=[10,81,101],
    #))

    #plots.append(Plot(name = "Z_mass_EB",
    #    texX = 'M(ll) (GeV)', texY = 'Number of Events / 10 GeV',
    #    attribute = lambda event, sample: event.dl_mass if ( ((abs(event.l1_eta)<1.479 and abs(event.l2_eta)>1.479) or (abs(event.l1_eta)>1.479 and abs(event.l2_eta)<1.479))) else float('nan'),
    #    binning=[30,0,300],
    #))

    #plots.append(Plot(name = "Z_mass_BB",
    #    texX = 'M(ll) (GeV)', texY = 'Number of Events / 20 GeV',
    #    attribute = lambda event, sample: event.dl_mass if ( abs(event.l2_eta)<1.479 and abs(event.l2_eta)<1.479) else float('nan'),
    #    binning=[30,0,300],
    #))

    plots.append(Plot(
      texX = 'E_{T}^{miss}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events',
      attribute = TreeVariable.fromString('metSig/F'),
      binning= [30,0,30],
    ))
    
    plots.append(Plot(
      texX = 'N_{jets}', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "nJetGood/I" ),
      binning=[5,2.5,7.5],
      addOverFlowBin='upper',
    ))

    plots.append(Plot( name = "nBTagCSVv2",
      texX = 'number of medium b-tags (CSVM)', texY = 'Number of Events',
      attribute = TreeVariable.fromString('nBTag/I'),
      binning=[8,0,8],
      addOverFlowBin='upper',
    ))

    #plots.append(Plot( name = "nBTagDeepCSV",
    #  texX = 'number of medium b-tags (DeepCSV)', texY = 'Number of Events',
    #  attribute = TreeVariable.fromString('nBTagDeepCSV/I'),
    #  binning=[8,0,8],
    #  addOverFlowBin='upper',
    #))

    plots.append(Plot(
      texX = 'H_{T} (GeV)', texY = 'Number of Events / 25 GeV',
      attribute = TreeVariable.fromString( "ht/F" ),
      binning=[500/25,0,600],
      addOverFlowBin='upper',
    ))
    
    plots.append(Plot(
      texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet1_pt', attribute = lambda event, sample: event.JetGood_pt[0],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet1_eta', attribute = lambda event, sample: abs(event.JetGood_eta[0]),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet1_phi', attribute = lambda event, sample: event.JetGood_phi[0],
      binning=[10,-pi,pi],
    ))
    
    plots.append(Plot(
      texX = 'leading jet b-tag Disc. CSVv2', texY = 'Number of Events',
      name = 'jet1_CSVv2', attribute = lambda event, sample: event.JetGood_btagCSVV2[0],
      binning=[40,0,1],
    ))

    plots.append(Plot(
      texX = 'leading jet b-tag Disc. DeepCSV', texY = 'Number of Events',
      name = 'jet1_DeepCSV', attribute = lambda event, sample: event.JetGood_btagDeepB[0],
      binning=[40,0,1],
    ))
    
    plots.append(Plot(
      texX = 'p_{T}(2nd leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet2_pt', attribute = lambda event, sample: event.JetGood_pt[1],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(2nd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet2_eta', attribute = lambda event, sample: abs(event.JetGood_eta[1]),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(2nd leading jet) (GeV)', texY = 'Number of Events',
      name = 'jet2_phi', attribute = lambda event, sample: event.JetGood_phi[1],
      binning=[10,-pi,pi],
    ))
    
    plots.append(Plot(
      texX = '2nd leading jet b-tag Disc. CSVv2', texY = 'Number of Events',
      name = 'jet2_CSVv2', attribute = lambda event, sample: event.JetGood_btagCSVV2[1],
      binning=[40,0,1],
    ))

    plots.append(Plot(
      texX = '2nd leading jet b-tag Disc. DeepCSV', texY = 'Number of Events',
      name = 'jet2_DeepCSV', attribute = lambda event, sample: event.JetGood_btagDeepB[1],
      binning=[40,0,1],
    ))

    plots.append(Plot( name = "l1_pt",
      texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 15 GeV',
      attribute = lambda event, sample: event.l1_pt[0], 
      binning=[20,0,300],
    ))
  
    plots.append(Plot( name = "l1_dxy",
      texX = 'd_{xy}(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_dxy[0], 
      binning=[40,-0.2,0.2],
    ))

    plots.append(Plot( name = "l1_dz",
      texX = 'd_{z}(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_dz[0], 
      binning=[40,-0.2,0.2],
    ))
  
    plots.append(Plot( name = "l1_eta",
      texX = '#eta(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_eta[0], 
      binning=[30,-3,3],
    ))
  
    plots.append(Plot( name = "l1_phi",
      texX = '#phi(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_phi[0], 
      binning=[10,-pi,pi],
    ))
 
    #plots.append(Plot( name = "l1_etaSc",
    #  texX = '#etaSc(l_{1})', texY = 'Number of Events',
    #  attribute = lambda event, sample: event.lep_etaSc[0], 
    #  binning=[30,-3,3],
    #))

    plots.append(Plot( name = "l1_relIso03",
      texX = 'relIso03(l_{1})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l1_relIso03[0], 
      binning=[30,0,1],
    ))

    #plots.append(Plot( name = "l1_sip3d",
    #  texX = 'sip3d(l_{1})', texY = 'Number of Events',
    #  attribute = lambda event, sample: event.l1_sip3d, 
    #  binning=[50,0,5],
    #))
 
    plots.append(Plot( name = "l2_pt",
      texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 15 GeV',
      attribute = lambda event, sample: event.l2_pt[0], 
      binning=[20,0,300],
    ))
  
    plots.append(Plot( name = "l2_dxy",
      texX = 'd_{xy}(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_dxy[0], 
      binning=[40,-0.2,0.2],
    ))

    plots.append(Plot( name = "l2_dz",
      texX = 'd_{z}(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_dz[0], 
      binning=[40,-0.2,0.2],
    ))
  
    plots.append(Plot( name = "l2_eta",
      texX = '#eta(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_eta[0], 
      binning=[30,-3,3],
    ))
  
    plots.append(Plot( name = "l2_phi",
      texX = '#phi(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_phi[0], 
      binning=[10,-pi,pi],
    ))

    #plots.append(Plot( name = "l2_etaSc",
    #  texX = '#etaSc(l_{2})', texY = 'Number of Events',
    #  attribute = lambda event, sample: event.lep_etaSc[1], 
    #  binning=[30,-3,3],
    #))

    plots.append(Plot( name = "l2_relIso03",
      texX = 'relIso03(l_{2})', texY = 'Number of Events',
      attribute = lambda event, sample: event.l2_relIso03[0], 
      binning=[30,0,1],
    ))

    #plots.append(Plot( name = "l2_sip3d",
    #  texX = 'sip3d(l_{2})', texY = 'Number of Events',
    #  attribute = lambda event, sample: event.l2_sip3d, 
    #  binning=[50,0,5],
    #))
 
    plots.append(Plot(
      name = 'cosMetJet1phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.MET_phi - event.JetGood_phi[0]), 
      read_variables = ["MET_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet1phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.MET_phi - event.JetGood_phi[0] ) , 
      read_variables = ["MET_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosMetJet2phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.MET_phi - event.JetGood_phi[1] ) , 
      read_variables = ["MET_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet2phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.MET_phi - event.JetGood_phi[1] ) , 
      read_variables = ["MET_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosJet1Jet2phi',
      texX = 'Cos(#Delta#phi(leading jet, 2nd leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.JetGood_phi[1] - event.JetGood_phi[0] ) ,
      read_variables =  ["JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plotting.fill(plots, read_variables = read_variables, sequence = sequence)

    # Get normalization yields from yield histogram
    for plot in plots:
      if plot.name == "yield":
        for i, l in enumerate(plot.histos):
          for j, h in enumerate(l):
            yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
            h.GetXaxis().SetBinLabel(1, "#mu#mu")
            h.GetXaxis().SetBinLabel(2, "#mue")
            h.GetXaxis().SetBinLabel(3, "ee")

    drawPlots(plots, mode, lumi_2017_scale)
    allPlots[mode] = plots

# Add the different channels into SF and all
for mode in ["comb1","comb2","all"]:
    yields[mode] = {}
    for y in yields[allModes[0]]:
        try:    yields[mode][y] = sum(yields[c][y] for c in allModes)
        except: yields[mode][y] = 0
    
    for plot in allPlots['mumu']:
        if mode=="comb1":
            tmp = allPlots['mue'] if 'mue' in allModes else []
        elif mode=="comb2":
            tmp = allPlots['ee']
        for plot2 in (p for p in tmp if p.name == plot.name):
            for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
                for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
                    if i==k:
                        j.Add(l)
    
    if mode == "all": drawPlots(allPlots['mumu'], mode, lumi_2017_scale)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )


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

from math                                import sqrt, cos, sin, pi, atan2
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.helpers         import deltaPhi
from Samples.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
from StopsDilepton.tools.mt2Calculator   import mt2Calculator
from Analysis.Tools.puProfileCache import *

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='v02')
argParser.add_argument('--selection',          action='store',      default='lepSel-POGMetSig12-njet2p-btag1p-relIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
argParser.add_argument('--badMuonFilters',     action='store',      default="Summer2016",  help="Which bad muon filters" )
argParser.add_argument('--noBadPFMuonFilter',           action='store_true', default=False)
argParser.add_argument('--noBadChargedCandidateFilter', action='store_true', default=False)
#argParser.add_argument('--reweightPU',         action='store', default='Central', choices=['VDown', 'Down', 'Central', 'Up', 'VUp', 'VVUp', 'noPUReweighting'])
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"
if args.badMuonFilters!="Summer2016": args.plot_directory += "_badMuonFilters_"+args.badMuonFilters
#if args.reweightPU:                   args.plot_directory += "_%s"%args.reweightPU
if args.noBadPFMuonFilter:            args.plot_directory += "_noBadPFMuonFilter"
if args.noBadChargedCandidateFilter:  args.plot_directory += "_noBadChargedCandidateFilter"

# Make samples, will be searched for in the postProcessing directory
#
from Analysis.Tools.puReweighting import getReweightingFunction

from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
#from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
#from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *

#samples = [ Top_pow_16, Top_pow_17, Top_pow_18 ]
samples = [ Top_pow_16]

if args.small:
    for sample in samples:
        #sample.reduceFiles( factor=40 )
        sample.reduceFiles( to=1 )

# Text on the plots
#
tex = ROOT.TLatex()
tex.SetNDC()
tex.SetTextSize(0.04)
tex.SetTextAlign(11) # align right

def drawObjects( plotData ):
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'), 
    ]
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlots(plots, mode):
  for log in [False, True]:
    plot_directory_ = os.path.join(plot_directory, 'analysisPlots', args.plot_directory, mode + ("_log" if log else ""), args.selection)
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot

      _drawObjects = []

      plotting.draw(plot,
	    plot_directory = plot_directory_,
	    ratio = None,
	    logX = False, logY = log, sorting = False,
	    yRange = (0.03, "auto") if log else (0.001, "auto"),
	    scaling = {},
	    legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
	    drawObjects = drawObjects( False ) + _drawObjects,
        copyIndexPHP = True, extensions = ["png"],
      )


# Read variables and sequences
read_variables = [
            "weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "l1_muIndex/I", "l2_muIndex/I",
            "JetGood[pt/F,eta/F,phi/F,genPt/F]", 
            "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I"]
read_variables += [
            "nMuon/I",
            "Muon[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,genPartIdx/I,genPartFlav/b,cleanmask/b]"
            ]

read_variables += ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F', 'reweightL1Prefire/F']

sequence = []

#def make_jet_weight( event, sample):
#
#    jet_pt_mism = [ abs(event.JetGood_pt[i] - event.JetGood_genPt[i]) for i in range( event.nJetGood ) ]
#
#    event.onlyGoodJets = max( jet_pt_mism )<40
#
#sequence.append( make_jet_weight ) 
#
#def make_lepton_selection( event, sample ):

    # 0 unmatched, 1 prompt (gamma*) , 15 tau, 22 prompt photon (conv), 5 b, 4 c, 3 light/unknown
    # remember: if type is /b use ord()
    #if event.l1_muIndex>=0 and  ord(event.Muon_genPartFlav[event.l1_muIndex])==1:
       # print event.Muon_pt[event.l1_muIndex], event.l1_pt
       # print ord(event.Muon_genPartFlav[event.l1_muIndex])
#    if event.l2_muIndex>=0:
#        print event.Muon_pt[event.l2_muIndex], event.l2_pt
#    event.PrPr = 0
#    event.tauX=0
#    event.unmatchX=0
#    if (ord(event.Muon_genPartFlav[event.l1_muIndex])==1 and ord(event.Muon_genPartFlav[event.l2_muIndex])==1) or (ord(event.Muon_genPartFlav[event.l2_muIndex])==1 and ord(event.Muon_genPartFlav[event.l1_muIndex])==1):
#        #if ord(event.Muon_genPartFlav[event.l2_muIndex])==1 and ord(event.Muon_genPartFlav[event.l1_muIndex])==1: 
#         print ord(event.Muon_genPartFlav[event.l1_muIndex])
#         event.PrPr = 1    
#    elif ord(event.Muon_genPartFlav[event.l1_muIndex])==15 or ord(event.Muon_genPartFlav[event.l2_muIndex])==15:
#        event.tauX = 1
#    elif ord(event.Muon_genPartFlav[event.l1_muIndex])==0 or ord(event.Muon_genPartFlav[event.l2_muIndex])==0:
#        event.unmatchX = 1
#sequence.append( make_lepton_selection )




# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)" + offZ+")||isEMu)"

# Loop over channels
allPlots   = {}
#allModes   = ['mumu','mue','ee']
allModes   = ['mumu']
for index, mode in enumerate(allModes):

  for sample in samples:
    # Need individual pu reweighting functions for each sample in 2017, so nTrueInt_puRW is only defined here
    #if args.reweightPU and args.reweightPU not in ["noPUReweighting"]:
    #    sample.read_variables.append( 'reweightPU%s/F'%args.reweightPU )

    #if args.reweightPU == "noPUReweighting":
    #    sample.weight         = lambda event, sample: event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    #elif args.reweightPU:
    #    pu_getter = operator.attrgetter("reweightPU%s"%args.reweightPU)
    #    sample.weight         = lambda event, sample: pu_getter(event) * event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    #else: #default
    sample.weight         = lambda event, sample: event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF

  Top_pow_16.setSelectionString([getFilterCut(isData=False, year=2016, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
  #Top_pow_17.setSelectionString([getFilterCut(isData=False, year=2017, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
  #Top_pow_18.setSelectionString([getFilterCut(isData=False, year=2018, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])

  Top_pow_16.style = styles.lineStyle(ROOT.kBlue, errors = True)
  #Top_pow_17.style = styles.lineStyle(ROOT.kGreen, errors = True)
  #Top_pow_18.style = styles.lineStyle(ROOT.kRed, errors = True)
  Top_pow_16.name += "_2016"
  #Top_pow_17.name += "_2017"
  #Top_pow_18.name += "_2018"
  Top_pow_16.texName += " (2016)"
  #Top_pow_17.texName += " (2017)"
  #Top_pow_18.texName += " (2018)"

  #stack = Stack( *list([s] for s in samples) )
  stack = Stack( Top_pow_16 )
  #stack = Stack( Top_pow_16,Top_pow_17, Top_pow_18 )
 # stack = Stack(event.PrPr, event.onlyGoodJets  )

 # Use some defaults
  Plot.setDefaults(stack = stack, selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
  
  plots = []

  plots.append(Plot( name = "w_o_L1Prefire",
    texX = 'M_{T2}(ll) (GeV) ', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    #attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    binning=[400/20, 0,400]),
  )

 # plots.append(Plot( name = "dl_mt2ll_onlyGoodJets",
 #    texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
 #    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
 #    weight = lambda event, sample: event.onlyGoodJets, 
 #    binning=[400/20, 0,400]),
 # )
 # plots.append(Plot( name = "dl_mt2ll_onlyPromptPair",
 #   texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
 #   attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
 #   weight = lambda event, sample: event.PrPr , 
 #   binning=[400/20, 0,400]),
 #
 #)

 # plots.append(Plot( name = "dl_mt2ll_onetau",
 #   texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
 #   attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
 #   weight = lambda event, sample: event.tauX ,  
 #   binning=[400/20, 0,400]),
 #
 #)

 # plots.append(Plot( name = "dl_mt2ll_oneunmatched",
 #   texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
 #   attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
 #   weight = lambda event, sample:  event.unmatchX,  
 #   binning=[400/20, 0,400]),
 #
 #)

  plotting.fill(plots, read_variables = read_variables, sequence = sequence)

  drawPlots(plots, mode)

logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )


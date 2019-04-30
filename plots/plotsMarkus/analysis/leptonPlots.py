#!/usr/bin/env python
''' Lepton analysis script
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
# from Analysis.Tools.puProfileCache import *

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',             action='store',      default=None,            nargs='?', choices=[None, "T2tt", "DM", "T8bbllnunu", "compilation"], help="Add signal to plot")
argParser.add_argument('--noData',             action='store_true', default=False,           help='also plot data?')
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--plot_directory',     action='store',      default='v2')
argParser.add_argument('--era',                action='store', type=str,      default="Run2016")
argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
argParser.add_argument('--study',              action='store', type=str,      default="Muon", choices = ["Muon", "Electron"])
argParser.add_argument('--minmax',                                   action='store_true')
argParser.add_argument('--recoil',             action='store', type=str,      default=None, choices = ["nvtx", "VUp", None])
argParser.add_argument('--nvtxReweightSelection',          action='store',      default=None)
argParser.add_argument('--splitBosons',        action='store_true', default=False)
argParser.add_argument('--splitBosons2',       action='store_true', default=False)
argParser.add_argument('--badMuonFilters',     action='store',      default="Summer2016",  help="Which bad muon filters" )
argParser.add_argument('--noBadPFMuonFilter',           action='store_true', default=False)
argParser.add_argument('--noBadChargedCandidateFilter', action='store_true', default=False)
argParser.add_argument('--unblinded',          action='store_true', default=False)
argParser.add_argument('--blinded',            action='store_true', default=False)
argParser.add_argument('--reweightPU',         action='store', default='Central', choices=['VDown', 'Down', 'Central', 'Up', 'VUp', 'VVUp', 'noPUReweighting', 'nvtx'])
argParser.add_argument('--isr',                action='store_true', default=False)
argParser.add_argument('--splitMET',           action='store_true',     help='Split in MET bins?' )
argParser.add_argument('--splitMETSig',        action='store_true',     help='Split in METSig bins?' )
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.small:                        args.plot_directory += "_small"
if args.study:                        args.plot_directory += "_%s"%args.study
if args.minmax:                       args.plot_directory += "_minmax"
# if args.reweightPU:                   args.plot_directory += "_%s"%args.reweightPU
if args.recoil:                       args.plot_directory += '_recoil_'+args.recoil
if args.splitMET:                     args.plot_directory += "_splitMET"
if args.splitMETSig:                  args.plot_directory += "_splitMETSig"
if args.noData:                       args.plot_directory += "_noData"
if args.splitBosons:                  args.plot_directory += "_splitMultiBoson"
if args.splitBosons2:                 args.plot_directory += "_splitMultiBoson2"
if args.signal == "DM":               args.plot_directory += "_DM"
if args.badMuonFilters!="Summer2016": args.plot_directory += "_badMuonFilters_"+args.badMuonFilters
if args.noBadPFMuonFilter:            args.plot_directory += "_noBadPFMuonFilter"
if args.noBadChargedCandidateFilter:  args.plot_directory += "_noBadChargedCandidateFilter"
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

if year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16]
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]
elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    mc             = [ Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_HT_LO_18]

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
        sample.reduceFiles( factor = 40 )
        sample.scale /= sample.normalization

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

      plotting.draw(plot,
	    plot_directory = plot_directory_,
	    ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
	    logX = False, logY = log, sorting = not (args.splitMET or args.splitMETSig),
	    yRange = (0.03, "auto") if log else (0.001, "auto"),
	    #scaling = {0:1},
	    legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
	    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
        copyIndexPHP = True, extensions = ["png"],
      )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I"]
read_variables += [
            "l1_pdgId/I", "l2_pdgId/I",
#            "l1_muIndex/I", "l2_muIndex/I",
            "nMuon/I", "Muon[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,cleanmask/b]",
             "nElectron/I", "Electron[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O]" 
            #"nMuon/I", "Muon[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,cleanmask/b]" if args.study == "Muon" elif "nElectron/I", "Electron[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O]" else pass
#,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,cleanmask/b]"
            ]

sequence = []

def make_muon_selection( event, sample ):
    if "data" in sample.name:
        event.l1_muIndex = -1
        event.l2_muIndex = -1
        for i in range(event.nMuon):
            if event.l1_pt==event.Muon_pt[i]:
                event.l1_muIndex = i
            if event.l2_pt==event.Muon_pt[i]:
                event.l2_muIndex = i
    if abs(event.l1_pdgId)==13 and event.l1_muIndex>=0: # if l1 is a muon
        event.l1_dxy = event.Muon_dxy[event.l1_muIndex]
        event.l1_dxyErr = event.Muon_dxyErr[event.l1_muIndex]
        event.l1_dz = event.Muon_dz[event.l1_muIndex]
        event.l1_dzErr = event.Muon_dzErr[event.l1_muIndex]
        event.l1_ip3d = event.Muon_ip3d[event.l1_muIndex]
        event.l1_jetRelIso = event.Muon_jetRelIso[event.l1_muIndex]
        event.l1_miniPFRelIso_all = event.Muon_miniPFRelIso_all[event.l1_muIndex]
        event.l1_pfRelIso03_all = event.Muon_pfRelIso03_all[event.l1_muIndex]
        event.l1_pfRelIso04_all = event.Muon_pfRelIso04_all[event.l1_muIndex]
        event.l1_pt = event.Muon_pt[event.l1_muIndex]
        event.l1_ptErr = event.Muon_ptErr[event.l1_muIndex]
        event.l1_segmentComp = event.Muon_segmentComp[event.l1_muIndex]
        event.l1_sip3d = event.Muon_sip3d[event.l1_muIndex]
        event.l1_mvaTTH = event.Muon_mvaTTH[event.l1_muIndex]
        event.l1_charge = event.Muon_charge[event.l1_muIndex]
        event.l1_nStations = event.Muon_nStations[event.l1_muIndex]
        event.l1_nTrackerLayers = event.Muon_nTrackerLayers[event.l1_muIndex]
        event.l1_pdgId = event.Muon_pdgId[event.l1_muIndex]
        event.l1_highPtId = event.Muon_highPtId[event.l1_muIndex]
        event.l1_inTimeMuon = event.Muon_inTimeMuon[event.l1_muIndex]
        #event.l1_mediumId = event.Muon_mediumId[event.l1_muIndex]
        #event.l1_mediumPromptId = event.Muon_mediumPromptId[event.l1_muIndex]
    else:
        event.l1_dxy = float('nan')
        event.l1_dxyErr = float('nan')
        event.l1_dz = float('nan')
        event.l1_dzErr = float('nan')
        event.l1_ip3d = float('nan')
        event.l1_jetRelIso = float('nan')
        event.l1_miniPFRelIso_all = float('nan')
        event.l1_pfRelIso03_all = float('nan')
        event.l1_pfRelIso04_all = float('nan')
        event.l1_pt = float('nan')
        event.l1_ptErr = float('nan')
        event.l1_segmentComp= float('nan')
        event.l1_sip3d = float('nan')
        event.l1_mvaTTH = float('nan')
        event.l1_charge = float('nan')
        event.l1_nStations = float('nan')
        event.l1_nTrackerLayers = float('nan')
        event.l1_pdgId = 0 
        event.l1_highPtId = float('nan')
        event.l1_inTimeMuon = float('nan')
        #event.l1_mediumId = float('nan')
        #event.l1_mediumPromptId = float('nan')

    if abs(event.l2_pdgId)==13 and event.l2_muIndex>=0: # if l2 is a muon
        event.l2_dxy = event.Muon_dxy[event.l2_muIndex]
        event.l2_dxyErr = event.Muon_dxyErr[event.l2_muIndex]
        event.l2_dz = event.Muon_dz[event.l2_muIndex]
        event.l2_dzErr = event.Muon_dzErr[event.l2_muIndex]
        event.l2_ip3d = event.Muon_ip3d[event.l2_muIndex]
        event.l2_jetRelIso = event.Muon_jetRelIso[event.l2_muIndex]
        event.l2_miniPFRelIso_all = event.Muon_miniPFRelIso_all[event.l2_muIndex]
        event.l2_pfRelIso03_all = event.Muon_pfRelIso03_all[event.l2_muIndex]
        event.l2_pfRelIso04_all = event.Muon_pfRelIso04_all[event.l2_muIndex]
        event.l2_pt = event.Muon_pt[event.l2_muIndex]
        event.l2_ptErr = event.Muon_ptErr[event.l2_muIndex]
        event.l2_segmentComp = event.Muon_segmentComp[event.l2_muIndex]
        event.l2_sip3d = event.Muon_sip3d[event.l2_muIndex]
        event.l2_mvaTTH = event.Muon_mvaTTH[event.l2_muIndex]
        event.l2_charge = event.Muon_charge[event.l2_muIndex]
        event.l2_nStations = event.Muon_nStations[event.l2_muIndex]
        event.l2_nTrackerLayers = event.Muon_nTrackerLayers[event.l2_muIndex]
        event.l2_pdgId = event.Muon_pdgId[event.l2_muIndex]
        event.l2_highPtId = event.Muon_highPtId[event.l2_muIndex]
        event.l2_inTimeMuon = event.Muon_inTimeMuon[event.l2_muIndex]
        #event.l2_mediumId = event.Muon_mediumId[event.l2_muIndex]
        #event.l2_mediumPromptId = event.Muon_mediumPromptId[event.l2_muIndex]
    else:
        event.l2_dxy = float('nan')
        event.l2_dxyErr = float('nan')
        event.l2_dz = float('nan')
        event.l2_dzErr = float('nan')
        event.l2_ip3d = float('nan')
        event.l2_jetRelIso = float('nan')
        event.l2_miniPFRelIso_all = float('nan')
        event.l2_pfRelIso03_all = float('nan')
        event.l2_pfRelIso04_all = float('nan')
        event.l2_pt = float('nan')
        event.l2_ptErr = float('nan')
        event.l2_segmentComp= float('nan')
        event.l2_sip3d = float('nan')
        event.l2_mvaTTH = float('nan')
        event.l2_charge = float('nan')
        event.l2_nStations = float('nan')
        event.l2_nTrackerLayers = float('nan')
        event.l2_pdgId = 0 
        event.l2_highPtId = float('nan')
        event.l2_inTimeMuon = float('nan')
        #event.l2_mediumId = float('nan')
        #event.l2_mediumPromptId = float('nan')

def make_electron_selection( event, sample ):
    if "data" in sample.name:
        event.l1_eleIndex = -1
        event.l2_eleIndex = -1
        for i in range(event.nElectron):
            if event.l1_pt==event.Electron_pt[i]:
                event.l1_eleIndex = i
            if event.l2_pt==event.Electron_pt[i]:
                event.l2_eleIndex = i
    else:
        if not event.l1_eleIndex or not event.l2_eleIndex:
            print "~~~~~> %i, %i"%(event.l1_eleIndex,event.l2_eleIndex) 
    if abs(event.l1_pdgId)==11 and event.l1_eleIndex>=0: # if l1 is an electron
        event.l1_dxy = event.Muon_dxy[event.l1_eleIndex]
        event.l1_dxyErr = event.Muon_dxyErr[event.l1_eleIndex]
        event.l1_dz = event.Muon_dz[event.l1_eleIndex]
        event.l1_dzErr = event.Muon_dzErr[event.l1_eleIndex]
        event.l1_ip3d = event.Muon_ip3d[event.l1_eleIndex]
        event.l1_jetRelIso = event.Muon_jetRelIso[event.l1_eleIndex]
        event.l1_miniPFRelIso_all = event.Muon_miniPFRelIso_all[event.l1_eleIndex]
        event.l1_pfRelIso03_all = event.Muon_pfRelIso03_all[event.l1_eleIndex]
        event.l1_pfRelIso04_all = event.Muon_pfRelIso04_all[event.l1_eleIndex]
        event.l1_pt = event.Muon_pt[event.l1_eleIndex]
        event.l1_ptErr = event.Muon_ptErr[event.l1_eleIndex]
        event.l1_segmentComp= event.Muon_segmentComp[event.l1_eleIndex]
        event.l1_sip3d = event.Muon_sip3d[event.l1_eleIndex]
        event.l1_mvaTTH = event.Muon_mvaTTH[event.l1_eleIndex]
        event.l1_charge = event.Muon_charge[event.l1_eleIndex]
        event.l1_nStations = event.Muon_nStations[event.l1_eleIndex]
        event.l1_nTrackerLayers = event.Muon_nTrackerLayers[event.l1_eleIndex]
        event.l1_pdgId = event.Muon_pdgId[event.l1_eleIndex]
        event.l1_highPtId = event.Muon_highPtId[event.l1_eleIndex]
        event.l1_inTimeMuon = event.Muon_inTimeMuon[event.l1_eleIndex]
        #event.l1_mediumId = event.Muon_mediumId[event.l1_eleIndex]
        #event.l1_mediumPromptId = event.Muon_mediumPromptId[event.l1_eleIndex]
    else:
        event.l1_dxy = float('nan')
        event.l1_dxyErr = float('nan')
        event.l1_dz = float('nan')
        event.l1_dzErr = float('nan')
        event.l1_ip3d = float('nan')
        event.l1_jetRelIso = float('nan')
        event.l1_miniPFRelIso_all = float('nan')
        event.l1_pfRelIso03_all = float('nan')
        event.l1_pfRelIso04_all = float('nan')
        event.l1_pt = float('nan')
        event.l1_ptErr = float('nan')
        event.l1_segmentComp = float('nan')
        event.l1_sip3d = float('nan')
        event.l1_mvaTTH = float('nan')
        event.l1_charge = float('nan')
        event.l1_nStations = float('nan')
        event.l1_nTrackerLayers = float('nan')
        event.l1_pdgId = 0 
        event.l1_highPtId = float('nan')
        event.l1_inTimeMuon = float('nan')
        #event.l1_mediumId = float('nan')
        #event.l1_mediumPromptId = float('nan')
    if abs(event.l2_pdgId)==11 and event.l2_eleIndex>=0: # if l2 is an electron
        event.l2_dxy = event.Muon_dxy[event.l2_eleIndex]
        event.l2_dxyErr = event.Muon_dxyErr[event.l2_eleIndex]
        event.l2_dz = event.Muon_dz[event.l2_eleIndex]
        event.l2_dzErr = event.Muon_dzErr[event.l2_eleIndex]
        event.l2_ip3d = event.Muon_ip3d[event.l2_eleIndex]
        event.l2_jetRelIso = event.Muon_jetRelIso[event.l2_eleIndex]
        event.l2_miniPFRelIso_all = event.Muon_miniPFRelIso_all[event.l2_eleIndex]
        event.l2_pfRelIso03_all = event.Muon_pfRelIso03_all[event.l2_eleIndex]
        event.l2_pfRelIso04_all = event.Muon_pfRelIso04_all[event.l2_eleIndex]
        event.l2_pt = event.Muon_pt[event.l2_eleIndex]
        event.l2_ptErr = event.Muon_ptErr[event.l2_eleIndex]
        event.l2_segmentComp= event.Muon_segmentComp[event.l2_eleIndex]
        event.l2_sip3d = event.Muon_sip3d[event.l2_eleIndex]
        event.l2_mvaTTH = event.Muon_mvaTTH[event.l2_eleIndex]
        event.l2_charge = event.Muon_charge[event.l2_eleIndex]
        event.l2_nStations = event.Muon_nStations[event.l2_eleIndex]
        event.l2_nTrackerLayers = event.Muon_nTrackerLayers[event.l2_eleIndex]
        event.l2_pdgId = event.Muon_pdgId[event.l2_eleIndex]
        event.l2_highPtId = event.Muon_highPtId[event.l2_eleIndex]
        event.l2_inTimeMuon = event.Muon_inTimeMuon[event.l2_eleIndex]
        #event.l2_mediumId = event.Muon_mediumId[event.l2_eleIndex]
        #event.l2_mediumPromptId = event.Muon_mediumPromptId[event.l2_eleIndex]
    else:
        event.l2_dxy = float('nan')
        event.l2_dxyErr = float('nan')
        event.l2_dz = float('nan')
        event.l2_dzErr = float('nan')
        event.l2_ip3d = float('nan')
        event.l2_jetRelIso = float('nan')
        event.l2_miniPFRelIso_all = float('nan')
        event.l2_pfRelIso03_all = float('nan')
        event.l2_pfRelIso04_all = float('nan')
        event.l2_pt = float('nan')
        event.l2_ptErr = float('nan')
        event.l2_segmentComp = float('nan')
        event.l2_sip3d = float('nan')
        event.l2_mvaTTH = float('nan')
        event.l2_charge = float('nan')
        event.l2_nStations = float('nan')
        event.l2_nTrackerLayers = float('nan')
        event.l2_pdgId = 0 
        event.l2_highPtId = float('nan')
        event.l2_inTimeMuon = float('nan')
        #event.l2_mediumId = float('nan')
        #event.l2_mediumPromptId = float('nan')

def make_minmax_selection( event, sample ):
    event.l1_dxy = max(event.l1_dxy, event.l2_dxy) 
    event.l1_dxyErr = max(event.l1_dxyErr, event.l2_dxyErr) 
    event.l1_dz = max(event.l1_dz, event.l2_dz) 
    event.l1_dzErr = max(event.l1_dzErr, event.l2_dzErr) 
    event.l1_ip3d = max(event.l1_ip3d, event.l2_ip3d) 
    event.l1_jetRelIso = max(event.l1_jetRelIso, event.l2_jetRelIso) 
    event.l1_miniPFRelIso_all = max(event.l1_miniPFRelIso_all, event.l2_miniPFRelIso_all) 
    event.l1_pfRelIso03_all = max(event.l1_pfRelIso03_all, event.l2_pfRelIso03_all) 
    event.l1_pfRelIso04_all = max(event.l1_pfRelIso04_all, event.l2_pfRelIso04_all) 
    event.l1_pt = max(event.l1_pt, event.l2_pt) 
    event.l1_ptErr = max(event.l1_ptErr, event.l2_ptErr) 
    event.l1_segmentComp = max(event.l1_segmentComp, event.l2_segmentComp) 
    event.l1_sip3d = max(event.l1_sip3d, event.l2_sip3d) 
    event.l1_mvaTTH = max(event.l1_mvaTTH, event.l2_mvaTTH) 
    event.l1_charge = max(event.l1_charge, event.l2_charge) 
    event.l1_nStations = max(event.l1_nStations, event.l2_nStations) 
    event.l1_nTrackerLayers = max(event.l1_nTrackerLayers, event.l2_nTrackerLayers) 
    event.l1_pdgId = max(event.l1_pdgId, event.l2_pdgId) 
    event.l1_highPtId = max(event.l1_highPtId, event.l2_highPtId) 
    event.l1_inTimeMuon = max(event.l1_inTimeMuon, event.l2_inTimeMuon) 
    #event.l1_mediumId = max(event.l1_mediumId, event.l2_mediumId) 
    #event.l1_mediumPromptId = max(event.l1_mediumPromptId, event.l2_mediumPromptId) 

    event.l2_dxy = min(event.l1_dxy, event.l2_dxy) 
    event.l2_dxyErr = min(event.l1_dxyErr, event.l2_dxyErr) 
    event.l2_dz = min(event.l1_dz, event.l2_dz) 
    event.l2_dzErr = min(event.l1_dzErr, event.l2_dzErr) 
    event.l2_ip3d = min(event.l1_ip3d, event.l2_ip3d) 
    event.l2_jetRelIso = min(event.l1_jetRelIso, event.l2_jetRelIso) 
    event.l2_miniPFRelIso_all = min(event.l1_miniPFRelIso_all, event.l2_miniPFRelIso_all) 
    event.l2_pfRelIso03_all = min(event.l1_pfRelIso03_all, event.l2_pfRelIso03_all) 
    event.l2_pfRelIso04_all = min(event.l1_pfRelIso04_all, event.l2_pfRelIso04_all) 
    event.l2_pt = min(event.l1_pt, event.l2_pt) 
    event.l2_ptErr = min(event.l1_ptErr, event.l2_ptErr) 
    event.l2_segmentComp = min(event.l1_segmentComp, event.l2_segmentComp) 
    event.l2_sip3d = min(event.l1_sip3d, event.l2_sip3d) 
    event.l2_mvaTTH = min(event.l1_mvaTTH, event.l2_mvaTTH) 
    event.l2_charge = min(event.l1_charge, event.l2_charge) 
    event.l2_nStations = min(event.l1_nStations, event.l2_nStations) 
    event.l2_nTrackerLayers = min(event.l1_nTrackerLayers, event.l2_nTrackerLayers) 
    event.l2_pdgId = min(event.l1_pdgId, event.l2_pdgId) 
    event.l2_highPtId = min(event.l1_highPtId, event.l2_highPtId) 
    event.l2_inTimeMuon = min(event.l1_inTimeMuon, event.l2_inTimeMuon) 
    #event.l2_mediumId = min(event.l1_mediumId, event.l2_mediumId) 
    #event.l2_mediumPromptId = min(event.l1_mediumPromptId, event.l2_mediumPromptId) 

print "~~~~> Studying %s"%args.study
if args.study == "Muon":
  sequence.append( make_muon_selection )
elif args.study == "Electron":
  sequence.append( make_electron_selection )

if args.minmax:
  sequence.append( make_minmax_selection )

#
#
# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)&&" + offZ+")||isEMu)"

#
# Loop over channels
#
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}

  data_sample.setSelectionString([getFilterCut(isData=True, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
  data_sample.name           = "data"
  data_sample.read_variables = ["event/I","run/I"]
  data_sample.style          = styles.errorStyle(ROOT.kBlack)
  weight_ = lambda event, sample: event.weight

  for sample in mc:
    sample.read_variables = ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F', "l1_muIndex/I", "l2_muIndex/I"]
    sample.weight         = lambda event, sample: event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF
    sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])

  for sample in mc: sample.style = styles.fillStyle(sample.color)

  if not args.noData:
    stack = Stack(mc, data_sample)
  else:
    stack = Stack(mc)

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
  
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    attribute = lambda event, sample: 0.5 + index,
    binning=[3, 0, 3],
  ))

  if not args.blinded:
    plots.append(Plot(
      texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
      binning=[300/20, 100,400] if args.selection.count('mt2ll100') else ([300/20, 140, 440] if args.selection.count('mt2ll140') else [300/20,0,300]),
    ))

  plots.append(Plot(
    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "l1_pt/F" ),
    binning=[20,0,100], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    texX = 'p_{T} error(l_{1}) (GeV)', texY = 'Number of Events / 15 GeV',
    name = 'l1_ptErr', attribute = lambda event, sample: event.l1_ptErr,
    binning=[20,0,100],
  ))

  plots.append(Plot(
    texX = 'ptErr/pt(p_{T})(l_{1}) (GeV)', texY = 'Number of Events / 15 GeV',
    name = 'l1_ptSig', attribute = lambda event, sample: (event.l1_ptErr/event.l1_pt),
    binning=[50,0,2],
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
    texX = 'd_{xy}(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_dxy', attribute = lambda event, sample: event.l1_dxy,
    binning=[50,-.05,.05],
  ))

  plots.append(Plot(
    texX = 'error d_{xy}(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_dxyErr', attribute = lambda event, sample: event.l1_dxyErr,
    binning=[50,0,0.05],
  ))

  plots.append(Plot(
    texX = 'd_{z}(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_dz', attribute = lambda event, sample: event.l1_dz,
    binning=[50,-.05,.05], addOverFlowBin = 'both',
  ))

  plots.append(Plot(
    texX = 'error d_{z}(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_dzErr', attribute = lambda event, sample: event.l1_dzErr,
    binning=[50,0,0.05], addOverFlowBin = 'both',
  ))

  plots.append(Plot(
    texX = 'ip3d(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_ip3d', attribute = lambda event, sample: event.l1_ip3d,
    binning=[50,-.05,.05], addOverFlowBin = 'both',
  ))

  plots.append(Plot(
    texX = 'relIso(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_jetRelIso', attribute = lambda event, sample: event.l1_jetRelIso,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_miniPFRelIso_all', attribute = lambda event, sample: event.l1_miniPFRelIso_all,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_pfRelIso03_all', attribute = lambda event, sample: event.l1_pfRelIso03_all,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_pfRelIso04_all', attribute = lambda event, sample: event.l1_pfRelIso04_all,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'segmentComp(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_segmentComp', attribute = lambda event, sample: event.l1_segmentComp,
    binning=[50,0,1], 
  ))

  plots.append(Plot(
    texX = 'sip3d(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_sip3d', attribute = lambda event, sample: event.l1_sip3d,
    binning=[10,0,10], 
  ))

#  plots.append(Plot(
#    texX = 'mvaTTH(l_{1}) (GeV)', texY = 'Number of Events',
#    name = 'l1_mvaTTH', attribute = lambda event, sample: event.l1_mvaTTH,
#    binning=[50,-10,10], addOverFlowBin = 'both', 
#  ))
#?
  plots.append(Plot(
    texX = 'charge(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_charge', attribute = lambda event, sample: event.l1_charge,
    binning=[3,-1,1], 
  ))

  plots.append(Plot(
    texX = 'nStations(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_nStations', attribute = lambda event, sample: event.l1_nStations,
    binning=[20,0,20], addOverFlowBin = 'both',
  ))
#?
  plots.append(Plot(
    texX = 'nTrackerLayers(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_nTrackerLayers', attribute = lambda event, sample: event.l1_nTrackerLayers,
    binning=[20,0,20], 
  ))

  plots.append(Plot(
    texX = 'pdgId(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_pdgId', attribute = lambda event, sample: event.l1_pdgId,
    binning=[26,-13,13],
  ))

  plots.append(Plot(
    texX = 'highPtId(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_highPtId', attribute = lambda event, sample: event.l1_highPtId,
    binning=[3,0,3],  
  ))

  plots.append(Plot(
    texX = 'inTimeMuon(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_inTimeMuon', attribute = lambda event, sample: event.l1_inTimeMuon,
    binning=[50,-.2,.2], addOverFlowBin = 'both', 
  ))
#?
#  plots.append(Plot(
#    texX = 'mediumId(l_{1}) (GeV)', texY = 'Number of Events',
#    name = 'l1_mediumId', attribute = lambda event, sample: event.l1_mediumId,
#    binning=[2,0,2], 
#  ))
#
#  plots.append(Plot(
#    texX = 'mediumPromptId(l_{1}) (GeV)', texY = 'Number of Events',
#    name = 'l1_mediumPromptId', attribute = lambda event, sample: event.l1_mediumPromptId,
#    binning=[2,0,2], 
#  ))



  plots.append(Plot(
    texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "l2_pt/F" ),
    binning=[20,0,100], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    texX = 'p_{T} error(l_{2}) (GeV)', texY = 'Number of Events / 15 GeV',
    name = 'l2_ptErr', attribute = lambda event, sample: event.l2_ptErr,
    binning=[20,0,100],
  ))

  plots.append(Plot(
    texX = 'ptErr/pt(p_{T})(l_{2}) (GeV)', texY = 'Number of Events / 15 GeV',
    name = 'l2_ptSig', attribute = lambda event, sample: (event.l2_ptErr/event.l2_pt),
    binning=[50,0,2],
  ))

  plots.append(Plot(
    texX = '#eta(l_{2})', texY = 'Number of Events',
    name = 'l2_eta', attribute = lambda event, sample: abs(event.l2_eta), read_variables = ['l2_eta/F'],
    binning=[15,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(l_{2})', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "l2_phi/F" ),
    binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    texX = 'd_{xy}(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_dxy', attribute = lambda event, sample: event.l2_dxy,
    binning=[50,-.05,.05],
  ))

  plots.append(Plot(
    texX = 'error d_{xy}(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_dxyErr', attribute = lambda event, sample: event.l2_dxyErr,
    binning=[50,0,0.05],
  ))

  plots.append(Plot(
    texX = 'd_{z}(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_dz', attribute = lambda event, sample: event.l2_dz,
    binning=[50,-.05,.05], addOverFlowBin = 'both',
  ))

  plots.append(Plot(
    texX = 'error d_{z}(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_dzErr', attribute = lambda event, sample: event.l2_dzErr,
    binning=[50,0,0.05], addOverFlowBin = 'both',
  ))

  plots.append(Plot(
    texX = 'ip3d(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_ip3d', attribute = lambda event, sample: event.l2_ip3d,
    binning=[50,-.05,.05], addOverFlowBin = 'both',
  ))

  plots.append(Plot(
    texX = 'relIso(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_jetRelIso', attribute = lambda event, sample: event.l2_jetRelIso,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_miniPFRelIso_all', attribute = lambda event, sample: event.l2_miniPFRelIso_all,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_pfRelIso03_all', attribute = lambda event, sample: event.l2_pfRelIso03_all,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_pfRelIso04_all', attribute = lambda event, sample: event.l2_pfRelIso04_all,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'segmentComp(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_segmentComp', attribute = lambda event, sample: event.l2_segmentComp,
    binning=[50,0,1], 
  ))

  plots.append(Plot(
    texX = 'sip3d(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_sip3d', attribute = lambda event, sample: event.l2_sip3d,
    binning=[10,0,10], 
  ))

#  plots.append(Plot(
#    texX = 'mvaTTH(l_{2}) (GeV)', texY = 'Number of Events',
#    name = 'l2_mvaTTH', attribute = lambda event, sample: event.l2_mvaTTH,
#    binning=[50,-10,10], addOverFlowBin = 'both', 
#  ))
#?
  plots.append(Plot(
    texX = 'charge(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_charge', attribute = lambda event, sample: event.l2_charge,
    binning=[3,-1,1], 
  ))

  plots.append(Plot(
    texX = 'nStations(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_nStations', attribute = lambda event, sample: event.l2_nStations,
    binning=[20,0,20], addOverFlowBin = 'both',
  ))
#?
  plots.append(Plot(
    texX = 'nTrackerLayers(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_nTrackerLayers', attribute = lambda event, sample: event.l2_nTrackerLayers,
    binning=[20,0,20], 
  ))

  plots.append(Plot(
    texX = 'pdgId(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_pdgId', attribute = lambda event, sample: event.l2_pdgId,
    binning=[26,-13,13],
  ))

  plots.append(Plot(
    texX = 'highPtId(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_highPtId', attribute = lambda event, sample: event.l2_highPtId,
    binning=[3,0,3],  
  ))

  plots.append(Plot(
    texX = 'inTimeMuon(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_inTimeMuon', attribute = lambda event, sample: event.l2_inTimeMuon,
    binning=[50,-.2,.2], addOverFlowBin = 'both', 
  ))
#?
#  plots.append(Plot(
#    texX = 'mediumId(l_{2}) (GeV)', texY = 'Number of Events',
#    name = 'l2_mediumId', attribute = lambda event, sample: event.l2_mediumId,
#    binning=[2,0,2], 
#  ))
#
#  plots.append(Plot(
#    texX = 'mediumPromptId(l_{2}) (GeV)', texY = 'Number of Events',
#    name = 'l2_mediumPromptId', attribute = lambda event, sample: event.l2_mediumPromptId,
#    binning=[2,0,2], 
#  ))
 
  plotting.fill(plots, read_variables = read_variables, sequence = sequence)

  # Get normalization yields from yield histogram
  for plot in plots:
    if plot.name == "yield":
      for i, l in enumerate(plot.histos):
        for j, h in enumerate(l):
          yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
          h.GetXaxis().SetBinLabel(1, "#mu#mu")
          h.GetXaxis().SetBinLabel(2, "e#mu")
          h.GetXaxis().SetBinLabel(3, "ee")
  if args.noData: yields[mode]["data"] = 0
  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
  dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

  drawPlots(plots, mode, dataMCScale)
  allPlots[mode] = plots

# Add the different channels into SF and all
for mode in ["SF","all"]:
  yields[mode] = {}
  for y in yields[allModes[0]]:
    try:    yields[mode][y] = sum(yields[c][y] for c in (['ee','mumu'] if mode=="SF" else ['ee','mumu','mue']))
    except: yields[mode][y] = 0
  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

  for plot in allPlots['mumu']:
    for plot2 in (p for p in (allPlots['ee'] if mode=="SF" else allPlots["mue"]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
	for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
	  if i==k:
	    j.Add(l)

  drawPlots(allPlots['mumu'], mode, dataMCScale)


logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )


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
from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

# JEC corrector
from JetMET.JetCorrector.JetCorrector    import JetCorrector, correction_levels_data, correction_levels_mc
corrector_data     = JetCorrector.fromTarBalls( [(1, 'Autumn18_RunD_V8_DATA') ], correctionLevels = correction_levels_data )
corrector_mc       = JetCorrector.fromTarBalls( [(1, 'Autumn18_RunD_V8_DATA') ], correctionLevels = correction_levels_mc )

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
argParser.add_argument('--selection',          action='store',      default='lepSel-POGMetSig12-njet2p-btag0-miniIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
argParser.add_argument('--study',              action='store', type=str,      default=None, choices = [None, "Muon", "Electron"])
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
argParser.add_argument('--dpm',                action='store_true', default=False)
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
if args.reweightPU:                   args.plot_directory += "_%s"%args.reweightPU
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

# Load from DPM?
if args.dpm:
    data_directory          = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

if year == 2016:
    from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
    mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_HT_LO_16]
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_HT_LO_17]
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
	    scaling = {0:1},
	    legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
	    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
        copyIndexPHP = True, extensions = ["png"],
      )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I", "nGoodLeptons/I", "nlep/I", "nJet/I"]
read_variables += [
            "l1_pdgId/I", "l2_pdgId/I",
            "Jet[pt/F,rawFactor/F,pt_nom/F,eta/F,area/F]", "run/I", "fixedGridRhoFastjetAll/F",
            "nMuon/I", 
            "Muon[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,cleanmask/b]",
            "nElectron/I",
            "Electron[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,phi/F,pt/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,pdgId/I,tightCharge/I]" 
            ]

sequence = []

def make_variables( event, sample ):
    if sample.mode == "mumu":
        pdgID = 13
        lep = "mu"
        Lepton = "Muon"
    elif sample.mode == "ee":
        pdgID = 11
        lep = "ele"
        Lepton = "Electron"

    for i in [1,2]:
        if sample.isData:
            setattr(event, "l"+str(i)+"_"+lep+"Index", -1)
            for j in range(getattr(event, "n"+Lepton)):
                if getattr(event, "l"+str(i)+"_pt")==getattr(event, Lepton+"_pt")[j]:
                    setattr(event, "l"+str(i)+"_"+lep+"Index", j)
                if getattr(event, "l"+str(i)+"_pt")==getattr(event, Lepton+"_pt")[j]:
                    setattr(event, "l"+str(i)+"_"+lep+"Index", j)

        lepIdx = getattr(event, "l"+str(i)+"_"+lep+"Index")
        if abs(getattr(event, "l"+str(i)+"_pdgId"))==pdgID and lepIdx>=0:
            nLepton = getattr(event, "nElectron") + getattr(event, "nMuon")
            if lepIdx+1 > nLepton: 
                print "lepIndex > nLeptons: ", str(lepIdx+1), " > ", nLepton

            setattr(event, "l"+str(i)+"_dxy", getattr(event, Lepton+"_dxy")[lepIdx])
            setattr(event, "l"+str(i)+"_dxyErr", getattr(event, Lepton+"_dxyErr")[lepIdx])
            setattr(event, "l"+str(i)+"_dz", getattr(event, Lepton+"_dz")[lepIdx])
            setattr(event, "l"+str(i)+"_dzErr", getattr(event, Lepton+"_dzErr")[lepIdx])
            setattr(event, "l"+str(i)+"_ip3d", getattr(event, Lepton+"_ip3d")[lepIdx])
            setattr(event, "l"+str(i)+"_jetRelIso", getattr(event, Lepton+"_jetRelIso")[lepIdx])
            setattr(event, "l"+str(i)+"_miniPFRelIso_all", getattr(event, Lepton+"_miniPFRelIso_all")[lepIdx])
            setattr(event, "l"+str(i)+"_pfRelIso03_all", getattr(event, Lepton+"_pfRelIso03_all")[lepIdx])
            setattr(event, "l"+str(i)+"_pt", getattr(event, Lepton+"_pt")[lepIdx])
            setattr(event, "l"+str(i)+"_sip3d", getattr(event, Lepton+"_sip3d")[lepIdx])
            setattr(event, "l"+str(i)+"_mvaTTH", getattr(event, Lepton+"_mvaTTH")[lepIdx])
            setattr(event, "l"+str(i)+"_charge", getattr(event, Lepton+"_charge")[lepIdx])
            # Jet_pt
            # Electron_jetIdx
            # l1_eleIndex
            # nJetGood
            jetIdx_for_lepton = getattr(event, Lepton+"_jetIdx")[lepIdx]
            if jetIdx_for_lepton > getattr(event, "nJet"):
                print "jetIdx > nJet:"
                print str(jetIdx_for_lepton+1) 
                print str(getattr(event, "nJet"))

            try:
                setattr(event, "l"+str(i)+"_jetRelIsoCalc", (event.Jet_pt[jetIdx_for_lepton]-getattr(event, "l"+str(i)+"_pt"))/getattr(event, "l"+str(i)+"_pt"))
                setattr(event, "l"+str(i)+"_jetRawPt", event.Jet_pt[jetIdx_for_lepton]*(1-event.Jet_rawFactor[jetIdx_for_lepton]))
                setattr(event, "l"+str(i)+"_jetRelIsoCalcRaw", (getattr(event, "l"+str(i)+"_jetRawPt")-getattr(event, "l"+str(i)+"_pt"))/getattr(event, "l"+str(i)+"_pt"))
                setattr(event, "l"+str(i)+"_jetRelIsoNom", (event.Jet_pt_nom[jetIdx_for_lepton]-getattr(event, "l"+str(i)+"_pt"))/getattr(event, "l"+str(i)+"_pt") )

                corrector = corrector_data if sample.isData else corrector_mc
                setattr(event, "l"+str(i)+"_jetPtRecorrected", getattr(event, "l"+str(i)+"_jetRawPt")*corrector.correction( getattr(event, "l"+str(i)+"_jetRawPt"), event.Jet_eta[jetIdx_for_lepton], event.Jet_area[jetIdx_for_lepton], event.fixedGridRhoFastjetAll, event.run ) )
                setattr(event, "l"+str(i)+"_jetRelIsoRecorr", (getattr(event, "l"+str(i)+"_jetPtRecorrected")-getattr(event, "l"+str(i)+"_pt"))/getattr(event, "l"+str(i)+"_pt"))

                if (getattr(event, "l"+str(i)+"_jetRawPt") - getattr(event, "l"+str(i)+"_pt")) >= 15:
                    jetPtHad = (getattr(event, "l"+str(i)+"_jetRawPt") - getattr(event, "l"+str(i)+"_pt"))*corrector.correction( getattr(event, "l"+str(i)+"_jetRawPt") - getattr(event, "l"+str(i)+"_pt"), event.Jet_eta[jetIdx_for_lepton], event.Jet_area[jetIdx_for_lepton], event.fixedGridRhoFastjetAll, event.run ) 
                else:
                    jetPtHad = getattr(event, "l"+str(i)+"_jetRawPt") - getattr(event, "l"+str(i)+"_pt")
                setattr(event, "l"+str(i)+"_jetRelIsoRecorrHad", (jetPtHad)/getattr(event, "l"+str(i)+"_pt"))
            except:
                pass
            # not in Electron
            if Lepton is "Muon":
                setattr(event, "l"+str(i)+"_ptErr", getattr(event, Lepton+"_ptErr")[lepIdx])
                setattr(event, "l"+str(i)+"_pfRelIso04_all", getattr(event, Lepton+"_pfRelIso04_all")[lepIdx])
                setattr(event, "l"+str(i)+"_segmentComp", getattr(event, Lepton+"_segmentComp")[lepIdx])
                setattr(event, "l"+str(i)+"_nStations", getattr(event, Lepton+"_nStations")[lepIdx])
                setattr(event, "l"+str(i)+"_nTrackerLayers", getattr(event, Lepton+"_nTrackerLayers")[lepIdx])
                setattr(event, "l"+str(i)+"_highPtId", ord(getattr(event, Lepton+"_highPtId")[lepIdx]))
                setattr(event, "l"+str(i)+"_inTimeMuon", getattr(event, Lepton+"_inTimeMuon")[lepIdx])
        else:
            setattr(event, "l"+str(i)+"_dxy", float('nan'))
            setattr(event, "l"+str(i)+"_dxyErr", float('nan'))
            setattr(event, "l"+str(i)+"_dz", float('nan'))
            setattr(event, "l"+str(i)+"_dzErr", float('nan'))
            setattr(event, "l"+str(i)+"_ip3d", float('nan'))
            setattr(event, "l"+str(i)+"_jetRelIso", float('nan'))
            setattr(event, "l"+str(i)+"_miniPFRelIso_all", float('nan'))
            setattr(event, "l"+str(i)+"_pfRelIso03_all", float('nan'))
            setattr(event, "l"+str(i)+"_pt", float('nan'))
            setattr(event, "l"+str(i)+"_sip3d", float('nan'))
            setattr(event, "l"+str(i)+"_mvaTTH", float('nan'))
            setattr(event, "l"+str(i)+"_charge", float('nan'))

            #setattr(event, "l"+str(i)+"_jetRelIsoCalc", float('nan'))
            setattr(event, "l"+str(i)+"_jetRelIsoCalcRaw", float('nan'))
            setattr(event, "l"+str(i)+"_jetRawPt", float('nan'))
            setattr(event, "l"+str(i)+"_jetRelIsoNom", float('nan'))
            setattr(event, "l"+str(i)+"_jetPtRecorrected", float('nan'))
            setattr(event, "l"+str(i)+"_jetRelIsoRecorr", float('nan'))
            setattr(event, "l"+str(i)+"_jetRelIsoRecorrHad", float('nan'))
            
            if Lepton is "Muon":
                setattr(event, "l"+str(i)+"_ptErr", float('nan'))
                setattr(event, "l"+str(i)+"_pfRelIso04_all", float('nan'))
                setattr(event, "l"+str(i)+"_segmentComp", float('nan'))
                setattr(event, "l"+str(i)+"_nStations", float('nan'))
                setattr(event, "l"+str(i)+"_nTrackerLayers", float('nan'))
                setattr(event, "l"+str(i)+"_highPtId", float('nan'))
                setattr(event, "l"+str(i)+"_inTimeMuon", float('nan'))


sequence.append( make_variables )

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
allModes   = ['ee']
#allModes   = ['mumu','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}

  # little hack to have mode in sequence
  for s in [data_sample]+mc:
    s.mode = mode

  data_sample.setSelectionString([getFilterCut(isData=True, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
  data_sample.name           = "data"
  data_sample.read_variables = ["event/I", "run/I", "reweightHEM/F"]
  data_sample.style          = styles.errorStyle(ROOT.kBlack)
  data_sample.weight = lambda event, sample: event.weight*event.reweightHEM
  weight_ = lambda event, sample: event.weight

  for sample in mc:
    sample.read_variables = ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F', "l1_muIndex/I", "l2_muIndex/I", "l1_eleIndex/I", "l2_eleIndex/I", "reweightHEM/F"]
    sample.read_variables += ['reweightPU%s/F'%args.reweightPU if args.reweightPU != "Central" else "reweightPU/F"]
    if args.reweightPU == 'Central':
        sample.weight         = lambda event, sample: event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF*event.reweightHEM
    else:
        sample.weight         = lambda event, sample: getattr(event, "reweightPU"+args.reweightPU if args.reweightPU != "Central" else "reweightPU")*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF*event.reweightHEM
    sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])

  for sample in mc: sample.style = styles.fillStyle(sample.color)

  if not args.noData:
    stack = Stack(mc, data_sample)
  else:
    stack = Stack(mc)

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
  #Plot.setDefaults(stack = stack, selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
  
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
    texX = 'miniRelIso(l_{1}) (GeV)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "l1_miniRelIso/F" ),
    binning=[30,0,0.3], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    texX = 'jet raw p_{T}(l_{1})', texY = 'Number of Events',
    name = 'l1_jet_pt_raw', attribute = lambda event, sample: event.l1_jetRawPt,
    binning=[20,0,100], addOverFlowBin = 'upper',
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
    texX = 'error d_{xy}(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_dxyErrZoom', attribute = lambda event, sample: event.l1_dxyErr,
    binning=[50,0,0.02],
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
    binning=[50,0,.05], addOverFlowBin = 'both',
  ))

  plots.append(Plot(
    texX = 'jetRelIso(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_jetRelIso', attribute = lambda event, sample: event.l1_jetRelIso,
    binning=[50,-.15,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso(l_{1}) (GeV) calculated with Jet_pt_nom', texY = 'Number of Events',
    name = 'l1_jetRelIsoNom', attribute = lambda event, sample: event.l1_jetRelIsoNom,
    binning=[50,-.15,.5], 
  ))

#  plots.append(Plot(
#    texX = 'relIso(l_{1}) (GeV) calculated with Jet_pt', texY = 'Number of Events',
#    name = 'l1_jetRelIsoCalc', attribute = lambda event, sample: event.l1_jetRelIsoCalc,
#    binning=[50,-.15,.5], 
#  ))

  plots.append(Plot(
    texX = 'relIso(l_{1}) (GeV) calculated with raw Jet_pt', texY = 'Number of Events',
    name = 'l1_jetRelIsoCalcRaw', attribute = lambda event, sample: event.l1_jetRelIsoCalcRaw,
    binning=[50,-.15,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso(l_{1}) (GeV) with recorrected Jet_pt', texY = 'Number of Events',
    name = 'l1_jetRelIsoRecorr', attribute = lambda event, sample: event.l1_jetRelIsoRecorr,
    binning=[50,-.15,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso(l_{1}) (GeV) with recorrected Jet_pt', texY = 'Number of Events',
    name = 'l1_jetRelIsoRecorrHad', attribute = lambda event, sample: event.l1_jetRelIsoRecorrHad,
    binning=[50,-.15,.5], 
  ))

  plots.append(Plot(
    texX = 'miniPF relIso(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_miniPFRelIso_all', attribute = lambda event, sample: event.l1_miniPFRelIso_all,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'pf relIso03(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_pfRelIso03_all', attribute = lambda event, sample: event.l1_pfRelIso03_all,
    binning=[50,-.15,.5], 
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
    texX = 'pdgId(l_{1}) (GeV)', texY = 'Number of Events',
    name = 'l1_pdgId', attribute = lambda event, sample: event.l1_pdgId,
    binning=[26,-13,13],
  ))

  if mode == "mumu": 
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
      texX = 'pf relIso04(l_{1}) (GeV)', texY = 'Number of Events',
      name = 'l1_pfRelIso04_all', attribute = lambda event, sample: event.l1_pfRelIso04_all,
      binning=[50,-0.15,.5], 
    ))
  
    plots.append(Plot(
      texX = 'segmentComp(l_{1}) (GeV)', texY = 'Number of Events',
      name = 'l1_segmentComp', attribute = lambda event, sample: event.l1_segmentComp,
      binning=[50,0,1], 
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
    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "l1_pt/F" ),
    binning=[20,0,100], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "l2_pt/F" ),
    binning=[20,0,100], addOverFlowBin = 'upper',
  ))

  plots.append(Plot(
    texX = 'miniRelIso(l_{2}) (GeV)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "l2_miniRelIso/F" ),
    binning=[30,0,0.3], addOverFlowBin = 'upper',
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
    texX = 'error d_{xy}(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_dxyErrFine', attribute = lambda event, sample: event.l2_dxyErr,
    binning=[50,0,0.02],
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
    binning=[50,0,.05], addOverFlowBin = 'both',
  ))

  plots.append(Plot(
    texX = 'jet relIso(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_jetRelIso', attribute = lambda event, sample: event.l2_jetRelIso,
    binning=[50,-.15,.5], 
  ))

#  plots.append(Plot(
#    texX = 'calculated jet relIso(l_{2}) (GeV)', texY = 'Number of Events',
#    name = 'l2_jetRelIsoCalc', attribute = lambda event, sample: event.l2_jetRelIsoCalc,
#    binning=[50,-.15,.5], 
#  ))

  plots.append(Plot(
    texX = 'calculated raw jet relIso(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_jetRelIsoCalcRaw', attribute = lambda event, sample: event.l2_jetRelIsoCalcRaw,
    binning=[50,-.15,.5], 
  ))

  plots.append(Plot(
    texX = 'miniPF relIso(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_miniPFRelIso_all', attribute = lambda event, sample: event.l2_miniPFRelIso_all,
    binning=[50,0,.5], 
  ))

  plots.append(Plot(
    texX = 'relIso03(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_pfRelIso03_all', attribute = lambda event, sample: event.l2_pfRelIso03_all,
    binning=[50,-.15,.5], 
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
    texX = 'pdgId(l_{2}) (GeV)', texY = 'Number of Events',
    name = 'l2_pdgId', attribute = lambda event, sample: event.l2_pdgId,
    binning=[26,-13,13],
  ))

  if mode == "mumu":
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
      texX = 'relIso04(l_{2}) (GeV)', texY = 'Number of Events',
      name = 'l2_pfRelIso04_all', attribute = lambda event, sample: event.l2_pfRelIso04_all,
      binning=[50,-.15,.5], 
    ))
  
    plots.append(Plot(
      texX = 'segmentComp(l_{2}) (GeV)', texY = 'Number of Events',
      name = 'l2_segmentComp', attribute = lambda event, sample: event.l2_segmentComp,
      binning=[50,0,1], 
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
#for mode in ["SF","all"]:
#  yields[mode] = {}
#  for y in yields[allModes[0]]:
#    try:    yields[mode][y] = sum(yields[c][y] for c in (['ee','mumu'] if mode=="SF" else ['ee','mumu']))
#    except: yields[mode][y] = 0
#  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
#
#  for plot in allPlots['mumu']:
#    for plot2 in (p for p in (allPlots['ee'] if mode=="SF" else allPlots["mue"]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
#      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
#	for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
#	  if i==k:
#	    j.Add(l)
#
#  drawPlots(allPlots['mumu'], mode, dataMCScale)


logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection) )


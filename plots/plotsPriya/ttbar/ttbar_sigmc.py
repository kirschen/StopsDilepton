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
argParser.add_argument('--signal',             action='store',      default=None,            nargs='?', choices=[None, "T2tt", "DM", "T8bbllnunu", "compilation"], help="Add signal to plot")
argParser.add_argument('--noData',             action='store_true', default=False,           help='also plot data?')
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--dataMCScaling',      action='store_true',     help='Data MC scaling?', )
argParser.add_argument('--plot_directory',     action='store',      default='v04_ttbardist')
argParser.add_argument('--era',                action='store', type=str,      default="2016")
argParser.add_argument('--recoil',             action='store', type=str,      default=None, choices = ["nvtx", "VUp", None])
#argParser.add_argument('--selection',          action='store',      default='lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
argParser.add_argument('--selection',          action='store',      default='lepSel-POGMetSig12-njet2p-btag0-miniIso0.1-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
#argParser.add_argument('--selection',          action='store',      default='lepSel-POGMetSig12-njet2p-btag0-miniIso0.2-looseLeptonVeto-mll20-badEEJetVeto-dPhiJet0-dPhiJet1')
#argParser.add_argument('--selection',          action='store',      default='lepSel-POGMetSig12-njet2p-btag0-miniIso0.1-looseLeptonVeto-mll20-badEEJetVeto-dPhiJet0-dPhiJet1')
#argParser.add_argument('--selection',          action='store',      default='lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
#argParser.add_argument('--selection',          action='store',      default='lepSel-POGMetSig12-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-badEEJetVeto-dPhiJet0-dPhiJet1')
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
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

if args.recoil:                       args.plot_directory += '_recoil_'+args.recoil
if args.small:                        args.plot_directory += "_small"
if args.noData:                       args.plot_directory += "_noData"
if args.splitBosons:                  args.plot_directory += "_splitMultiBoson"
if args.splitBosons2:                 args.plot_directory += "_splitMultiBoson2"
if args.signal == "DM":               args.plot_directory += "_DM"
if args.badMuonFilters!="Summer2016": args.plot_directory += "_badMuonFilters_"+args.badMuonFilters
if args.reweightPU:                   args.plot_directory += "_%s"%args.reweightPU
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
    mc             = [ Top_pow_16, DY_HT_LO_16, multiBoson_16, TTXNoZ_16, TTZ_16]
    #if args.reweightPU and not args.reweightPU in ["noPUReweighting", "nvtx"]:
    #    nTrueInt_puRW = getReweightingFunction(data="PU_2016_35920_XSec%s"%args.reweightPU, mc="Summer16")
elif year == 2017:
    from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
    mc             = [ Top_pow_17,DY_HT_LO_17, multiBoson_17, TTXNoZ_17, TTZ_17]
    #if args.reweightPU:
    #    # need sample based weights
    #    pass
elif year == 2018:
    from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
    from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
    mc             = [ Top_pow_18, DY_HT_LO_18, multiBoson_18, TTXNoZ_18, TTZ_18]

    #from StopsDilepton.tools.vetoList import vetoList
    #Run2018D.vetoList = vetoList.fromDirectory('/afs/hephy.at/data/rschoefbeck02/StopsDilepton/splitMuonVeto/')
    #if args.reweightPU and not args.reweightPU in ["noPUReweighting", "nvtx"]:
    #    nTrueInt_puRW = getReweightingFunction(data="PU_2018_58830_XSec%s"%args.reweightPU, mc="Autumn18")

try:
  data_sample = eval(args.era)
except Exception as e:
  logger.error( "Didn't find %s", args.era )
  raise e

lumi_scale                 = data_sample.lumi/1000
data_sample.scale          = 1.
for sample in mc:
    sample.scale          = lumi_scale

## Four TTbar with different selections 
#TTbars = [copy.deepcopy(mc[0]) for i in range(4)] 
#TTbars[3].texName = "t#bar{t}:1 mismjet>40" 
#TTbars[3].color = ROOT.kCyan 
#TTbars[3].addSelectionString('Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) >=1' ) 
##print TTbars[3].selectionString 
#TTbars[2].texName = "t#bar{t}:~1& tot mismjet>40" 
#TTbars[2].color = ROOT.kCyan + 1 
#TTbars[2].addSelectionString('Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) >= 40') 
# 
# 
#TTbars[1].texName = "t#bar{t}:~1,2 & 1 promptlep" 
#TTbars[1].color = ROOT.kCyan + 2 
#TTbars[1].addSelectionString('Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) < 40 && ((l1_muIndex>=0 && (Muon_genPartFlav[l1_muIndex])!=1) || (l2_muIndex>=0 && (Muon_genPartFlav[l2_muIndex])!=1))') 
# 
#TTbars[0].texName = "t#bar{t}:~1,2,3" 
#TTbars[0].color = ROOT.kCyan + 3 
#TTbars[0].addSelectionString('Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) < 40 && (!((l1_muIndex>=0 && (Muon_genPartFlav[l1_muIndex])!=1) || (l2_muIndex>=0 && (Muon_genPartFlav[l2_muIndex])!=1)))') 
#mc = mc[1:3] + TTbars + mc[3:5] 


if args.small:
    for sample in mc + [data_sample]:
        sample.normalization = 1.
        sample.reduceFiles( factor = 40 )
        #sample.reduceFiles( to=4)
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
      if (not args.noData) and (len(plot.histos)>1) : 
        if mode == "all": plot.histos[1][0].legendText = "Data"
        if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"

      _drawObjects = []

      plotting.draw(plot,
	    plot_directory = plot_directory_,
	    ratio = {'yRange':(0.1,1.9)} if (not args.noData) and (len(plot.histos)>1) else None,
	    logX = False, logY = log, sorting = False,
	    yRange = (0.03, "auto") if log else (0.001, "auto"),
	    scaling = {0:1} if args.dataMCScaling else {},
        
	    legend = ( (0.18,0.88-0.03*sum(map(len, plot.histos)),0.9,0.88), 2),
	    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ) + _drawObjects,
        copyIndexPHP = True, extensions = ["png"],
      )

#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_pt/F", "dl_phi/F", "dl_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F","l1_muIndex/I", "l2_muIndex/I" ,"JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F", "met_pt/F", "met_phi/F", "MET_significance/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "PV_npvsGood/I", "RawMET_pt/F", "RawMET_phi/F", "event/l", "luminosityBlock/I", "run/I"]
#read_variables += ["Muon[dxy/F,dxyErr/F,dz/F,dzErr/F,eta/F,ip3d/F,jetRelIso/F,mass/F,miniPFRelIso_all/F,miniPFRelIso_chg/F,pfRelIso03_all/F,pfRelIso03_chg/F,pfRelIso04_all/F,phi/F,pt/F,ptErr/F,segmentComp/F,sip3d/F,mvaTTH/F,charge/I,jetIdx/I,nStations/I,nTrackerLayers/I,pdgId/I,tightCharge/I,highPtId/b,inTimeMuon/O,isGlobal/O,isPFcand/O,isTracker/O,mediumId/O,mediumPromptId/O,miniIsoId/b,multiIsoId/b,mvaId/b,pfIsoId/b,softId/O,softMvaId/O,tightId/O,tkIsoId/b,triggerIdLoose/O,genPartIdx/I,genPartFlav/b,cleanmask/b]",

for sample in mc:
    sample.read_variables  = [ "JetGood[genPt/F]" ] 

sequence = []
def makeWeight(event, sample):
    print event.weight

sequence.append(makeWeight)



# default offZ for SF
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""
def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ
  elif mode=="SF":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" + offZ
  elif mode=="all":   return "nGoodMuons+nGoodElectrons==2&&isOS&&(((isEE||isMuMu)" + offZ+")||isEMu)"

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
  #data_sample.texName        = "%s"
  data_sample.read_variables = ["event/I","run/I", "reweightHEM/F"]
  data_sample.style          = styles.errorStyle(ROOT.kBlack)
#                    weight_  = lambda event, sample: event.weight * event.reweightHEM
  if year == 2018:
    weight_ = lambda event, sample: event.weight*event.reweightHEM
    print "2018"
    print weight_
  else:
    weight_ = lambda event, sample: event.weight

  for sample in mc:
    sample.read_variables += ['reweightPU/F', 'Pileup_nTrueInt/F', 'reweightDilepTrigger/F','reweightLeptonSF/F','reweightBTag_SF/F', 'reweightLeptonTrackingSF/F', 'GenMET_pt/F', 'GenMET_phi/F','reweightL1Prefire/F','reweightHEM/F']
    if args.reweightPU and args.reweightPU not in ["noPUReweighting", "nvtx"]:
        sample.read_variables.append('reweightPU/F' if args.reweightPU=='Central' else 'reweightPU%s/F'%args.reweightPU )
    if args.reweightPU == "noPUReweighting":
        sample.weight         = lambda event, sample: event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF*event.reweightL1Prefire
    elif args.reweightPU == "nvtx":
        sample.weight         = lambda event, sample: nvtx_puRW(event.PV_npvsGood) * event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF*event.reweightL1Prefire
    elif args.reweightPU:
        pu_getter = operator.attrgetter('reweightPU' if args.reweightPU=='Central' else "reweightPU%s"%args.reweightPU)
        sample.weight         = lambda event, sample: pu_getter(event) * event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF*event.reweightL1Prefire
    else: #default

        sample.weight         = lambda event, sample: event.reweightPU*event.reweightDilepTrigger*event.reweightLeptonSF*event.reweightBTag_SF*event.reweightLeptonTrackingSF*event.reweightL1Prefire
    sample.setSelectionString([getFilterCut(isData=False, year=year, skipBadPFMuon=args.noBadPFMuonFilter, skipBadChargedCandidate=args.noBadChargedCandidateFilter), getLeptonSelection(mode)])
   # # Four TTbar with different selections 
  TTbars = [copy.deepcopy(mc[0]) for i in range(4)] 
  TTbars[3].texName = "t#bar{t}:1 mismjet>40" 
  TTbars[3].color = ROOT.kCyan 
  TTbars[3].addSelectionString('Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) >=1' ) 
  #print TTbars[3].selectionString 
  TTbars[2].texName = "t#bar{t}:~1& tot mismjet>40" 
  TTbars[2].color = ROOT.kCyan + 1 
  TTbars[2].addSelectionString('Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) >= 40') 
   
   
  TTbars[1].texName = "t#bar{t}:~1,2 & 1 promptlep" 
  TTbars[1].color = ROOT.kCyan + 2 
  TTbars[1].addSelectionString('Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) < 40 && ((l1_muIndex>=0 && (Muon_genPartFlav[l1_muIndex])!=1) || (l2_muIndex>=0 && (Muon_genPartFlav[l2_muIndex])!=1))') 
     
  TTbars[0].texName = "t#bar{t}:~1,2,3" 
  TTbars[0].color = ROOT.kCyan + 3 
  TTbars[0].addSelectionString('Sum$( abs(JetGood_pt - JetGood_genPt) >= 40) ==0 && Sum$(abs(JetGood_pt - JetGood_genPt)) < 40 && (!((l1_muIndex>=0 && (Muon_genPartFlav[l1_muIndex])!=1) || (l2_muIndex>=0 && (Muon_genPartFlav[l2_muIndex])!=1)))') 
  mc1 = mc[1:3] + TTbars + mc[3:5]
    
  for sample in mc1: sample.style = styles.fillStyle(sample.color)
    
  if not args.noData:
    stack = Stack(mc1, data_sample)
  else:
    stack = Stack(mc1)
  # Use some defaults
  Plot.setDefaults(stack = stack, weight = staticmethod(weight_), selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper', histo_class=ROOT.TH1D)
  
  plots = []

    #  plots.append(Plot(name="dl_mt2ll_onlyGoodJets50", 
#     texX = 'M_{T2}(ll) onlyGoodJets_mism>=50 (GeV)', texY = 'Number of Events / 20 GeV',
#     attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
#     weight = lambda event, sample: event.onlyGoodJets, 
#     binning=[400/20, 0,400]),
#  )
#  plots.append(Plot( name = "dl_mt2ll_nonePromptPair",
#    texX = 'M_{T2}(ll)no Prompt Pair(GeV)', texY = 'Number of Events / 20 GeV',
#    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
#    weight = lambda event, sample: event.PrPr , 
#    binning=[400/20, 0,400]),
# 
# )

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    attribute = lambda event, sample: 0.5 + index,
    binning=[3, 0, 3],
  ))
  binningmt2=[0,20,40,60,80,100,140,240,340]
  plots.append(Plot(
    texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    binning=Binning.fromThresholds(binningmt2),
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

  plots.append(Plot( name = "met_pt_raw",
      texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "RawMET_pt/F" ),
      binning=[400/20,0,400],
  ))

  plots.append(Plot(
      texX = 'E_{T}^{miss} significance', texY = 'Number of Events',
      attribute = TreeVariable.fromString( "MET_significance/F" ),
      binning=[40,0,100],
  ))
  plots.append(Plot(
      texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "met_phi/F" ),
      binning=[10,-pi,pi],
  ))

  plots.append(Plot( name = "met_phi_raw",
      texX = 'raw #phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
      attribute = TreeVariable.fromString( "RawMET_phi/F" ),
      binning=[10,-pi,pi],
  ))
  plots.append(Plot(
    texX = 'number of jets', texY = 'Number of Events',
    attribute = TreeVariable.fromString('nJetGood/I'),
    binning=[14,0,14],
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
    texX = 'm(ll) of leading dilepton (GeV)', texY = 'Number of Events / 4 GeV',
    attribute = TreeVariable.fromString( "dl_mass/F" ),
    binning=[200/4,0,200],
  ))
  plots.append(Plot(
    texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 10 GeV',
    attribute = TreeVariable.fromString( "dl_pt/F" ),
    binning=[20,0,400],
  ))
  plots.append(Plot(
    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 15 GeV',
    attribute = TreeVariable.fromString( "l1_pt/F" ),
    binning=[20,0,300],
  ))
  plots.append(Plot(
    texX = '#phi(l_{1})', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "l1_phi/F" ),
    binning=[10,-pi,pi],
  ))
  # Plots only when at least one jet:
  if args.selection.count('njet2') or args.selection.count('njet1') or args.selection.count('njet01'):
    plots.append(Plot(
      texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet1_pt', attribute = lambda event, sample: event.JetGood_pt[0],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      stack =  Stack(mc1),
      texX = 'genp_{T}(1st leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'genjet1_pt', attribute = lambda event, sample: event.JetGood_genPt[0],
      binning=[600/30,0,600],
    ))


#  # Plots only when at least two jets:
  if args.selection.count('njet2'):
    plots.append(Plot(
      texX = 'p_{T}(2nd leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'jet2_pt', attribute = lambda event, sample: event.JetGood_pt[1],
      binning=[600/30,0,600],
    ))
    plots.append(Plot(
      stack =  Stack(mc1),
      texX = 'genp_{T}(2nd leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      name = 'genjet2_pt', attribute = lambda event, sample: event.JetGood_genPt[1],
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
      name = 'cosZJet2phi',
      texX = 'Cos(#Delta#phi(Z, 2nd leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.dl_phi - event.JetGood_phi[0] ),
      read_variables = ["dl_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      name = 'cosJet1Jet2phi',
      texX = 'Cos(#Delta#phi(leading jet, 2nd leading jet))', texY = 'Number of Events',
      attribute = lambda event, sample: cos( event.JetGood_phi[1] - event.JetGood_phi[0] ) ,
      read_variables =  ["JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      texX = 'M_{T2}(bb) (GeV)', texY = 'Number of Events / 30 GeV',
      attribute = TreeVariable.fromString( "dl_mt2bb/F" ),
      binning=[420/30,70,470],
    ))

    mt2blblbin= [0,20,40,60,80,100,120,140,160,200,250,300,350]
    plots.append(Plot(
      texX = 'M_{T2}(blbl) (GeV)', texY = 'Number of Events / 30 GeV',
      attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
      binning=Binning.fromThresholds(mt2blblbin),
    ))
    plots.append(Plot( name = "dl_mt2blbl_coarse",       # SR binning of MT2ll
      texX = 'M_{T2}(blbl) (GeV)', texY = 'Number of Events / 30 GeV',
      attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
      binning=Binning.fromThresholds(mt2blblbin),
    ))

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

  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc1)
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


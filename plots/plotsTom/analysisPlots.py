#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)

from math                                import sqrt, cos, sin, pi
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.objectSelection import getFilterCut
from StopsDilepton.plots.pieChart        import makePieChart
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
<<<<<<< HEAD
argParser.add_argument('--logLevel',       action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',         action='store',      default='T2tt',          nargs='?', choices=[None, "T2tt", "DM", "T8"], help="Add signal to plot")
argParser.add_argument('--noData',         action='store_true', default=False,           help='do not plot data?')
=======
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',         action='store',      default=None,        nargs='?', choices=[None, "T2tt", "DM"], help="Add signal to plot")
argParser.add_argument('--plotData',       action='store_true', default=False,       help='also plot data?')
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca
argParser.add_argument('--plot_directory', action='store',      default='analysisPlots')
argParser.add_argument('--selection',      action='store',      default=None)
argParser.add_argument('--runLocal',       action='store_true', default=False)
argParser.add_argument('--scaleDYVV',      action='store_true', default=False)
argParser.add_argument('--LO',             action='store_true', default=False)
argParser.add_argument('--splitBosons',    action='store_true', default=False)
argParser.add_argument('--splitBosons2',   action='store_true', default=False)
argParser.add_argument('--isChild',        action='store_true', default=False)
argParser.add_argument('--dryRun',         action='store_true', default=False,           help='do not launch subjobs')
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

<<<<<<< HEAD
=======
#
# Selections (two leptons with pt > 20 GeV, photon)
#
from StopsDilepton.tools.objectSelection import looseMuIDString,looseEleIDString
def getLooseLeptonString(nMu, nE):
  return looseMuIDString(ptCut=10) + "==" + str(nMu) + "&&" + looseEleIDString(ptCut=10, absEtaCut=2.5) + "==" + str(nE)

def getLeptonString(nMu, nE):
#  return getLooseLeptonString(nMu, nE)
  return "nGoodMuons==" + str(nMu) + "&&nGoodElectrons==" + str(nE) + "&&l1_pt>25"


jetSelection    = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))"
bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890))"
bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.605))"
dataFilterCut   = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&vetoPassed&&jsonPassed&&weight>0)"
mcFilterCut     = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter)"

#
# Cuts to iterate over
#
cuts = [
    ("lepVeto",           "(1)"),
    ("njet1",             jetSelection+"==1"),
    ("njet2",             jetSelection+">=2"),
    ("btag0",             bJetSelectionM+"==0"),
    ("btagM",             bJetSelectionM+">=1"),
    ("mll20",             "dl_mass>20"),
    ("allZ",              "(1)"),                        # allZ and onZ switches off the offZ selection
    ("onZ",               "abs(dl_mass-91.1876)<15"),
    ("met50",             "met_pt>50"),
    ("met80",             "met_pt>80"),
    ("metSig5",           "metSig>5"),
    ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
    ("mt2ll100",          "dl_mt2ll>100"),
  ]


# To make piecharts
from array import array
import warnings
warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='creating converter.*' )
def makePieChart(name, yields, mode, samples):
  c        = ROOT.TCanvas("pie", "pie", 700, 700)
  labels   = [ array( 'c', s.name + '\0' ) for s in samples]
  labels_  = array( 'l', map( lambda x: x.buffer_info()[0], labels ) )
  piechart = ROOT.TPie(name, name, len(samples), array('f', [yields[mode][s.name] for s in samples]), array('i', [s.color for s in samples]), labels_)
  piechart.Draw("rsc")
  c.Print(os.path.join(plot_directory, args.plot_directory, mode, args.selection, name + ".png"))

>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca

#
# Selection strings for which plots need to be produced, as interpreted by the cutInterpreter
#
<<<<<<< HEAD
selectionStrings = ['relIso0.12',
                    'relIso0.12-btag1p',
                    'njet2p-relIso0.12-btag1p',
                    'relIso0.12-allZ',
                    'relIso0.12-looseLeptonVeto',
                    'relIso0.12-looseLeptonVeto-allZ',
                    'relIso0.12-looseLeptonVeto-mll20',
                    'relIso0.12-looseLeptonVeto-mll20-allZ',
                    'njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metInv',
                    'njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5',
                    'njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-mt2ll100',
                    'njet01-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5',
                    'njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv',
                    'njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5',
                    'njet2p-relIso0.12-looseLeptonVeto-mll20',
                    'njet2p-relIso0.12-looseLeptonVeto-mll20-onZ',
                    'njet2p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-mt2ll100',
                    'njet2p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv-mt2ll100',
                    'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metInv',
                    'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5',
                    'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-mt2ll100',
                    'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5',
                    'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-mt2ll100',
                    'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv',                          # DY control
                    'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv-mt2ll100',
                    'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1',                # VV control
                    'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll0to25',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll25to50',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll50to75',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll75to100',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll140',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100',
                    'njet2p-btag1p-relIso0.12-veryLooseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1',
                    'njet2p-btag1p-relIso0.12-veryLooseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100']

selectionStrings = ['njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1',
                    'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100']

def launch(command, logfile):
  if args.runLocal: os.system(command + " --isChild &> " + logfile)
  else:             os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=20:00:00 runPlotsOnCream02.sh")
=======
import itertools
selectionStrings = {}
for i_comb in reversed( range( len(cuts)+1 ) ):
    for comb in itertools.combinations( cuts, i_comb ):
        presel = [] 
        presel.extend( comb )
        selection = '-'.join([p[0] for p in presel])
        if selection.count("onZ")    and selection.count("allZ"):       continue
        if selection.count("met80")  and not selection.count("mll"):    continue
        if selection.count("metSig") and not selection.count("met80"): continue
        if selection.count("dPhi")   and not selection.count("metSig"): continue
        if selection.count("dPhi")   and not selection.count("njet2"):  continue
        if selection.count("mt2")    and not selection.count("met"):    continue
        if selection.count("njet") > 1:    continue
        if selection.count("btag") > 1:    continue
        if selection.count("mt2ll") > 1:   continue
        if selection.count("mt2blbl") > 1: continue
        if selection.count("mt2bb") > 1:   continue
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca

#
# If this is the mother process, launch the childs and exit
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
<<<<<<< HEAD
    command = "./analysisPlots.py --selection=" + selection + (" --noData"                if args.noData       else "")\
                                                            + (" --scaleDYVV"             if args.scaleDYVV    else "")\
                                                            + (" --splitBosons2"          if args.splitBosons2 else "")\
                                                            + (" --signal=" + args.signal if args.signal       else "")\
=======
    command = "./analysisPlots.py --selection=" + selection + (" --plotData" if args.plotData else "")\
                                                            + (" --signal=" + args.signal if args.signal else "")\
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca
                                                            + (" --plot_directory=" + args.plot_directory)\
                                                            + (" --logLevel=" + args.logLevel)
    logfile = "log/" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
<<<<<<< HEAD
    if not args.dryRun:                                                                                   launch(command, logfile)
    if selection.count('njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1'): launch(command + ' --noData', logfile)
=======
    if not args.dryRun: os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=10:00:00 runPlotsOnCream02.sh")
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca
  logger.info("All jobs launched")
  exit(0)

if args.noData:                   args.plot_directory += "_noData"
if args.scaleDYVV:                args.plot_directory += "_scaleDYVV"
if args.splitBosons:              args.plot_directory += "_splitMultiBoson"
if args.splitBosons2:             args.plot_directory += "_splitMultiBoson2"
if args.signal == "DM":           args.plot_directory += "_DM"
if args.signal == "T8":           args.plot_directory += "_T8bbllnunu"
if args.LO:                       args.plot_directory += "_ttZLO"
DManalysis = (args.signal == "DM")

# Plot no signal for following selections
if args.selection.count("btag0") and args.selection.count("onZ"):                                      args.signal = None
if args.selection.count("njet2p-relIso0.12-looseLeptonVeto-mll20-onZ"):                                args.signal = None
if args.selection.count("njet2p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv-mt2ll100"): args.signal = None

#
# Make samples, will be searched for in the postProcessing directory
#
<<<<<<< HEAD
postProcessing_directory = 'postProcessed_80X_v31/dilepTiny'
from StopsDilepton.samples.cmgTuples_Data25ns_80X_03Feb_postProcessed import *
postProcessing_directory = 'postProcessed_80X_v35/dilepTiny'
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *

signals = []
if args.signal == "T2tt":
  from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
  T2tt                    = T2tt_750_1
  T2tt2                   = T2tt_600_300
  T2tt2.style             = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
  T2tt.style              = styles.lineStyle( ROOT.kBlack, width=3 )
  signals                 = [T2tt, T2tt2]
elif args.signal == "DM":
  from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10, TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10
  DM                      = TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10
  DM2                     = TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10
  DM.style                = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
  DM2.style               = styles.lineStyle( ROOT.kBlack,          width=3)
  signals                 = [DM, DM2]
elif args.signal == "T8":
  from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
  from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import *
  T2tt                    = T2tt_750_1
  T8                      = T8bbllnunu_XCha0p5_XSlep0p05_1100_1
  T82                     = T8bbllnunu_XCha0p5_XSlep0p05_1100_150
  T83                     = T8bbllnunu_XCha0p5_XSlep0p05_800_200
  T2tt.style              = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
  T8.style                = styles.lineStyle( ROOT.kRed, width=3)
  T82.style               = styles.lineStyle( ROOT.kBlack, width=3 )
  T83.style               = styles.lineStyle( 28, width=3 )
  signals                 = [T2tt, T8, T82, T83]
  T8.isFastSim = False   # No FastSim SF in those trees?
  T82.isFastSim = False
  T83.isFastSim = False


=======
#postProcessing_directory = "postProcessed_Fall15_mAODv2/dilepTiny_may2"
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_postProcessed_photonSamples import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import TTbarDMJets_scalar_Mchi1_Mphi100
TTbarDMJets_scalar_Mchi1_Mphi100.texName += "(#times 10)"
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca
#
# Text on the plots
#
def drawObjects( plotData, dataMCScale, lumi_scale ):
  lumi_scale = 35.9 # fix rounding
  def drawTex(align, size, line):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(size)
    tex.SetTextAlign(align)
    return tex.DrawLatex(*line)

  lines =[
    (11,0.06,(0.15, 0.95, 'CMS' if plotData else 'CMS Simulation')), 
    (31,0.04,(0.95, 0.95, ('%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale )) if plotData else ('%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)))
  ]
  if "mt2ll100" in args.selection and args.noData: lines += [(11,0.05,(0.55, 0.5, 'M_{T2}(ll) > 100 GeV'))] # Manually put the mt2ll > 100 GeV label
  return [drawTex(*l) for l in lines] 



def drawPlots(plots, mode, dataMCScale):
  for log in [False, True]:
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      if not args.noData: 
        if mode == "all": plot.histos[1][0].legendText = "Data"
        if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"
      plotting.draw(plot,
            plot_directory = os.path.join(plot_directory, args.plot_directory, mode + ("_log" if log else ""), args.selection),
            ratio = {'yRange':(0.1,1.9), 'texY':'Obs./Exp.'} if not args.noData else None,
            logX = False, logY = log, sorting = True,
            yRange = (0.03, "auto") if log else (0.001, "auto"),
            scaling = {},
            legend = (0.55,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88) if not args.noData else (0.55,0.9-0.047*sum(map(len, plot.histos)),0.9,0.9),
            drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale ),
            copyIndexPHP = True,
            ratioModifications = [lambda h: h.GetXaxis().SetTitleOffset(4)],
            histModifications = [lambda h: h.GetXaxis().SetTitleOffset(1.15)],
      )


#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I"]

offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ")) else ""
def getLeptonSelection(mode):
  if   mode=="mumu": return "(nGoodMuons==2&&nGoodElectrons==0&&isOS&&l1_pt>25&&isMuMu" + offZ + ")"
  elif mode=="mue":  return "(nGoodMuons==1&&nGoodElectrons==1&&isOS&&l1_pt>25&&isEMu)"
  elif mode=="ee":   return "(nGoodMuons==0&&nGoodElectrons==2&&isOS&&l1_pt>25&&isEE" + offZ + ")"


<<<<<<< HEAD
def calcBJetPt(event, sample):
  bJetIndices = [j for j in range(event.nJetGood) if event.JetGood_btagCSV[j] > 0.800]
  if len(bJetIndices) > 0: event.bJetGoodPt = event.JetGood_pt[bJetIndices[0]]
  else:                    event.bJetGoodPt = -1
=======
offZ            = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ")) else ""
mumuSelection   = getLeptonString(2, 0) + "&&isOS&&isMuMu&&HLT_mumuIso" + offZ + (("&&" + getLooseLeptonString(2, 0)) if args.selection.count("lepVeto") else "")
mueSelection    = getLeptonString(1, 1) + "&&isOS&&isEMu&&HLT_mue"             + (("&&" + getLooseLeptonString(1, 1)) if args.selection.count("lepVeto") else "")
eeSelection     = getLeptonString(0, 2) + "&&isOS&&isEE&&HLT_ee_DZ" + offZ     + (("&&" + getLooseLeptonString(0, 2)) if args.selection.count("lepVeto") else "")
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca

#
# Loop over channels
#
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}
<<<<<<< HEAD
  if   mode=="mumu": data_sample = DoubleMuon_Run2016_backup
  elif mode=="ee":   data_sample = DoubleEG_Run2016_backup
  elif mode=="mue":  data_sample = MuonEG_Run2016_backup
  if   mode=="mumu": data_sample.texName = "data (2 #mu)"
  elif mode=="ee":   data_sample.texName = "data (2 e)"
  elif mode=="mue":  data_sample.texName = "data (1 #mu, 1 e)"

  data_sample.setSelectionString([getFilterCut(isData=True, badMuonFilters="Moriond2017Official"), getLeptonSelection(mode)])
  data_sample.name           = "data"
  data_sample.read_variables = ["evt/I","run/I"]
  data_sample.style          = styles.errorStyle(ROOT.kBlack)
  lumi_scale                 = data_sample.lumi/1000

  if args.noData: lumi_scale = 36
  weight_ = lambda event, sample: event.weight

  multiBosonList = [WWNo2L2Nu, WZ, ZZNo2L2Nu, VVTo2L2Nu, triBoson] if args.splitBosons else ([WW, WZ, ZZ, triBoson] if args.splitBosons2 else [multiBoson])
  mc             = [ Top_pow, TTZ_LO if args.LO else TTZ, TTXNoZ] + multiBosonList + [DY_HT_LO]

  for sample in mc: sample.style = styles.fillStyle(sample.color, lineColor = sample.color)

  for sample in mc + signals:
    if not hasattr(sample, 'isFastSim'): sample.isFastSim = False
    if   args.scaleDYVV and sample in [DY_HT_LO]:     sample.scale = lumi_scale*1.31
    elif args.scaleDYVV and sample in multiBosonList: sample.scale = lumi_scale*1.19
    else:                                             sample.scale = lumi_scale
    sample.read_variables = ['reweightLeptonTrackingSF/F','reweightTopPt/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F', 'nTrueInt/F'] + (['reweightLeptonFastSimSF/F'] if sample.isFastSim else [])
    sample.weight         = lambda event, sample: event.reweightLeptonTrackingSF*event.reweightTopPt*event.reweightLeptonSF*event.reweightDilepTriggerBackup*event.reweightPU36fb*event.reweightBTag_SF*(event.reweightLeptonFastSimSF if sample.isFastSim else 1.)
    sample.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])


  if args.noData: stack = Stack(mc, *signals)
  else:           stack = Stack(mc, data_sample, *signals)
=======
  if mode=="mumu":
    data_sample     = DoubleMuon_Run2015D
    qcd_sample      = QCD_Mu5 #FIXME
    leptonSelection = mumuSelection
  elif mode=="ee":
    data_sample     = DoubleEG_Run2015D
    qcd_sample      = QCD_EMbcToE
    leptonSelection = eeSelection
  elif mode=="mue":
    data_sample     = MuonEG_Run2015D
    qcd_sample      = QCD_Mu5EMbcToE
    leptonSelection = mueSelection

  qcd_sample.name  = "QCD"  # Give same name in all modes such that it combines easily
  data_sample.name = "data"

  data_sample.style = styles.errorStyle( ROOT.kBlack )
  if args.plotData: lumi_scale = data_sample.lumi/1000
  else:             lumi_scale = 10

  mc = [ DY_HT_LO, TTJets_Lep, singleTop, TTZ, TTXNoZ, WW, WZ, ZZ, VV, triBoson]
  for sample in mc:
    sample.scale = lumi_scale
    sample.style = styles.fillStyle(sample.color, lineColor = sample.color)

  TTbarDMJets_scalar_Mchi1_Mphi100.scale = lumi_scale*10
  TTbarDMJets_scalar_Mchi1_Mphi100.style = styles.lineStyle( ROOT.kBlack, width=3 )
  T2tt_650_250.style = styles.lineStyle( ROOT.kBlack, width=3 )

  if args.plotData:
    if not args.signal:         stack = Stack(mc, data_sample)
    elif args.signal == "DM":   stack = Stack(mc, data_sample, TTbarDMJets_scalar_Mchi1_Mphi100)
    elif args.signal == "T2tt": stack = Stack(mc, data_sample, T2tt_650_250)
  else:
    if not args.signal:         stack = Stack(mc)
    elif args.signal == "DM":   stack = Stack(mc, TTbarDMJets_scalar_Mchi1_Mphi100)
    elif args.signal == "T2tt": stack = Stack(mc, T2tt_650_250)

  data_sample.setSelectionString([dataFilterCut, leptonSelection])
  for sample in mc:
    sample.setSelectionString([mcFilterCut, leptonSelection])
  TTbarDMJets_scalar_Mchi1_Mphi100.setSelectionString([mcFilterCut, leptonSelection])
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = weight_, selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper')
  
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Events',
    attribute = lambda event, sample: 0.5 + index,
    binning=[3, 0, 3],
  ))

  plots.append(Plot(
<<<<<<< HEAD
    name = 'nVtxs', texX = 'vertex multiplicity', texY = 'Events',
    attribute = TreeVariable.fromString( "nVert/I" ),
    binning=[50,0,50],
  ))

  plots.append(Plot(
      texX = 'p_{T}^{miss} (GeV)', texY = 'Events',
      attribute = TreeVariable.fromString( "met_pt/F" ),
      binning=[320/20,80,400],
  ))

  plots.append(Plot(
      texX = '#phi(E_{T}^{miss})', texY = 'Events',
      attribute = TreeVariable.fromString( "met_phi/F" ),
      binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    texX = 'E_{T}^{miss}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Events',
    attribute = TreeVariable.fromString('metSig/F'),
    binning= [80,20,100] if args.selection.count('metSig20') else ([25,5,30] if args.selection.count('metSig') else [30,0,30]),
  ))

  plots.append(Plot(
    texX = 'M_{T2}(ll) (GeV)', texY = 'Events',
    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    binning=[300/20, 100,400] if args.selection.count('mt2ll100') else ([300/20, 140, 440] if args.selection.count('mt2ll140') else [400/20,0,400]),
  ))

  plots.append(Plot(
    texX = 'number of jets', texY = 'Events',
    attribute = TreeVariable.fromString('nJetGood/I'),
    binning=[14,0,14],
  ))

  plots.append(Plot(
    texX = 'number of medium b-tags (CSVM)', texY = 'Events',
    attribute = TreeVariable.fromString('nBTag/I'),
    binning=[8,0,8],
=======
      texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
      variable = Variable.fromString( "met_pt/F" ),
      binning=[400/50,0,400],
  ))

  plots.append(Plot(
    texX = '#slash{E}_{T}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events',
    variable = Variable.fromString('metSig/F'),
    binning=[15,5,20],
  ))

  plots.append(Plot(
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2ll/F" ),
    binning=[300/20,0,300],
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca
  ))

  plots.append(Plot(
    texX = 'H_{T} (GeV)', texY = 'Events',
    attribute = TreeVariable.fromString( "ht/F" ),
    binning=[500/50,50,600],
  ))

  plots.append(Plot(
    texX = 'm(ll) of leading dilepton (GeV)', texY = 'Events',
    attribute = TreeVariable.fromString( "dl_mass/F" ),
    binning=[200/4,0,200],
  ))

  plots.append(Plot(
    texX = 'p_{T}(ll) (GeV)', texY = 'Events',
    attribute = TreeVariable.fromString( "dl_pt/F" ),
    binning=[20,0,400],
  ))

  plots.append(Plot(
      texX = '#eta(ll) ', texY = 'Events',
      name = 'dl_eta', attribute = lambda event, sample: abs(event.dl_eta), read_variables = ['dl_eta/F'],
      binning=[10,0,3],
  ))

  plots.append(Plot(
<<<<<<< HEAD
    texX = '#phi(ll)', texY = 'Events',
    attribute = TreeVariable.fromString( "dl_phi/F" ),
    binning=[10,-pi,pi],
  ))
=======
    texX = 'p_{T}(ll) (GeV)', texY = 'Number of Events / 10 GeV',
    variable = Variable.fromString( "dl_pt/F" ),
    binning=[20,0,400],
  ))

  plots.append(Plot(
      texX = '#eta(ll) ', texY = 'Number of Events',
      variable = Variable.fromString( "dl_eta/F" ).addFiller(lambda data: abs(data.dl_eta), uses = 'dl_eta/F'),
      binning=[10,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(ll) (GeV)', texY = 'Number of Events',
    variable = Variable.fromString( "dl_phi/F" ),
    binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    texX = 'Cos(#phi(ll, #slash{E}_{T}))', texY = 'Number of Events',
    variable = Variable.fromString('cosZMetphi/F').addFiller(helpers.uses(lambda data: cos( data.dl_phi - data.met_phi ) , ["met_phi/F", "dl_phi/F"])),
    binning = [10,-1,1],
  ))


  # Lepton plots
  plots.append(Plot(
    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Number of Events / 5 GeV',
    variable = Variable.fromString( "l1_pt/F" ),
    binning=[20,0,300],
  ))

  plots.append(Plot(
    texX = '#eta(l_{1})', texY = 'Number of Events',
    variable = Variable.fromString( "l1_eta/F" ).addFiller(lambda data: abs(data.l1_eta), uses = 'l1_eta/F'),
    binning=[15,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(l_{1})', texY = 'Number of Events',
    variable = Variable.fromString( "l1_phi/F" ),
    binning=[10,-pi,pi],
  ))

#  plots.append(Plot(
#    name = "l1_dxy",
#    texX = '|d_{xy}|', texY = 'Number of Events',
#    variable = ScalarType.uniqueFloat().addFiller(lambda data:abs(data.l1_dxy), uses = "l1_dxy/F"),
#    binning=[40,0,1],
#  ))

#  plots.append(Plot(
#      name = "l1_dz",
#      texX = '|d_{z}|', texY = 'Number of Events',
#      variable = ScalarType.uniqueFloat().addFiller(lambda data:abs(data.l1_dz), uses = "l1_dz/F"),
#      binning=[40,0,0.15],
#  ))


  plots.append(Plot(
    texX = 'p_{T}(l_{2}) (GeV)', texY = 'Number of Events / 5 GeV',
    variable = Variable.fromString( "l2_pt/F" ),
    binning=[20,0,300],
  ))

  plots.append(Plot(
    texX = '#eta(l_{2})', texY = 'Number of Events',
    variable = Variable.fromString( "l2_eta/F" ).addFiller(lambda data: abs(data.l2_eta), uses = 'l2_eta/F'),
    binning=[15,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(l_{2})', texY = 'Number of Events',
    variable = Variable.fromString( "l2_phi/F" ),
    binning=[10,-pi,pi],
  ))

#  plots.append(Plot(
#    name = "l2_dxy",
#    texX = '|d_{xy}|', texY = 'Number of Events',
#    variable = ScalarType.uniqueFloat().addFiller(lambda data:abs(data.l1_dxy), uses = "l2_dxy/F"),
#    binning=[40,0,1],
#  ))

#  plots.append(Plot(
#      name = "l2_dz",
#      texX = '|d_{z}|', texY = 'Number of Events',
#      variable = ScalarType.uniqueFloat().addFiller(lambda data:abs(data.l1_dz), uses = "l2_dz/F"),
#      binning=[40,0,0.15],
#  ))


  plots.append(Plot(
    texX = 'JZB (GeV)', texY = 'Number of Events / 32 GeV',
    variable = Variable.fromString('JZB/F').addFiller (
	helpers.uses( 
	    lambda data: sqrt( (data.met_pt*cos(data.met_phi)+data.dl_pt*cos(data.dl_phi))**2 + (data.met_pt*sin(data.met_phi)+data.dl_pt*sin(data.dl_phi))**2) - data.dl_pt, 
	    ["met_phi/F", "dl_phi/F", "met_pt/F", "dl_pt/F"])
    ), 
    binning=[25,-200,600],
  ))

  # Plots only when at least one jet:
  if args.selection.count('njet'):
    plots.append(Plot(
      texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      variable = Variable.fromString('jet1_pt/F').addFiller(helpers.uses(lambda data: data.JetGood_pt[0], "JetGood[pt/F]")),
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta_{T}(leading jet) (GeV)', texY = 'Number of Events',
      variable = Variable.fromString('jet1_eta/F').addFiller(helpers.uses(lambda data: abs(data.JetGood_eta[0]), "JetGood[eta/F]")),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi_{T}(leading jet) (GeV)', texY = 'Number of Events',
      variable = Variable.fromString('jet1_phi/F').addFiller(helpers.uses(lambda data: data.JetGood_phi[0], "JetGood[phi/F]")),
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      texX = 'Cos(#phi(#slash{E}_{T}, leading jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosMetJet1phi/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"])),
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      texX = 'Cos(#phi(#slash{E}_{T}, leading jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosMetJet1phi_smallBinning/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"])),
      binning = [35,-1,1],
    ))

    plots.append(Plot(
      texX = 'Cos(#phi(Z, leading jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosZJet1phi/F').addFiller(helpers.uses(lambda data: cos( data.dl_phi - data.JetGood_phi[0] ) , ["dl_phi/F", "JetGood[phi/F]"])),
      binning = [10,-1,1],
    ))
    


  # Plots only when at least two jets:
  if args.selection.count('njet2'):
    plots.append(Plot(
      texX = 'p_{T}(2nd leading jet) (GeV)', texY = 'Number of Events / 30 GeV',
      variable = Variable.fromString('jet2_pt/F').addFiller(helpers.uses(lambda data: data.JetGood_pt[1], "JetGood[pt/F]")),
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta_{T}(2nd leading jet) (GeV)', texY = 'Number of Events',
      variable = Variable.fromString('jet2_eta/F').addFiller(helpers.uses(lambda data: abs(data.JetGood_eta[1]), "JetGood[eta/F]")),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi_{T}(2nd leading jet) (GeV)', texY = 'Number of Events',
      variable = Variable.fromString('jet2_phi/F').addFiller(helpers.uses(lambda data: data.JetGood_phi[1], "JetGood[phi/F]")),
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      texX = 'Cos(#phi(#slash{E}_{T}, second jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosMetJet2phi/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"])),
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      texX = 'Cos(#phi(#slash{E}_{T}, second jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosMetJet2phi_smallBinning/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"])),
      binning = [35,-1,1],
    ))

    plots.append(Plot(
      texX = 'Cos(#phi(Z, 2nd leading jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosZJet2phi/F').addFiller(helpers.uses(lambda data: cos( data.dl_phi - data.JetGood_phi[0] ) , ["dl_phi/F", "JetGood[phi/F]"])),
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      texX = 'Cos(#phi(leading jet, 2nd leading jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosJet1Jet2phi/F').addFiller(helpers.uses(lambda data: cos( data.JetGood_phi[1] - data.JetGood_phi[0] ) , ["JetGood[phi/F]"])),
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
      variable = Variable.fromString( "dl_mt2bb/F" ),
      binning=[400/20,70,470],
    ))

    plots.append(Plot(
      texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
      variable = Variable.fromString( "dl_mt2blbl/F" ),
      binning=[400/20,0,400],
    ))

>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca

  plots.append(Plot(
    texX = 'Cos(#Delta#phi(ll, E_{T}^{miss}))', texY = 'Events',
    name = 'cosZMetphi',
    attribute = lambda event, sample: cos( event.dl_phi - event.met_phi ), 
    read_variables = ["met_phi/F", "dl_phi/F"],
    binning = [10,-1,1],
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{1}) (GeV)', texY = 'Events',
    attribute = TreeVariable.fromString( "l1_pt/F" ),
    binning=[20,0,300],
  ))

  plots.append(Plot(
    texX = '#eta(l_{1})', texY = 'Events',
    name = 'l1_eta', attribute = lambda event, sample: abs(event.l1_eta), read_variables = ['l1_eta/F'],
    binning=[15,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(l_{1})', texY = 'Events',
    attribute = TreeVariable.fromString( "l1_phi/F" ),
    binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{2}) (GeV)', texY = 'Events / 15 GeV',
    attribute = TreeVariable.fromString( "l2_pt/F" ),
    binning=[20,0,300],
  ))

  plots.append(Plot(
    texX = '#eta(l_{2})', texY = 'Events',
    name = 'l2_eta', attribute = lambda event, sample: abs(event.l2_eta), read_variables = ['l2_eta/F'],
    binning=[15,0,3],
  ))

  plots.append(Plot(
    texX = '#phi(l_{2})', texY = 'Events',
    attribute = TreeVariable.fromString( "l2_phi/F" ),
    binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    name = "JZB",
    texX = 'JZB (GeV)', texY = 'Events',
    attribute = lambda event, sample: sqrt( (event.met_pt*cos(event.met_phi)+event.dl_pt*cos(event.dl_phi))**2 + (event.met_pt*sin(event.met_phi)+event.dl_pt*sin(event.dl_phi))**2) - event.dl_pt, 
        read_variables = ["met_phi/F", "dl_phi/F", "met_pt/F", "dl_pt/F"],
    binning=[25,-200,600],
  ))

  # Plots only when at least one b-jet:
  if args.selection.count('btag1p'):
    plots.append(Plot(
      texX = 'p_{T}(leading b-jet) (GeV)', texY = 'Events',
      name = 'bjet1_pt', attribute = lambda event, sample: event.bJetGoodPt,
      binning=[600/30,0,600],
    ))

  # Plots only when at least one jet:
  if args.selection.count('njet'):
    plots.append(Plot(
      texX = 'p_{T}(leading jet) (GeV)', texY = 'Events',
      name = 'jet1_pt', attribute = lambda event, sample: event.JetGood_pt[0],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(leading jet) (GeV)', texY = 'Events',
      name = 'jet1_eta', attribute = lambda event, sample: abs(event.JetGood_eta[0]),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(leading jet) (GeV)', texY = 'Events',
      name = 'jet1_phi', attribute = lambda event, sample: event.JetGood_phi[0],
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      name = 'cosMetJet1phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0]), 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet1phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosZJet1phi',
      texX = 'Cos(#Delta#phi(Z, leading jet))', texY = 'Events',
      attribute = lambda event, sample: cos( event.dl_phi - event.JetGood_phi[0] ) ,
      read_variables =  ["dl_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

  # Plots only when at least two jets:
  if args.selection.count('njet2p'):
    plots.append(Plot(
      texX = 'p_{T}(2nd leading jet) (GeV)', texY = 'Events',
      name = 'jet2_pt', attribute = lambda event, sample: event.JetGood_pt[1],
      binning=[600/30,0,600],
    ))

    plots.append(Plot(
      texX = '#eta(2nd leading jet) (GeV)', texY = 'Events',
      name = 'jet2_eta', attribute = lambda event, sample: abs(event.JetGood_eta[1]),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(2nd leading jet) (GeV)', texY = 'Events',
      name = 'jet2_phi', attribute = lambda event, sample: event.JetGood_phi[1],
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      name = 'cosMetJet2phi',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      name = 'cosMetJet2phi_smallBinning',
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Events',
      attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ) , 
      read_variables = ["met_phi/F", "JetGood[phi/F]"],
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      name = 'cosZJet2phi',
      texX = 'Cos(#Delta#phi(Z, 2nd leading jet))', texY = 'Events',
      attribute = lambda event, sample: cos( event.dl_phi - event.JetGood_phi[0] ),
      read_variables = ["dl_phi/F", "JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      name = 'cosJet1Jet2phi',
      texX = 'Cos(#Delta#phi(leading jet, 2nd leading jet))', texY = 'Events',
      attribute = lambda event, sample: cos( event.JetGood_phi[1] - event.JetGood_phi[0] ) ,
      read_variables =  ["JetGood[phi/F]"],
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      texX = 'M_{T2}(bb) (GeV)', texY = 'Events',
      attribute = TreeVariable.fromString( "dl_mt2bb/F" ),
      binning=[420/30,70,470],
    ))

    plots.append(Plot(
      texX = 'M_{T2}(blbl) (GeV)', texY = 'Events',
      attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
      binning=[420/30,0,400],
    ))

  plotting.fill(plots, read_variables = read_variables, sequence = [calcBJetPt])

  # Get normalization yields from yield histogram
  for plot in plots:
    if plot.name == "yield":
      for i, l in enumerate(plot.histos):
        for j, h in enumerate(l):
          yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
          h.GetXaxis().SetBinLabel(1, "#mu#mu")
          h.GetXaxis().SetBinLabel(2, "e#mu")
          h.GetXaxis().SetBinLabel(3, "ee")
<<<<<<< HEAD
  if args.noData: yields[mode]["data"] = 0
=======
  if not args.plotData: yields[mode]["data"] = 0
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca

  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
  dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

<<<<<<< HEAD
  drawPlots(plots, mode, dataMCScale)
  makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart",    yields, mode, mc)
  makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart_VV", yields, mode, multiBosonList)
  allPlots[mode] = plots

=======
  for log in [False, True]:
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      print "Plotting of " + plot.name
      plotting.draw(plot, 
	  plot_directory = os.path.join(plot_directory, args.plot_directory, mode + ("_log" if log else ""), args.selection),
	  ratio = {'yRange':(0.1,1.9)} if args.plotData else None,
	  logX = False, logY = log, sorting = True, 
	  yRange = (0.003, "auto"),
	  scaling = {},
          legend = (0.50,0.93-0.04*sum(map(len, plot.histos)),0.95,0.93),
	  drawObjects = drawObjects( args.plotData, dataMCScale , lumi_scale )
      )
  allPlots[mode] = plots

  makePieChart("pie_chart", yields, mode, mc)
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca


# Add the different channels into SF and all
import itertools
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
  makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart",    yields, mode, mc)
  makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart_VV", yields, mode, multiBosonList)


# Write to tex file
<<<<<<< HEAD
columns = [i.name for i in mc] + ["MC", "data"] + ([DM.name, DM2.name] if args.signal=="DM" else []) + [s.name for s in signals]
=======
columns = [i.name for i in mc] + ["MC", "data"] + [TTbarDMJets_scalar_Mchi1_Mphi100.name] if args.signal=="DM" else [] + [T2tt_650_250] if args.signal=="T2tt" else []
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca
texdir = "tex"
if args.splitBosons:  texdir += "_splitBosons"
if args.splitBosons2: texdir += "_splitBosons2"
try:
  os.makedirs("./" + texdir)
except:
  pass
with open("./" + texdir + "/" + args.selection + ".tex", "w") as f:
  f.write("&" + " & ".join(columns) + "\\\\ \n")
  for mode in allModes + ["SF","all"]:
    f.write(mode + " & " + " & ".join([ (" %12.0f" if i == "data" else " %12.2f") % yields[mode][i] for i in columns]) + "\\\\ \n")



logger.info( "Done with prefix %s and selectionString %s", args.selection, cutInterpreter.cutString(args.selection))

<<<<<<< HEAD
=======
for log in [False, True]:
  for plot in allPlots[allModes[0]]:
    if args.plotData: plot.histos[1][0].legendText = "Data 2015 (all channels)"
    plotting.draw(plot,
	  plot_directory = os.path.join(plot_directory, args.plot_directory, "all" + ("_log" if log else ""), args.selection),
	  ratio = {'yRange':(0.1,1.9)} if args.plotData else None,
	  logX = False, logY = log, sorting = True,
	  yRange = (0.003, "auto"),
	  scaling = {},
          legend = (0.50,0.93-0.04*sum(map(len, plot.histos)),0.95,0.93),
	  drawObjects = drawObjects( args.plotData, dataMCScale , lumi_scale )
    )

makePieChart("pie_chart", yields, "all", mc)

logger.info( "Done with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )
>>>>>>> 91b230c6061836fc0b8d0465bb99d781d6f427ca

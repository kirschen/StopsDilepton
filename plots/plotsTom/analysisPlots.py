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
from StopsDilepton.tools.helpers         import deltaPhi
from StopsDilepton.tools.objectSelection import getFilterCut
from StopsDilepton.plots.pieChart        import makePieChart

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',         action='store',      default='DM',        nargs='?', choices=[None, "T2tt", "DM"], help="Add signal to plot")
argParser.add_argument('--noData',         action='store_true', default=False,       help='also plot data?')
argParser.add_argument('--plot_directory', action='store',      default='analysisPlots')
argParser.add_argument('--selection',      action='store',      default=None)
argParser.add_argument('--splitBosons',    action='store_true', default=False)
argParser.add_argument('--splitTop',       action='store_true', default=False)
argParser.add_argument('--powheg',         action='store_true', default=True)
argParser.add_argument('--isChild',        action='store_true', default=False)
argParser.add_argument('--dryRun',         action='store_true', default=False,       help='do not launch subjobs')
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

#
# Selections (two leptons with pt > 20 GeV)
#
from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWP = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
def getLeptonString(nMu, nE, multiIso=False, is74x=False):
  leptonString = "nGoodMuons==" + str(nMu) + "&&nGoodElectrons==" + str(nE) + "&&l1_pt>25"
  if multiIso and is74x: leptonString += "&&l1_index>=0&&l1_index<1000&&l2_index>=0&&l2_index<1000&&"+multiIsoWP
  elif multiIso:         leptonString += "&&l1_mIsoWP>4&&l2_mIsoWP>4"
  return leptonString


jetSelection    = "nJetGood"
bJetSelectionM  = "nBTag"

#
# Cuts to iterate over
#
cuts = [
    ("njet01",            jetSelection+"<=1"),
    ("njet1",             jetSelection+"==1"),
    ("njet2",             jetSelection+">=2"),
    ("btag0",             bJetSelectionM+"==0"),
    ("btagM",             bJetSelectionM+">=1"),
    ("multiIsoWP",        "(1)"),                                                   # implemented below
    ("looseLeptonVeto",   "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
    ("mll20",             "dl_mass>20"),
    ("allZ",              "(1)"),                                                   # allZ and onZ switches off the offZ selection
    ("onZ",               "abs(dl_mass-91.1876)<15"),
    ("met50",             "met_pt>50"),
    ("met80",             "met_pt>80"),
    ("metInv",            "met_pt<80"),
    ("metSig5",           "metSig>5"),
#    ("metSig20",          "metSig>20"),
    ("metSigInv",         "metSig<5"),
    ("dPhiJet0",          "cos(met_phi-JetGood_phi[0])<0.8"),
    ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<0.8&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
    ("dPhiInv",           "!(cos(met_phi-JetGood_phi[0])<0.8&&cos(met_phi-JetGood_phi[1])<cos(0.25))"),
    ("mt2ll100",          "dl_mt2ll>100"),
    ("mt2ll140",          "dl_mt2ll>140"),
  ]


#
# Construct prefixes and selectionstring and filter on possible cut combinations
#
import itertools
selectionStrings = {}
for i_comb in reversed( range( len(cuts)+1 ) ):
    for comb in itertools.combinations( cuts, i_comb ):
        presel = [] 
        presel.extend( comb )
        selection = '-'.join([p[0] for p in presel])
        if not selection.count("multiIsoWP"):      continue
        if not selection.count("looseLeptonVeto"): continue
        if not selection.count("mll20"):           continue
 #       if not selection.count("njet"):            continue
        if selection.count("met50")  and selection.count("met80"):      continue
        if (selection.count("met50")  or selection.count("met80")) and selection.count('metInv'):      continue
        if selection.count("onZ")    and selection.count("allZ"):       continue
        if selection.count("met80")  and not selection.count("mll"):    continue
        if selection.count("met50")  and not selection.count("btag0"):  continue #met50 only for btag0
        if selection.count("metSig") and not (selection.count("met80") or selection.count("met50")):  continue
        if selection.count("dPhi")   and not selection.count("mll20"):    continue
        if selection.count("dPhi")   and not selection.count("njet2"):  continue
        if selection.count("dPhiInv") and selection.count("PhiJet1"):   continue
        if selection.count("dPhiInv") and selection.count("mt2ll140"):  continue
        if selection.count("metSigInv") and selection.count("mt2ll140"):  continue
        if selection.count("mt2")    and not selection.count("met"):    continue
        if selection.count("njet0")  and not selection.count('njet01') and selection.count("metSig"):    continue
        if selection.count("njet0")  and selection.count("dPhi"):    continue
        if selection.count("njet0")  and selection.count("mt2"):    continue
        if selection.count("njet1")  and selection.count("dPhi"):    continue
        if selection.count("njet1")  and selection.count("mt2"):    continue
        if selection.count("njet0")  and selection.count("btag") and not selection.count("njet01"):    continue
        if selection.count("njet01")  and selection.count("onZ"):    continue
        if selection.count("njet01")  and selection.count("allZ"):    continue
        if selection.count("njet") > 1:    continue
        if selection.count("btag") > 1:    continue
        if selection.count("mt2ll") > 1:   continue
        if selection.count("mt2blbl") > 1: continue
        if selection.count("mt2bb") > 1:   continue
        if selection.count("metSig") > 1:  continue
        if selection.count("dPhiJet0") > 1:  continue

#        if selection not in ['njet2-btagM-multiIsoWP-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100',
#                             'njet2-btag0-multiIsoWP-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100',
#                             'njet2-btag0-multiIsoWP-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv-mt2ll100']: continue

        if selection not in ['multiIsoWP-looseLeptonVeto-mll20',
                             'njet2-multiIsoWP-looseLeptonVeto-mll20',
			     'njet2-btagM-multiIsoWP-looseLeptonVeto-mll20',
			     'njet2-btagM-multiIsoWP-looseLeptonVeto-mll20-met80',
			     'njet2-btagM-multiIsoWP-looseLeptonVeto-mll20-met80-metSig5',
			     'njet2-btagM-multiIsoWP-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0',
			     'njet2-btagM-multiIsoWP-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1',
			     'njet2-btagM-multiIsoWP-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100',
			     'njet2-btagM-multiIsoWP-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll140']: continue


        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./analysisPlots.py --selection=" + selection + (" --noData" if args.noData else "")\
                                                            + (" --splitBosons" if args.splitBosons else "")\
                                                            + (" --splitTop" if args.splitTop else "")\
                                                            + (" --powheg" if args.powheg else "")\
                                                            + (" --signal=" + args.signal if args.signal else "")\
                                                            + (" --plot_directory=" + args.plot_directory)\
                                                            + (" --logLevel=" + args.logLevel)
    logfile = "log/" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    if not args.dryRun:          os.system("qsub -v command=\"" + command + "          --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=10:00:00 runPlotsOnCream02.sh")
    if selection.count('mt2ll'): os.system("qsub -v command=\"" + command + " --noData --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=10:00:00 runPlotsOnCream02.sh")
  logger.info("All jobs launched")
  exit(0)

if args.noData:                   args.plot_directory += "_noData"
if args.splitBosons:              args.plot_directory += "_splitMultiBoson"
if args.powheg:                   args.plot_directory += "_topPowheg"
if args.splitTop:                 args.plot_directory += "_splitTop"
#if args.selection.count("mt2ll") and args.selection.count('btagM'): args.noData = True

if args.selection.count("btag0") and args.selection.count("onZ"): args.signal = None
if args.selection.count("njet2-multiIsoWP-looseLeptonVeto-mll20-onZ"): args.signal = None
if args.selection.count("njet2-multiIsoWP-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv-mt2ll100"): args.signal = None

#
# Make samples, will be searched for in the postProcessing directory
#
postProcessing_directory = "postProcessed_80X_v12/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import *
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
T2tt                    = T2tt_650_1 # Take 450,0 as default to plot
T2tt2                   = T2tt_500_250
T2tt3                   = T2tt_450_250
T2tt2.style             = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
T2tt3.style             = styles.lineStyle( ROOT.kBlack, width=3, dashed=True )
T2tt.style              = styles.lineStyle( ROOT.kBlack, width=3 )

DM                      = TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10
DM2                     = TTbarDMJets_pseudoscalar_Mchi_10_Mphi_100
DM3                     = TTbarDMJets_pseudoscalar_Mchi_50_Mphi_200
DM4                     = TTbarDMJets_scalar_Mchi_1_Mphi_10
DM5                     = TTbarDMJets_scalar_Mchi_10_Mphi_100
DM6                     = TTbarDMJets_scalar_Mchi_50_Mphi_200
DM.style                = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
DM2.style               = styles.lineStyle( ROOT.kBlack, width=3, dashed=True )
DM3.style               = styles.lineStyle( ROOT.kBlack, width=3 )
DM4.style               = styles.lineStyle( 28,          width=3, dotted=True )
DM5.style               = styles.lineStyle( 28,          width=3, dashed=True )
DM6.style               = styles.lineStyle( 28,          width=3 )




#
# Text on the plots
#
def drawObjects( plotData, dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'), 
      (0.45, 0.95, 'L=12.9 fb{}^{-1} (13 TeV) Scale %3.2f'% ( dataMCScale ) ) if plotData else (0.45, 0.95, 'L=12.9 fb{}^{-1} (13 TeV)')
    ]
    if args.selection=="njet2-btagM-multiIsoWP-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100" and args.noData:
      lines += [(0.55, 0.5, 'M_{T2}(ll) > 100 GeV')]
    return [tex.DrawLatex(*l) for l in lines] 



def drawPlots(plots, mode, dataMCScale):
  for log in [False, True]:
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      if not args.noData: 
        if mode == "all": plot.histos[1][0].legendText = "Data"
        if mode == "SF":  plot.histos[1][0].legendText = "Data (SF)"
      plotting.draw(plot,
	    plot_directory = os.path.join(plot_directory, args.plot_directory, mode + ("_log" if log else ""), args.selection),
	    ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
	    logX = False, logY = log, sorting = True,
	    yRange = (0.03, "auto") if log else (0.001, "auto"),
	    scaling = {},
	    legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.9,0.88) if not args.noData else (0.50,0.9-0.047*sum(map(len, plot.histos)),0.85,0.9),
	    drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale )
      )





#
# Read variables and sequences
#
read_variables = ["weight/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F",
                  "metSig/F", "ht/F", "nBTag/I", "nJetGood/I"]

sequence = []

offZ            = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ")) else ""

def getLeptonSelection(mode, is74x=False):
  if   mode=="mumu": return getLeptonString(2, 0, args.selection.count("multiIsoWP"), is74x) + "&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return getLeptonString(1, 1, args.selection.count("multiIsoWP"), is74x) + "&&isOS&&isEMu"
  elif mode=="ee":   return getLeptonString(0, 2, args.selection.count("multiIsoWP"), is74x) + "&&isOS&&isEE" + offZ

#
# Loop over channels
#
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}
  if mode=="mumu":
    data_sample         = DoubleMuon_Run2016BCD_backup
    data_sample.texName = "data (2 #mu)"
  elif mode=="ee":
    data_sample         = DoubleEG_Run2016BCD_backup 
    data_sample.texName = "data (2 e)"
  elif mode=="mue":
    data_sample         = MuonEG_Run2016BCD_backup 
    data_sample.texName = "data (1 #mu, 1 e)"

  data_sample.setSelectionString([getFilterCut(isData=True), getLeptonSelection(mode)])
  data_sample.name  = "data"
  data_sample.read_variables = ["weight/F"]
  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale        = data_sample.lumi/1000

  if args.powheg and args.splitBosons:   mc = [ Top_pow, TTZ_LO, TTXNoZ, WWNo2L2Nu, WZ, ZZNo2L2Nu, VVTo2L2Nu, triBoson, DY_HT_LO]
  elif args.splitBosons:                 mc = [ Top, TTZ_LO, TTXNoZ, WWNo2L2Nu, WZ, ZZNo2L2Nu, VVTo2L2Nu, triBoson, DY_HT_LO]
  elif args.splitTop:                    mc = [ TTLep_pow, singleTop, TTZ_LO, TTXNoZ, multiBoson, DY_HT_LO]
  elif args.powheg:                      mc = [ Top_pow, TTZ_LO, TTXNoZ, multiBoson, DY_HT_LO]
  else:                                  mc = [ Top, TTZ_LO, TTXNoZ, multiBoson, DY_HT_LO]

  for sample in mc:
    sample.scale          = lumi_scale
    sample.style          = styles.fillStyle(sample.color, lineColor = sample.color)
    sample.read_variables = ['reweightLeptonHIPSF/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU12fb/F']
    sample.weight         = lambda data: data.reweightBTag_SF*data.reweightLeptonSF*data.reweightLeptonHIPSF*data.reweightDilepTriggerBackup*data.reweightPU12fb
    sample.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])


  if not args.noData:
    if not args.signal:         stack = Stack(mc, data_sample)
    elif args.signal == "DM":   stack = Stack(mc, data_sample, DM, DM2, DM3, DM4, DM5, DM6)
    elif args.signal == "T2tt": stack = Stack(mc, data_sample, T2tt, T2tt2)
  else:
    if not args.signal:         stack = Stack(mc)
    elif args.signal == "DM":   stack = Stack(mc, DM1, DM2, DM3, DM4, DM5, DM6)
    elif args.signal == "T2tt": stack = Stack(mc, T2tt, T2tt2)

  for sample in [T2tt, T2tt2, T2tt3]:
    sample.scale          = lumi_scale
    sample.read_variables = ['reweightLeptonHIPSF/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightLeptonFastSimSF/F','reweightBTag_SF/F','reweightPU12fb/F']
    sample.weight         = lambda data: data.reweightBTag_SF*data.reweightLeptonSF*data.reweightLeptonFastSimSF*data.reweightLeptonHIPSF*data.reweightDilepTriggerBackup*data.reweightPU12fb
    sample.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])

  for sample in [DM, DM2, DM3, DM4, DM5, DM6]:
    sample.scale          = lumi_scale
    sample.read_variables = ['reweightLeptonHIPSF/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU12fb/F']
    sample.weight         = lambda data: data.reweightBTag_SF*data.reweightLeptonSF*data.reweightLeptonHIPSF*data.reweightDilepTriggerBackup*data.reweightPU12fb
    sample.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])



  # Use some defaults
  Plot.setDefaults(stack = stack, weight = lambda data: data.weight, selectionString = selectionStrings[args.selection], addOverFlowBin='upper')
  
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    variable = Variable.fromString( "yield/F" ).addFiller(lambda data: 0.5 + index),
    binning=[3, 0, 3],
  ))

  plots.append(Plot(
    name = 'nVtxs', texX = 'vertex multiplicity', texY = 'Number of Events',
    variable = Variable.fromString( "nVert/I" ),
    binning=[50,0,50],
  ))

  plots.append(Plot(
      texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 20 GeV',
      variable = Variable.fromString( "met_pt/F" ),
      binning=[400/20,0,400],
  ))

  plots.append(Plot(
      texX = '#phi(E_{T}^{miss})', texY = 'Number of Events / 20 GeV',
      variable = Variable.fromString( "met_phi/F" ),
      binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    texX = 'E_{T}^{miss}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events',
    variable = Variable.fromString('metSig/F'),
    binning= [80,20,100] if args.selection.count('metSig20') else ([25,5,30] if args.selection.count('metSig') else [30,0,30]),
  ))

  plots.append(Plot(
    texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2ll/F" ),
    binning=[300/20, 100,400] if args.selection.count('mt2ll100') else ([300/20, 140, 440] if args.selection.count('mt2ll140') else [300/20,0,300]),
  ))

  plots.append(Plot(
    texX = 'number of jets', texY = 'Number of Events',
    variable = Variable.fromString('nJetGood/I'),
    binning=[14,0,14],
  ))

  plots.append(Plot(
    texX = 'number of medium b-tags (CSVM)', texY = 'Number of Events',
    variable = Variable.fromString('nBTag/I'),
    binning=[8,0,8],
  ))

  plots.append(Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    variable = Variable.fromString( "ht/F" ),
    binning=[500/50,50,600],
  ))

  plots.append(Plot(
    texX = 'm(ll) of leading dilepton (GeV)', texY = 'Number of Events / 4 GeV',
    variable = Variable.fromString( "dl_mass/F" ),
    binning=[200/4,0,200],
  ))

  plots.append(Plot(
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
    texX = '#phi(ll)', texY = 'Number of Events',
    variable = Variable.fromString( "dl_phi/F" ),
    binning=[10,-pi,pi],
  ))

  plots.append(Plot(
    texX = 'Cos(#Delta#phi(ll, E_{T}^{miss}))', texY = 'Number of Events',
    variable = Variable.fromString('cosZMetphi/F').addFiller(helpers.uses(lambda data: cos( data.dl_phi - data.met_phi ) , ["met_phi/F", "dl_phi/F"])),
    binning = [10,-1,1],
  ))

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
      texX = '#eta(leading jet) (GeV)', texY = 'Number of Events',
      variable = Variable.fromString('jet1_eta/F').addFiller(helpers.uses(lambda data: abs(data.JetGood_eta[0]), "JetGood[eta/F]")),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(leading jet) (GeV)', texY = 'Number of Events',
      variable = Variable.fromString('jet1_phi/F').addFiller(helpers.uses(lambda data: data.JetGood_phi[0], "JetGood[phi/F]")),
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosMetJet1phi/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"])),
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, leading jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosMetJet1phi_smallBinning/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"])),
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      texX = 'Cos(#Delta#phi(Z, leading jet))', texY = 'Number of Events',
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
      texX = '#eta(2nd leading jet) (GeV)', texY = 'Number of Events',
      variable = Variable.fromString('jet2_eta/F').addFiller(helpers.uses(lambda data: abs(data.JetGood_eta[1]), "JetGood[eta/F]")),
      binning=[10,0,3],
    ))

    plots.append(Plot(
      texX = '#phi(2nd leading jet) (GeV)', texY = 'Number of Events',
      variable = Variable.fromString('jet2_phi/F').addFiller(helpers.uses(lambda data: data.JetGood_phi[1], "JetGood[phi/F]")),
      binning=[10,-pi,pi],
    ))

    plots.append(Plot(
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosMetJet2phi/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"])),
      binning = [10,-1,1],
    ))
    
    plots.append(Plot(
      texX = 'Cos(#Delta#phi(E_{T}^{miss}, second jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosMetJet2phi_smallBinning/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"])),
      binning = [20,-1,1],
    ))

    plots.append(Plot(
      texX = 'Cos(#Delta#phi(Z, 2nd leading jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosZJet2phi/F').addFiller(helpers.uses(lambda data: cos( data.dl_phi - data.JetGood_phi[0] ) , ["dl_phi/F", "JetGood[phi/F]"])),
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      texX = 'Cos(#Delta#phi(leading jet, 2nd leading jet))', texY = 'Number of Events',
      variable = Variable.fromString('cosJet1Jet2phi/F').addFiller(helpers.uses(lambda data: cos( data.JetGood_phi[1] - data.JetGood_phi[0] ) , ["JetGood[phi/F]"])),
      binning = [10,-1,1],
    ))

    plots.append(Plot(
      texX = 'M_{T2}(bb) (GeV)', texY = 'Number of Events / 30 GeV',
      variable = Variable.fromString( "dl_mt2bb/F" ),
      binning=[420/30,70,470],
    ))

    plots.append(Plot(
      texX = 'M_{T2}(blbl) (GeV)', texY = 'Number of Events / 30 GeV',
      variable = Variable.fromString( "dl_mt2blbl/F" ),
      binning=[420/30,0,400],
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

  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
  dataMCScale        = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')

  drawPlots(plots, mode, dataMCScale)
  makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart", yields, mode, mc)
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
  makePieChart(os.path.join(plot_directory, args.plot_directory, mode, args.selection), "pie_chart", yields, mode, mc)


# Write to tex file
columns = [i.name for i in mc] + ["MC", "data"] + ([DM.name] if args.signal=="DM" else []) + ([T2tt.name, T2tt2.name] if args.signal=="T2tt" else [])
texdir = "tex"
if args.powheg: texdir += "_powheg"
try:
  os.makedirs("./" + texdir)
except:
  pass
with open("./" + texdir + "/" + args.selection + ".tex", "w") as f:
  f.write("&" + " & ".join(columns) + "\\\\ \n")
  for mode in allModes + ["SF","all"]:
    f.write(mode + " & " + " & ".join([ (" %12.0f" if i == "data" else " %12.2f") % yields[mode][i] for i in columns]) + "\\\\ \n")



logger.info( "Done with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )


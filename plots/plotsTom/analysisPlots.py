#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT, os
ROOT.gROOT.SetBatch(True)

from math import sqrt, cos, sin, pi
from RootTools.core.standard import *
from StopsDilepton.tools.user import plot_directory
from StopsDilepton.tools.helpers import deltaPhi
from StopsDilepton.tools.objectSelection import getFilterCut

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',         action='store',      default='T2tt',      nargs='?', choices=[None, "T2tt", "DM"], help="Add signal to plot")
argParser.add_argument('--noData',         action='store_true', default=False,       help='also plot data?')
argParser.add_argument('--plot_directory', action='store',      default='analysisPlots')
argParser.add_argument('--pu',             action='store',      default=None)
argParser.add_argument('--selection',      action='store',      default=None)
argParser.add_argument('--isChild',        action='store_true', default=False)
argParser.add_argument('--unblind',        action='store_true', default=False,       help='unblind?')
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
def getLeptonString(nMu, nE):
  return "nGoodMuons==" + str(nMu) + "&&nGoodElectrons==" + str(nE)


jetSelection    = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))"
bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.800))"
bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.460))"

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWP = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
#
# Cuts to iterate over
#
cuts = [
    ("njet2",             jetSelection+">=2"),
    ("btag0",             bJetSelectionM+"==0"),
    ("btagM",             bJetSelectionM+">=1"),
    ("multiIsoWP",        "l1_index>=0&&l1_index<1000&&l2_index>=0&&l2_index<1000&&"+multiIsoWP),
    ("looseLeptonVeto",   "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
    ("mll20",             "dl_mass>20"),
    ("allZ",              "(1)"),                        # allZ and onZ switches off the offZ selection
    ("onZ",               "abs(dl_mass-91.1876)<15"),
    ("met50",             "met_pt>50"),
    ("met80",             "met_pt>80"),
    ("metSig5",           "metSig>5"),
    ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
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
        if not selection.count("njet2"):           continue
        if not selection.count("mll20"):           continue
        if selection.count("met50")  and selection.count("met80"):      continue
        if selection.count("onZ")    and selection.count("allZ"):       continue
        if selection.count("met80")  and not selection.count("mll"):    continue
        if selection.count("met50")  and not selection.count("btag0"):  continue #met50 only for btag0
        if selection.count("metSig") and not (selection.count("met80") or selection.count("met50")):  continue
        if selection.count("dPhi")   and not selection.count("metSig"): continue
        if selection.count("dPhi")   and not selection.count("njet2"):  continue
        if selection.count("mt2")    and not selection.count("met"):    continue
        if selection.count("njet") > 1:    continue
        if selection.count("btag") > 1:    continue
        if selection.count("mt2ll") > 1:   continue
        if selection.count("mt2blbl") > 1: continue
        if selection.count("mt2bb") > 1:   continue
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./analysisPlots.py --selection=" + selection + (" --noData" if args.noData else "")\
                                                            + (" --unblind" if args.unblind else "")\
                                                            + (" --signal=" + args.signal if args.signal else "")\
                                                            + (" --plot_directory=" + args.plot_directory)\
                                                            + (" --logLevel=" + args.logLevel)
    logfile = "log/" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    if not args.dryRun: os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=10:00:00 runPlotsOnCream02.sh")
  logger.info("All jobs launched")
  exit(0)

if args.selection.count("btag0"):
  args.signal = None


if args.pu: args.plot_directory = os.path.join(args.plot_directory, args.pu)

from array import array
import warnings
warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='creating converter.*' )
def makePieChart(name, yields, mode, samples, withLabels=False):
  c        = ROOT.TCanvas("pie", "pie", 1000, 1000)
  labels   = [ array( 'c', ((s.texName if hasattr(s, 'texName') else s.name) if yields[mode][s.name] > 0.01*yields[mode]['MC'] else '') + '\0' ) for s in samples]
  labels_  = array( 'l', map( lambda x: x.buffer_info()[0], labels ) )
  piechart = ROOT.TPie(name, name, len(samples), array('f', [yields[mode][s.name] for s in samples]), array('i', [s.color for s in samples]), labels_)
  piechart.SetRadius(0.3 if withLabels else 0.45)
  piechart.SetTextSize(0.02)
  piechart.SetLabelsOffset(.02 if withLabels else 1.);
  piechart.Draw("NOLrsc>")
  c.Print(os.path.join(plot_directory, args.plot_directory, mode, args.selection, name + ".png"))



#
# Make samples, will be searched for in the postProcessing directory
#
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import *
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import TTbarDMJets_scalar_Mchi1_Mphi100
T2tt = T2tt_450_0 # Take 450,0 as default to plot
TTbarDMJets_scalar_Mchi1_Mphi100.texName += "(#times 10)"
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
      (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(lumi_scale*100)/100., dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV)'% ( int(lumi_scale*100)/100.) )
    ]
    return [tex.DrawLatex(*l) for l in lines] 


#
# Read variables and sequences
#
read_variables = ["weight/F" , "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F",
                  "metSig/F", "ht/F", "nBTag/I", "nJetGood/I"]

sequence = []


offZ            = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ")) else ""
mumuSelection   = getLeptonString(2, 0) + "&&isOS&&isMuMu" + offZ
mueSelection    = getLeptonString(1, 1) + "&&isOS&&isEMu"
eeSelection     = getLeptonString(0, 2) + "&&isOS&&isEE" + offZ

#
# Loop over channels
#
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}
  if mode=="mumu":
    data_sample     = DoubleMuon_Run2016B
#    qcd_sample      = QCD_Mu5 #FIXME
    leptonSelection = mumuSelection
    trigger         = "HLT_mumuIso"
  elif mode=="ee":
    data_sample     = DoubleEG_Run2016B
#    qcd_sample      = QCD_EMbcToE
    leptonSelection = eeSelection
    trigger         = "HLT_ee_DZ"
  elif mode=="mue":
    data_sample     = MuonEG_Run2016B
#    qcd_sample      = QCD_Mu5EMbcToE
    leptonSelection = mueSelection
    trigger         = "HLT_mue"

#  qcd_sample.name  = "QCD"  # Give same name in all modes such that it combines easily
  data_sample.name = "data"

  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale        = data_sample.lumi/1000

  mc = [ Top, TTZ, TTXNoZ, multiBoson, DY_HT_LO]
#  if args.selection.count("btag0"): mc = [ Top, TTZ, TTXNoZ, WW, WZ, ZZ, triBoson, DY_HT_LO] # Split diboson up for the nbtag=0 control region
  for sample in mc:
    sample.scale = lumi_scale
    sample.style = styles.fillStyle(sample.color, lineColor = sample.color)
    sample.read_variables = ['reweightPU/F','reweightPUUp/F','reweightPUDown/F', 'reweightPUVUp/F','reweightPUVDown/F', 'reweightNVTX/F','reweightNVTXUp/F','reweightNVTXDown/F', 'reweightNVTXVUp/F','reweightNVTXVDown/F']
    if   args.pu == "reweightPUUp":      sample.weight = lambda data: data.reweightPUUp
    elif args.pu == "reweightPUDown":    sample.weight = lambda data: data.reweightPUDown
    elif args.pu == "reweightPUVUp":     sample.weight = lambda data: data.reweightPUVUp
    elif args.pu == "reweightPUVDown":   sample.weight = lambda data: data.reweightPUVDown
    elif args.pu == "reweightNVTX":      sample.weight = lambda data: data.reweightNVTX
    elif args.pu == "reweightNVTXUp":    sample.weight = lambda data: data.reweightNVTXUp
    elif args.pu == "reweightNVTXDown":  sample.weight = lambda data: data.reweightNVTXDown
    elif args.pu == "reweightNVTXVUp":   sample.weight = lambda data: data.reweightNVTXVUp
    elif args.pu == "reweightNVTXVDown": sample.weight = lambda data: data.reweightNVTXVDown
    else:                                sample.weight = lambda data: data.reweightPU

  TTbarDMJets_scalar_Mchi1_Mphi100.scale = lumi_scale*10
  TTbarDMJets_scalar_Mchi1_Mphi100.style = styles.lineStyle( ROOT.kBlack, width=3 )
  T2tt.style = styles.lineStyle( ROOT.kBlack, width=3 )

  if not args.noData:
    if not args.signal:         stack = Stack(mc, data_sample)
    elif args.signal == "DM":   stack = Stack(mc, data_sample, TTbarDMJets_scalar_Mchi1_Mphi100)
    elif args.signal == "T2tt": stack = Stack(mc, data_sample, T2tt)
  else:
    if not args.signal:         stack = Stack(mc)
    elif args.signal == "DM":   stack = Stack(mc, TTbarDMJets_scalar_Mchi1_Mphi100)
    elif args.signal == "T2tt": stack = Stack(mc, T2tt)

  data_sample.setSelectionString([getFilterCut(isData=True), leptonSelection, trigger])
  for sample in mc:
    sample.setSelectionString([getFilterCut(isData=False), leptonSelection])
  TTbarDMJets_scalar_Mchi1_Mphi100.setSelectionString([getFilterCut(isData=False), leptonSelection])

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = lambda data:data.weight, selectionString = selectionStrings[args.selection])
  
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    variable = Variable.fromString( "yield/F" ).addFiller(lambda data: 0.5 + index),
    binning=[3, 0, 3],
  ))

  plots.append(Plot(
      texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 20 GeV',
      variable = Variable.fromString( "met_pt/F" ),
      binning=[400/20,0,400],
  ))

  plots.append(Plot(
    texX = '#slash{E}_{T}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events',
    variable = Variable.fromString('metSig/F'),
    binning=[15,5,20] if args.selection.count('metSig') else [15,0,15],
  ))

  plots.append(Plot(
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2ll/F" ),
    binning=[300/15,0,300],
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
      texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 30 GeV',
      variable = Variable.fromString( "dl_mt2bb/F" ),
      binning=[420/30,70,470],
    ))

    plots.append(Plot(
      texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 30 GeV',
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
  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
  logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yields[mode]["MC"], yields[mode]["data"], lumi_scale )

  for log in [False, True]:
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      print "Plotting of " + plot.name
      plotting.draw(plot, 
	  plot_directory = os.path.join(plot_directory, args.plot_directory, mode + ("_log" if log else ""), args.selection),
	  ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
	  logX = False, logY = log, sorting = True,
	  yRange = (0.03, "auto"),
	  scaling = {},
          legend = (0.50,0.93-0.04*sum(map(len, plot.histos)),0.95,0.93),
	  drawObjects = drawObjects( not args.noData, dataMCScale , lumi_scale )
      )
  allPlots[mode] = plots

  makePieChart("pie_chart", yields, mode, mc)
#  if args.selection.count("btag0"): makePieChart("VV_chart", yields, mode, [WW, WZ, ZZ])


# Add yields in channels
dataMCScale = {}
for mode in ["SF","all"]:
  yields[mode] = {}
  for y in yields[allModes[0]]:
    try:
      yields[mode][y] = sum(yields[c][y] for c in (['ee','mumu'] if mode=="SF" else ['ee','mumu','mue']))
    except:
      yields[mode][y] = 0
  dataMCScale[mode] = yields[mode]["data"]/(yields[mode]["MC"]) if yields[mode]["MC"] > 0 else 0

  makePieChart("pie_chart", yields, mode, mc)
#/  if args.selection.count("btag0"): makePieChart("VV_chart", yields, mode, [WW, WZ, ZZ])


# Write to tex file
columns = [i.name for i in mc] + ["MC", "data"] + ([TTbarDMJets_scalar_Mchi1_Mphi100.name] if args.signal=="DM" else []) + ([T2tt.name] if args.signal=="T2tt" else [])
texdir = "tex"
try:
  os.makedirs("./" + texdir)
except:
  pass
with open("./" + texdir + "/" + args.selection + ".tex", "w") as f:
  f.write("&" + " & ".join(columns) + "\\\\ \n")
  for mode in allModes + ["SF","all"]:
    f.write(mode + " & " + " & ".join([ " %12.1f" % yields[mode][i] for i in columns]) + "\\\\ \n")


# Add the different channels and plot the sums
for mode in ["SF","all"]:
  for plot in allPlots['mumu']:
    logger.info("Adding " + plot.name + " for ee and mumu to SF")
    for plot2 in (p for p in (allPlots['ee'] if mode=="SF" else allPlots["mue"]) if p.name == plot.name):  #For SF add EE, second round add EMu for all
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
	for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
	  if i==k:
	    j.Add(l)

  for log in [False, True]:
    for plot in allPlots[allModes[0]]:
      if not args.noData: plot.histos[1][0].legendText = "Data 2016 (all channels)"
      plotting.draw(plot,
	    plot_directory = os.path.join(plot_directory, args.plot_directory, mode + ("_log" if log else ""), args.selection),
	    ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
	    logX = False, logY = log, sorting = True,
	    yRange = (0.03, "auto"),
	    scaling = {},
	    legend = (0.50,0.93-0.04*sum(map(len, plot.histos)),0.95,0.93),
	    drawObjects = drawObjects( not args.noData, dataMCScale[mode] , lumi_scale )
      )

logger.info( "Done with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )

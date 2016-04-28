#!/usr/bin/env python
''' Analysis script for TTG selection (g bbllnunu or g bbjjlnu)
'''
#
# Standard imports and batch mode
#
import ROOT
ROOT.gROOT.SetBatch(True)

from math import sqrt, cos, sin, pi
from RootTools.core.standard import *
from StopsDilepton.tools.user import plot_directory


#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--overwrite',      action='store_true', default=True,        help='overwrite?')
argParser.add_argument('--plot_directory', action='store',      default='TTG')
argParser.add_argument('--pdType',         action='store',      default='singleLep', choices=['singleLep','doubleLep'])
argParser.add_argument('--selection',      action='store',      default=None)
argParser.add_argument('--isChild',        action='store_true', default=False)
args = argParser.parse_args()

args.plot_directory += "_" + args.pdType

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

#
# Selections (three leptons with pt > 30, 20, 10 GeV)
#
from StopsDilepton.tools.objectSelection import looseMuIDString,looseEleIDString
def getLooseLeptonString(nMu, nE):
  return looseMuIDString(ptCut=10) + "==" + str(nMu) + "&&" + looseEleIDString(ptCut=10, absEtaCut=2.5) + "==" + str(nE)

def getLeptonString(nMu, nE):
#  return getLooseLeptonString(nMu, nE)
  return "nGoodMuons==" + str(nMu) + "&&nGoodElectrons==" + str(nE)


offZ          = "abs(dl_mass-91.1876)>15"
mumuSelection = getLeptonString(2, 0) + "&&isOS&&isMuMu&&HLT_mumuIso&&" + offZ 
mueSelection  = getLeptonString(1, 1) + "&&isOS&&isEMu&&HLT_mue"
eeSelection   = getLeptonString(0, 2) + "&&isOS&&isEE&&HLT_ee_DZ&&" + offZ
muSelection   = getLeptonString(1, 0)
eSelection    = getLeptonString(0, 1)

jetSelection    = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>="
bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890))>="
bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.605))>="
photonSelection = "nPhotonGood>0&&photon_idCutBased>2&&photon_pt>"
filterCut       = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&vetoPassed&&jsonPassed&&weight>0)"

#
# Cuts to iterate over
#
if args.pdType == "doubleLep":
  jetCuts=[
    ("njet1",             jetSelection+"1"),
    ("njet2",             jetSelection+"2"),
  ]
else:
  jetCuts=[
    ("njet3",             jetSelection+"3"),
    ("njet4",             jetSelection+"4"),
  ]

cuts = jetCuts + [
    ("nbtagL",            bJetSelectionL+"1"),
    ("nbtagM",            bJetSelectionM+"1"),
    ("nbtagML",           bJetSelectionM+"1&&"+bJetSelectionL+"2"),
    ("nbtagLL",           bJetSelectionL+"2"),
    ("nbtagMM",           bJetSelectionM+"2"),
    ("photon30",          photonSelection+"30"),
    ("photon50",          photonSelection+"50"),
    ("photon75",          photonSelection+"75"),
    ("photon100",         photonSelection+"100"),
    ("photon125",         photonSelection+"125"),
    ("mll20",             "dl_mass>20"),
    ("met80",             "met_pt_photonEstimated>80"),
#    ("metSig5",           "metSig_photonEstimated>5"),
#    ("dPhiJet0-dPhiJet1", "cos(met_phi_photonEstimated-JetGood_phi[0])<cos(0.25)&&cos(met_phi_photonEstimate-JetGood_phi[1])<cos(0.25)"),
  ]


#
# Construct prefixes and selectionstring
#
import itertools
selectionStrings = {}
for i_comb in reversed( range( len(cuts)+1 ) ):
    for comb in itertools.combinations( cuts, i_comb ):
        presel = [] 
        presel.extend( comb )
        selection = '-'.join([p[0] for p in presel])
        if selection.count("nbtag") > 1:   continue
        if selection.count("photon") != 1: continue
        if selection.count("njet") != 1:   continue
        if selection.count("njet1") and (selection.count("LL") or selection.count("ML") or selection.count("MM")):   continue
        if selection.count("met") > 1:     continue
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./ttG.py --selection=" + selection + " --pdType=" + args.pdType
    logfile = "log/" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=03:00:00 runPlotsOnCream02.sh")
  logger.info("All jobs launched")
  exit(0)



#
# Make samples, will be searched for in the postProcessing directory
#
if args.pdType == "singleLep": postProcessing_directory = "postProcessed_Fall15_mAODv2/singlelepTiny"
else:                          postProcessing_directory = "postProcessed_Fall15_mAODv2/dilepTiny"
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *


#
# Text on the plots
#
def drawObjects( dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'), 
      (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(lumi_scale*100)/100., dataMCScale ) )
    ]
    return [tex.DrawLatex(*l) for l in lines] 

yield_mc   = {}
yield_data = {}
allPlots   = {}
if args.pdType == "singleLep": allModes = ["mu","e"]
else:                          allModes   = ['mumu','mue','ee']
for mode in allModes:
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
  if mode=="mu":
    data_sample     = SingleMuon_Run2015D
    qcd_sample      = QCD_Mu5 #FIXME
    leptonSelection = muSelection
  elif mode=="ee":
    data_sample     = SingleElectron_Run2015D
    qcd_sample      = QCD_EMbcToE
    leptonSelection = eSelection

  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale = data_sample.lumi/1000

  mc = [ diBoson, WJetsToLNu, WZZ, DY_HT_LO, qcd_sample, singleTop, TTLep_pow, TTXNoZ, TTZtoQQ, TTZtoLLNuNu, TTG ]
  for sample in mc:
    sample.scale = lumi_scale
    sample.style = styles.fillStyle(sample.color)

  stack = Stack(mc, [data_sample])
  data_sample.setSelectionString([filterCut, leptonSelection])
  for sample in mc:
    sample.setSelectionString([leptonSelection])

  # For TTJets, do TTGJets overlap events removal
  TTJets.setSelectionString(["!isTTGJetsEvent", leptonSelection])

  logger.info( "Calculating normalization constants" )        
  yield_mc[mode]   = sum(      s.getYieldFromDraw( selectionString = selectionStrings[args.selection], weightString = 'weight')['val'] for s in mc)
  yield_data[mode] = data_sample.getYieldFromDraw( selectionString = selectionStrings[args.selection], weightString = 'weight')['val']
  if yield_mc[mode] == 0:
    logger.info("No MC yields for this selection in mode " + mode + ", skipping")
    allModes.remove(mode)
    continue
  dataMCScale      = yield_data[mode]/(yield_mc[mode]*lumi_scale)

  logger.info( "Now plotting with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )
  logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yield_mc[mode], yield_data[mode], lumi_scale )

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = lambda data:data.weight, selectionString = selectionStrings[args.selection])
  
  plots = []

  if mode in ["mumu","mue","ee"]:
    plots.append(Plot(
      texX = 'm(ll) of leading dilepton (GeV)', texY = 'Number of Events / 3 GeV',
      variable = Variable.fromString( "dl_mass/F" ),
      binning=[50/3,0,150],
      ))

    plots.append(Plot(
      texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
      variable = Variable.fromString( "dl_mt2ll_photonEstimated/F" ),
      binning=[300/20,0,300],
      ))

    plots.append(Plot(
      texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
      variable = Variable.fromString( "dl_mt2bb_photonEstimated/F" ),
      binning=[300/20,0,300],
      ))

    plots.append(Plot(
      texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
      variable = Variable.fromString( "dl_mt2blbl_photonEstimated/F" ),
      binning=[300/20,0,300],
      )) 

  plots.append(Plot(
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    variable = Variable.fromString( "met_pt_photonEstimated/F" ),
    binning=[15,0,300],
    ))

  plots.append(Plot(
    texX = '#slash{E}_{T}/#sqrt(H_{T}) (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
    variable = Variable.fromString('metSig_photonEstimated/F'),
    binning=[15,0,15],
    ))

  plots.append(Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    variable = Variable.fromString( "ht/F" ),
    binning=[510/30,90,600],
    ))

  plots.append(Plot(
    texX = 'Cos(#phi(#slash{E}_{T}, Jet[0]))', texY = 'Number of Events',
    variable = Variable.fromString('cosMetJet0phi/F').addFiller (
        helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"] )
    ), 
    binning = [10,-1,1], 
  ))

  plots.append(Plot(
    texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
    variable = Variable.fromString('cosMetJet1phi/F').addFiller (
        helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"] )
    ), 
    binning = [10,-1,1], 
  ))

  plots.append(Plot(
    texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet0pt/F').addFiller (
        helpers.uses(lambda data: data.JetGood_pt[0], "JetGood[pt/F]" )
    ), 
    binning=[900/20,30,930],
    ))

  plots.append(Plot(
    texX = 'p_{T}(2^{nd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet1pt/F').addFiller (
        helpers.uses(lambda data: data.JetGood_pt[1], "JetGood[pt/F]" )
    ), 
    binning=[600/20,30,630],
    ))

  plots.append(Plot(
    texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
    variable = Variable.fromString('nBTag/I'),
    binning=[8,0,8],
    ))

  plots.append(Plot(
    texX = 'number of jets', texY = 'Number of Events',
    variable = Variable.fromString('nJetGood/I'),
    binning=[14,0,14],
    ))

  plots.append(Plot(
    texX = 'm_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    variable = Variable.fromString( "mt_photonEstimated/F" ),
    binning=[300/10,0,300],
    ))

  plots.append(Plot(
    texX = '#eta(#gamma)', texY = 'Number of Events',
    variable = Variable.fromString( "photon_eta/F" ),
    binning=[10,-2.4,2.4],
    ))

  plots.append(Plot(
    texX = 'p_{T}(#gamma)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "photon_pt/F" ),
    binning=[10, 50,250],
    ))

  plots.append(Plot(
    texX = '#phi(#gamma)', texY = 'Number of Events',
    variable = Variable.fromString( "photon_phi/F" ),
    binning=[15,-pi,pi],
    ))

  plots.append(Plot(
    texX = '#Delta R(#gamma, l)', texY = 'Number of Events',
    variable = Variable.fromString( "photonLepdR/F" ),
    binning=[20, 0, 5],
    ))

  plots.append(Plot(
    texX = '#Delta R(#gamma, l)', texY = 'Number of Events',
    variable = Variable.fromString( "photonJetdR/F" ),
    binning=[20, 0, 5],
    ))

  read_variables = ["weight/F" , "JetGood[pt/F,eta/F,phi/F]", "dl_mass/F", "dl_mt2ll_photonEstimated/F", "dl_mt2bb_photonEstimated/F", "dl_mt2blbl_photonEstimated/F","met_pt_photonEstimated/F",
                    "metSig_photonEstimated/F", "ht/F", "nBTag/I", "nJetGood/I", "mt_photonEstimated/F", "photon_eta/F", "photon_pt/F", "photon_phi/F", "photonJetdR/F", "photonLepdR/F"]
  plotting.fill(plots, read_variables = read_variables)
  for plot in plots:
    plotting.draw(plot, 
        plot_directory = os.path.join(plot_directory, args.plot_directory, mode, args.selection),
        ratio = {'yRange':(0.1,1.9)}, 
        logX = False, logY = False, sorting = False, 
        yRange = (0.003, "auto"),
        drawObjects = drawObjects( dataMCScale, lumi_scale )
    )
  allPlots[mode] = plots



# Add yields in channels
total_mc    = sum(y for y in yield_mc.values())
total_data  = sum(y for y in yield_data.values())
lumi_scale  = 2.165
dataMCScale = total_data/(total_mc*lumi_scale)

# Add the different channels and plot the sums
for plot in allPlots[allModes[0]]:
  logger.info("Adding " + plot.name + " for mode " + allModes[0] + " to all")
  for mode in allModes[1:]:
    for plot2 in (p for p in allPlots[mode] if p.name == plot.name):
      logger.info("Adding " + plot.name + " for mode " + mode + " to all")
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
        for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
          if i==k:
            j.Add(l)

  plot.histos[1][0].legendText = "Data 2015 (all channels)"
  plotting.draw(plot,
        plot_directory = os.path.join(plot_directory, args.plot_directory, "all", args.selection),
        ratio = {'yRange':(0.1,1.9)},
        logX = False, logY = False, sorting = False,
        yRange = (0.003, "auto"),
        drawObjects = drawObjects( dataMCScale, lumi_scale )
  )

logger.info( "Done with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )

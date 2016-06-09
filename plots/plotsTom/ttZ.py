#!/usr/bin/env python
''' Analysis script for 1D 2l plots with TTZ selection (blnu bjj ll)
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
argParser.add_argument('--plot_directory', action='store',      default='TTZ')
argParser.add_argument('--pdType',         action='store',      default='doubleLep', choices=['singleLep','doubleLep'])
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
  return getLooseLeptonString(nMu, nE)

def getPtThresholdString(firstPt, secondPt, thirdPt):
  return "(Sum$(LepGood_pt>" + str(firstPt) + ")>=1&&Sum$(LepGood_pt>" + str(secondPt) + ")>=2&&Sum$(LepGood_pt>" + str(thirdPt) + ")>=3)"

useTrigger      = False #Trigger seems to be highly inefficient
mumumuSelection = "&&".join([getLeptonString(3, 0), getPtThresholdString(30, 20, 10)]) + ("&&HLT_3mu"   if useTrigger else "")
mumueSelection  = "&&".join([getLeptonString(2, 1), getPtThresholdString(30, 20, 10)]) + ("&&HLT_2mu1e" if useTrigger else "") 
mueeSelection   = "&&".join([getLeptonString(1, 2), getPtThresholdString(30, 20, 10)]) + ("&&HLT_2e1mu" if useTrigger else "")
eeeSelection    = "&&".join([getLeptonString(0, 3), getPtThresholdString(30, 20, 10)]) + ("&&HLT_3e"    if useTrigger else "")

jetSelection    = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>="
bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890))>="
bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.605))>="
zMassSelection  = "abs(mlmZ_mass-91.1876)<10"
filterCut       = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&vetoPassed&&jsonPassed&&weight>0)"


#
# Cuts to iterate over: at least 3/4 jets with 1/2 btags
#
cuts=[
    ("njet3",             jetSelection+"3"),
    ("njet4",             jetSelection+"4"),
    ("nbtagL",            bJetSelectionL+"1"),
    ("nbtagM",            bJetSelectionM+"1"),
    ("nbtagML",           bJetSelectionM+"1&&"+bJetSelectionL+"2"),
    ("nbtagLL",           bJetSelectionL+"2"),
    ("nbtagMM",           bJetSelectionM+"2"),
#    ("mll20",             "dl_mass>20"),
#    ("met50",             "met_pt>50"),
#    ("met80",             "met_pt>80"),
#    ("metSig5",           "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
#    ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
    ("onZ",               zMassSelection),
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
        if selection.count("nbtag") > 1: continue
        if selection.count("njet") != 1: continue
        if selection.count("met") > 1:   continue
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./ttZ.py --selection=" + selection + " --pdType=" + args.pdType
    logfile = "log/" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=01:00:00 runPlotsOnCream02.sh")
  logger.info("All jobs launched")
  exit(0)



#
# Make samples, will be searched for in the postProcessing directory
#
#postProcessing_directory = "postProcessed_Fall15_mAODv2/dilepTiny_3jet"
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
allModes   = ['3mu', '3e', '2mu1e','2e1mu']
for mode in allModes:
  if mode=="3mu":
    data_sample     = SingleMuon_Run2015D if args.pdType == "singleLep" else DoubleMuon_Run2015D
    qcd_sample      = QCD_Mu5 #FIXME
    leptonSelection = mumumuSelection
  elif mode=="3e":
    data_sample     = SingleElectron_Run2015D if args.pdType == "singleLep" else DoubleEG_Run2015D
    qcd_sample      = QCD_EMbcToE
    leptonSelection = eeeSelection
  elif mode=="2mu1e":
    data_sample     = SingleMuon_Run2015D if args.pdType == "singleLep" else MuonEG_Run2015D
    qcd_sample      = QCD_Mu5EMbcToE
    leptonSelection = mumueSelection
  elif mode=="2e1mu":
    data_sample     = SingleElectron_Run2015D if args.pdType == "singleLep" else MuonEG_Run2015D
    qcd_sample      = QCD_Mu5EMbcToE
    leptonSelection = mueeSelection

  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale = data_sample.lumi/1000

  mc = [ DY_HT_LO, qcd_sample, singleTop, diBoson, triBoson, WJetsToLNu, TTLep_pow, TTXNoZ, TTZtoQQ, TTZtoLLNuNu]
  for sample in mc:
    sample.scale = lumi_scale
    sample.style = styles.fillStyle(sample.color)

  stack = Stack(mc, [data_sample])
  data_sample.setSelectionString([filterCut, leptonSelection])
  for sample in mc:
    sample.setSelectionString([leptonSelection])

  logger.info( "Calculating normalization constants" )        
  yield_mc[mode]   = sum(      s.getYieldFromDraw( selectionString = selectionStrings[args.selection], weightString = 'weight')['val'] for s in mc)
  yield_data[mode] = data_sample.getYieldFromDraw( selectionString = selectionStrings[args.selection], weightString = 'weight')['val']
  dataMCScale      = yield_data[mode]/(yield_mc[mode]*lumi_scale)

  logger.info( "Now plotting with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )
  logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yield_mc[mode], yield_data[mode], lumi_scale )

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = lambda data:data.weight, selectionString = selectionStrings[args.selection])
 
  plots = []
  dl_mass  = Plot(
    texX = 'm(ll) of leading dilepton (GeV)', texY = 'Number of Events / 3 GeV',
    variable = Variable.fromString( "dl_mass/F" ),
    binning=[50/3,0,150],
    )
  plots.append( dl_mass )

  mlmZ_mass  = Plot(
    texX = 'm(ll) of best Z candidate (GeV)', texY = 'Number of Events / 3 GeV',
    variable = Variable.fromString( "mlmZ_mass/F" ),
    binning=[50/3,0,150],
    )
  plots.append( mlmZ_mass )

  dl_mt2ll  = Plot(
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2ll/F" ),
    binning=[300/20,0,300],
    )
  plots.append( dl_mt2ll )

  dl_mt2bb  = Plot(
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2bb/F" ),
    binning=[300/20,0,300],
    )
  plots.append( dl_mt2bb )

  dl_mt2blbl  = Plot(
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2blbl/F" ),
    binning=[300/20,0,300],
    ) 
  plots.append( dl_mt2blbl )

  met  = Plot(
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    variable = Variable.fromString( "met_pt/F" ),
    binning=[15,0,300],
    )
  plots.append( met )

  metSig  = Plot(
    texX = '#slash{E}_{T}/#sqrt(H_{T}) (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
    variable = Variable.fromString('metSig/F').addFiller (
        helpers.uses( 
            lambda data: data.met_pt/sqrt(data.ht) if data.ht>0 else float('nan') , 
            ["met_pt/F", "ht/F"])
    ), 
    binning=[15,0,15],
    )
  plots.append( metSig )

  ht  = Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    variable = Variable.fromString( "ht/F" ),
    binning=[510/30,90,600],
    )
  plots.append( ht )

  cosMetJet0phi = Plot(\
    texX = 'Cos(#phi(#slash{E}_{T}, Jet[0]))', texY = 'Number of Events',
    variable = Variable.fromString('cosMetJet0phi/F').addFiller (
        helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"] )
    ), 
    binning = [10,-1,1], 
  )
  plots.append( cosMetJet0phi )

  cosMetJet1phi = Plot(\
    texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
    variable = Variable.fromString('cosMetJet1phi/F').addFiller (
        helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"] )
    ), 
    binning = [10,-1,1], 
  )
  plots.append( cosMetJet1phi )

  lep0pt  = Plot(
    texX = 'p_{T}(leading lepton) (GeV)', texY = 'Number of Events / 20 GeV',
        variable = Variable.fromString('lepton0pt/F').addFiller (
        helpers.uses(lambda data: data.LepGood_pt[0], "LepGood[pt/F]" )
    ), 
    binning=[300/20,0,300],
    )
  plots.append( lep0pt )

  lep1pt  = Plot(
    texX = 'p_{T}(2nd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton1pt/F').addFiller (
        helpers.uses(lambda data: data.LepGood_pt[1], "LepGood[pt/F]" )
    ), 
    binning=[300/20,0,300],
    )
  plots.append( lep1pt )

  lep2pt  = Plot(
    texX = 'p_{T}(3rd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton2pt/F').addFiller (
        helpers.uses(lambda data: data.LepGood_pt[2], "LepGood[pt/F]" )
    ), 
    binning=[300/20,0,300],
    )
  plots.append( lep2pt )

  jet0pt  = Plot(
    texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet0pt/F').addFiller (
        helpers.uses(lambda data: data.JetGood_pt[0], "JetGood[pt/F]" )
    ), 
    binning=[900/20,30,930],
    )
  plots.append( jet0pt )

  jet1pt  = Plot(
    texX = 'p_{T}(2^{nd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet1pt/F').addFiller (
        helpers.uses(lambda data: data.JetGood_pt[1], "JetGood[pt/F]" )
    ), 
    binning=[600/20,30,630],
    )
  plots.append( jet1pt )

  jet2pt  = Plot(
    texX = 'p_{T}(3^{rd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet2pt/F').addFiller (
        helpers.uses(lambda data: data.JetGood_pt[2], "JetGood[pt/F]" )
    ), 
    binning=[300/20,30,330],
    )
  plots.append( jet2pt )

  jet3pt  = Plot(
    texX = 'p_{T}(4^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet3pt/F').addFiller (
        helpers.uses(lambda data: data.JetGood_pt[3], "JetGood[pt/F]" )
    ), 
    binning=[250/20,30,280],
    )
  plots.append( jet3pt )

  jet4pt  = Plot(
    texX = 'p_{T}(5^{th.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet4pt/F').addFiller (
        helpers.uses(lambda data: data.JetGood_pt[4], "JetGood[pt/F]" )
    ), 
    binning=[200/20,30,230],
    )
  plots.append( jet4pt )

  nbtags  = Plot(
    texX = 'number of b-tags (CSVM)', texY = 'Number of Events',
    variable = Variable.fromString('nBTag/I'),
    binning=[8,0,8],
    )
  plots.append( nbtags )

  njets  = Plot(
    texX = 'number of jets', texY = 'Number of Events',
    variable = Variable.fromString('nJetGood/I'),
    binning=[14,0,14],
    )
  plots.append( njets )

  nlep  = Plot(
    texX = 'number of leptons', texY = 'Number of Events',
    variable = Variable.fromString('nLepGood/I'),
    binning=[10,0,10],
    )
  plots.append( nlep )

  plots.append(Plot(
    texX = 'm_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    variable = Variable.fromString( "mt/F" ),
    binning=[300/10,0,300],
    ))

  read_variables = ["weight/F" , "met_phi/F", "JetGood[pt/F,eta/F,phi/F]", "LepGood[pt/F,eta/F,phi/F]", "mt/F", "nLepGood/I", "nJetGood/I", "nBTag/I", "ht/F", "metSig/F", "met_pt/F", "met_phi/F",
                    "dl_mass/F", "mlmZ_mass/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F"]
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

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
from StopsDilepton.tools.objectSelection import getFilterCut


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
# Selections (three leptons with pt > 30, 20, 10 GeV)
#
isoCut="VT" if args.selection and args.selection.count("VT") else 0.6
from StopsDilepton.tools.objectSelection import muonSelectorString,eleSelectorString
def getLooseLeptonString(nMu, nE):
  return muonSelectorString(ptCut=10, iso=isoCut) + "==" + str(nMu) + "&&" + eleSelectorString(ptCut=10, absEtaCut=2.5, iso=isoCut) + "==" + str(nE)

def getLeptonString(nMu, nE):
  return getLooseLeptonString(nMu, nE)

def getPtThresholdString(firstPt, secondPt):
    return "&&".join([muonSelectorString(ptCut=firstPt,  iso=isoCut) + "+" + eleSelectorString(ptCut=firstPt,  iso=isoCut) + ">=1",
                      muonSelectorString(ptCut=secondPt, iso=isoCut) + "+" + eleSelectorString(ptCut=secondPt, iso=isoCut) + ">=2"])

lllSelection          = {}
lllSelection['MuMu']  = "&&".join([getLeptonString(3, 0), getPtThresholdString(30, 20)])
lllSelection['MuMuE'] = "&&".join([getLeptonString(2, 1), getPtThresholdString(30, 20)])
lllSelection['MuEE']  = "&&".join([getLeptonString(1, 2), getPtThresholdString(30, 20)])
lllSelection['EE']    = "&&".join([getLeptonString(0, 3), getPtThresholdString(30, 20)])
lllSelection['EMu']   = "(("+lllSelection['MuMuE']+")||("+lllSelection['MuEE']+"))"

jetSelection    = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))"
bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.800))"
bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.460))"
zMassSelection  = "abs(mlmZ_mass-91.1876)<10"


#
# Cuts to iterate over: at least 3/4 jets with 1/2 btags
#
cuts=[
    ("njet01",            jetSelection+"<2"),
    ("njet2",             jetSelection+">=2"),
    ("njet3",             jetSelection+">=3"),
    ("njet4",             jetSelection+">=4"),
    ("nbtag0",            bJetSelectionL+"==0"),
    ("nbtagL",            bJetSelectionL+">=1"),
    ("nbtagM",            bJetSelectionM+">=1"),
    ("nbtagLL",           bJetSelectionL+">=2"),
    ("nbtagMM",           bJetSelectionM+">=2"),
    ("onZ",               zMassSelection),
    ("met30",             "met_pt>30"),
    ("mt50",              "mt>50"),
    ("dR",                "(1)"),
    ("VT",                "(1)"),
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
        if selection.count("njet01") and (selection.count("nbtagL") or selection.count("nbtagM")): continue # only look at 0b for diboson CR
        if selection.count("nbtag0") and not selection.count("njet01"): continue # only look at 0b for diboson CR
        if selection.count("met")    and not selection.count("njet01"): continue # only look at met cut for diboson CR
        if selection.count("mt")     and not selection.count("njet01"): continue # only look at met cut for diboson CR
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./ttZ.py --selection=" + selection + (" --plot_directory=" + args.plot_directory)\
                                                  + (" --logLevel=" + args.logLevel)
    logfile = "log/" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    if not args.dryRun: os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=03:00:00 runPlotsOnCream02.sh")
  logger.info("All jobs launched")
  exit(0)


#
# Read variables and sequences
#
read_variables = ["weight/F" , "met_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "LepGood[pt/F,eta/F,phi/F]", "nLepGood/I", "nJetGood/I", "nBTag/I", "ht/F", "metSig/F", "met_pt/F", "met_phi/F",
		  "dl_mass/F", "mlmZ_mass/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F"]

from StopsDilepton.tools.helpers import deltaPhi
def deltaR(eta, phi, eta2, phi2):
  return sqrt(deltaPhi(phi, phi2)**2 + (eta - eta2)**2)

def makeDeltaR(data):
  data.dR_lep0lep1 = deltaR(data.LepGood_eta[0], data.LepGood_phi[0], data.LepGood_eta[1], data.LepGood_phi[1])
  data.dR_lep1lep2 = deltaR(data.LepGood_eta[1], data.LepGood_phi[1], data.LepGood_eta[2], data.LepGood_phi[2])
  data.dR_lep0lep2 = deltaR(data.LepGood_eta[2], data.LepGood_phi[2], data.LepGood_eta[0], data.LepGood_phi[0])

  data.dR_lep0jet  = min([deltaR(data.JetGood_eta[i], data.JetGood_phi[i], data.LepGood_eta[0], data.LepGood_phi[0]) for i in range(data.nJetGood)]) if data.nJetGood else 999
  data.dR_lep1jet  = min([deltaR(data.JetGood_eta[i], data.JetGood_phi[i], data.LepGood_eta[1], data.LepGood_phi[1]) for i in range(data.nJetGood)]) if data.nJetGood else 999
  data.dR_lep2jet  = min([deltaR(data.JetGood_eta[i], data.JetGood_phi[i], data.LepGood_eta[2], data.LepGood_phi[2]) for i in range(data.nJetGood)]) if data.nJetGood else 999

  data.passed      = not args.selection.count("dR") or (data.dR_lep0lep1 > 0.1 and data.dR_lep1lep2 > 0.1 and data.dR_lep0lep2 > 0.1 and data.dR_lep0jet > 0.4 and data.dR_lep1jet > 0.4 and data.dR_lep2jet > 0.4)


def calcBTag(data):
  data.nBTag       = len([j for j in range(data.nJetGood) if data.JetGood_btagCSV[j] > 0.800])
  data.nBTagLoose  = len([j for j in range(data.nJetGood) if data.JetGood_btagCSV[j] > 0.460])
  csvValues        = [data.JetGood_btagCSV[j] for j in range(data.nJetGood)]
  csvValues.sort()
  data.leadingCSV  = csvValues[-1] if len(csvValues) > 1 else -20
  data.secondCSV   = csvValues[-2] if len(csvValues) > 2 else -20

def calcInvMass(data):
  l1 = ROOT.TLorentzVector()
  l2 = ROOT.TLorentzVector()
  l3 = ROOT.TLorentzVector()
  l1.SetPtEtaPhiM(data.LepGood_pt[0], data.LepGood_eta[0], data.LepGood_phi[0], 0)
  l2.SetPtEtaPhiM(data.LepGood_pt[1], data.LepGood_eta[1], data.LepGood_phi[1], 0)
  l3.SetPtEtaPhiM(data.LepGood_pt[2], data.LepGood_eta[2], data.LepGood_phi[2], 0)

  data.mlll = (l1 + l2 + l3).M()

  if ((l1 + l2).M() - 91.1876) < 10:
    data.mt = sqrt(2*l3.Pt()*data.met_pt*(1-cos(l3.Phi()-data.met_phi)))
  elif ((l1 + l3).M() - 91.1876) < 10:
    data.mt = sqrt(2*l2.Pt()*data.met_pt*(1-cos(l2.Phi()-data.met_phi)))
  elif ((l3 + l2).M() - 91.1876) < 10:
    data.mt = sqrt(2*l1.Pt()*data.met_pt*(1-cos(l1.Phi()-data.met_phi)))
  else:
    data.mt = 0
    data.passed = False
  
  data.passed = data.passed and (not args.selection.count("mt50") or data.mt > 50)


sequence = [makeDeltaR, calcBTag, calcInvMass]

#
# Make samples, will be searched for in the postProcessing directory
#
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import *


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

yields     = {}
allPlots   = {}
allModes   = ['3mu', '3e', '2mu1e','2e1mu']
for index, mode in enumerate(allModes):
  yields[mode] = {}

  if mode=="3mu":
    data_sample     = DoubleMuon_Run2016B
    leptonSelection = lllSelection['MuMu']
    trigger         = "HLT_mumuIso"
  elif mode=="3e":
    data_sample     = DoubleEG_Run2016B
    leptonSelection = lllSelection['EE']
    trigger         = "HLT_ee_DZ"
  elif mode=="2mu1e":
    data_sample     = MuonEG_Run2016B
    leptonSelection = lllSelection['MuMuE']
    trigger         = "HLT_mue"
  elif mode=="2e1mu":
    data_sample     = MuonEG_Run2016B
    leptonSelection = lllSelection['MuEE']
    trigger         = "HLT_mue"

  print leptonSelection

  data_sample.name = "data"
  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale = data_sample.lumi/1000

#  mc = [ DY_HT_LO, Top, EWK, TTXNoZ, TTZtoQQ, TTZtoLLNuNu]
  mc = [ DY_HT_LO, Top, multiBoson, TTXNoZ, TTZ_LO]
  for sample in mc:
    sample.scale = lumi_scale
    sample.style = styles.fillStyle(sample.color)
    sample.read_variables = ['reweightDilepTrigger/F','reweightPU/F']
    sample.weight = lambda data: data.reweightDilepTrigger*data.reweightPU

  stack = Stack(mc, [data_sample])
  data_sample.setSelectionString([getFilterCut(isData=True), leptonSelection, trigger])
  for sample in mc:
    sample.setSelectionString([getFilterCut(isData=False), leptonSelection])

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = (lambda data:data.weight if data.passed else 0), selectionString = selectionStrings[args.selection])
 
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    variable = Variable.fromString( "yield/F" ).addFiller(lambda data: 0.5 + index),
    binning=[4, 0, 4],
  ))

  plots.append(Plot(
    texX = 'm(ll) of leading dilepton (GeV)', texY = 'Number of Events / 3 GeV',
    variable = Variable.fromString( "dl_mass/F" ),
    binning=[50/3,0,150],
  ))

  plots.append(Plot(
    texX = 'm(lll) (GeV)', texY = 'Number of Events / 3 GeV',
    variable = Variable.fromString( "lll_mass/F" ).addFiller(lambda data: data.mlll),
    binning=[50/3,0,150],
  ))

  plots.append(Plot(
    texX = 'm(ll) of best Z candidate (GeV)', texY = 'Number of Events / 3 GeV',
    variable = Variable.fromString( "mlmZ_mass/F" ),
    binning=[50/3,0,150],
  ))

  plots.append(Plot(
    texX = 'm_{T} of non-Z lepton (GeV)', texY = 'Number of Events / 3 GeV',
    variable = Variable.fromString( "mt/F" ).addFiller(lambda data: data.mt),
    binning=[50/3,0,150],
  ))
  
  plots.append(Plot(
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2ll/F" ),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2bb/F" ),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2blbl/F" ),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
    variable = Variable.fromString( "met_pt/F" ),
    binning=[15,0,300],
  ))

  plots.append(Plot(
    texX = '#slash{E}_{T}/#sqrt(H_{T}) (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
    variable = Variable.fromString('metSig/F').addFiller(helpers.uses(lambda data: data.met_pt/sqrt(data.ht) if data.ht>0 else float('nan'), ["met_pt/F", "ht/F"])),
    binning=[15,0,15],
  )), 

  plots.append(Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    variable = Variable.fromString( "ht/F" ),
    binning=[510/30,90,600],
  ))

  plots.append(Plot(\
    texX = 'Cos(#phi(#slash{E}_{T}, Jet[0]))', texY = 'Number of Events',
    variable = Variable.fromString('cosMetJet0phi/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"])),
    binning = [10,-1,1], 
  ))

  plots.append(Plot(\
    texX = 'Cos(#phi(#slash{E}_{T}, Jet[1]))', texY = 'Number of Events',
    variable = Variable.fromString('cosMetJet1phi/F').addFiller(helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"])),
    binning = [10,-1,1], 
  ))

  plots.append(Plot(
    texX = 'p_{T}(leading lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton0pt/F').addFiller(helpers.uses(lambda data: data.LepGood_pt[0], "LepGood[pt/F]")),
    binning=[300/20,0,300],
  )), 

  plots.append(Plot(
    texX = 'p_{T}(2nd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton1pt/F').addFiller(helpers.uses(lambda data: data.LepGood_pt[1], "LepGood[pt/F]")),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'p_{T}(3rd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton2pt/F').addFiller(helpers.uses(lambda data: data.LepGood_pt[2], "LepGood[pt/F]")),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = '#eta(leading lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton0eta/F').addFiller(helpers.uses(lambda data: abs(data.LepGood_eta[0]), "LepGood[eta/F]")),
    binning=[10, 0, 2.4],
  ))

  plots.append(Plot(
    texX = '#eta(2nd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton1eta/F').addFiller(helpers.uses(lambda data: abs(data.LepGood_eta[1]), "LepGood[eta/F]")),
    binning=[10, 0, 2.4],
  ))

  plots.append(Plot(
    texX = '#eta(3rd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton2eta/F').addFiller(helpers.uses(lambda data: abs(data.LepGood_eta[2]), "LepGood[eta/F]")),
    binning=[10, 0, 2.4],
  ))

  plots.append(Plot(
    texX = '#phi(leading lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton0phi/F').addFiller(helpers.uses(lambda data: data.LepGood_phi[0], "LepGood[phi/F]")), 
    binning=[10, -pi, pi],
  ))

  plots.append(Plot(
    texX = '#phi(2nd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('lepton1phi/F').addFiller(helpers.uses(lambda data: data.LepGood_phi[1], "LepGood[phi/F]")), 
    binning=[10, -pi, pi],
  ))

  plots.append(Plot(
    texX = '#phi(3rd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
        variable = Variable.fromString('lepton2phi/F').addFiller(helpers.uses(lambda data: data.LepGood_phi[2], "LepGood[phi/F]")),
    binning=[10, -pi, pi],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{1},l_{2}) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('dR_lep1lep2/I').addFiller(lambda data: data.dR_lep1lep2),
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{0},l_{2}) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('dR_lep0lep2/I').addFiller(lambda data: data.dR_lep0lep2),
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{0},l_{1}) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('dR_lep0lep1/I').addFiller(lambda data: data.dR_lep0lep1),
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{0},j) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('dR_lep0jet/I').addFiller(lambda data: data.dR_lep0jet),
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{1},j) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('dR_lep1jet/I').addFiller(lambda data: data.dR_lep1jet),
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{2},j) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('dR_lep2jet/I').addFiller(lambda data: data.dR_lep2jet),
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet0pt/F').addFiller(helpers.uses(lambda data: data.JetGood_pt[0] if data.nJetGood > 0 else -1, "JetGood[pt/F]")), 
    binning=[900/20,30,930],
  ))

  plots.append(Plot(
    texX = 'p_{T}(2^{nd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet1pt/F').addFiller(helpers.uses(lambda data: data.JetGood_pt[1] if data.nJetGood > 1 else -1, "JetGood[pt/F]")), 
    binning=[600/20,30,630],
  ))

  plots.append(Plot(
    texX = 'p_{T}(3^{rd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString('jet2pt/F').addFiller(helpers.uses(lambda data: data.JetGood_pt[2] if data.nJetGood > 2 else -1, "JetGood[pt/F]")), 
    binning=[300/20,30,330],
  ))

  plots.append(Plot(
    texX = 'number of jets', texY = 'Number of Events',
    variable = Variable.fromString('nJetGood/I'),
    binning=[14,0,14],
  ))

  plots.append(Plot(
    texX = 'number of leptons', texY = 'Number of Events',
    variable = Variable.fromString('nLepGood/I'),
    binning=[10,0,10],
  ))

  if not selection.count("nbtag0"):
    plots.append(Plot(
      texX = 'number of loose b-tags (CSV)', texY = 'Number of Events',
      variable = Variable.fromString('nBTagLoose/I').addFiller(lambda data: data.nBTagLoose),
      binning=[8,0,8],
    ))

    plots.append(Plot(
      texX = 'number of medium b-tags (CSV)', texY = 'Number of Events',
      variable = Variable.fromString('nBTag/I').addFiller(lambda data: data.nBTag),
      binning=[8,0,8],
    ))

  plots.append(Plot(
    texX = 'highest CSV', texY = 'Number of Events',
    variable = Variable.fromString('leadingCSV/I').addFiller(lambda data: data.leadingCSV),
    binning=[10,0,1],
  ))

  plots.append(Plot(
    texX = 'highest CSV', texY = 'Number of Events',
    variable = Variable.fromString('secondCSV/I').addFiller(lambda data: data.secondCSV),
    binning=[10,0,1],
  ))

  plotting.fill(plots, read_variables = read_variables, sequence=sequence)

  # Get normalization yields from yield histogram
  for plot in plots:
    if plot.name == "yield":
      for i, l in enumerate(plot.histos):
        for j, h in enumerate(l):
          yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
          h.GetXaxis().SetBinLabel(1, "#mu#mu#mu")
          h.GetXaxis().SetBinLabel(2, "eee")
          h.GetXaxis().SetBinLabel(3, "#mu#mue")
          h.GetXaxis().SetBinLabel(4, "#muee")

  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
  logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yields[mode]["MC"], yields[mode]["data"], lumi_scale )

  for plot in plots:
    plotting.draw(plot, 
        plot_directory = os.path.join(plot_directory, args.plot_directory, mode, args.selection),
        ratio = {'yRange':(0.1,1.9)}, 
        logX = False, logY = False, sorting = True, 
        yRange = (0.003, "auto"),
        drawObjects = drawObjects( dataMCScale, lumi_scale )
    )
  allPlots[mode] = plots


# Add yields in channels
yields["all"] = {}
for y in yields[allModes[0]]:
  try:
    yields["all"][y] = sum(yields[mode][y] for mode in allModes)
  except:
    yields["all"][y] = 0
dataMCScale = yields["all"]["data"]/(yields["all"]["MC"])



# Write to tex file
columns = [i.name for i in mc] + ["MC", "data"]
texdir = "tex_ttZ"
try:
  os.makedirs("./" + texdir)
except:
  pass
with open("./" + texdir + "/" + args.selection + ".tex", "w") as f:
  f.write("&" + " & ".join(columns) + "\\\\ \n")
  for mode in allModes + ["all"]:
    f.write(mode + " & " + " & ".join([ " %12.1f" % yields[mode][i] for i in columns]) + "\\\\ \n")







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

  plot.histos[1][0].legendText = "Data 2016 (all channels)"
  plotting.draw(plot,
        plot_directory = os.path.join(plot_directory, args.plot_directory, "all", args.selection),
        ratio = {'yRange':(0.1,1.9)},
        logX = False, logY = False, sorting = True,
        yRange = (0.003, "auto"),
        drawObjects = drawObjects( dataMCScale, lumi_scale )
  )

logger.info( "Done with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )

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
argParser.add_argument('--selection',      action='store',      default=None)
argParser.add_argument('--isChild',        action='store_true', default=False)
argParser.add_argument('--runLocal',       action='store_true', default=False)
argParser.add_argument('--LO',             action='store_true', default=False)
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
from StopsDilepton.tools.trilepSelection import getTrilepSelection

jetSelection    = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))"
jetSelection40  = "(Sum$(JetGood_pt>40&&abs(JetGood_eta)<2.4&&JetGood_id))"
bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.8484))"
bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.5426))"
zMassSelection  = "abs(mlmZ_mass-91.1876)<10"


#
# Cuts to iterate over: at least 3/4 jets with 1/2 btags
#
cuts=[
#   ("lpt_40_20_20",      '(1)'),
#   ("njet01",            jetSelection+"<2"),
    ("njet2",             jetSelection+"==2"),
    ("njet3",             jetSelection+"==3"),
    ("njet4",             jetSelection+"==4"),
#   ("njet40_3",          jetSelection40+"==3"),
#   ("njet40_4",          jetSelection40+"==4"),
#   ("nbtag0",            bJetSelectionM+"==0"),
#   ("nbtagL",            bJetSelectionL+"==1"),
    ("nbtagM",            bJetSelectionM+"==1"),
#   ("nbtagLL",           bJetSelectionL+"==2"),
    ("nbtagMM",           bJetSelectionM+"==2"),
    ("onZ",               zMassSelection),
    ("met30",             "met_pt>30"),
#   ("mt50",              "mt>50"),
    ("dR",                "(1)"),
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
        if selection.count("mt")     and not selection.count("njet01"): continue # only look at met cut for diboson CR
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

def launch(command, logfile):
  if args.runLocal: os.system(command + " --isChild &> " + logfile)
  else:             os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=10:00:00 runPlotsOnCream02.sh")

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./ttZ.py --selection=" + selection + (" --plot_directory=" + args.plot_directory)\
                                                  + (" --logLevel=" + args.logLevel)\
                                                  + (" --LO" if args.LO else "")
    logfile = "log/" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    if not args.dryRun: launch(command, logfile)
  logger.info("All jobs launched")
  exit(0)


if args.LO: args.plot_directory += "LO"

#
# Read variables and sequences
#
read_variables = ["weight/F" , "met_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "LepGood[pt/F,eta/F,phi/F]", "nLepGood/I", "nJetGood/I", "nBTag/I", "ht/F", "metSig/F", "met_pt/F", "met_phi/F",
                  "dl_mass/F", "mlmZ_mass/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F"]

from StopsDilepton.tools.helpers import deltaPhi
def deltaR(eta, phi, eta2, phi2):
  return sqrt(deltaPhi(phi, phi2)**2 + (eta - eta2)**2)

def makeDeltaR(event, sample):
  event.dR_lep0lep1 = deltaR(event.LepGood_eta[0], event.LepGood_phi[0], event.LepGood_eta[1], event.LepGood_phi[1])
  event.dR_lep1lep2 = deltaR(event.LepGood_eta[1], event.LepGood_phi[1], event.LepGood_eta[2], event.LepGood_phi[2])
  event.dR_lep0lep2 = deltaR(event.LepGood_eta[2], event.LepGood_phi[2], event.LepGood_eta[0], event.LepGood_phi[0])

  event.dR_lep0jet  = min([deltaR(event.JetGood_eta[i], event.JetGood_phi[i], event.LepGood_eta[0], event.LepGood_phi[0]) for i in range(event.nJetGood)]) if event.nJetGood else 999
  event.dR_lep1jet  = min([deltaR(event.JetGood_eta[i], event.JetGood_phi[i], event.LepGood_eta[1], event.LepGood_phi[1]) for i in range(event.nJetGood)]) if event.nJetGood else 999
  event.dR_lep2jet  = min([deltaR(event.JetGood_eta[i], event.JetGood_phi[i], event.LepGood_eta[2], event.LepGood_phi[2]) for i in range(event.nJetGood)]) if event.nJetGood else 999

  event.passed      = not args.selection.count("dR") or (event.dR_lep0lep1 > 0.1 and event.dR_lep1lep2 > 0.1 and event.dR_lep0lep2 > 0.1 and event.dR_lep0jet > 0.4 and event.dR_lep1jet > 0.4 and event.dR_lep2jet > 0.4)


def calcBTag(event, sample):
  event.nJetGood    = len([j for j in range(event.nJetGood) if event.JetGood_pt[j] > 40])
  event.nBTag       = len([j for j in range(event.nJetGood) if event.JetGood_btagCSV[j] > 0.8484])
  event.nBTagLoose  = len([j for j in range(event.nJetGood) if event.JetGood_btagCSV[j] > 0.5426])
  csvValues        = [event.JetGood_btagCSV[j] for j in range(event.nJetGood)]
  csvValues.sort()
  event.leadingCSV  = csvValues[-1] if len(csvValues) > 1 else -20
  event.secondCSV   = csvValues[-2] if len(csvValues) > 2 else -20

def calcInvMass(event, sample):
  l1 = ROOT.TLorentzVector()
  l2 = ROOT.TLorentzVector()
  l3 = ROOT.TLorentzVector()
  l1.SetPtEtaPhiM(event.LepGood_pt[0], event.LepGood_eta[0], event.LepGood_phi[0], 0)
  l2.SetPtEtaPhiM(event.LepGood_pt[1], event.LepGood_eta[1], event.LepGood_phi[1], 0)
  l3.SetPtEtaPhiM(event.LepGood_pt[2], event.LepGood_eta[2], event.LepGood_phi[2], 0)

  event.mlll = (l1 + l2 + l3).M()

  if ((l1 + l2).M() - 91.1876) < 10:   event.mt = sqrt(2*l3.Pt()*event.met_pt*(1-cos(l3.Phi()-event.met_phi)))
  elif ((l1 + l3).M() - 91.1876) < 10: event.mt = sqrt(2*l2.Pt()*event.met_pt*(1-cos(l2.Phi()-event.met_phi)))
  elif ((l3 + l2).M() - 91.1876) < 10: event.mt = sqrt(2*l1.Pt()*event.met_pt*(1-cos(l1.Phi()-event.met_phi)))
  else:
    event.mt = 0
    event.passed = False
  
  event.passed = event.passed and (not args.selection.count("mt50") or event.mt > 50)


sequence = [makeDeltaR, calcBTag, calcInvMass]

#
# Make samples, will be searched for in the postProcessing directory
#
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import *


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

  if   mode=="3mu":   data_sample         = DoubleMuon_Run2016_backup
  elif mode=="3e":    data_sample         = DoubleEG_Run2016_backup
  elif mode=="2mu1e": data_sample         = MuonEG_Run2016_backup
  elif mode=="2e1mu": data_sample         = MuonEG_Run2016_backup

  if mode=="3mu":     data_sample.texName = "data (3 #mu)"
  elif mode=="3e":    data_sample.texName = "data (3 e)"
  elif mode=="2mu1e": data_sample.texName = "data (2 #mu, 1 e)"
  elif mode=="2e1mu": data_sample.texName = "data (2 e, 1 #mu)"


  data_sample.setSelectionString([getFilterCut(isData=True), getTrilepSelection(mode, args.selection.count('lpt_40_20_20'))])
  data_sample.name = "data"
  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale = data_sample.lumi/1000

  mc = [ DY_HT_LO, Top_pow, multiBoson, TTXNoZ, TTZ_LO if args.LO else TTZ]
  for sample in mc:
    sample.scale          = lumi_scale
    sample.style          = styles.fillStyle(sample.color, lineColor = sample.color)
    sample.read_variables = ['reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F', 'nTrueInt/F']
   # sample.weight         = lambda event, sample: event.reweightBTag_SF*event.reweightLeptonHIPSF*event.reweightDilepTriggerBackup*nTrueInt27fb_puRW(event.nTrueInt)
    sample.weight         = lambda event, sample: event.reweightDilepTriggerBackup*event.reweightPU36fb
    sample.setSelectionString([getFilterCut(isData=False), getTrilepSelection(mode, args.selection.count('lpt_40_20_20'))])

  stack = Stack(mc, data_sample)

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = (lambda event, sample:event.weight if event.passed else 0), selectionString = selectionStrings[args.selection])
 
  plots = []

  plots.append(Plot(
    texX = 'yield', texY = 'Number of Events',
    name = 'yield', attribute = lambda event, sample: 0.5 + index,
    binning=[4, 0, 4],
  ))

  plots.append(Plot(
    texX = 'm(ll) of leading dilepton (GeV)', texY = 'Number of Events / 3 GeV',
    attribute = TreeVariable.fromString( "dl_mass/F" ),
    binning=[50/3,0,150],
  ))

  plots.append(Plot(
    texX = 'm(lll) (GeV)', texY = 'Number of Events / 3 GeV',
    name = 'lll_mass', attribute = lambda event, sample: event.mlll,
    binning=[50/3,0,150],
  ))

  plots.append(Plot(
    texX = 'm(ll) of best Z candidate (GeV)', texY = 'Number of Events / 3 GeV',
    attribute = TreeVariable.fromString( "mlmZ_mass/F" ),
    binning=[50/3,0,150],
  ))

  plots.append(Plot(
    texX = 'm_{T} of non-Z lepton (GeV)', texY = 'Number of Events / 3 GeV',
    name = 'mt', attribute = lambda event, sample: event.mt,
    binning=[50/3,0,150],
  ))
  
  plots.append(Plot(
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'MT_{2}^{bb} (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2bb/F" ),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'MT_{2}^{blbl} (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2blbl/F" ),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'E_{T}^{miss} (GeV)', texY = 'Number of Events / 50 GeV',
    attribute = TreeVariable.fromString( "met_pt/F" ),
    binning=[15,0,300],
  ))

  plots.append(Plot(
    texX = 'E_{T}^{miss}/#sqrt(H_{T}) (GeV^{1/2})', texY = 'Number of Events / 100 GeV',
    name = 'metSig',
    attribute = lambda event, sample: event.met_pt/sqrt(event.ht) if event.ht>0 else float('nan'), 
    read_variables = ["met_pt/F", "ht/F"],
    binning=[15,0,15],
  )), 

  plots.append(Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    attribute = TreeVariable.fromString( "ht/F" ),
    binning=[510/30,90,600],
  ))

  plots.append(Plot(\
    texX = 'Cos(#phi(#E_{T}^{miss} Jet[0]))', texY = 'Number of Events',
    name = 'cosMetJet0phi',
    attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[0] ) , 
    read_variables = ["met_phi/F", "JetGood[phi/F]"],
    binning = [10,-1,1], 
  ))

  plots.append(Plot(\
    texX = 'Cos(#phi(E_{T}^{miss}, Jet[1]))', texY = 'Number of Events',
    name = 'cosMetJet1phi',
    attribute = lambda event, sample: cos( event.met_phi - event.JetGood_phi[1] ), 
    read_variables = ["met_phi/F", "JetGood[phi/F]"],
    binning = [10,-1,1], 
  ))

  plots.append(Plot(
    texX = 'p_{T}(leading lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'lepton0pt', attribute = lambda event, sample: event.LepGood_pt[0],
    binning=[300/20,0,300],
  )), 

  plots.append(Plot(
    texX = 'p_{T}(2nd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'lepton1pt', attribute = lambda event, sample: event.LepGood_pt[1],
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'p_{T}(3rd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'lepton2pt', attribute = lambda event, sample: event.LepGood_pt[2],
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = '#eta(leading lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'lepton0eta', attribute = lambda event, sample: abs(event.LepGood_eta[0]),
    binning=[10, 0, 2.4],
  ))

  plots.append(Plot(
    texX = '#eta(2nd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'lepton1eta', attribute = lambda event, sample: abs(event.LepGood_eta[1]),
    binning=[10, 0, 2.4],
  ))

  plots.append(Plot(
    texX = '#eta(3rd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'lepton2eta', attribute = lambda event, sample: abs(event.LepGood_eta[2]),
    binning=[10, 0, 2.4],
  ))

  plots.append(Plot(
    texX = '#phi(leading lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'lepton0phi', attribute = lambda event, sample: event.LepGood_phi[0], 
    binning=[10, -pi, pi],
  ))

  plots.append(Plot(
    texX = '#phi(2nd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'lepton1phi', attribute = lambda event, sample: event.LepGood_phi[1], 
    binning=[10, -pi, pi],
  ))

  plots.append(Plot(
    texX = '#phi(3rd lepton) (GeV)', texY = 'Number of Events / 20 GeV',
        name = 'lepton2phi', attribute = lambda event, sample: event.LepGood_phi[2],
    binning=[10, -pi, pi],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{1},l_{2})', texY = 'Number of Events / 20 GeV',
    name = 'dR_lep1lep2', attribute = lambda event, sample: event.dR_lep1lep2,
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{0},l_{2})', texY = 'Number of Events / 20 GeV',
    name = 'dR_lep0lep2', attribute = lambda event, sample: event.dR_lep0lep2,
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{0},l_{1})', texY = 'Number of Events / 20 GeV',
    name = 'dR_lep0lep1', attribute = lambda event, sample: event.dR_lep0lep1,
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{0},j)', texY = 'Number of Events / 20 GeV',
    name = 'dR_lep0jet', attribute = lambda event, sample: event.dR_lep0jet,
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{1},j)', texY = 'Number of Events / 20 GeV',
    name = 'dR_lep1jet', attribute = lambda event, sample: event.dR_lep1jet,
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#DeltaR(l_{2},j)', texY = 'Number of Events / 20 GeV',
    name = 'dR_lep2jet', attribute = lambda event, sample: event.dR_lep2jet,
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'jet0pt', attribute = lambda event, sample: event.JetGood_pt[0] if event.nJetGood > 0 else -1, 
    binning=[900/20,30,930],
  ))

  plots.append(Plot(
    texX = 'p_{T}(2^{nd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'jet1pt', attribute = lambda event, sample: event.JetGood_pt[1] if event.nJetGood > 1 else -1, 
    binning=[600/20,30,630],
  ))

  plots.append(Plot(
    texX = 'p_{T}(3^{rd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'jet2pt', attribute = lambda event, sample: event.JetGood_pt[2] if event.nJetGood > 2 else -1, 
    binning=[300/20,30,330],
  ))

  plots.append(Plot(
    texX = 'number of jets', texY = 'Number of Events',
    name = 'nJetGood',
    attribute = lambda event, sample: event.nJetGood,
    binning=[14,0,14],
  ))

  plots.append(Plot(
    texX = 'number of leptons', texY = 'Number of Events',
    attribute = TreeVariable.fromString('nLepGood/I'),
    binning=[10,0,10],
  ))

  if not selection.count("nbtag0"):
    plots.append(Plot(
      texX = 'number of loose b-tags (CSV)', texY = 'Number of Events',
      name = 'nBTagLoose', attribute = lambda event, sample: event.nBTagLoose,
      binning=[8,0,8],
    ))

    plots.append(Plot(
      texX = 'number of medium b-tags (CSV)', texY = 'Number of Events',
      name = 'nBTag', attribute = lambda event, sample: event.nBTag,
      binning=[8,0,8],
    ))

  plots.append(Plot(
    texX = 'highest CSV', texY = 'Number of Events',
    name = 'leadingCSV', attribute = lambda event, sample: event.leadingCSV,
    binning=[10,0,1],
  ))

  plots.append(Plot(
    texX = 'highest CSV', texY = 'Number of Events',
    name = 'secondCSV', attribute = lambda event, sample: event.secondCSV,
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
with open("./" + texdir + "/" + args.selection + ("_LO" if args.LO else "") + ".tex", "w") as f:
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

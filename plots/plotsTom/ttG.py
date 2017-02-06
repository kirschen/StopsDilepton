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
from StopsDilepton.tools.helpers import deltaPhi
from StopsDilepton.tools.objectSelection import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--subtract',       action='store_true', default=False,       help='subtract residual backgrounds?')
argParser.add_argument('--add2015',        action='store_true', default=False,       help='add 2015?')
argParser.add_argument('--plot_directory', action='store',      default='TTG')
argParser.add_argument('--selection',      action='store',      default=None)
argParser.add_argument('--isChild',        action='store_true', default=False)
argParser.add_argument('--runLocal',       action='store_true', default=False)
argParser.add_argument('--dryRun',         action='store_true', default=False,       help='do not launch subjobs')
args = argParser.parse_args()
if args.subtract: args.plot_directory += "_subtracted"

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

selectionStrings = ["njet2p-relIso0.12-looseLeptonVeto-photon30",
                    "njet2p-relIso0.12-looseLeptonVeto-photon30-llgNoZ",
                    "njet2p-relIso0.12-looseLeptonVeto-photon30-llgNoZ-mll40",
                    "njet2p-relIso0.12-looseLeptonVeto-photon30-gJetdR-gLepdR-btag1p",
                    "njet2p-relIso0.12-looseLeptonVeto-photon30-llgNoZ-gJetdR-gLepdR-btag1p",
                    "njet2p-relIso0.12-looseLeptonVeto-photon30-llgNoZ-gJetdR-gLepdR-btag1p-mll40",
                    "njet2p-relIso0.12-looseLeptonVeto-photon30-llgNoZ-gJetdR-gLepdR-btag1p-mll40-met80",
                    "njet2p-relIso0.12-looseLeptonVeto-photon30-llgNoZ-gJetdR-gLepdR-btag1p-mll40-met80-metSig5-dPhiJet0-dPhiJet1",
                    "njet2p-relIso0.12-looseLeptonVeto-photon50",
                    "njet2p-relIso0.12-looseLeptonVeto-photon50-llgNoZ",
                    "njet2p-relIso0.12-looseLeptonVeto-photon50-llgNoZ-mll40",
                    "njet2p-relIso0.12-looseLeptonVeto-photon50-llgNoZ-gJetdR-gLepdR-btag1p",
                    "njet2p-relIso0.12-looseLeptonVeto-photon50-llgNoZ-gJetdR-gLepdR-btag1p-mll40",
                    "njet2p-relIso0.12-looseLeptonVeto-photon50-llgNoZ-gJetdR-gLepdR-btag1p-mll40-met80",
                    "njet2p-relIso0.12-looseLeptonVeto-photon50-llgNoZ-gJetdR-gLepdR-btag1p-mll40-met80-metSig5-dPhiJet0-dPhiJet1"]


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
    command = "./ttG.py --selection=" + selection + (" --subtract" if args.subtract else "") + (" --add2015" if args.add2015 else "")
    logfile = "log/" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    if not args.dryRun: launch(command, logfile)
  logger.info("All jobs launched")
  exit(0)

if args.add2015:
  args.plot_directory += "_combined"

#
# Make samples, will be searched for in the postProcessing directory
#
postProcessing_directory = "postProcessed_80X_v22/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import *
postProcessing_directory = "postProcessed_80X_v23/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
postProcessing_directory = "postProcessed_80X_v23/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed_photonSamples import *


#
# Text on the plots
#
def drawObjects( dataMCScale, lumi_scale ):
    if args.add2015: lumi_scale += 2.16
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'), 
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) )
    ]
    return [tex.DrawLatex(*l) for l in lines] 


#
# Read variables and sequences
#
read_variables = ["weight/F" , "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll_photonEstimated/F", "dl_mt2bb_photonEstimated/F", "dl_mt2blbl_photonEstimated/F",
                  "met_pt_photonEstimated/F", "met_phi_photonEstimated/F",
                  "metSig_photonEstimated/F", "ht/F", "nBTag/I", "nJetGood/I", "mt_photonEstimated/F", "photon_pt/F", "photon_eta/F",  "photon_phi/F", "photonJetdR/F", "photonLepdR/F"]

def photonDeltaR(event, eta, phi):
  return sqrt(deltaPhi(event.photon_phi, phi)**2 + (event.photon_eta - eta)**2)

def makeDeltaR(event, sample):
  event.photonLep1DeltaR     = photonDeltaR(event, event.l1_eta, event.l1_phi)
  event.photonLep2DeltaR     = photonDeltaR(event, event.l2_eta, event.l2_phi)
  event.JetGood_photonDeltaR = [photonDeltaR(event, event.JetGood_eta[i], event.JetGood_phi[i]) for i in range(event.nJetGood)]

# Filter on dR jets and recalculate jet var
def filterJets(event, sample):
  if args.selection.count("gJetdR"): event.goodJetIndices = [i for i in range(event.nJetGood) if event.JetGood_photonDeltaR[i] > 0.3]
  else:                              event.goodJetIndices = [i for i in range(event.nJetGood)]
  event.nJetGood               = len(event.goodJetIndices)
  event.ht                     = sum([event.JetGood_pt[j] for j in event.goodJetIndices])
  event.metSig_photonEstimated = event.met_pt_photonEstimated/sqrt(event.ht) if event.ht !=0 else float('nan')
  event.nBTag                  = len([j for j in event.goodJetIndices if event.JetGood_btagCSV[j] > 0.800])
  event.nBTagLoose             = len([j for j in event.goodJetIndices if event.JetGood_btagCSV[j] > 0.460])
  event.dPhiMetJet             = [cos(event.met_phi_photonEstimated - event.JetGood_phi[j]) for j in event.goodJetIndices]

# Make photonLepdR selection or re-evaluate jet selection after photonJetdR
def otherSelections(event, sample):
  event.passed = True
  if args.selection.count("gLepdR"):
   # event.passed = (event.passed and event.photonLep1DeltaR > 0.3 and event.photonLep2DeltaR > 0.3)
    event.passed = (event.passed and event.photonLep1DeltaR > 0.5 and event.photonLep2DeltaR > 0.5)
  if args.selection.count("gJetdR"):
    if args.selection.count("njet2p"):            event.passed = (event.passed and event.nJetGood > 1)
    if args.selection.count("btagL"):             event.passed = (event.passed and event.nBTagLoose > 0)
    if args.selection.count("btag1p"):            event.passed = (event.passed and event.nBTag > 0)
    if args.selection.count("metSig5"):           event.passed = (event.passed and event.metSig_photonEstimated > 5)
    if args.selection.count("dPhiJet0-dPhiJet1"): event.passed = (event.passed and max(event.dPhiMetJet[0], event.dPhiMetJet[1]) < cos(0.25))

sequence = [makeDeltaR, filterJets, otherSelections]

offZ            = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ")) else ""
photonSelection = "(nPhotonGood>0&&photon_eta<2.5&&photon_idCutBased>2)"
def getLeptonSelection(mode):
  if   mode=="mumu": return photonSelection + "&&(nGoodMuons==2&&nGoodElectrons==0&&isOS&&l1_pt>25&&isMuMu" + offZ + ")"
  elif mode=="mue":  return photonSelection + "&&(nGoodMuons==1&&nGoodElectrons==1&&isOS&&l1_pt>25&&isEMu)"
  elif mode=="ee":   return photonSelection + "&&(nGoodMuons==0&&nGoodElectrons==2&&isOS&&l1_pt>25&&isEE" + offZ + ")"


#
# Loop over channels
#
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}
  if   mode=="mumu": data_sample = DoubleMuon_Run2016_backup
  elif mode=="ee":   data_sample = DoubleEG_Run2016_backup
  elif mode=="mue":  data_sample = MuonEG_Run2016_backup

  if   mode=="mumu": data_sample.texName = "data (2 #mu)"
  elif mode=="ee":   data_sample.texName = "data (2 e)"
  elif mode=="mue":  data_sample.texName = "data (1 #mu, 1 e)"

  data_sample.setSelectionString([getFilterCut(isData=True), getLeptonSelection(mode)])
  data_sample.name  = "data"
  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale        = data_sample.lumi/1000

  mc    = [TTG, ZG, DY_HT_LO, multiBoson, TTJets_Lep, singleTop, TTX]
  stack = Stack(mc, [data_sample])

  for sample in mc:
    sample.scale          = lumi_scale
    sample.style          = styles.fillStyle(sample.color)
    sample.read_variables = ['reweightBTag_SF/F','reweightDilepTrigger/F','reweightPU/F','reweightLeptonHIPSF/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F', 'nTrueInt/F']
    sample.weight         = lambda event, sample: event.reweightLeptonSF*event.reweightDilepTriggerBackup*event.reweightPU36fb
    sample.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])


  # For TTJets, do TTGJets overlap events removal
  TTJets_Lep.setSelectionString(["TTGJetsEventType<4", getFilterCut(isData=False), getLeptonSelection(mode)])
  DY_HT_LO.setSelectionString(  ["TTGJetsEventType<4", getFilterCut(isData=False), getLeptonSelection(mode)])

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = (lambda event, sample:event.weight if event.passed else 0), selectionString = cutInterpreter.cutString(args.selection, photonEstimated=True))
  
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    attribute = lambda event, sample: 0.5 + index,
    binning=[3, 0, 3],
  ))

  plots.append(Plot(
    texX = 'm(ll) of leading dilepton (GeV)', texY = 'Number of Events / GeV',
    attribute = TreeVariable.fromString( "dl_mass/F" ),
    binning=[200/4,0,200],
  ))

  theDlgPlot = Plot(
    texX = 'm(ll#gamma) of leading dilepton and photon (GeV)', texY = 'Number of Events / GeV',
    attribute = TreeVariable.fromString( "dlg_mass/F" ),
    binning=Binning.fromThresholds([50,70,80,84,88,92,94,100,120,140,160,180,200,230,260,290,320,360]),
  )
  theDlgPlot.binWidth = 1
  plots.append(theDlgPlot)

  plots.append(Plot(
    texX = 'm(ll#gamma) of leading dilepton and photon (GeV)', texY = 'Number of Events / GeV',
    attribute = TreeVariable.fromString( "dlg_mass/F" ),
    name = "dlg_mass_zoomed",
    binning=[80, 50, 130],
  ))

  plots.append(Plot(
    texX = 'M_{T2}(ll) (including #gamma) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2ll_photonEstimated/F" ),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'M_{T2}(bb) (including #gamma) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2bb_photonEstimated/F" ),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'M_{T2}(blbl) (including #gamma) (GeV)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "dl_mt2blbl_photonEstimated/F" ),
    binning=[300/20,0,300],
  ))

  plots.append(Plot(
    texX = 'E_{T}^{miss} (including #gamma) (GeV)', texY = 'Number of Events / 50 GeV',
    attribute = TreeVariable.fromString( "met_pt_photonEstimated/F" ),
    binning=[300/50,0,300],
  ))

  plots.append(Plot(
    texX = 'E_{T}^{miss}/#sqrt{H_{T}} (including #gamma) (GeV^{1/2})', texY = 'Number of Events',
    name = 'metSig_photonEstimated', attribute = lambda event, sample: event.met_pt_photonEstimated/sqrt(event.ht),
    binning=[15,0,15],
  ))

  plots.append(Plot(
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    name = 'ht', attribute = lambda event, sample: event.ht,
    binning=[510/30,90,600],
  ))

  plots.append(Plot(
    texX = 'Cos(#phi(E_{T}^{miss}, Jet[0]))', texY = 'Number of Events',
    name = 'cosMetJet0phi', attribute = lambda event, sample: event.dPhiMetJet[0] if event.nJetGood > 0 else -1,
    binning = [10,-1,1], 
  ))

  plots.append(Plot(
    texX = 'Cos(#phi(E_{T}^{miss}, Jet[1]))', texY = 'Number of Events',
    name = 'cosMetJet1phi', attribute = lambda event, sample: event.dPhiMetJet[1] if event.nJetGood > 1 else -1,
    binning = [10,-1,1], 
  ))

  plots.append(Plot(
    texX = 'p_{T}(leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'jet1pt', attribute = lambda event, sample: event.JetGood_pt[event.goodJetIndices[0]] if event.nJetGood > 0 else -1,
    binning=[500/20,30,530],
  ))

  plots.append(Plot(
    texX = 'p_{T}(2^{nd.} leading jet) (GeV)', texY = 'Number of Events / 20 GeV',
    name = 'jet2pt', attribute = lambda event, sample: event.JetGood_pt[event.goodJetIndices[1]] if event.nJetGood > 1 else -1,
    binning=[400/20,30,430],
  ))

  plots.append(Plot(
    texX = 'number of medium b-tags (CSVM)', texY = 'Number of Events',
    name = 'nBTag', attribute = lambda event, sample: event.nBTag,
    binning=[8,0,8],
  ))

  plots.append(Plot(
    texX = 'number of loose b-tags (CSVM)', texY = 'Number of Events',
    name = 'nBTagLoose', attribute = lambda event, sample: event.nBTagLoose,
    binning=[8,0,8],
  ))

  plots.append(Plot(
    texX = 'number of jets', texY = 'Number of Events',
    name = 'nJetGood', attribute = lambda event, sample: event.nJetGood,
    binning=[14,0,14],
  ))

  plots.append(Plot(
    texX = '#eta(#gamma)', texY = 'Number of Events',
    name = 'photon_eta', attribute = lambda event, sample: abs(event.photon_eta),
    binning=[10, 0, 2.4],
  ))

  plots.append(Plot(
    texX = 'p_{T}(#gamma)', texY = 'Number of Events / 20 GeV',
    attribute = TreeVariable.fromString( "photon_pt/F" ),
    binning=[10, 30,230],
  ))

  plots.append(Plot(
    texX = '#phi(#gamma)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "photon_phi/F" ),
    binning=[15,-pi,pi],
  ))

  plots.append(Plot(
    texX = '#Delta R(#gamma, l)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "photonLepdR/F" ),
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX = '#Delta R(#gamma, j)', texY = 'Number of Events',
    attribute = TreeVariable.fromString( "photonJetdR/F" ),
    binning=[20, 0, 5],
  ))

  plots.append(Plot(
    texX     = '#Delta R(#gamma, l_{1})', texY = 'Number of Events',
    name = 'photonLep1DeltaR', attribute = lambda event, sample: event.photonLep1DeltaR,
    binning  = [20, 0, 5]
  ))

  plots.append(Plot(
    texX     = '#Delta R(#gamma, l_{2})', texY = 'Number of Events',
    name = 'photonLep2DeltaR', attribute = lambda event, sample: event.photonLep2DeltaR,
    binning  = [20, 0, 5]
  ))

  plots.append(Plot(
    texX     = '#Delta R(#gamma, j_{1})', texY = 'Number of Events',
    attribute = lambda event, sample: event.JetGood_photonDeltaR[event.goodJetIndices[0]] if event.nJetGood > 0 else -1,
    name     = "photonJet1DeltaR",
    binning  = [20, 0, 5]
  ))

  plots.append(Plot(
    texX     = '#Delta R(#gamma, j_{2})', texY = 'Number of Events',
    attribute = lambda event, sample: event.JetGood_photonDeltaR[event.goodJetIndices[1]] if event.nJetGood > 1 else -1,
    name     = "photonJet2DeltaR",
    binning  = [20, 0, 5]
  ))

  plotting.fill(plots, read_variables = read_variables, sequence = sequence)

  if args.add2015:
    for plot in plots:
      plot.addPlot(os.path.join("/user/tomc/StopsDilepton/plots/ttG2015", mode, args.selection))

  # Subtract other MC's from data
  if args.subtract:
    for plot in plots:
      for j, h in enumerate(plot.histos[0]):
        if plot.stack[0][j].name != 'TTGJets': plot.histos[1][0].Add(h, -1)
        else:                                  plot.histos[0] = [h]
      plot.stack = Stack([TTG], [data_sample])


  # Get normalization yields from yield histogram
  for plot in plots:
    if plot.name == "yield":
      for i, l in enumerate(plot.histos):
        for j, h in enumerate(l):
          yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
          h.GetXaxis().SetBinLabel(1, "#mu#mu")
          h.GetXaxis().SetBinLabel(2, "e#mu")
          h.GetXaxis().SetBinLabel(3, "ee")
      yields[mode]["MC"] = sum(yields[mode][s.name] for s in plot.stack[0])

  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
  logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yields[mode]["MC"], yields[mode]["data"], lumi_scale )

  for plot in plots: #To get normalized bins in variable binning
    if hasattr(plot, 'binWidth'):
      for histo in sum(plot.histos, []):
        for ib in range(histo.GetXaxis().GetNbins()+1):
	  val = histo.GetBinContent( ib )
	  err = histo.GetBinError( ib )
	  width = histo.GetBinWidth( ib )
	  histo.SetBinContent(ib, val / (width / plot.binWidth))
	  histo.SetBinError(ib, err / (width / plot.binWidth))

    if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
    plotting.draw(plot, 
        plot_directory = os.path.join(plot_directory, args.plot_directory, mode, args.selection),
        ratio = {'yRange':(0.1,1.9)}, 
        logX = False, logY = False, sorting = False, 
        yRange = (0.003, "auto"),
        scaling = {},
        drawObjects = drawObjects( dataMCScale, lumi_scale),
    )
  allPlots[mode] = plots



# Add yields in channels
yields["all"] = {}
for y in yields[allModes[0]]:
  try:    yields["all"][y] = sum(yields[mode][y] for mode in allModes)
  except: yields["all"][y] = 0
dataMCScale = yields["all"]["data"]/(yields["all"]["MC"])


# Write to tex file
columns = [i.name for i in (mc if not args.subtract else [TTG])] + ["MC", "data"]
texdir = "tex"
try:
  os.makedirs("./" + texdir)
except:
  pass
with open("./" + texdir + "/" + args.selection + ".tex", "w") as f:
  f.write("&" + " & ".join(columns) + "\\\\ \n")
  for mode in allModes + ["all"]:
    f.write(mode + " & " + " & ".join([ " %12.1f" % yields[mode][i] for i in columns]) + "\\\\ \n")


# Add the different channels and plot the sums
import itertools
for plot in allPlots[allModes[0]]:
  logger.info("Adding " + plot.name + " for mode " + allModes[0] + " to all")
  for mode in allModes[1:]:
    for plot2 in (p for p in allPlots[mode] if p.name == plot.name):
      logger.info("Adding " + plot.name + " for mode " + mode + " to all")
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
        for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
          if i==k:
            j.Add(l)

for plot in allPlots[allModes[0]]:
  plot.histos[1][0].legendText = "Data 2015+2016 (all)" if args.add2015 else "Data"
  plotting.draw(plot,
        plot_directory = os.path.join(plot_directory, args.plot_directory, "all", args.selection),
        ratio = {'yRange':(0.1,1.9)},
        logX = False, logY = False, sorting = False,
        yRange = (0.003, "auto"),
        scaling = {},
        drawObjects = drawObjects( dataMCScale, lumi_scale ),
  )

logger.info( "Done with prefix %s", args.selection )

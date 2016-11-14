#!/usr/bin/env python
''' Analysis script for comparing generator level TTZ vs TTG
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


#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--overwrite',      action='store_true', default=True,        help='overwrite?')
argParser.add_argument('--plot_directory', action='store',      default='TTG_gen')
argParser.add_argument('--selection',      action='store',      default=None)
argParser.add_argument('--smoothFactor',   action='store',      default=None)
argParser.add_argument('--isChild',        action='store_true', default=False)
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


#
# Cuts to iterate over
#
cuts = [
     ("etaGamma25",      "(1)"),           # Implemented in otherSelections() method
     ("ptGamma30",       "(1)"),           # Implemented in otherSelections() method
     ("ptGamma50",       "(1)"),           # Implemented in otherSelections() method
     ("ptGamma75",       "(1)"),           # Implemented in otherSelections() method
     ("met50",           "(1)"),           # Implemented in otherSelections() method
     ("met80",           "(1)"),           # Implemented in otherSelections() method
     ("mt2ll100",        "(1)"),           # Implemented in otherSelections() method
     ("mt2ll140",        "(1)"),           # Implemented in otherSelections() method
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
        if selection.count('ptGamma') > 1: continue
        if selection.count('mt2ll') > 1:   continue
        if selection.count('met') > 1:     continue
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./ttG_gen.py --log=TRACE --selection=" + selection + ((" --smoothFactor=" + args.smoothFactor) if args.smoothFactor is not None else "")
    logfile = "log/" + selection + (("_smoothFactor=" + args.smoothFactor) if args.smoothFactor is not None else "") + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=03:00:00 runPlotsOnCream02.sh")
  logger.info("All jobs launched")
  exit(0)



#
# Make samples, will be searched for in the postProcessing directory
#
postProcessing_directory = "80X_v6/gen"
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_gen import *

#
# Text on the plots
#
lumi_scale = 10
def drawObjects( dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Simulation 13 TeV'), 
#      (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(lumi_scale*100)/100., dataMCScale ) )
    ]
    return [tex.DrawLatex(*l) for l in lines] 

def drawPlot(plot, subdir, useScaling, TTG_scale):
  if useScaling:
    temp = plot.texY
    plot.texY = "Normalized units"
    subdir += "_normalized"
  plotting.draw(plot,
    plot_directory = os.path.join(plot_directory, args.plot_directory, subdir, args.selection),
    ratio          = {'yRange':(0.1,1.9),'style':styles.errorStyle(ROOT.kBlack),'texY':'t#bar{t}#gamma/t#bar{t}Z'},
    logX           = False, logY = False, sorting = False,
    yRange         = (0.003, "auto"),
    scaling        = {} if not useScaling else {0:1,2:3} if len(plot.histos) == 4 else {0:1},
    drawObjects    = drawObjects( TTG_scale, lumi_scale),
  )
  if useScaling:
    plot.texY = temp


#
# Read variables and sequences
#
read_variables = ["weight/F" , "leptonicDecays/I", "mt2ll/F", "mt2bb/F", "mt2blbl/F",
                  "met_pt/F", "met_phi/F",
                  "l1_pt/F", "l1_eta/F", "l1_phi/F", "l1_pdgId/I",
                  "l2_pt/F", "l2_eta/F", "l2_phi/F", "l2_pdgId/I",
                  "t1_pt/F", "t1_eta/F", "t1_phi/F", "t1_pdgId/I",
                  "t2_pt/F", "t2_eta/F", "t2_phi/F", "t2_pdgId/I",
                  "nunu_pt/F", "nunu_eta/F", "nunu_phi/F",
                  "mt1/F", "mt2/F"
                 ]

# TreeVariables only to be read/available for specific samples (i.e. variables only in MC)
TTG.read_variables = ["photon_genPt/F", "photon_genEta/F", "photon_genPhi/F", "met_pt_photon/F", "met_phi_photon/F", "mt2ll_photon/F","mt2bb_photon/F","mt2blbl_photon/F"]
TTZ.read_variables = ["zBoson_genPt/F", "zBoson_genEta/F", "zBoson_genPhi/F", "zBoson_isNeutrinoDecay/O"]

minBosonPt = int(args.selection.split('ptGamma')[1].split('-')[0]) if args.selection.count('ptGamma') else 0
minMt2ll   = int(args.selection.split('mt2ll')[1].split('-')[0])   if args.selection.count('mt2ll') else 0
minMet     = int(args.selection.split('met')[1].split('-')[0])     if args.selection.count('met') else 0


def otherSelections(event, sample):
  event.passed = True
  if args.selection.count("etaGamma") and sample == TTG: event.passed = (event.passed and abs(event.photon_genEta) < 2.5)
  if args.selection.count("ptGamma")  and sample == TTG: event.passed = (event.passed and event.photon_genPt > minBosonPt)
  event.forReweight = event.passed
  if args.selection.count("met"):                        event.passed = (event.passed and event.boson_met > minMet)
  if args.selection.count("mt2ll"):                      event.passed = (event.passed and event.boson_mt2ll > minMt2ll)


# Compare different variable types for TTZ vs TTG
def makeCompareTreeVariables(event, sample):
  if sample == TTZ:
    event.boson_genPt   = event.zBoson_genPt
    event.boson_genEta  = event.zBoson_genEta
    event.boson_genPhi  = event.zBoson_genPhi
    event.boson_mt2ll   = event.mt2ll
    event.boson_mt2bb   = event.mt2bb
    event.boson_mt2blbl = event.mt2blbl
    event.boson_met     = event.met_pt
  elif sample == TTG:
    event.boson_genPt   = event.photon_genPt
    event.boson_genEta  = event.photon_genEta
    event.boson_genPhi  = event.photon_genPhi
    event.boson_mt2ll   = event.mt2ll_photon
    event.boson_mt2bb   = event.mt2bb_photon
    event.boson_mt2blbl = event.mt2blbl_photon
    event.boson_met     = event.met_pt_photon
  else:
    raise Exception("Sample not known")

def doReweighting(event, sample):
  if sample == TTG:
    ttzHist = TTZ.ptHists[TTG.mode]
    ttgHist = TTG.ptHists[TTG.mode]
    ttz = ttzHist.GetBinContent(ttzHist.FindBin(event.photon_genPt)) / ttzHist.Integral()
    ttg = ttgHist.GetBinContent(ttgHist.FindBin(event.photon_genPt)) / ttgHist.Integral()
    event.weight = event.weight*ttz/ttg if ttg > 0 else 0

sequence = [makeCompareTreeVariables, otherSelections]
reweight = [doReweighting]



mumuSelection   = "leptonicDecays==2&&abs(l1_pdgId)==13&&abs(l2_pdgId)==13"
mueSelection    = "leptonicDecays==2&&((abs(l1_pdgId)==11&&abs(l2_pdgId)==13)||(abs(l1_pdgId)==13&&abs(l2_pdgId)==11))"
eeSelection     = "leptonicDecays==2&&abs(l1_pdgId)==11&&abs(l2_pdgId)==11"

TTZ.ptHists = {}
TTG.ptHists = {}


#
# Loop over channels
# First iteration: no pt reweighting, second iteration apply reweighting
#
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
if args.smoothFactor is not None: args.plot_directory = os.path.join(args.plot_directory, "smooth" + str(args.smoothFactor))
for doPtReweight in [False, True]:
  if doPtReweight: args.plot_directory = os.path.join(args.plot_directory, "reweighted")
  for index, mode in enumerate(allModes):
    TTG.mode = mode # little hack
    yields[mode] = {}

    if mode=="mumu":  leptonSelection = mumuSelection
    elif mode=="ee":  leptonSelection = eeSelection
    elif mode=="mue": leptonSelection = mueSelection


    mc = [ TTZ,  TTG ]
    for sample in mc:
      sample.scale = lumi_scale
      sample.style = styles.errorStyle(sample.color)

    TTZ.setSelectionString([leptonSelection, "zBoson_isNeutrinoDecay"])
    TTG.setSelectionString([leptonSelection])

    stack = Stack(TTZ, TTG)

    weight = lambda event, sample: event.weight if event.passed else 0

    # Use some defaults
    Plot.setDefaults(stack = stack, weight = weight, selectionString = selectionStrings[args.selection])

    plots = []

    plots.append(Plot(
      name = 'yield', texX = 'yield', texY = 'Events',
      name = 'yield', attribute = lambda event, sample: 0.5 + index,
      binning=[3, 0, 3],
    ))

    plots.append(Plot(
      texX     = 'p_{T}^{gen} (Z or #gamma) (GeV)', texY = "Events / 20 GeV",
      name = 'boson_pt', attribute = lambda event, sample: event.boson_genPt,
      name     = "boson_pt_high",
      binning  = [10, 150,350],
    ))

    plots.append(Plot(
      texX     = 'p_{T}^{gen} (Z or #gamma) (GeV)', texY = "Events /10 GeV",
      name = 'boson_pt', attribute = lambda event, sample: event.boson_genPt,
      binning  = [25, minBosonPt, minBosonPt+10*25],
    ))

    plots.append(Plot(
      texX     = 'p_{T}^{gen} (Z or #gamma) (GeV)', texY = "Events /10 GeV",
      name = 'reweighting', attribute = lambda event, sample: event.boson_genPt,
      weight   = lambda event, sample: event.weight if event.forReweight else 0,
      binning  = [25, minBosonPt, minBosonPt+10*25],
    ))

    plots.append(Plot(
      texX     = 'min(p_{T} (t,#bar{t})) (GeV)', texY = "Events /10 GeV",
      name = 't_minpt', attribute = lambda event, sample: min(event.t1_pt, event.t2_pt),
      binning  = [50, 0, 10*50],
    ))

    plots.append(Plot(
      texX     = 'max(p_{T} (t,#bar{t})) (GeV)', texY = "Events /10 GeV",
      name = 't_maxpt', attribute = lambda event, sample: max(event.t1_pt, event.t2_pt),
      binning  = [50, 0, 10*50],
    ))

    plots.append(Plot(
      texX     = 'min(#Delta#phi(Z or #gamma, t/#bar{t})) (GeV)', texY = "Events /5 GeV",
      name = 'deltaPhi_topBoson', attribute = lambda event, sample: min(deltaPhi(event.t1_phi, event.boson_genPhi), deltaPhi(event.t2_phi, event.boson_genPhi)),
      binning  = [20, 0, 3.1415],
    ))

    plots.append(Plot(
      texX     = 'min(#Delta R(Z or #gamma, t/#bar{t})) (GeV)', texY = "Events /5 GeV",
      name = 'deltaR_topBoson', attribute = lambda event, sample: min(sqrt(deltaPhi(event.t1_phi, event.boson_genPhi)**2 + (event.t1_eta - event.boson_genEta)**2, 
                                                                                       sqrt(deltaPhi(event.t2_phi, event.boson_genPhi)**2 + (event.t2_eta - event.boson_genEta)**2))),
      binning  = [20, 0, 8],
    ))

    plots.append(Plot(
      texX     = '#Delta#phi(#nu#nu, Z or #gamma) (#nu from W decays) (GeV)', texY = "Events /5 GeV",
      name = 'deltaPhi_nunuBoson', attribute = lambda event, sample: deltaPhi(event.nunu_phi, event.boson_genPhi),
      binning  = [20, 0, 3.1415],
    ))

    plots.append(Plot(
      texX     = 'p_{T}^{#nu#nu} (#nu from W decays) (GeV)', texY = "Events /5 GeV",
      name = 'nunu_pt', attribute = lambda event, sample: event.nunu_pt,
      binning  = [50, 0, 250],
    ))

    plots.append(Plot(
      texX     = '#eta^{#nu#nu} (#nu from W decays) (GeV)', texY = "Events /5 GeV",
      name = 'nunu_eta', attribute = lambda event, sample: event.nunu_eta,
      binning  = [25, 0, 5],
    ))

    plots.append(Plot(
      texX     = '#Delta#phi(#nu#nu, Z or #gamma) (#nu from W decays) (GeV)', texY = "Events /5 GeV",
      name = 'deltaPhi_nunuBoson', attribute = lambda event, sample: deltaPhi(event.nunu_phi, event.boson_genPhi),
      binning  = [20, 0, 3.1415],
    ))

    plots.append(Plot(
      texX     = '#Delta R(#nu#nu, Z or #gamma) (#nu from W decays) (GeV)', texY = "Events /5 GeV",
      name = 'deltaR_nunuBoson', attribute = lambda event, sample: sqrt(deltaPhi(event.nunu_phi, event.boson_genPhi)**2 + (event.nunu_eta - event.boson_genEta)**2),
      binning  = [20, 0, 10],
    ))

    plots.append(Plot(
      texX     = '#eta^{gen} (Z or #gamma) (GeV)', texY = "Events",
      name = 'boson_eta', attribute = lambda event, sample: abs(event.boson_genEta),
      binning  = [12, 0, 3],
    ))

    plots.append(Plot(
      texX     = 'E_{T}^{miss} (#gamma included for t#bar{t}#gamma) (GeV)', texY = "Events / 20 GeV",
      name = 'met_photonIncluded', attribute = lambda event, sample: event.boson_met,
      binning  = [15, 0, 300],
    ))

    plots.append(Plot(
      texX     = 'E_{T}^{miss} (GeV)', texY = "Events / 20 GeV",
      name = 'met', attribute = lambda event, sample: event.met_pt,
      binning  = [15, 0, 300],
    ))

    plots.append(Plot(
      texX     = 'min(M_{T}) (GeV)', texY = "Events / 30 GeV",
      name = 'mtmin', attribute = lambda event, sample: min(event.mt1, event.mt2),
      binning  = [30, 0, 120],
    ))

    plots.append(Plot(
      texX     = 'max(M_{T}) (GeV)', texY = "Events / 30 GeV",
      name = 'mtmax', attribute = lambda event, sample: max(event.mt1, event.mt2),
      binning  = [30, 0, 120],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{ll}  (#gamma included for t#bar{t}#gamma) (GeV)', texY = "Events / 30 GeV",
      name = 'mt2ll_photonIncluded', attribute = lambda event, sample: event.boson_mt2ll,
      binning  = [10, 0, 300],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{ll} (GeV)', texY = "Events / 30 GeV",
      name = 'mt2ll', attribute = lambda event, sample: event.mt2ll,
      binning  = [10, 0, 300],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{ll}  (#gamma included for t#bar{t}#gamma) (GeV)', texY = "Events / 30 GeV",
      name = 'mt2ll_photonIncluded_high', attribute = lambda event, sample: event.boson_mt2ll,
      binning  = [10, 100, 400],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{ll}  (#gamma included for t#bar{t}#gamma) (GeV)', texY = "Events / 30 GeV",
      name = 'mt2ll_high', attribute = lambda event, sample: event.mt2ll,
      binning  = [10, 100, 400],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{bb}  (#gamma included for t#bar{t}#gamma) (GeV)', texY = "Events / 30 GeV",
      name = 'mt2bb_photonIncluded', attribute = lambda event, sample: event.boson_mt2bb,
      binning  = [10, 70, 370],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{bb} (GeV)', texY = "Events / 30 GeV",
      name = 'mt2bb', attribute = lambda event, sample: event.mt2bb,
      binning  = [10, 70, 370],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{blbl}  (#gamma included for t#bar{t}#gamma) (GeV)', texY = "Events / 30 GeV",
      name = 'mt2blbl_photonIncluded', attribute = lambda event, sample: event.boson_mt2blbl,
      binning  = [10, 0, 300],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{blbl} (GeV)', texY = "Events / 30 GeV",
      name = 'mt2blbl', attribute = lambda event, sample: event.mt2blbl,
      binning  = [10, 0, 300],
    ))

    plots2D = []
    plots2D.append(Plot2D(
      name  = "TTZ_met_vs_pt",
      texX  = 'p_{T}^{gen} (Z) (GeV)', texY = "#slash{E}_{T} (GeV)'",
      stack = Stack([TTZ]),
      attributes = (
          lambda event, sample: event.boson_genPt,
          lambda event, sample: event.met_pt,
      ),
      binning =[200, 0, 200, 200,0,200],
      weight  = weight,
      selectionString = selectionStrings[args.selection]
    ))

    plots2D.append(Plot2D(
      name  = "TTG_met_vs_pt",
      texX  = 'p_{T}^{gen} (#gamma) (GeV)', texY = "#slash{E}_{T} (GeV)'",
      stack = Stack([TTG]),
      attributes = (
          lambda event, sample: event.boson_genPt,
          lambda event, sample: event.met_pt,
      ),
      binning=[200, 0, 200, 200,0,200],
      weight = weight,
      selectionString = selectionStrings[args.selection]
    ))

    plots2D.append(Plot2D(
      name  = "TTG_met_photonIncluded_vs_pt",
      texX  = 'p_{T}^{gen} (#gamma) (GeV)', texY = "#slash{E}_{T} (#gamma included) (GeV)",
      stack = Stack([TTG]),
      attributes = (
          lambda event, sample: event.boson_genPt,
          lambda event, sample: event.boson_met,
      ),
      binning=[200, 0, 200, 200,0,200],
      weight = weight,
      selectionString = selectionStrings[args.selection]
    ))

    plotting.fill(plots + plots2D, read_variables = read_variables, sequence = sequence + reweight if doPtReweight else sequence)

    # Get normalization yields from yield histogram
    for plot in plots:
      if plot.name == "yield":
	for i, l in enumerate(plot.histos):
	  for j, h in enumerate(l):
	    yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
	    h.GetXaxis().SetBinLabel(1, "#mu#mu")
	    h.GetXaxis().SetBinLabel(2, "e#mu")
	    h.GetXaxis().SetBinLabel(3, "ee")

    TTG_scale = yields[mode][TTG.name]/yields[mode][TTZ.name]

    for plot in plots:
      if not min(l[0].GetMaximum() for l in plot.histos) > 0: continue # Plot has empty contributions

      # Double the stack/histos for smoothing histograms
      if plot.name == "reweighting":
        if args.smoothFactor is not None:
	  for i, l in enumerate(plot.histos[:]):
	    plot.stack.append( copy.deepcopy(plot.stack[i]))
	    plot.histos.append(copy.deepcopy(plot.histos[i]))
	    for j, h in enumerate(l):
	      plot.histos[-1][j].sample = plot.stack[i][j]
	      plot.histos[-1][j].texName = "smoothed " + plot.stack[i][j].texName
	      plot.histos[-1][j].style = styles.lineStyle(plot.stack[i][j].color-5, 1)
	      plot.histos[-1][j].Smooth(int(args.smoothFactor))
	      plot.stack[i][j].ptHists[mode] = copy.deepcopy(plot.histos[-1][j])
        else:
	  for i, l in enumerate(plot.histos[:]):
	    for j, h in enumerate(l):
	      plot.stack[i][j].ptHists[mode] = copy.deepcopy(h)

      drawPlot(plot, mode, False, TTG_scale)
      drawPlot(plot, mode, True,  TTG_scale)

    for plot in plots2D:
      plotting.draw2D(
	plot = plot,
	plot_directory = os.path.join(plot_directory, args.plot_directory, mode, args.selection),
	logX = False, logY = False, logZ = True,
      )
    allPlots[mode] = plots
      

  yields["all"] = {}
  for y in yields[allModes[0]]:
    yields["all"][y] = sum(yields[mode][y] for mode in allModes)

  TTG_scale = yields[mode][TTG.name]/yields[mode][TTZ.name]

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

  for plot in allPlots[allModes[0]]:
    if not min(l[0].GetMaximum() for l in plot.histos) > 0: continue # Plot has empty contributions
    drawPlot(plot, "all", False, TTG_scale)
    drawPlot(plot, "all", True, TTG_scale)

logger.info( "Done with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )

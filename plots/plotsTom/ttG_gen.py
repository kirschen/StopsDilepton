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
     ("ptGamma100",      "(1)"),           # Implemented in otherSelections() method
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
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./ttG_gen.py --selection=" + selection + ((" --smoothFactor=" + args.smoothFactor) if args.smoothFactor is not None else "")
    logfile = "log/" + selection + (("_smoothFactor=" + args.smoothFactor) if args.smoothFactor is not None else "") + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=03:00:00 runPlotsOnCream02.sh")
  logger.info("All jobs launched")
  exit(0)



#
# Make samples, will be searched for in the postProcessing directory
#
postProcessing_directory = "postProcessed_Fall15_mAODv2/gen"
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_gen import *


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


#
# Read variables and sequences
#
read_variables = ["weight/F" , "leptonicDecays/I", "mt2ll/F",
                  "met_pt/F", "met_phi/F",
                  "l1_pt/F", "l1_eta/F", "l1_phi/F", "l1_pdgId/I",
                  "l2_pt/F", "l2_eta/F", "l2_phi/F", "l2_pdgId/I",
                 ]

# Variables only to be read/available for specific samples (i.e. variables only in MC)
TTG.read_variables         = ["photon_genPt/F", "photon_genEta/F", "met_pt_photon/F", "met_phi_photon/F", "mt2ll_photon/F"]
TTZtoLLNuNu.read_variables = ["zBoson_genPt/F", "zBoson_genEta/F", "zBoson_isNeutrinoDecay/O"]

minBosonPt = int(args.selection.split('ptGamma')[1].split('-')[0]) if args.selection.count('ptGamma') else 0



def otherSelections(data, sample):
  data.passed = True
  if args.selection.count("etaGamma") and sample == TTG: data.passed = (data.passed and abs(data.photon_genEta) < 2.5)
  if args.selection.count("ptGamma")  and sample == TTG: data.passed = (data.passed and data.photon_genPt > minBosonPt)


# Compare different variable types for TTZ vs TTG
def makeCompareVariables(data, sample):
  if sample == TTZtoLLNuNu:
    data.boson_genPt  = data.zBoson_genPt
    data.boson_genEta = data.zBoson_genEta
    data.boson_mt2ll  = data.mt2ll
    data.met          = data.met_pt
  elif sample == TTG:
    data.boson_genPt  = data.photon_genPt
    data.boson_genEta = data.photon_genEta
    data.boson_mt2ll  = data.mt2ll_photon
    data.met          = data.met_pt_photon

def doReweighting(data, sample):
  if sample == TTG:
    ttzHist = TTZtoLLNuNu.ptHists[TTG.mode]
    ttgHist = TTG.ptHists[TTG.mode]
    ttz = ttzHist.GetBinContent(ttzHist.FindBin(data.photon_genPt)) / ttzHist.Integral()
    ttg = ttgHist.GetBinContent(ttgHist.FindBin(data.photon_genPt)) / ttgHist.Integral()
    data.weight = data.weight*ttz/ttg if ttg > 0 else 0

sequence = [otherSelections, makeCompareVariables]
reweight = [doReweighting]



mumuSelection   = "abs(l1_pdgId)==13&&abs(l2_pdgId)==13"
mueSelection    = "(abs(l1_pdgId)==11&&abs(l2_pdgId)==13)||(abs(l1_pdgId)==13&&abs(l2_pdgId)==11)"
eeSelection     = "abs(l1_pdgId)==11&&abs(l2_pdgId)==11"

TTZtoLLNuNu.ptHists = {}
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

    lumi_scale = 10

    mc = [ TTZtoLLNuNu,  TTG ]
    for sample in mc:
      sample.scale = lumi_scale
      sample.style = styles.lineStyle(sample.color, 2)
   #   sample.reduceFiles(to = 1)

    TTZtoLLNuNu.setSelectionString([leptonSelection, "zBoson_isNeutrinoDecay"])
    TTG.setSelectionString([leptonSelection])

    stack = Stack(TTZtoLLNuNu, TTG)

    weight = lambda data: data.weight if data.passed else 0

    # Use some defaults
    Plot.setDefaults(stack = stack, weight = weight, selectionString = selectionStrings[args.selection])

    plots = []

    plots.append(Plot(
      name = 'yield', texX = 'yield', texY = 'Events',
      variable = Variable.fromString( "yield/F" ).addFiller(lambda data: 0.5 + index),
      binning=[3, 0, 3],
    ))

    plots.append(Plot(
      texX     = 'p_{T}^{gen} (Z or #gamma) (GeV)', texY = "Events / 20 GeV",
      variable = Variable.fromString( "boson_genPt/F" ).addFiller(lambda data: data.boson_genPt),
      name     = "boson_genPt_highPt",
      binning  = [10, 150,350],
    ))

    plots.append(Plot(
      texX     = 'p_{T}^{gen} (Z or #gamma) (GeV)', texY = "Events /5 GeV",
      variable = Variable.fromString( "boson_genPt/F" ).addFiller(lambda data: data.boson_genPt),
      binning  = [50, minBosonPt, minBosonPt+5*50],
    ))

    plots.append(Plot(
      texX     = '#eta^{gen} (Z or #gamma) (GeV)', texY = "Events",
      variable = Variable.fromString( "boson_genEta/F" ).addFiller(lambda data: abs(data.boson_genEta)),
      binning  = [30, 0, 3],
    ))

    plots.append(Plot(
      texX     = '#slash{E}_{T} (#gamma in included for t#bar{t}#gamma) (GeV)', texY = "Events / 10 GeV",
      variable = Variable.fromString( "met_photonIncluded/F" ).addFiller(lambda data: data.met),
      binning  = [20, 0, 200],
    ))

    plots.append(Plot(
      texX     = '#slash{E}_{T} (GeV)', texY = "Events / 10 GeV",
      variable = Variable.fromString( "met/F" ).addFiller(lambda data: data.met_pt),
      binning  = [20, 0, 200],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{ll}  (#gamma in included for t#bar{t}#gamma) (GeV)', texY = "Events / 30 GeV",
      variable = Variable.fromString( "mt2ll_photonIncluded/F" ).addFiller(lambda data: data.boson_mt2ll),
      binning  = [10, 50, 350],
    ))

    plots.append(Plot(
      texX     = 'MT_{2}^{ll} (GeV)', texY = "Events / 30 GeV",
      variable = Variable.fromString( "mt2ll/F" ).addFiller(lambda data: data.mt2ll),
      binning  = [10, 50, 350],
    ))

    plotting.fill(plots, read_variables = read_variables, sequence = sequence + reweight if doPtReweight else sequence)

    # Get normalization yields from yield histogram
    for plot in plots:
      if plot.name == "yield":
	for i, l in enumerate(plot.histos):
	  for j, h in enumerate(l):
	    yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
	    h.GetXaxis().SetBinLabel(1, "#mu#mu")
	    h.GetXaxis().SetBinLabel(2, "e#mu")
	    h.GetXaxis().SetBinLabel(3, "ee")

    TTG_scale = yields[mode][TTG.name]/yields[mode][TTZtoLLNuNu.name]

    for plot in plots:

      # Double the stack/histos for smoothing histograms
      if plot.name == "boson_genPt":
	for i, l in enumerate(plot.histos[:]):
          plot.stack.append( copy.deepcopy(plot.stack[i]))
          plot.histos.append(copy.deepcopy(plot.histos[i]))
	  for j, h in enumerate(l):
            plot.histos[-1][j].sample = plot.stack[i][j]
            plot.histos[-1][j].texName = "smoothed " + plot.stack[i][j].texName
            plot.histos[-1][j].style = styles.lineStyle(plot.stack[i][j].color-5, 1)
	    if args.smoothFactor is not None: plot.histos[-1][j].Smooth(int(args.smoothFactor))
	    plot.stack[i][j].ptHists[mode] = copy.deepcopy(plot.histos[-1][j])


      plotting.draw(plot,
	  plot_directory = os.path.join(plot_directory, args.plot_directory, mode, args.selection),
	  ratio = {'yRange':(0.1,1.9)}, 
	  logX = False, logY = False, sorting = False, 
	  yRange = (0.003, "auto"),
	  drawObjects = drawObjects( TTG_scale, lumi_scale),
      )

      temp = plot.texY
      plot.texY = "Normalized units"
      plotting.draw(plot,
	  plot_directory = os.path.join(plot_directory, args.plot_directory, mode + "_normalized", args.selection),
	  ratio = {'yRange':(0.1,1.9)}, 
	  logX = False, logY = False, sorting = False, 
	  yRange = (0.003, "auto"),
	  scaling = {0:1,2:3} if len(plot.histos) == 4 else {0:1},
	  drawObjects = drawObjects( TTG_scale, lumi_scale),
      )
      plot.texY = temp

    allPlots[mode] = plots
      

  yields["all"] = {}
  for y in yields[allModes[0]]:
    yields["all"][y] = sum(yields[mode][y] for mode in allModes)

  TTG_scale = yields[mode][TTG.name]/yields[mode][TTZtoLLNuNu.name]

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
    plotting.draw(plot,
      plot_directory = os.path.join(plot_directory, args.plot_directory, "all", args.selection),
      ratio = {'yRange':(0.1,1.9)}, 
      logX = False, logY = False, sorting = False, 
      yRange = (0.003, "auto"),
      drawObjects = drawObjects( TTG_scale, lumi_scale),
    )

    plot.texY = "Normalized units"
    plotting.draw(plot,
      plot_directory = os.path.join(plot_directory, args.plot_directory, "all_normalized", args.selection),
      ratio = {'yRange':(0.1,1.9)}, 
      logX = False, logY = False, sorting = False, 
      yRange = (0.003, "auto"),
      scaling = {0:1,2:3} if len(plot.histos) == 4 else {0:1},
      drawObjects = drawObjects( TTG_scale, lumi_scale),
    )


logger.info( "Done with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )

#!/usr/bin/env python
''' Analysis script for standard plots
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
argParser.add_argument('--plotData',       action='store_true', default=False,       help='also plot data?')
argParser.add_argument('--plot_directory', action='store',      default='analysisPlots')
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

# Selections (two leptons with pt > 20 GeV, photon)

def getLeptonString(nMu, nE):
  return "nGoodMuons==" + str(nMu) + "&&nGoodElectrons==" + str(nE)


jetSelection    = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>="
bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890))>="
bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.605))>="
dataFilterCut   = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&vetoPassed&&jsonPassed&&weight>0)"
mcFilterCut     = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter)"

#
# Cuts to iterate over
#
cuts = [
    ("njet2",             jetSelection+"2"),
    ("btagM",             bJetSelectionM+"1"),
    ("mll20",             "dl_mass>20"),
    ("met80",             "met_pt>80"),
    ("metSig5",           "metSig>5"),
    ("dPhiJet0-dPhiJet1", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
    ("mt2ll100",          "dl_mt2ll>100"),
    ("mt2ll140",          "dl_mt2ll>140"),
    ("mt2ll240",          "dl_mt2ll>240"),
    ("mt2blbl100",        "dl_mt2blbl>100"),
    ("mt2blbl200",        "dl_mt2blbl>200"),
#    ("looseLeptonVeto",   "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
  ]


# To make piecharts
from array import array
def makePieChart(yields, mode, samples):
  c        = ROOT.TCanvas("pie", "pie", 700, 700)
  labels   = [ array( 'c', s.name + '\0' ) for s in samples]
  labels_  = array( 'l', map( lambda x: x.buffer_info()[0], labels ) )
  piechart = ROOT.TPie("TTX pie", "TTX pie", 3, array('f', [yields[mode][s.name] for s in samples]), array('i', [s.color for s in samples]), labels_)
  piechart.Draw("rsc")
  c.Print(os.path.join(plot_directory, args.plot_directory, mode, args.selection, "TTX_pie.png"))


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
        if selection.count("btag")   and not selection.count("njet"):   continue
        if selection.count("mll")    and not selection.count("btag"):   continue
        if selection.count("met")    and not selection.count("mll"):    continue
        if selection.count("metSig") and not selection.count("met"):    continue
        if selection.count("dPhi")   and not selection.count("metSig"): continue
        if selection.count("mt2")    and not selection.count("dPhi"):   continue
        if selection.count("mt2ll") > 1:  continue
        if selection.count("mt2blbl") > 1:  continue
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./analysisPlots.py --selection=" + selection
    logfile = "log/" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    if not args.dryRun: os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=03:00:00 runPlotsOnCream02.sh")
  logger.info("All jobs launched")
  exit(0)



#
# Make samples, will be searched for in the postProcessing directory
#
#postProcessing_directory = "postProcessed_Fall15_mAODv2/dilepTiny_may2"
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_postProcessed_photonSamples import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import TTbarDMJets_scalar_Mchi1_Mphi100
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
      (0.15, 0.95, 'CMS Preliminary'), 
      (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(lumi_scale*100)/100., dataMCScale ) ) if plotData else (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV)'% ( int(lumi_scale*100)/100.) )
    ]
    return [tex.DrawLatex(*l) for l in lines] 


#
# Read variables and sequences
#
read_variables = ["weight/F" , "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F",
                  "metSig/F", "ht/F", "nBTag/I", "nJetGood/I", "mt/F"]

sequence = []


offZ            = "abs(dl_mass-91.1876)>15"
mumuSelection   = getLeptonString(2, 0) + "&&isOS&&isMuMu&&HLT_mumuIso&&" + offZ 
mueSelection    = getLeptonString(1, 1) + "&&isOS&&isEMu&&HLT_mue"
eeSelection     = getLeptonString(0, 2) + "&&isOS&&isEE&&HLT_ee_DZ&&" + offZ

#
# Loop over channels
#
plotData   = False
yields     = {}
allPlots   = {}
allModes   = ['mumu','mue','ee']
for index, mode in enumerate(allModes):
  yields[mode] = {}
  if mode=="mumu":
    data_sample     = DoubleMuon_Run2015D
    qcd_sample      = QCD_Mu5 #FIXME
    leptonSelection = mumuSelection + "&&" + offZ
  elif mode=="ee":
    data_sample     = DoubleEG_Run2015D
    qcd_sample      = QCD_EMbcToE
    leptonSelection = eeSelection + "&&" + offZ
  elif mode=="mue":
    data_sample     = MuonEG_Run2015D
    qcd_sample      = QCD_Mu5EMbcToE
    leptonSelection = mueSelection

  qcd_sample.name  = "QCD"  # Give same name in all modes such that it combines easily
  data_sample.name = "data"

  data_sample.style = styles.errorStyle( ROOT.kBlack )
  if plotData: lumi_scale = data_sample.lumi/1000
  else:        lumi_scale = 10

  mc = [ DY_HT_LO, TTJets_Lep, qcd_sample, singleTop, TTZ, TTW, TTH, TZQ, EWK]
  for sample in mc:
    sample.scale = lumi_scale
    sample.style = styles.fillStyle(sample.color, lineColor = sample.color)

  TTbarDMJets_scalar_Mchi1_Mphi100.scale = lumi_scale*10
  TTbarDMJets_scalar_Mchi1_Mphi100.style = styles.lineStyle( ROOT.kBlack, width=3 )

  stack = Stack(mc, [data_sample], TTbarDMJets_scalar_Mchi1_Mphi100)
  if not plotData: stack = Stack(mc, TTbarDMJets_scalar_Mchi1_Mphi100)
  data_sample.setSelectionString([dataFilterCut, leptonSelection])
  for sample in mc:
    sample.setSelectionString([mcFilterCut, leptonSelection])
  TTbarDMJets_scalar_Mchi1_Mphi100.setSelectionString([mcFilterCut, leptonSelection])

  # Use some defaults
  Plot.setDefaults(stack = stack, weight = lambda data:data.weight, selectionString = selectionStrings[args.selection])
  
  plots = []

  plots.append(Plot(
    name = 'yield', texX = 'yield', texY = 'Number of Events',
    variable = Variable.fromString( "yield/F" ).addFiller(lambda data: 0.5 + index),
    binning=[3, 0, 3],
  ))

  plots.append(Plot(
    texX = 'MT_{2}^{ll} (GeV)', texY = 'Number of Events / 20 GeV',
    variable = Variable.fromString( "dl_mt2ll/F" ),
    binning=[300/20,0,300],
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

  plots.append(Plot(
      texX = '#slash{E}_{T} (GeV)', texY = 'Number of Events / 50 GeV',
      variable = Variable.fromString( "met_pt/F" ),
      binning=[300/50,0,300],
  ))

  plots.append(Plot(
    texX = '#slash{E}_{T}/#sqrt{H_{T}} (GeV^{1/2})', texY = 'Number of Events',
    variable = Variable.fromString('metSig/F'),
    binning=[15,0,15],
  ))

  plots.append(Plot(
    texX = 'Cos(#phi(#slash{E}_{T}, leading jet))', texY = 'Number of Events',
    variable = Variable.fromString('cosMetJet0phi/F').addFiller (
	helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[0] ) , ["met_phi/F", "JetGood[phi/F]"] )
    ),
    binning = [30,-1,1],
  ))

  plots.append(Plot(
    texX = 'Cos(#phi(#slash{E}_{T}, second jet))', texY = 'Number of Events',
    variable = Variable.fromString('cosMetJet1phi/F').addFiller (
	helpers.uses(lambda data: cos( data.met_phi - data.JetGood_phi[1] ) , ["met_phi/F", "JetGood[phi/F]"] )
    ),
    binning = [30,-1,1],
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
    texX = 'H_{T} (GeV)', texY = 'Number of Events / 30 GeV',
    variable = Variable.fromString( "ht/F" ),
    binning=[510/30,90,600],
  ))

  plots.append(Plot(
    texX = 'm(ll) of leading dilepton (GeV)', texY = 'Number of Events / 4 GeV',
    variable = Variable.fromString( "dl_mass/F" ),
    binning=[200/4,0,200],
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
  if not plotData: yields[mode]["data"] = 0

  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
  logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yields[mode]["MC"], yields[mode]["data"], lumi_scale )

  for log in [False, True]:
    for plot in plots:
      if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
      print "Plotting of " + plot.name
      plotting.draw(plot, 
	  plot_directory = os.path.join(plot_directory, args.plot_directory, mode + ("_log" if log else ""), args.selection),
	  ratio = {'yRange':(0.1,1.9)} if plotData else None,
	  logX = False, logY = log, sorting = True, 
	  yRange = (0.003, "auto"),
	  scaling = {},
          legend = (0.50,0.93-0.04*sum(map(len, plot.histos)),0.95,0.93),
	  drawObjects = drawObjects( plotData, dataMCScale , lumi_scale )
      )
  allPlots[mode] = plots

  makePieChart(yields, mode, [TTH, TTW, TZQ])


# Add yields in channels
yields["all"] = {}
for y in yields[allModes[0]]:
  try:
    yields["all"][y] = sum(yields[mode][y] for mode in allModes)
  except:
    yields["all"][y] = 0
dataMCScale = yields["all"]["data"]/(yields["all"]["MC"])

# Write to tex file
columns = [i.name for i in mc] + ["MC", "data", TTbarDMJets_scalar_Mchi1_Mphi100.name]
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
for plot in allPlots[allModes[0]]:
  logger.info("Adding " + plot.name + " for mode " + allModes[0] + " to all")
  for mode in allModes[1:]:
    for plot2 in (p for p in allPlots[mode] if p.name == plot.name):
      logger.info("Adding " + plot.name + " for mode " + mode + " to all")
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
        for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
          if i==k:
            j.Add(l)

for log in [False, True]:
  for plot in allPlots[allModes[0]]:
    if plotData: plot.histos[1][0].legendText = "Data 2015 (all channels)"
    plotting.draw(plot,
	  plot_directory = os.path.join(plot_directory, args.plot_directory, "all" + ("_log" if log else ""), args.selection),
	  ratio = {'yRange':(0.1,1.9)} if plotData else None,
	  logX = False, logY = log, sorting = True,
	  yRange = (0.003, "auto"),
	  scaling = {},
          legend = (0.50,0.93-0.04*sum(map(len, plot.histos)),0.95,0.93),
	  drawObjects = drawObjects( plotData, dataMCScale , lumi_scale )
    )

makePieChart(yields, "all", [TTH, TTW, TZQ])

logger.info( "Done with prefix %s and selectionString %s", args.selection, selectionStrings[args.selection] )

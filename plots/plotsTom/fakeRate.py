#!/usr/bin/env python
''' Analysis script for fake rate measurement
'''
#
# Standard imports and batch mode
#
import ROOT
ROOT.gROOT.SetBatch(True)

from math import sqrt, cos, sin, pi
from RootTools.core.standard import *
from StopsDilepton.tools.user import plot_directory
from StopsDilepton.tools.objectSelection import getFilterCut, getGoodAndOtherLeptons, getGoodLeptons, muonSelector, eleSelector, leptonVars


#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--overwrite',      action='store_true', default=True,        help='overwrite?')
argParser.add_argument('--subtract',       action='store_true', default=False,       help='subtract residual backgrounds?')
argParser.add_argument('--plot_directory', action='store',      default='fakeRate')
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
# Selections
#
def getLeptonString(nMu, nE, multiIso=False):
  return "nGoodMuons==" + str(nMu) + "&&nGoodElectrons==" + str(nE) + "&&l1_pt>25"

def getLeptonSelection(mode):
  offZ = "&&abs(dl_mass-91.1876)>15"
  if   mode=="mumu": return getLeptonString(2, 0) + "&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return getLeptonString(1, 1) + "&&isOS&&isEMu"
  elif mode=="ee":   return getLeptonString(0, 2) + "&&isOS&&isEE" + offZ


jetSelection    = "nJetGood"
bJetSelectionM  = "nBTag"


from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWP = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
#
# Cuts to iterate over: at least 3/4 jets with 1/2 btags
#
cuts=[
    ("njet2",             jetSelection+">=2"),
    ("btagM",             bJetSelectionM+">=1"),
    ("multiIsoWP",        "l1_mIsoWP>4&&l2_mIsoWP>4"),
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
        if not selection.count("njet2"):           continue
        selectionStrings[selection] = "&&".join( [p[1] for p in presel])

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None:
  import os
  os.system("mkdir -p log")
  for selection in selectionStrings:
    command = "./fakeRate.py --selection=" + selection + (" --plot_directory=" + args.plot_directory) + (" --subtract" if args.subtract else "") + (" --logLevel=" + args.logLevel)
    logfile = "log/fakeRate_" + selection + ".log"
    logger.info("Launching " + selection + " on cream02 with child command: " + command)
    if not args.dryRun: os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=10:00:00 runPlotsOnCream02.sh")
  logger.info("All jobs launched")
  exit(0)

if args.subtract: args.plot_directory += "_subtracted"
#
# Text on the plots
#
postProcessing_directory = "postProcessed_80X_tom/trilep"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed_trilep import *
#from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_80X_postProcessed import *
def drawObjects( dataMCScale, lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'), 
      (0.45, 0.95, 'L=12.9 fb{}^{-1} (13 TeV)')
#      (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(lumi_scale*100)/100., dataMCScale ))
    ]
    return [tex.DrawLatex(*l) for l in lines] 


read_variables = [
    "weight/F" , "JetGood[pt/F,eta/F,phi/F]",
    "nLepGood/I",  "LepGood[eta/F,etaSc/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso04/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,mvaIdSpring15/F,jetPtRelv2/F,jetPtRatiov2/F,eleCutIdSpring15_25ns_v1/I]",
    "nLepOther/I", "LepOther[eta/F,etaSc/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso04/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,mvaIdSpring15/F,jetPtRelv2/F,jetPtRatiov2/F,eleCutIdSpring15_25ns_v1/I]",
]

# For third loose lepton: no isolation, but still apply id
# Keep loosened id because otherwise we have almost no stats
mu_selector_loose  = muonSelector(iso=999, dxy=99, dz=99, loose=True)
ele_selector_loose = eleSelector(iso=999, eleId = 0, dxy=99, dz=99, loose=True)
mu_selector_tight  = muonSelector(iso='VT', dxy=99, dz=99)
ele_selector_tight = eleSelector(iso='VT', eleId = 4, dxy=99, dz=99)

yields     = {}
allPlots   = {}
allModes   = ['ee','mumu','mue']
for index, mode in enumerate(allModes):
 for thirdLeptonFlavour in ['e','mu',"all"]:
  def getThirdLepton( data ):
      goodLeptons = getGoodLeptons( data, ptCut=20, collVars = leptonVars)
      allExtraLeptonsLoose = [l for l in getGoodAndOtherLeptons(data, collVars=leptonVars, ptCut=10, mu_selector=mu_selector_loose, ele_selector=ele_selector_loose) if l not in goodLeptons]
      allExtraLeptonsTight = [l for l in getGoodAndOtherLeptons(data, collVars=leptonVars, ptCut=10, mu_selector=mu_selector_tight, ele_selector=ele_selector_tight) if l not in goodLeptons]

      if thirdLeptonFlavour == "e":
        allExtraLeptonsLoose = filter(lambda l: abs(l['pdgId']) == 11, allExtraLeptonsLoose)
        allExtraLeptonsTight = filter(lambda l: abs(l['pdgId']) == 11, allExtraLeptonsTight)
      if thirdLeptonFlavour == "mu":
        allExtraLeptonsLoose = filter(lambda l: abs(l['pdgId']) == 13, allExtraLeptonsLoose)
        allExtraLeptonsTight = filter(lambda l: abs(l['pdgId']) == 13, allExtraLeptonsTight)

      if len(allExtraLeptonsLoose) >= 1:
	data.hasLooseThirdLepton   = True
	data.thirdLeptonPt         = allExtraLeptonsLoose[0]['pt']
	data.thirdLeptonMiniRelIso = allExtraLeptonsLoose[0]['miniRelIso']
#	data.thirdLeptonRelIso     = allExtraLeptonsLoose[0]['relIso04']
	data.hasTightThirdLepton   = (len(allExtraLeptonsTight) >= 1)
      else:
	data.hasLooseThirdLepton   = False
	data.hasTightThirdLepton   = False
	data.thirdLeptonPt         = -1
	data.thirdLeptonMiniRelIso = -1
#	data.thirdLeptonRelIso     = -1

  sequence = [getThirdLepton]

  yields[mode] = {}
  if   thirdLeptonFlavour == "e":   looseFlavour = "loose e"
  elif thirdLeptonFlavour == "mu":  looseFlavour = "loose #mu"
  elif thirdLeptonFlavour == "all": looseFlavour = "loose e/#mu"
  if mode=="mumu":   
    data_sample         = DoubleMuon_Run2016BCD_backup
    data_sample.texName = "Data (2#mu + " + looseFlavour + ")"
  elif mode=="ee":   
    data_sample         = DoubleEG_Run2016BCD_backup 
    data_sample.texName = "Data (2e + " + looseFlavour + ")"
  elif mode=="mue":  
    data_sample         = MuonEG_Run2016BCD_backup 
    data_sample.texName = "Data (1e, 1#mu + " + looseFlavour + ")"

  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale        = data_sample.lumi/1000

  mc = [ Top_pow, DY_HT_LO, TTXNoZ, TTZ_LO, multiBoson]
  for sample in mc:
    sample.scale = lumi_scale
    sample.style = styles.fillStyle(sample.color, lineColor = sample.color)
    sample.read_variables = ['reweightLeptonHIPSF/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU12fb/F']
    sample.weight         = lambda data: data.reweightBTag_SF*data.reweightLeptonSF*data.reweightLeptonHIPSF*data.reweightDilepTriggerBackup*data.reweightPU12fb

  data_sample.setSelectionString([getFilterCut(isData=True), getLeptonSelection(mode)])
  for sample in mc:
    sample.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])
 
  stack = Stack(mc, data_sample)

  looseWeight = lambda data:data.weight*data.hasLooseThirdLepton
  tightWeight = lambda data:data.weight*data.hasTightThirdLepton

  Plot.setDefaults(stack = stack, weight = lambda data:data.weight, selectionString = selectionStrings[args.selection])

  plots = []
  plots.append(Plot(  # Fill with tight third leptons, will transform in fake rate below
    texX = 'Fake rate', texY = 'Number of Events / 10 GeV',
    variable = Variable.fromString( "fakeRate/F" ).addFiller(lambda data: data.thirdLeptonPt),
    weight = tightWeight,
    binning=[9,10,100],
  ))

  plots.append(Plot(  # Fill with tight third leptons, will transform in fake rate below
    texX = 'Fake rate', texY = 'Number of Events / 10 GeV',
    variable = Variable.fromString( "fakeRateAll/F" ).addFiller(lambda data: data.thirdLeptonPt),
    weight = tightWeight,
    binning=[9,10,100],
  ))
 
  plots.append(Plot(
    texX = 'p_{T}(l_{3}, loose) (GeV)', texY = 'Number of Events / 10 GeV',
    variable = Variable.fromString( "l3_loose_pt/F" ).addFiller(lambda data: data.thirdLeptonPt),
    weight = looseWeight,
    binning=[9,10,100],
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{3}, tight) (GeV)', texY = 'Number of Events / 10 GeV',
    variable = Variable.fromString( "l3_tight_pt/F" ).addFiller(lambda data: data.thirdLeptonPt),
    weight = tightWeight,
    binning=[9,10,100],
  ))

  plots.append(Plot(
    texX = 'I_{rel.mini}(l_{3})', texY = 'Number of Events',
    variable = Variable.fromString( "l3_miniRelIso/F" ).addFiller(lambda data: data.thirdLeptonMiniRelIso),
    binning=[20,0,1.8],
    weight = looseWeight,
  ))

#  plots.append(Plot(
#    texX = 'I_{rel.Iso}(l_{3})', texY = 'Number of Events',
#    variable = Variable.fromString( "l3_relIso04/F" ).addFiller(lambda data: data.thirdLeptonRelIso),
#    binning=[20,0,1.8],
#    weight = looseWeight,
#  ))


  plotting.fill(plots, read_variables = read_variables, sequence = sequence)

  # Subtract other MC's from data
  if args.subtract:
    for plot in plots:
      for j, h in enumerate(plot.histos[0]):
        if plot.stack[0][j].name.count('Top'):
          plot.histos[1][0].Add(h, -1)
      for j, h in enumerate(plot.histos[0]):
        if plot.stack[0][j].name.count('Top'):
          plot.histos[0] = [h]
      plot.stack = Stack([Top_pow], [data_sample])

  # Now divide tight third lepton by loose third lepton
  for plot in plots:
    if plot.name == "fakeRate":
      for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
	for plot2 in plots:
	  if plot2.name == "l3_loose_pt":
	    for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
	      if i == k:
		temp = l.Clone()
		temp.Add(j, -1)
		j.Divide(l)

  # Make sure that for the fakeRate we only plot top, even when no subtraction is done
  for plot in plots:
    if plot.name == "fakeRate":
      for j, h in enumerate(plot.histos[0]):
	if plot.stack[0][j].name.count('Top'):
	  plot.histos[0] = [h]
      plot.stack = Stack([Top_pow], [data_sample])


  # Get normalization yields from yield histogram
#  for plot in plots:
#    if plot.name == "yield":
#      for i, l in enumerate(plot.histos):
#        for j, h in enumerate(l):
#          yields[mode][plot.stack[i][j].name] = h.GetBinContent(h.FindBin(0.5+index))
#          h.GetXaxis().SetBinLabel(1, "#mu#mu")
#          h.GetXaxis().SetBinLabel(2, "e#mu")
#          h.GetXaxis().SetBinLabel(3, "ee")

#  yields[mode]["MC"] = sum(yields[mode][s.name] for s in mc)
#  dataMCScale = yields[mode]["data"]/yields[mode]["MC"] if yields[mode]["MC"] != 0 else float('nan')
#  logger.info( "Data/MC Scale: %4.4f Yield MC %4.4f Yield Data %4.4f Lumi-scale %4.4f", dataMCScale, yields[mode]["MC"], yields[mode]["data"], lumi_scale )
  dataMCScale = 0

  for log in [False, True]:
    for plot in plots:
      if plot.name == "fakeRateAll": continue
      plotting.draw(plot, 
	plot_directory = os.path.join(plot_directory, args.plot_directory, mode + "_loose_" + thirdLeptonFlavour + ("_log" if log else ""), args.selection),
	ratio = {'yRange':(0.1,1.9)},
	logX = False, logY = log, sorting = False, 
	yRange = (0.03, "auto"), 
	drawObjects = drawObjects( dataMCScale, lumi_scale)
      )
  allPlots[mode+thirdLeptonFlavour] = plots

for plot in allPlots['mumuall']:
  logger.info("Adding " + plot.name + " for ee and mumu to all")
  for plot2 in (p for p in (allPlots['eeall']) if p.name == plot.name):
    for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
      for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
	if i==k:
	  j.Add(l)

# Now divide tight third lepton by loose third lepton
for plot in plots:
  if plot.name == "fakeRateAll":
    for i, j in enumerate(list(itertools.chain.from_iterable(plot.histos))):
      for plot2 in plots:
	if plot2.name == "l3_loose_pt":
	  for k, l in enumerate(list(itertools.chain.from_iterable(plot2.histos))):
	    if i == k:
	      temp = l.Clone()
	      temp.Add(j, -1)
	      j.Divide(l)

# Make sure that for the fakeRate we only plot top, even when no subtraction is done
for plot in plots:
  if plot.name == "fakeRateAll":
    for j, h in enumerate(plot.histos[0]):
      if plot.stack[0][j].name.count('Top'):
	plot.histos[0] = [h]
    plot.stack = Stack([Top_pow], [data_sample])





for log in [False, True]:
  for plot in plots:
    if plot.name == "fakeRate": continue
    plot.histos[1][0].legendText = "Data 2016 (ee/mumu + loose e/mu)"
    plotting.draw(plot, 
      plot_directory = os.path.join(plot_directory, args.plot_directory, "all" + ("_log" if log else ""), args.selection),
      ratio = {'yRange':(0.1,1.9)},
      logX = False, logY = log, sorting = False, 
      yRange = (0.03, "auto"), 
      drawObjects = drawObjects( dataMCScale, lumi_scale)
    )

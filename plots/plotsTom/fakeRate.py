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
from StopsDilepton.tools.objectSelection import getFilterCut, getGoodAndOtherLeptons, getLeptons, getGoodLeptons, default_muon_selector, default_ele_selector, muonSelector, eleSelector, leptonVars
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

import itertools
#
# Arguments
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--overwrite',      action='store_true', default=True,        help='overwrite?')
argParser.add_argument('--subtract',       action='store_true', default=False,       help='subtract residual backgrounds?')
argParser.add_argument('--plot_directory', action='store',      default='fakeRate')
argParser.add_argument('--filters',        action='store',      default='Moriond2017Official')
argParser.add_argument('--channel',        action='store',      default=None)
argParser.add_argument('--selection',      action='store',      default=None)
argParser.add_argument('--runLocal',       action='store_true', default=False)
argParser.add_argument('--norm',           action='store_true', default=False)
argParser.add_argument('--looseEle',       action='store_true', default=False)
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

def getLeptonSelection(mode):
  offZ = "&&abs(dl_mass-91.1876)>15"
  if   mode=="mumu": return "(nGoodMuons==2&&nGoodElectrons==0&&isOS&&l1_pt>25&&isMuMu" + offZ + ")"
  elif mode=="mue":  return "(nGoodMuons==1&&nGoodElectrons==1&&isOS&&l1_pt>25&&isEMu)"
  elif mode=="ee":   return "(nGoodMuons==0&&nGoodElectrons==2&&isOS&&l1_pt>25&&isEE" + offZ + ")"

selectionStrings = ['njet2p-relIso0.12','njet2p-relIso0.12-btag1p','njet2p-relIso0.12-mll20','njet2p-relIso0.12-btag1p-mll20']


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
    for channel in ["ee","mumu","mue"]:
      command = "./fakeRate.py --selection=" + selection + (" --channel="+ channel)\
                                                         + (" --plot_directory=" + args.plot_directory)\
                                                         + (" --subtract" if args.subtract else "")\
                                                         + (" --norm" if args.norm else "")\
                                                         + (" --looseEle" if args.looseEle else "")\
                                                         + (" --logLevel=" + args.logLevel)\
                                                         + (" --filters=" + args.filters)
      logfile = "log/fakeRate_" + selection + "_" + channel + ".log"
      logger.info("Launching " + selection + " on cream02 with child command: " + command)
      if not args.dryRun: launch(command, logfile)
  logger.info("All jobs launched")
  exit(0)

if args.norm:     args.plot_directory += "_normalized"
if args.looseEle: args.plot_directory += "_looseEleId"
if not args.filters == "Moriond2017Official": args.plot_directory += "_filters" + args.filters

#
# Text on the plots
#
postProcessing_directory = "postProcessed_80X_v31/trilep"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_03Feb_postProcessed import *
postProcessing_directory = "postProcessed_80X_v30/trilep"
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed2 import *
def drawObjects(lumi_scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'),
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)'% (lumi_scale) )
    ]
    return [tex.DrawLatex(*l) for l in lines]

read_variables = [
    "weight/F" , "JetGood[pt/F,eta/F,phi/F]",
    "l1_eta/F", "l2_eta/F", "l1_phi/F", "l2_phi/F",
    "nLepGood/I",  "LepGood[eta/F,etaSc/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso03/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,eleCutId_Spring2016_25ns_v1_ConvVetoDxyDz/I,mvaIdSpring15/I,jetPtRelv2/F,jetPtRatiov2/F]",
    "nLepOther/I", "LepOther[eta/F,etaSc/F,pt/F,phi/F,dxy/F,dz/F,tightId/I,pdgId/I,mediumMuonId/I,relIso03/F,miniRelIso/F,sip3d/F,convVeto/I,lostHits/I,eleCutId_Spring2016_25ns_v1_ConvVetoDxyDz/I,mvaIdSpring15/I,jetPtRelv2/F,jetPtRatiov2/F]",
]

for i in leptonVars:
  for j in read_variables:
    if (j.count('LepGood[') or j.count('LepOther[')) and not j.count(i):
      logger.warning('Missing ' + i + ' in read_variables!')

# For third loose lepton: no isolation, but still apply id
# Keep loosened id because otherwise we have almost no stats
mu_selector_loose  = muonSelector(relIso03=999)
ele_selector_loose = eleSelector(relIso03=999, eleId = 0, dxy=99, dz=99, loose=True) if args.looseEle else eleSelector(relIso03=999)
mu_selector_tight  = muonSelector(relIso03=0.12)
ele_selector_tight = eleSelector(relIso03=0.12)#, eleId = 4, dxy=99, dz=99)

mode = args.channel
for thirdLeptonFlavour in ['mu','e']:
  if mode != args.channel: continue
  def isGoodLepton(l):
      return (abs(l["pdgId"])==11 and default_ele_selector(l, ptCut = 20)) or (abs(l["pdgId"])==13 and default_muon_selector(l, ptCut = 20))

  def isTightLepton(l):
      return (abs(l["pdgId"])==11 and ele_selector_tight(l, ptCut=10)) or (abs(l["pdgId"])==13 and mu_selector_tight(l, ptCut=10))

  from StopsDilepton.tools.helpers import deltaPhi
  def deltaR(eta, phi, eta2, phi2):
    return sqrt(deltaPhi(phi, phi2)**2 + (eta - eta2)**2)

  def getThirdLepton( event, sample ):
      allExtraLeptonsLoose = [l for l in getGoodAndOtherLeptons(event, collVars=leptonVars, ptCut=10, mu_selector=mu_selector_loose, ele_selector=ele_selector_loose) if not isGoodLepton(l)]
      allExtraLeptonsTight = [l for l in getGoodAndOtherLeptons(event, collVars=leptonVars, ptCut=10, mu_selector=mu_selector_tight, ele_selector=ele_selector_tight) if not isGoodLepton(l)]

      if thirdLeptonFlavour == "e":
        allExtraLeptonsLoose = filter(lambda l: abs(l['pdgId']) == 11, allExtraLeptonsLoose)
        allExtraLeptonsTight = filter(lambda l: abs(l['pdgId']) == 11, allExtraLeptonsTight)
      if thirdLeptonFlavour == "mu":
        allExtraLeptonsLoose = filter(lambda l: abs(l['pdgId']) == 13, allExtraLeptonsLoose)
        allExtraLeptonsTight = filter(lambda l: abs(l['pdgId']) == 13, allExtraLeptonsTight)

      if len(allExtraLeptonsLoose) >= 1:
        event.hasLooseThirdLepton   = True
        event.thirdLeptonPt         = allExtraLeptonsLoose[0]['pt']
        event.thirdLeptonRelIso     = allExtraLeptonsLoose[0]['relIso03']
        event.hasTightThirdLepton   = isTightLepton(allExtraLeptonsLoose[0])
        event.l1deltaR              = deltaR(event.l1_eta, event.l1_phi, allExtraLeptonsLoose[0]['eta'], allExtraLeptonsLoose[0]['phi'])
        event.l2deltaR              = deltaR(event.l2_eta, event.l2_phi, allExtraLeptonsLoose[0]['eta'], allExtraLeptonsLoose[0]['phi'])
      else:
        event.hasLooseThirdLepton   = False
        event.hasTightThirdLepton   = False
        event.thirdLeptonPt         = -1
        event.thirdLeptonRelIso     = -1
        event.l1deltaR              = -1
        event.l2deltaR              = -1


  sequence = [getThirdLepton]

  if   thirdLeptonFlavour == "e":   looseFlavour = "loose e" if args.looseEle else "e"
  elif thirdLeptonFlavour == "mu":  looseFlavour = "#mu"
  if mode=="mumu":
    data_sample         = DoubleMuon_Run2016_backup
    data_sample.texName = "Data (2#mu + " + looseFlavour + ")"
  elif mode=="ee":
    data_sample         = DoubleEG_Run2016_backup
    data_sample.texName = "Data (2e + " + looseFlavour + ")"
  elif mode=="mue":
    data_sample         = MuonEG_Run2016_backup
    data_sample.texName = "Data (1e, 1#mu + " + looseFlavour + ")"

  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale        = data_sample.lumi/1000

  mc = [ Top_pow, DY_HT_LO, TTXNoZ, TTZ, multiBoson]
  for sample in mc:
    sample.scale = lumi_scale
    sample.style = styles.fillStyle(sample.color, lineColor = sample.color)
    sample.read_variables = ['reweightTopPt/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F']
    sample.weight         = lambda event, sample: event.reweightLeptonSF*event.reweightDilepTriggerBackup*event.reweightPU36fb*event.reweightBTag_SF*event.reweightTopPt

  data_sample.setSelectionString([getFilterCut(isData=True, badMuonFilters="Moriond2017Official"), getLeptonSelection(mode)])
  for sample in mc:
    sample.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])
  stack = Stack(mc, data_sample)

  looseWeight      = lambda event, sample:event.weight*event.hasLooseThirdLepton
  tightWeight      = lambda event, sample:event.weight*event.hasTightThirdLepton
  lowRelIsoWeight  = lambda event, sample:event.weight*event.hasLooseThirdLepton*(event.thirdLeptonRelIso < 0.12)
  highRelIsoWeight = lambda event, sample:event.weight*event.hasLooseThirdLepton*(event.thirdLeptonRelIso > 0.6)

  Plot.setDefaults(stack = stack, weight = lambda event, sample:event.weight, selectionString = cutInterpreter.cutString(args.selection))

  plots = []
  plots.append(Plot(  # Fill with tight third leptons, will transform in fake rate below
    texX = 'Fake rate', texY = 'Number of Events / 10 GeV',
    name = 'fakeRate', attribute = lambda event, sample: event.thirdLeptonPt,
    weight = tightWeight,
    binning=[9,10,100],
  ))

  plots.append(Plot(
    texX = 'p_{T}(l_{3}, loose) (GeV)', texY = 'Number of Events / 10 GeV',
    name = 'l3_loose_pt', attribute = lambda event, sample: event.thirdLeptonPt,
    weight = looseWeight,
    binning=[9,10,100],
  ))

  for (weight, postfix) in [(looseWeight, ''), (lowRelIsoWeight, '_relIso_lt_0.12'), (highRelIsoWeight, '_relIso_gt_0.6')]:
    plots.append(Plot(
      texX = '#DeltaR(l_{1}, l_{3})', texY = 'number of events / 10 gev',
      name = 'deltaR_l1l3' + postfix, attribute = lambda event, sample: event.l1deltaR,
      weight = weight,
      binning=[20, 0, 5],
    ))

    plots.append(Plot(
      texX = '#DeltaR(l_{2}, l_{3})', texY = 'number of events / 10 gev',
      name = 'deltaR_l1l2' + postfix, attribute = lambda event, sample: event.l2deltaR,
      weight = weight,
      binning=[20, 0, 5],
    ))

    plots.append(Plot(
      texX = 'min(#DeltaR(l_{1}, l_{3}),#DeltaR(l_{2}, l_{3}))', texY = 'number of events / 10 gev',
      name = 'minDeltaR' + postfix, attribute = lambda event, sample: min(event.l1deltaR, event.l2deltaR),
      weight = weight,
      binning=[20, 0, 5],
    ))

  plots.append(Plot(
    texX = 'p_{T}(l_{3}, tight) (GeV)', texY = 'Number of Events / 10 GeV',
    name = 'l3_tight_pt', attribute = lambda event, sample: event.thirdLeptonPt,
    weight = tightWeight,
    binning=[9,10,100],
  ))

  plots.append(Plot(
    texX = 'I_{rel.}(l_{3})', texY = 'Number of Events',
    name = 'l3_RelIso', attribute = lambda event, sample: event.thirdLeptonRelIso,
    binning=[20,0,2.4],
    weight = looseWeight,
  ))


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

  for log in [False, True]:
    for plot in plots:
      if plot.name == "fakeRateAll": continue
      plotting.draw(plot,
        plot_directory = os.path.join(plot_directory, args.plot_directory, mode + "_loose_" + thirdLeptonFlavour + ("_log" if log else ""), args.selection),
        ratio = {'yRange':(0.1,1.9)},
        logX = False, logY = log, sorting = False,
        yRange = (0.03, "auto"),
        scaling = {0:1} if args.norm else None,
        drawObjects = drawObjects(lumi_scale)
      )

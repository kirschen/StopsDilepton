#!/usr/bin/env python
''' Analysis script for standard plots
'''
#
# Standard imports and batch mode
#
import ROOT
ROOT.gROOT.SetBatch(True)

from math                                import sqrt
from RootTools.core.standard             import *
from StopsDilepton.tools.user            import plot_directory
from StopsDilepton.tools.objectSelection import getFilterCut
from StopsDilepton.plots.pieChart        import makePieChart
from StopsDilepton.tools.cutInterpreter  import cutInterpreter

import pickle, os, time
import errno
#
# Arguments
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',          action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--signal',            action='store',      default='T2tt',      nargs='?', choices=["None", "T2tt",'DM'], help="Add signal to plot")
argParser.add_argument('--noData',            action='store_true', default=False,       help='also plot data?')
argParser.add_argument('--plot_directory',    action='store',      default='systematicsPlots')
argParser.add_argument('--selection',         action='store',      default=None)
argParser.add_argument('--normString',        action='store',      default=None)
argParser.add_argument('--channel',           action='store',      default=None)
argParser.add_argument('--selectSys',         action='store',      default='all')
argParser.add_argument('--showOnly',          action='store',      default=None)
argParser.add_argument('--unblind',           action='store_true', default=False)
argParser.add_argument('--splitBosons',       action='store_true', default=False)
argParser.add_argument('--scaleDYVV',         action='store_true', default=False)
argParser.add_argument('--LO',                action='store_true', default=False)
argParser.add_argument('--splitTop',          action='store_true', default=False)
argParser.add_argument('--powheg',            action='store_true', default=True)
argParser.add_argument('--isChild',           action='store_true', default=False)
argParser.add_argument('--normalizeBinWidth', action='store_true', default=False,       help='normalize wider bins?')
argParser.add_argument('--dryRun',            action='store_true', default=False,       help='do not launch subjobs')
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

#
# Selection strings for which plots need to be produced, as interpreted by the cutInterpreter
#
selections = ['njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metInv',
              'njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5',
              'njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv',
              'njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5',
              'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metInv',
              'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5',
              'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5',
              'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-mt2ll100',
              'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv',
              'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv-mt2ll100',
              'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1',
              'njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll0To25',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll25To50',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll50To75',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll75To100',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100To140',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100',
              'njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll140'
           ]


#
# Systematics to run over
#
jet_systematics    = ['JECUp','JECDown']# 'JERDown','JECVUp','JECVDown']
met_systematics    = ['UnclusteredEnUp', 'UnclusteredEnDown']
jme_systematics    = jet_systematics + met_systematics
weight_systematics = ['PU36fbUp', 'PU36fbDown', 'TopPt', 'DilepTriggerBackupDown', 'DilepTriggerBackupUp', 'LeptonSFDown', 'LeptonSFUp','BTag_SF_b_Down', 'BTag_SF_b_Up','BTag_SF_l_Down', 'BTag_SF_l_Up']


if args.selectSys != "all" and args.selectSys != "combine": all_systematics = [args.selectSys if args.selectSys != 'None' else None]
else:                                                       all_systematics = [None] + weight_systematics + jme_systematics


sys_pairs = [\
    ('JEC',         'JECUp', 'JECDown'),
    ('Unclustered', 'UnclusteredEnUp', 'UnclusteredEnDown'),
    ('PU36fb',      'PU36fbUp', 'PU36fbDown'),
    ('TopPt',       'TopPt', None),
#   ('JER',         'JERUp', 'JERDown'),
    ('BTag_b',      'BTag_SF_b_Down', 'BTag_SF_b_Up'),
    ('BTag_l',      'BTag_SF_l_Down', 'BTag_SF_l_Up'),
    ('trigger',     'DilepTriggerBackupDown', 'DilepTriggerBackupUp'),
    ('leptonSF',    'LeptonSFDown', 'LeptonSFUp'),
]

def launch(command, logfile, local=False):
  if local: os.system(command + " --isChild &> " + logfile)
  else:     os.system("qsub -v command=\"" + command + " --isChild\" -q localgrid@cream02 -o " + logfile + " -e " + logfile + " -l walltime=50:00:00 runPlotsOnCream02.sh")

#
# If this is the mother process, launch the childs and exit (I know, this could potententially be dangereous if the --isChild and --selection commands are not given...)
#
if not args.isChild and args.selection is None: # and (args.selectSys == "all" or args.selectSys == "combine"):
  os.system("mkdir -p log")
  for channel in ['mue','SF','all','ee','mumu']:
    for sys in (all_systematics if args.selectSys == "all" else [args.selectSys]):
      if not sys: sys = 'None'
      for selection in selections:
        command = "./systematicsPlots.py --selection=" + selection + (" --noData"            if args.noData            else "")\
                                                                   + (" --splitBosons"       if args.splitBosons       else "")\
                                                                   + (" --splitTop"          if args.splitTop          else "")\
                                                                   + (" --unblind"           if args.unblind           else "")\
                                                                   + (" --scaleDYVV"         if args.scaleDYVV         else "")\
                                                                   + (" --LO"                if args.LO                else "")\
                                                                   + (" --powheg"            if args.powheg            else "")\
                                                                   + (" --normalizeBinWidth" if args.normalizeBinWidth else "")\
                                                                   + ((" --normString="     + args.normString) if args.normString else "")\
                                                                   + (" --plot_directory=" + args.plot_directory)\
                                                                   + (" --logLevel="       + args.logLevel)\
                                                                   + (" --signal="         + args.signal)\
                                                                   + (" --channel="        + channel)\
                                                                   + (" --selectSys="      + sys)
        logfile = "log/systematicPlots_" + selection + "_" + sys + ".log"
        logger.info("Launching " + selection + " on cream02 with child command: " + command)
        if not args.dryRun: launch(command, logfile, sys=="combine")
  logger.info("All jobs launched")
  exit(0)

if args.noData:                   args.plot_directory += "_noData"
if args.unblind:                  args.plot_directory += "_unblinded"
if args.splitBosons:              args.plot_directory += "_splitMultiBoson"
if args.signal == "DM":           args.plot_directory += "_DM"
if args.scaleDYVV:                args.plot_directory += "_scaleDYVV"
#if not args.LO:                   args.plot_directory += "_ttZNLO"
if args.normString:               args.plot_directory += "_alternativeNorm/"+args.normString

if args.selection == "njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-mt2ll100": args.signal = None

#
# Make samples, will be searched for in the postProcessing directory
#
postProcessing_directory = 'postProcessed_80X_v31/dilepTiny'
from StopsDilepton.samples.cmgTuples_Data25ns_80X_03Feb_postProcessed import *
postProcessing_directory = 'postProcessed_80X_v35/dilepTiny'
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *

signals = []
if   args.signal == "T2tt":
  from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
 #from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import *
  T2tt        = T2tt_750_1
  T2tt2       = T2tt_600_300
  T2tt.style  = styles.lineStyle( ROOT.kBlack, width=3 )
  T2tt2.style = styles.lineStyle( ROOT.kBlack, width=3, dotted=True )
  signals     = [T2tt, T2tt2]
elif args.signal == "DM":
  from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10, TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10
  DM        = TTbarDMJets_DiLept_pseudoscalar_Mchi_1_Mphi_10
  DM2       = TTbarDMJets_DiLept_scalar_Mchi_1_Mphi_10
  DM.style  = styles.lineStyle( ROOT.kBlack, width=3)
  DM2.style = styles.lineStyle( 28,          width=3)
  signals   = [DM, DM2]


#
# Text on the plots
#
def drawObjects( plotData, dataMCScale, lumi_scale ):
    lumi_scale = 35.9
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary' if plotData else 'CMS Simulation'),
      (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV) Scale %3.2f'% ( lumi_scale, dataMCScale ) ) if False else (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)' % lumi_scale)
    ]
    return [tex.DrawLatex(*l) for l in lines]




def addSys( selectionString , sys = None ):
    if   sys in jet_systematics: return selectionString.replace('nJetGood', 'nJetGood_' + sys).replace('nBTag', 'nBTag_' + sys).replace('mt2ll', 'mt2ll_'+sys).replace('mt2bb', 'mt2bb_' + sys).replace('mt2blbl', 'mt2blbl' + sys)
    elif sys in met_systematics: return selectionString.replace('met_pt', 'met_pt_' + sys).replace('metSig', 'metSig_' + sys).replace('mt2ll', 'mt2ll_'+sys).replace('mt2bb', 'mt2bb_' + sys).replace('mt2blbl', 'mt2blbl' + sys)
    else:                        return selectionString


def weightMC( sys = None ):
    if sys is None:                 return (lambda event, sample:event.weight*event.reweightLeptonTrackingSF*event.reweightTopPt*event.reweightLeptonSF*event.reweightPU36fb*event.reweightDilepTriggerBackup*event.reweightBTag_SF,                                "weight*reweightLeptonTrackingSF*reweightTopPt*reweightLeptonSF*reweightPU36fb*reweightDilepTriggerBackup*reweightBTag_SF")
    elif 'TopPt' in sys:            return (lambda event, sample:event.weight*event.reweightLeptonTrackingSF*                    event.reweightLeptonSF*event.reweightPU36fb*event.reweightDilepTriggerBackup*event.reweightBTag_SF,                                "weight*reweightLeptonTrackingSF*              reweightLeptonSF*reweightPU36fb*reweightDilepTriggerBackup*reweightBTag_SF")
    elif 'LeptonSF' in sys:         return (lambda event, sample:event.weight*event.reweightLeptonTrackingSF*event.reweightTopPt*                       event.reweightPU36fb*event.reweightDilepTriggerBackup*event.reweightBTag_SF*getattr(event, "reweight"+sys), "weight*reweightLeptonTrackingSF*reweightTopPt*                 reweightPU36fb*reweightDilepTriggerBackup*reweightBTag_SF*reweight"+sys)
    elif 'PU' in sys:               return (lambda event, sample:event.weight*event.reweightLeptonTrackingSF*event.reweightTopPt*event.reweightLeptonSF*                     event.reweightDilepTriggerBackup*event.reweightBTag_SF*getattr(event, "reweight"+sys), "weight*reweightLeptonTrackingSF*reweightTopPt*reweightLeptonSF*               reweightDilepTriggerBackup*reweightBTag_SF*reweight"+sys)
    elif 'Trigger' in sys:          return (lambda event, sample:event.weight*event.reweightLeptonTrackingSF*event.reweightTopPt*event.reweightLeptonSF*event.reweightPU36fb*                                 event.reweightBTag_SF*getattr(event, "reweight"+sys), "weight*reweightLeptonTrackingSF*reweightTopPt*reweightLeptonSF*reweightPU36fb*                          *reweightBTag_SF*reweight"+sys)
    elif 'BTag' in sys:             return (lambda event, sample:event.weight*event.reweightLeptonTrackingSF*event.reweightTopPt*event.reweightLeptonSF*event.reweightPU36fb*event.reweightDilepTriggerBackup*                      getattr(event, "reweight"+sys), "weight*reweightLeptonTrackingSF*reweightTopPt*reweightLeptonSF*reweightPU36fb*reweightDilepTriggerBackup*                reweight"+sys)
    elif sys in jme_systematics :   return weightMC( sys = None )
    else:                           raise ValueError( "Systematic %s not known"%sys )



#
# Read variables
#
read_variables = ["weight/F", "l1_pt/F", "l2_pt/F", "l1_eta/F" , "l1_phi/F", "l2_eta/F", "l2_phi/F", "JetGood[pt/F,eta/F,phi/F,btagCSV/F]", "dl_mass/F", "dl_eta/F", "dl_mt2ll/F", "dl_mt2bb/F", "dl_mt2blbl/F",
                  "met_pt/F", "met_phi/F", "LepGood[pt/F,eta/F,miniRelIso/F]", "metSig/F", "ht/F", "nBTag/I", "nJetGood/I","run/I","evt/I"]

offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ")) else ""
def getLeptonSelection(mode):
  if   mode=="mumu": return "(nGoodMuons==2&&nGoodElectrons==0&&isOS&&l1_pt>25&&isMuMu" + offZ + ")"
  elif mode=="mue":  return "(nGoodMuons==1&&nGoodElectrons==1&&isOS&&l1_pt>25&&isEMu)"
  elif mode=="ee":   return "(nGoodMuons==0&&nGoodElectrons==2&&isOS&&l1_pt>25&&isEE" + offZ + ")"
  elif mode=="SF":   return "(" + "||".join([getLeptonSelection(m) for m in ["mumu","ee"]]) + ")"
  elif mode=="all":  return "(" + "||".join([getLeptonSelection(m) for m in ["mumu","mue","ee"]]) + ")"



#
# Loop over channels
#
allPlots   = {}
mode =args.channel
if mode=="mumu":
  data_sample         = DoubleMuon_Run2016_backup
  data_sample.texName = "data (2 #mu)"
elif mode=="ee":
  data_sample         = DoubleEG_Run2016_backup
  data_sample.texName = "data (2 e)"
elif mode=="mue":
  data_sample         = MuonEG_Run2016_backup
  data_sample.texName = "data (1 #mu, 1 e)"
elif mode=="SF":
  data_sample = [DoubleMuon_Run2016_backup, DoubleEG_Run2016_backup]
  DoubleMuon_Run2016_backup.setSelectionString([getFilterCut(isData=True, badMuonFilters="Moriond2017Official"), getLeptonSelection("mumu")])
  DoubleEG_Run2016_backup.setSelectionString([getFilterCut(isData=True, badMuonFilters="Moriond2017Official"), getLeptonSelection("ee")])
  for d in data_sample:
    d.texName = "data (SF)"
    d.style   = styles.errorStyle( ROOT.kBlack )
  lumi_scale = sum(d.lumi for d in data_sample)/float(len(data_sample))/1000
elif mode=="all":
  data_sample = [DoubleMuon_Run2016_backup, DoubleEG_Run2016_backup, MuonEG_Run2016_backup]
  DoubleMuon_Run2016_backup.setSelectionString([getFilterCut(isData=True, badMuonFilters="Moriond2017Official"), getLeptonSelection("mumu")])
  DoubleEG_Run2016_backup.setSelectionString([getFilterCut(isData=True, badMuonFilters="Moriond2017Official"), getLeptonSelection("ee")])
  MuonEG_Run2016_backup.setSelectionString([getFilterCut(isData=True, badMuonFilters="Moriond2017Official"), getLeptonSelection("mue")])
  for d in data_sample:
    d.texName = "data"
    d.style   = styles.errorStyle( ROOT.kBlack )
  lumi_scale = sum(d.lumi for d in data_sample)/float(len(data_sample))/1000

if mode != "all" and mode != "SF":
  data_sample.setSelectionString([getFilterCut(isData=True, badMuonFilters="Moriond2017Official"), getLeptonSelection(mode)])
  data_sample.name  = "data"
  data_sample.style = styles.errorStyle( ROOT.kBlack )
  lumi_scale        = data_sample.lumi/1000

weight_       = lambda event, sample: event.weight
weightString_ = "weight"

logger.info('Lumi scale is ' + str(lumi_scale))

if args.splitBosons: mc = [ Top_pow, TTZ_LO if args.LO else TTZ, TTXNoZ, WWNo2L2Nu, WZ, ZZNo2L2Nu, VVTo2L2Nu, triBoson, DY_HT_LO]
else:                mc = [ Top_pow, TTZ_LO if args.LO else TTZ, TTXNoZ, multiBoson, DY_HT_LO]

for sample in mc:
  if   args.scaleDYVV and sample in [DY_HT_LO]:                                                  sample.scale = lumi_scale*1.31
  elif args.scaleDYVV and sample in [multiBoson, WWNo2L2Nu, WZ, ZZNo2L2Nu, VVTo2L2Nu, triBoson]: sample.scale = lumi_scale*1.19
  else:                                                                                          sample.scale = lumi_scale
  sample.style           = styles.fillStyle(sample.color, lineColor = sample.color)
  sample.read_variables  = ['reweightLeptonTrackingSF/F','reweightTopPt/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F','nTrueInt/F']
  sample.read_variables += ["reweight%s/F"%s    for s in weight_systematics]
  sample.read_variables += ["dl_mt2ll_%s/F"%s   for s in jme_systematics]
  sample.read_variables += ["dl_mt2bb_%s/F"%s   for s in jme_systematics]
  sample.read_variables += ["dl_mt2blbl_%s/F"%s for s in jme_systematics]
  sample.read_variables += ["nJetGood_%s/I"%s   for s in jet_systematics]
  sample.read_variables += ["nBTag_%s/I"%s      for s in jet_systematics]
  sample.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])


# Using older tuples for signals, currently do not use filtercut and read in 36 PU weights
if args.signal == "T2tt":
  for s in signals:
    s.scale          = lumi_scale
    s.read_variables = ['reweightLeptonTrackingSF/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightLeptonFastSimSF/F','reweightBTag_SF/F','reweightPU36fb/F','nTrueInt/F','reweightTopPt/F']
    s.weight         = lambda event, sample: event.reweightLeptonTrackingSF*event.reweightLeptonSF*event.reweightLeptonFastSimSF*event.reweightDilepTriggerBackup*event.reweightPU36fb*event.reweightBTag_SF*event.reweightTopPt
    s.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])

if args.signal == "DM":
  for s in signals:
    s.scale          = lumi_scale
    s.read_variables = ['reweightLeptonTrackingSF/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU36fb/F','nTrueInt/F','reweightTopPt/F']
    s.weight         = lambda event, sample: event.reweightLeptonTrackingSF*event.reweightLeptonSF*event.reweightDilepTriggerBackup*event.reweightPU36fb*event.reweightBTag_SF*event.reweightTopPt
    s.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])


# Use some defaults
selectionString = cutInterpreter.cutString(args.selection)
print selectionString
Plot.setDefaults(weight = weight_, selectionString = cutInterpreter.cutString(args.selection))

stack_mc = Stack( mc )

if   args.signal == "T2tt": stack_data = Stack(data_sample, T2tt, T2tt2)
elif args.signal == "DM":   stack_data = Stack(data_sample, DM, DM2)
else:                       stack_data = Stack(data_sample)
sys_stacks = {sys:copy.deepcopy(stack_mc) for sys in [None] + weight_systematics + jme_systematics }

plots       = []
plotConfigs = []

def appendPlots(name, texX, texY, binning, attribute, binWidth):
  plots_mc = {sys: Plot(
      name            = name if sys is None else name + sys, texX = texX, texY = texY,
      binning         = binning,
      stack           = sys_stacks[sys],
      attribute       = attribute[sys],
      selectionString = addSys(selectionString, sys),
      weight          = weightMC(sys=sys)[0],
    ) for sys in all_systematics}

  plots.extend(plots_mc.values())

  if None in all_systematics: # Only run these when we are in None child job or in combine
    plot_data = Plot(
      name      = name + "_data", texX = texX, texY = texY,
      binning   = binning,
      stack     = stack_data,
      attribute = attribute[None],
    )
    plots.append(plot_data)
    plotConfigs.append([plots_mc, plot_data, binWidth])


appendPlots(
  name      = "dl_mt2ll",
  texX      = 'M_{T2}(ll) (GeV)',
  texY      = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
  binWidth  = 20,
  binning   = Binning.fromThresholds([0,20,40,60,80,100,140,240,340]),
  attribute = {sys: TreeVariable.fromString("dl_mt2ll/F" if not sys or sys in weight_systematics else "dl_mt2ll_%s/F" % sys) for sys in all_systematics}
)

appendPlots(
  name      = "dl_mt2ll_2",
  texX      = 'M_{T2}(ll) (GeV)',
  texY      = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
  binWidth  = 20,
  binning   = Binning.fromThresholds([100,140,180,220,260,300,340]),
  attribute = {sys: TreeVariable.fromString("dl_mt2ll/F" if not sys or sys in weight_systematics else "dl_mt2ll_%s/F" % sys) for sys in all_systematics}
)

if args.selection.count('njet2p'):
  appendPlots(
    name      = "dl_mt2bb",
    texX      = 'M_{T2}(bb) (GeV)',
    texY      = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
    binWidth  = 20,
    binning   = Binning.fromThresholds([70,90,110,130,150,170,190,210,230,250,300,350,400,450]),
    attribute = {sys: TreeVariable.fromString("dl_mt2bb/F" if not sys or sys in weight_systematics else "dl_mt2bb_%s/F" % sys) for sys in all_systematics}
  )

  appendPlots(
    name      = "dl_mt2bb_2",
    texX      = 'M_{T2}(bb) (GeV)',
    texY      = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
    binWidth  = 20,
    binning   = Binning.fromThresholds([70,90,110,130,150,170,190,210,230,250,300,350,400,450,500,550,600,700,800,1000]),
    attribute = {sys: TreeVariable.fromString("dl_mt2bb/F" if not sys or sys in weight_systematics else "dl_mt2bb_%s/F" % sys) for sys in all_systematics}
  )

  appendPlots(
    name      = "dl_mt2blbl",
    texX      = 'M_{T2}(blbl) (GeV)',
    texY      = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
    binWidth  = 20,
    binning   = Binning.fromThresholds([0,20,40,60,80,100,120,140,160,200,250,300,350]),
    attribute = {sys: TreeVariable.fromString("dl_mt2blbl/F" if not sys or sys in weight_systematics else "dl_mt2blbl_%s/F" % sys) for sys in all_systematics}
  )

  appendPlots(
    name      = "dl_mt2blbl_2",
    texX      = 'M_{T2}(blbl) (GeV)',
    texY      = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Events",
    binWidth  = 20,
    binning   = Binning.fromThresholds([0,20,40,60,80,100,120,140,160,200,250,300,350,400,450,500,600,700]),
    attribute = {sys: TreeVariable.fromString("dl_mt2blbl/F" if not sys or sys in weight_systematics else "dl_mt2blbl_%s/F" % sys) for sys in all_systematics}
  )

appendPlots(
  name      = "nbtags",
  texX      = 'number of b-tags (CSVM)',
  texY      = 'Number of Events',
  binWidth  = -1,
  binning   = [5, 1, 6] if args.selection.count('btag1p') else [1,0,1],
  attribute = {sys: TreeVariable.fromString('nBTag/I' if not sys or sys in weight_systematics or sys in met_systematics else "nBTag_%s/I" % sys) for sys in all_systematics},
)

appendPlots(
  name      = "njets",
  texX      = 'number of jets',
  texY      = 'Number of Events',
  binWidth  = -1,
  binning   = [8,2,10] if args.selection.count('njet2p') else [2,0,2],
  attribute = {sys: TreeVariable.fromString('nJetGood/I' if not sys or sys in weight_systematics or sys in met_systematics else "nJetGood_%s/I" % sys) for sys in all_systematics},
)

appendPlots(
  name      = "met",
  texX      = 'E_{T}^{miss} (GeV)',
  texY      = 'Number of Events / 20 GeV' if args.normalizeBinWidth else "Number of Event",
  binWidth  = 20,
  binning   = Binning.fromThresholds([0,20,40,60,80] if args.selection.count('metInv') else [80,100,120,140,160,200,500] if args.selection.count('met80') else [0,80,100,120,140,160,200,500]),
  attribute = {sys: TreeVariable.fromString('met_pt/F' if not sys or sys not in met_systematics else "met_pt_%s/F" % sys) for sys in all_systematics},
)

if not args.selection.count('metInv'):
  appendPlots(
    name      = "met_2",
    texX      = 'E_{T}^{miss} (GeV)',
    texY      = 'Number of Events / 50 GeV' if args.normalizeBinWidth else "Number of Event",
    binWidth  = 50,
    binning   = Binning.fromThresholds([80,130,180,230,280,320,420,520,800] if args.selection.count('met80') else [0,80,130,180,230,280,320,420,520,800]),
    attribute = {sys: TreeVariable.fromString('met_pt/F' if not sys or sys not in met_systematics else "met_pt_%s/F" % sys) for sys in all_systematics},
  )

result_file = os.path.join(plot_directory, args.plot_directory, mode, args.selection, 'results.pkl')
try: os.makedirs(os.path.join(plot_directory, args.plot_directory, mode, args.selection))
except: pass

if args.selectSys != "combine":

  # mc_selection_string is used for scaling the top on the mt2ll < 100 regions
  if args.normString: selectionString = args.normString
  else:               selectionString = args.selection.split('-mt2ll')[0]  # assumes that mt2ll is always the last variable in args.selection
  mc_selection_string = cutInterpreter.cutString(selectionString)
  mc_weight_func, mc_weight_string = weightMC( sys = (args.selectSys if args.selectSys != 'None' else None) )
  print mc_selection_string

  yield_mc = {s.name + (args.selectSys if sys else ""):s.scale*s.getYieldFromDraw( selectionString =  addSys(mc_selection_string + "&&dl_mt2ll<100" ), weightString = mc_weight_string)['val'] for s in mc}
  if mode == "all" or mode == 'SF': yield_data = sum(s.getYieldFromDraw(       selectionString = mc_selection_string + "&&dl_mt2ll<100", weightString = weightString_)['val'] for s in data_sample )
  else:                             yield_data = data_sample.getYieldFromDraw( selectionString = mc_selection_string + "&&dl_mt2ll<100", weightString = weightString_)['val']

  plotting.fill(plots, read_variables = read_variables, sequence = [])

  from StopsDilepton.tools.lock import waitForLock, removeLock
  waitForLock( result_file )
  if os.path.exists(result_file):
    (allPlots, yields) = pickle.load(file( result_file ))
    allPlots.update({p.name : p.histos for p in plots})
    yields.update(yield_mc)
  else:
    allPlots = {p.name : p.histos for p in plots}
    yields = yield_mc
  yields['data'] = yield_data
  pickle.dump( (allPlots, yields), file( result_file, 'w' ) )
  removeLock( result_file )
  logger.info( "Done for sys " + args.selectSys )

else:
  (allPlots, yields) = pickle.load(file( result_file ))

  from RootTools.plot.Plot import addOverFlowBin1D
  for p in plots:
    p.histos = allPlots[p.name]
    for s in p.histos:
      for h in s:
        addOverFlowBin1D(h, "upper")
        if h.Integral()==0: logger.warning( "Found empty histogram %s in results file %s", h.GetName(), result_file )

  topName = Top_pow.name if args.powheg else Top.name
  top_sf = {}





  dataMCScaling = True
  if dataMCScaling:
    yield_data    = yields['data']
    yield_non_top = sum(yields[s.name + 'None'] for s in mc if s.name != topName)
    top_sf[None]  = (yield_data - yield_non_top)/yields[topName+'None']
    total         = yield_data
    logger.info( "Data: %i MC TT %3.2f MC other %3.2f SF %3.2f", yield_data, yields[topName+'None'], yield_non_top, top_sf[None] )
    if args.selection.count('njet01-btag0-looseLeptonVeto-mll20-metInv') and mode != "mue":
      top_sf[None] = 1
  else:
    top_sf[None] = 1
    total        = sum(yield_mc.values())


  #Scaling systematic shapes to MT2ll<100 region
  for sys_pair in sys_pairs:
    for sys in sys_pair[1:]:
      if not top_sf.has_key( sys ):
          mc_sys_weight_func, mc_sys_weight_string = weightMC( sys = sys )
          non_top                                  = sum(yields[s.name+sys] for s in mc if s.name != topName)
          top_sf[sys]                              = (total - non_top)/yields[topName+sys]
          logger.info( "Total: %i sys %s MC TT %3.2f MC other %3.2f SF %3.2f", total, sys, yields[topName+sys], non_top, top_sf[sys] )

          if args.selection.count('njet01-btag0-looseLeptonVeto-mll20-metInv') and mode != "mue":
            top_sf[sys] = 1
            logger.info( "NOT scaling top for " + args.selection + " (mode " + mode + ")" )


  for plots_mc, plot_data, bin_width in plotConfigs:
      if args.normalizeBinWidth and bin_width>0:
              for p in plots_mc.values() + [plot_data]:
                  for histo in sum(p.histos, []):
                      for ib in range(histo.GetXaxis().GetNbins()+1):
                          val = histo.GetBinContent( ib )
                          err = histo.GetBinError( ib )
                          width = histo.GetBinWidth( ib )
                          histo.SetBinContent(ib, val / (width / bin_width))
                          histo.SetBinError(ib, err / (width / bin_width))
      topHist = None
      ttzHist = None
      ttxHist = None
      mbHist  = None
      dyHist  = None

      # Scaling Top
      for k in plots_mc.keys():
          for s in plots_mc[k].histos:
              pos_top = [i for i,x in enumerate(mc) if x == (Top_pow if args.powheg else Top)][0]
              plots_mc[k].histos[0][pos_top].Scale(top_sf[k])
              pos_ttz = [i for i,x in enumerate(mc) if x == (TTZ_LO if args.LO else TTZ)][0]
              pos_ttx = [i for i,x in enumerate(mc) if x == TTXNoZ][0]
              pos_dy  = [i for i,x in enumerate(mc) if x == DY_HT_LO][0]
              pos_mb  = [i for i,x in enumerate(mc) if x == multiBoson][0]

              topHist = plots_mc[k].histos[0][pos_top]
              ttzHist = plots_mc[k].histos[0][pos_ttz]
              ttxHist = plots_mc[k].histos[0][pos_ttx]
              mbHist  = plots_mc[k].histos[0][pos_mb]
              dyHist  = plots_mc[k].histos[0][pos_dy]
                    
      #Calculating systematics
      h_summed = {k: plots_mc[k].histos_added[0][0].Clone() for k in plots_mc.keys()}

      ##Normalize systematic shapes
      #if args.sysScaling:
      #    for k in h_summed.keys():
      #        if k is None: continue
      #        h_summed[k].Scale( top_sf[ k ] )

      h_rel_err = h_summed[None].Clone()
      h_rel_err.Reset()

      #MC statistical error
      for ib in range( 1 + h_rel_err.GetNbinsX() ):
          h_rel_err.SetBinContent(ib, h_summed[None].GetBinError(ib)**2 )

      h_sys = {}
      goOn = False
      for k, s1, s2 in ([s for s in sys_pairs if s[0] == args.showOnly] if args.showOnly else sys_pairs):
          goOn = True
          h_sys[k] = h_summed[s1].Clone()
          h_sys[k].Scale(-1)
          h_sys[k].Add(h_summed[s2])
      if not goOn: continue

      # Adding in quadrature
      for k in h_sys.keys():
          for ib in range( 1 + h_rel_err.GetNbinsX() ):
              h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + h_sys[k].GetBinContent(ib)**2 )

      # When making plots with mt2ll > 100 GeV, include also our background shape uncertainties
      if (args.selection.count('mt2ll100') or plots_mc[None].name == "dl_mt2ll") and False:
          for ib in range(1 + h_rel_err.GetNbinsX() ):
              if plots_mc[None].name == "dl_mt2ll" and h_rel_err.GetBinCenter(ib) < 100: continue
              topUnc = 1 if (plots_mc == dl_mt2ll_mc and h_rel_err.GetBinCenter(ib) > 240) else 0.5
              h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + (topUnc*topHist.GetBinContent(ib))**2 )
              h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + (0.2*ttxHist.GetBinContent(ib))**2 )
              h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + (0.25*ttxHist.GetBinContent(ib))**2 )
              h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + (0.25*dyHist.GetBinContent(ib))**2 )
              h_rel_err.SetBinContent(ib, h_rel_err.GetBinContent(ib) + (0.25*mbHist.GetBinContent(ib))**2 )

      # take sqrt
      for ib in range( 1 + h_rel_err.GetNbinsX() ):
          h_rel_err.SetBinContent(ib, sqrt( h_rel_err.GetBinContent(ib) ) )

      # Divide
      h_rel_err.Divide(h_summed[None])

      plot = plots_mc[None]
      if args.normalizeBinWidth: plot.name += "_normalizeBinWidth"
      signal_histos = plot_data.histos[1:] if args.signal != 'None' else []
      data_histo    = plot_data.histos[0][0]
      for h in plot_data.histos[0][1:]:
        data_histo.Add(h)

      data_histo.style = styles.errorStyle( ROOT.kBlack )
      plot.histos += [[ data_histo ]]
      for h in signal_histos: plot.histos += [h]
      plot_data.stack[0][0].texName = data_sample.texName if mode != "all" and mode != 'SF' else data_sample[0].texName
      plot.stack += [[ plot_data.stack[0][0] ]]
      for i, signal in enumerate(signals):
        plot_data.stack[i+1][0].texName = signal.texName
        plot_data.stack[i+1][0].style   = signal.style
        plot.stack += [[ plot_data.stack[i+1][0] ]]

      boxes = []
      ratio_boxes = []
      for ib in range(1, 1 + h_rel_err.GetNbinsX() ):
          val = h_summed[None].GetBinContent(ib)
          if val<0: continue
          sys = h_rel_err.GetBinContent(ib)
          box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max([0.03, (1-sys)*val]), h_rel_err.GetXaxis().GetBinUpEdge(ib), max([0.03, (1+sys)*val]) )
          box.SetLineColor(ROOT.kBlack)
          box.SetFillStyle(3444)
          box.SetFillColor(ROOT.kBlack)
          r_box = ROOT.TBox( h_rel_err.GetXaxis().GetBinLowEdge(ib),  max(0.1, 1-sys), h_rel_err.GetXaxis().GetBinUpEdge(ib), min(1.9, 1+sys) )
          r_box.SetLineColor(ROOT.kBlack)
          r_box.SetFillStyle(3444)
          r_box.SetFillColor(ROOT.kBlack)

          boxes.append( box )
          ratio_boxes.append( r_box )

      ratio = {'yRange':(0.1,1.9), 'drawObjects':ratio_boxes}

      for log in [False, True]:
        plotDir = os.path.join(plot_directory, args.plot_directory, mode + ("_log" if log else "") + "_scaled", args.selection)
        if args.showOnly: plotDir = os.path.join(plotDir, "only_" + args.showOnly)
        plotting.draw(plot,
            plot_directory = plotDir,
            ratio = ratio,
            legend = (0.50,0.88-0.04*sum(map(len, plot.histos)),0.95,0.88),
            logX = False, logY = log, #sorting = True,
            yRange = (0.3, "auto") if args.selection == "njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-mt2ll100" else (0.03, "auto"),
            drawObjects = drawObjects( True, top_sf[None], lumi_scale ) + boxes,
            copyIndexPHP = True
        )

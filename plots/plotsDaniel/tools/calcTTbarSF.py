''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools

#RootTools
from RootTools.core.standard import *

from StopsDilepton.tools.cutInterpreter import cutInterpreter
from StopsDilepton.tools.objectSelection import getFilterCut

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', action='store', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], default='INFO', help="Log level for logging")
argParser.add_argument('--selection', action='store', default='njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1')
argParser.add_argument('--mode', default='mumu', action='store', choices=['mumu', 'ee',  'mue'])
argParser.add_argument('--small', action='store_true', help='Small?')
argParser.add_argument('--diBosonScaleFactor', type = float, default = 1., action='store')
argParser.add_argument('--ttjets', default='pow', action='store', choices=['mg', 'pow', 'powIncl', 'amc'], help='ttjets sample')
argParser.add_argument('--scaleDY', action='store_true', help='Scale DY sample')

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

postProcessing_directory = "postProcessed_80X_v23/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *
postProcessing_directory = "postProcessed_80X_v22/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Data25ns_80X_23Sep_postProcessed import *

#postProcessing_directory = "postProcessed_80X_v26/dilepTiny/"
#from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
#postProcessing_directory = "postProcessed_80X_v27/dilepTiny/"
#from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *


mode = args.mode
offZ = "&&abs(dl_mass-91.1876)>15" if not (args.selection.count("onZ") or args.selection.count("allZ") or args.selection.count("offZ")) else ""

##Full dataset
sample_DoubleMuon  = DoubleMuon_Run2016_backup
sample_DoubleEG    = DoubleEG_Run2016_backup
sample_MuonEG      = MuonEG_Run2016_backup

def getLeptonSelection( mode ):
  if   mode=="mumu": return "nGoodMuons==2&&nGoodElectrons==0&&isOS&&isMuMu" + offZ
  elif mode=="mue":  return "nGoodMuons==1&&nGoodElectrons==1&&isOS&&isEMu"
  elif mode=="ee":   return "nGoodMuons==0&&nGoodElectrons==2&&isOS&&isEE" + offZ

if   mode=="mumu": data_sample = DoubleMuon_Run2016_backup
elif mode=="ee":   data_sample = DoubleEG_Run2016_backup
elif mode=="mue":  data_sample = MuonEG_Run2016_backup

data_sample.setSelectionString([getFilterCut(isData=True), getLeptonSelection(mode)])
data_sample.name           = "data"
data_sample.read_variables = ["evt/I","run/I"]
data_sample.style          = styles.errorStyle(ROOT.kBlack)
lumi_scale                 = data_sample.lumi/1000

data_samples = [data_sample]

if args.ttjets=='mg':
    TTJets_sample = Top
elif args.ttjets=='pow':
    TTJets_sample = Top_pow 
elif args.ttjets=='powIncl':
    TTJets_sample = Top_pow_incl
elif args.ttjets=='amc':
    TTJets_sample = Top_amc

diBoson_samples = [diBoson]
mc_samples = [ TTJets_sample] + diBoson_samples + [DY_HT_LO, TTZ_LO, TTXNoZ, triBoson, TWZ]

if args.small:
    for sample in mc_samples + [data_sample]:
        sample.reduceFiles(to = 1)

for sample in mc_samples:
  sample.scale          = lumi_scale
  sample.read_variables = ['reweightLeptonHIPSF/F','reweightDilepTriggerBackup/F','reweightLeptonSF/F','reweightBTag_SF/F','reweightPU12fb/F', 'nTrueInt/F']
  sample.weight         = lambda event, sample: event.reweightLeptonSF*event.reweightDilepTriggerBackup*event.reweightPU36fb
  sample.setSelectionString([getFilterCut(isData=False), getLeptonSelection(mode)])
  sample.style = styles.fillStyle( sample.color)

stack = Stack(mc_samples) 
stack.append( data_sample ) 

#Averaging lumi
lumi_scale = sum(d.lumi for d in data_samples)/float(len(data_samples))/1000

logger.info( "Lumi scale for mode %s is %3.2f", args.mode, lumi_scale )

mc_weight_string = "weight*reweightDilepTriggerBackup*reweightLeptonSF"

data_weight_string = "weight"

#for sample in mc_samples + signal_samples:
#    sample.setSelectionString([ mcFilterCut, lepton_selection_string_mc])
#    sample.read_variables = ['reweightPU36fb/F', 'reweightDilepTriggerBackup/F', 'reweightLeptonSF/F']
#    sample.weight = lambda event, sample: event.reweightPU36fb*event.reweightDilepTriggerBackup*event.reweightLeptonSF

weight = lambda event, sample: event.weight

# add in cut interpreter

def drawObjects( scale ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    lines = [ (0.15, 0.95, 'CMS Preliminary') ]
    if scale is not None: 
        lines.append( (0.45, 0.95, 'L=%3.2f fb{}^{-1} (13 TeV) Scale %3.2f'% ( int(lumi_scale*10)/10., scale ) ) )
    else:
        lines.append( (0.50, 0.95, '13 TeV' ) )
    return [tex.DrawLatex(*l) for l in lines] 

sequence = []
read_variables = ["weight/F"]

cutList = cutInterpreter.cutList(args.selection)
print cutList

cut = "(1)"

plotFile = '/afs/hephy.at/user/d/dspitzbart/www/stopsDilepton/txtFiles/flow_'+args.selection+'_'+mode
txtFile = plotFile + '.txt'
txt = open(txtFile,'w')



print '{:60}{:>12}{:>12}{:>12}{:>12}'.format("Cut in addition to previous one", "ttbar SF", "MC", "Data", "total SF")
txt.write('{:60}{:>12}{:>12}{:>12}{:>12}\n'.format("Cut in addition to previous one", "ttbar SF", "MC", "Data", "total SF"))


for i in range(len(cutList)):
  cut += "&&" + cutList[i]
  selectionString = cut
  
  #logger.info( "Calculating normalization constants" )
  logger.info( "Using cut %s",cut)
  logger.info( "Sample selection string %s", sample.selectionString)
  yield_mc    = {s.name: s.scale*s.getYieldFromDraw( selectionString = selectionString+"&&dl_mt2ll<100", weightString = mc_weight_string)['val'] for s in mc_samples}
  yield_data  = sum(s.getYieldFromDraw( selectionString = selectionString+"&&dl_mt2ll<100", weightString = data_weight_string)['val'] for s in [data_sample])
  
  non_top = sum(yield_mc[s.name] for s in mc_samples if s.name != TTJets_sample.name)
  total_mc = sum(yield_mc[s.name] for s in mc_samples)
  top_sf = (yield_data - non_top)/yield_mc[TTJets_sample.name]
  total_sf = yield_data/total_mc
  
  print '{:60}{:12.3f}{:12.2f}{:12.0f}{:12.3f}'.format(cutList[i], top_sf, total_mc, yield_data, total_sf)
  txt.write('{:60}{:12.3f}{:12.2f}{:12.0f}{:12.3f}\n'.format(cutList[i], top_sf, total_mc, yield_data, total_sf))

  ## Use some defaults
  #Plot.setDefaults(stack = stack, weight = weight_, selectionString = cutInterpreter.cutString(args.selection), addOverFlowBin='upper')
  #
  #plots = []

  #plots.append(Plot(
  #  texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 20 GeV',
  #  attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
  #  binning=[300/20, 100,400] if args.selection.count('mt2ll100') else ([300/20, 140, 440] if args.selection.count('mt2ll140') else [300/20,0,300]),
  #))

txt.close()

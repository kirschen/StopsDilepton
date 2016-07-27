import copy, os, sys
from StopsDilepton.tools.user import data_directory
from RootTools.core.Sample import Sample 
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

# Data directory
try:
    data_directory = sys.modules['__main__'].data_directory
except:
    from StopsDilepton.tools.user import data_directory as user_data_directory
    data_directory = user_data_directory 

# Take post processing directory if defined in main module
try:
    postProcessing_directory = sys.modules['__main__'].postProcessing_directory
except:
    postProcessing_directory = "postProcessed_80X_v12/dilepTiny"

logger.info("Loading data samples from directory %s", os.path.join(data_directory, postProcessing_directory))

dirs = {}
dirs['DoubleEG_Run2016B']       = ["DoubleEG_Run2016B_PromptReco_v2"]
dirs['DoubleMuon_Run2016B']     = ["DoubleMuon_Run2016B_PromptReco_v2"]
dirs['MuonEG_Run2016B']         = ["MuonEG_Run2016B_PromptReco_v2"]

dirs["DoubleEG_Run2016B_backup"]    = ["DoubleEG_Run2016B_PromptReco_v2_Trig_ee", "SingleElectron_Run2016B_PromptReco_v2_Trig_e_for_ee"]
dirs["DoubleMuon_Run2016B_backup"]  = ["DoubleMuon_Run2016B_PromptReco_v2_Trig_mumu", "SingleMuon_Run2016B_PromptReco_v2_Trig_mu_for_mumu"]
dirs["MuonEG_Run2016B_backup"]      = ["MuonEG_Run2016B_PromptReco_v2_Trig_mue", "SingleElectron_Run2016B_PromptReco_v2_Trig_e_for_mue", "SingleMuon_Run2016B_PromptReco_v2_Trig_mu_for_mue"]

for key in dirs:
  dirs[key] = [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]]

#DoubleEG_Run2016B       = Sample.fromDirectory(name="DoubleEG_Run2016B",       treeName="Events", texName="DoubleEG (Run2016B)",       directory=dirs["DoubleEG_Run2016B"])
#DoubleMuon_Run2016B     = Sample.fromDirectory(name="DoubleMuon_Run2016B",     treeName="Events", texName="DoubleMuon (Run2016B)",     directory=dirs["DoubleMuon_Run2016B"])
#MuonEG_Run2016B         = Sample.fromDirectory(name="MuonEG_Run2016B",         treeName="Events", texName="MuonEG (Run2016B)",         directory=dirs["MuonEG_Run2016B"])
#DoubleEG_Run2016B      .lumi = 5.907*1000 
#DoubleMuon_Run2016B    .lumi = 5.876*1000 
#MuonEG_Run2016B        .lumi = 5.916*1000

DoubleEG_Run2016B_backup       = Sample.fromDirectory(name="DoubleEG_Run2016B_backup",       treeName="Events", texName="DoubleEG (Run2016B)",       directory=dirs["DoubleEG_Run2016B_backup"])
DoubleMuon_Run2016B_backup     = Sample.fromDirectory(name="DoubleMuon_Run2016B_backup",     treeName="Events", texName="DoubleMuon (Run2016B)",     directory=dirs["DoubleMuon_Run2016B_backup"])
MuonEG_Run2016B_backup         = Sample.fromDirectory(name="MuonEG_Run2016B_backup",         treeName="Events", texName="MuonEG (Run2016B)",         directory=dirs["MuonEG_Run2016B_backup"])

DoubleEG_Run2016B_backup      .lumi = 5.93*1000 
DoubleMuon_Run2016B_backup    .lumi = 5.93*1000 
MuonEG_Run2016B_backup        .lumi = 5.93*1000

allSamples_Data25ns = []
#allSamples_Data25ns += [DoubleEG_Run2016B, MuonEG_Run2016B, DoubleMuon_Run2016B]#, SingleElectron_Run2016B, SingleMuon_Run2016B]
allSamples_Data25ns += [DoubleEG_Run2016B_backup, MuonEG_Run2016B_backup, DoubleMuon_Run2016B_backup]#, SingleElectron_Run2016B_backup, SingleMuon_Run2016B_backup]
for s in allSamples_Data25ns:
  s.color   = ROOT.kBlack
  s.isData  = True

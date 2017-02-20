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
    postProcessing_directory = 'postProcessed_80X_v31/dilepTiny'

logger.info("Loading data samples from directory %s", os.path.join(data_directory, postProcessing_directory))

dirs = {}

dirs["DoubleEG_Run2016B_backup"]    = ["DoubleEG_Run2016B_03Feb2017_v2_Trig_ee", "SingleElectron_Run2016B_03Feb2017_v2_Trig_e_for_ee"]
dirs["DoubleMuon_Run2016B_backup"]  = ["DoubleMuon_Run2016B_03Feb2017_v2_Trig_mumu", "SingleMuon_Run2016B_03Feb2017_v2_Trig_mu_for_mumu"]
dirs["MuonEG_Run2016B_backup"]      = ["MuonEG_Run2016B_03Feb2017_v2_Trig_mue", "SingleElectron_Run2016B_03Feb2017_v2_Trig_e_for_mue", "SingleMuon_Run2016B_03Feb2017_v2_Trig_mu_for_mue"]

dirs["DoubleEG_Run2016C_backup"]    = ["DoubleEG_Run2016C_03Feb2017_Trig_ee", "SingleElectron_Run2016C_03Feb2017_Trig_e_for_ee"]
dirs["DoubleMuon_Run2016C_backup"]  = ["DoubleMuon_Run2016C_03Feb2017_Trig_mumu", "SingleMuon_Run2016C_03Feb2017_Trig_mu_for_mumu"]
dirs["MuonEG_Run2016C_backup"]      = ["MuonEG_Run2016C_03Feb2017_Trig_mue", "SingleElectron_Run2016C_03Feb2017_Trig_e_for_mue", "SingleMuon_Run2016C_03Feb2017_Trig_mu_for_mue"]

dirs["DoubleEG_Run2016D_backup"]    = ["DoubleEG_Run2016D_03Feb2017_Trig_ee", "SingleElectron_Run2016D_03Feb2017_Trig_e_for_ee"]
dirs["DoubleMuon_Run2016D_backup"]  = ["DoubleMuon_Run2016D_03Feb2017_Trig_mumu", "SingleMuon_Run2016D_03Feb2017_Trig_mu_for_mumu"]
dirs["MuonEG_Run2016D_backup"]      = ["MuonEG_Run2016D_03Feb2017_Trig_mue", "SingleElectron_Run2016D_03Feb2017_Trig_e_for_mue", "SingleMuon_Run2016D_03Feb2017_Trig_mu_for_mue"]

dirs["DoubleEG_Run2016E_backup"]    = ["DoubleEG_Run2016E_03Feb2017_Trig_ee", "SingleElectron_Run2016E_03Feb2017_Trig_e_for_ee"]
dirs["DoubleMuon_Run2016E_backup"]  = ["DoubleMuon_Run2016E_03Feb2017_Trig_mumu", "SingleMuon_Run2016E_03Feb2017_Trig_mu_for_mumu"]
dirs["MuonEG_Run2016E_backup"]      = ["MuonEG_Run2016E_03Feb2017_Trig_mue", "SingleElectron_Run2016E_03Feb2017_Trig_e_for_mue", "SingleMuon_Run2016E_03Feb2017_Trig_mu_for_mue"]

dirs["DoubleEG_Run2016F_backup"]    = ["DoubleEG_Run2016F_03Feb2017_Trig_ee", "SingleElectron_Run2016F_03Feb2017_Trig_e_for_ee"]
dirs["DoubleMuon_Run2016F_backup"]  = ["DoubleMuon_Run2016F_03Feb2017_Trig_mumu", "SingleMuon_Run2016F_03Feb2017_Trig_mu_for_mumu"]
dirs["MuonEG_Run2016F_backup"]      = ["MuonEG_Run2016F_03Feb2017_Trig_mue", "SingleElectron_Run2016F_03Feb2017_Trig_e_for_mue", "SingleMuon_Run2016F_03Feb2017_Trig_mu_for_mue"]

dirs["DoubleEG_Run2016G_backup"]    = ["DoubleEG_Run2016G_03Feb2017_Trig_ee", "SingleElectron_Run2016G_03Feb2017_Trig_e_for_ee"]
dirs["DoubleMuon_Run2016G_backup"]  = ["DoubleMuon_Run2016G_03Feb2017_Trig_mumu", "SingleMuon_Run2016G_03Feb2017_Trig_mu_for_mumu"]
dirs["MuonEG_Run2016G_backup"]      = ["MuonEG_Run2016G_03Feb2017_Trig_mue", "SingleElectron_Run2016G_03Feb2017_Trig_e_for_mue", "SingleMuon_Run2016G_03Feb2017_Trig_mu_for_mue"]

dirs["DoubleEG_Run2016H_v2_backup"]    = ["DoubleEG_Run2016H_03Feb2017_v2_Trig_ee", "SingleElectron_Run2016H_03Feb2017_v2_Trig_e_for_ee"]
dirs["DoubleMuon_Run2016H_v2_backup"]  = ["DoubleMuon_Run2016H_03Feb2017_v2_Trig_mumu", "SingleMuon_Run2016H_03Feb2017_v2_Trig_mu_for_mumu"]
dirs["MuonEG_Run2016H_v2_backup"]      = ["MuonEG_Run2016H_03Feb2017_v2_Trig_mue", "SingleElectron_Run2016H_03Feb2017_v2_Trig_e_for_mue", "SingleMuon_Run2016H_03Feb2017_v2_Trig_mu_for_mue"]

dirs["DoubleEG_Run2016H_v3_backup"]    = ["DoubleEG_Run2016H_03Feb2017_v3_Trig_ee", "SingleElectron_Run2016H_03Feb2017_v3_Trig_e_for_ee"]
dirs["DoubleMuon_Run2016H_v3_backup"]  = ["DoubleMuon_Run2016H_03Feb2017_v3_Trig_mumu", "SingleMuon_Run2016H_03Feb2017_v3_Trig_mu_for_mumu"]
dirs["MuonEG_Run2016H_v3_backup"]      = ["MuonEG_Run2016H_03Feb2017_v3_Trig_mue", "SingleElectron_Run2016H_03Feb2017_v3_Trig_e_for_mue", "SingleMuon_Run2016H_03Feb2017_v3_Trig_mu_for_mue"]


dirs["DoubleEG_Run2016BCD_backup"]   =  dirs["DoubleEG_Run2016B_backup"]   + dirs["DoubleEG_Run2016C_backup"]   +  dirs["DoubleEG_Run2016D_backup"]  
dirs["DoubleMuon_Run2016BCD_backup"] =  dirs["DoubleMuon_Run2016B_backup"] + dirs["DoubleMuon_Run2016C_backup"] +  dirs["DoubleMuon_Run2016D_backup"]
dirs["DoubleMuon_Run2016BCD_backup"] =  dirs["DoubleMuon_Run2016C_backup"]
dirs["MuonEG_Run2016BCD_backup"]     =  dirs["MuonEG_Run2016B_backup"]     + dirs["MuonEG_Run2016C_backup"]     +  dirs["MuonEG_Run2016D_backup"]    
dirs["MuonEG_Run2016BCD_backup"]     =  dirs["MuonEG_Run2016D_backup"]    

dirs["DoubleEG_Run2016BCDEFG_backup"]   =  dirs["DoubleEG_Run2016BCD_backup"]   + dirs["DoubleEG_Run2016E_backup"]   + dirs["DoubleEG_Run2016F_backup"]   +  dirs["DoubleEG_Run2016G_backup"]
dirs["DoubleMuon_Run2016BCDEFG_backup"] =  dirs["DoubleMuon_Run2016BCD_backup"] + dirs["DoubleMuon_Run2016E_backup"] + dirs["DoubleMuon_Run2016F_backup"] +  dirs["DoubleMuon_Run2016G_backup"]
dirs["DoubleMuon_Run2016BCDEFG_backup"] =  dirs["DoubleMuon_Run2016BCD_backup"] + dirs["DoubleMuon_Run2016F_backup"] +  dirs["DoubleMuon_Run2016G_backup"]
dirs["MuonEG_Run2016BCDEFG_backup"]     =  dirs["MuonEG_Run2016BCD_backup"]     + dirs["MuonEG_Run2016E_backup"]     + dirs["MuonEG_Run2016F_backup"]     +  dirs["MuonEG_Run2016G_backup"]
dirs["MuonEG_Run2016BCDEFG_backup"]     =  dirs["MuonEG_Run2016BCD_backup"]     + dirs["MuonEG_Run2016F_backup"]     +  dirs["MuonEG_Run2016G_backup"]

dirs["DoubleEG_Run2016_backup"]   =  dirs["DoubleEG_Run2016BCDEFG_backup"]   + dirs["DoubleEG_Run2016H_v2_backup"]   + dirs["DoubleEG_Run2016H_v3_backup"]  
dirs["DoubleMuon_Run2016_backup"] =  dirs["DoubleMuon_Run2016BCDEFG_backup"] + dirs["DoubleMuon_Run2016H_v2_backup"] + dirs["DoubleMuon_Run2016H_v3_backup"]
dirs["MuonEG_Run2016_backup"]     =  dirs["MuonEG_Run2016BCDEFG_backup"]     + dirs["MuonEG_Run2016H_v2_backup"]     + dirs["MuonEG_Run2016H_v3_backup"]    


for key in dirs:
  dirs[key] = [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]]

DoubleEG_Run2016H_v3_backup       = Sample.fromDirectory(name="DoubleEG_Run2016H_v3_backup",       treeName="Events", texName="DoubleEG (Run2016H_v3)",       directory=dirs["DoubleEG_Run2016H_v3_backup"])
DoubleEG_Run2016G_backup       = Sample.fromDirectory(name="DoubleEG_Run2016G_backup",       treeName="Events", texName="DoubleEG (Run2016G)",       directory=dirs["DoubleEG_Run2016G_backup"])

DoubleEG_Run2016BCD_backup       = Sample.fromDirectory(name="DoubleEG_Run2016BCD_backup",       treeName="Events", texName="DoubleEG (Run2016BCD)",       directory=dirs["DoubleEG_Run2016BCD_backup"])
DoubleMuon_Run2016BCD_backup     = Sample.fromDirectory(name="DoubleMuon_Run2016BCD_backup",     treeName="Events", texName="DoubleMuon (Run2016BCD)",     directory=dirs["DoubleMuon_Run2016BCD_backup"])
MuonEG_Run2016BCD_backup         = Sample.fromDirectory(name="MuonEG_Run2016BCD_backup",         treeName="Events", texName="MuonEG (Run2016BCD)",         directory=dirs["MuonEG_Run2016BCD_backup"])

DoubleEG_Run2016BCDEFG_backup       = Sample.fromDirectory(name="DoubleEG_Run2016BCDEFG_backup",       treeName="Events", texName="DoubleEG (Run2016BCDEFG)",       directory=dirs["DoubleEG_Run2016BCDEFG_backup"])
DoubleMuon_Run2016BCDEFG_backup     = Sample.fromDirectory(name="DoubleMuon_Run2016BCDEFG_backup",     treeName="Events", texName="DoubleMuon (Run2016BCDEFG)",     directory=dirs["DoubleMuon_Run2016BCDEFG_backup"])
MuonEG_Run2016BCDEFG_backup         = Sample.fromDirectory(name="MuonEG_Run2016BCDEFG_backup",         treeName="Events", texName="MuonEG (Run2016BCDEFG)",         directory=dirs["MuonEG_Run2016BCDEFG_backup"])

DoubleEG_Run2016_backup       = Sample.fromDirectory(name="DoubleEG_Run2016_backup",       treeName="Events", texName="DoubleEG (Run2016)",       directory=dirs["DoubleEG_Run2016_backup"])
DoubleMuon_Run2016_backup     = Sample.fromDirectory(name="DoubleMuon_Run2016_backup",     treeName="Events", texName="DoubleMuon (Run2016)",     directory=dirs["DoubleMuon_Run2016_backup"])
MuonEG_Run2016_backup         = Sample.fromDirectory(name="MuonEG_Run2016_backup",         treeName="Events", texName="MuonEG (Run2016)",         directory=dirs["MuonEG_Run2016_backup"])

DoubleEG_Run2016BCD_backup      .lumi = (5.744+2.573+4.248)*1000
DoubleMuon_Run2016BCD_backup    .lumi = (5.744+2.573+4.248)*1000
MuonEG_Run2016BCD_backup        .lumi = (5.743+2.573+4.248)*1000

DoubleEG_Run2016BCDEFG_backup      .lumi = (5.744+2.573+4.248+4.009+3.101+7.540)*1000
DoubleMuon_Run2016BCDEFG_backup    .lumi = (5.744+2.573+4.248+4.009+3.101+7.540)*1000
MuonEG_Run2016BCDEFG_backup        .lumi = (5.743+2.573+4.248+4.009+3.101+7.540)*1000

DoubleEG_Run2016_backup      .lumi = (5.744+2.573+4.248+4.009+3.101+7.540+8.329+0.210)*1000
DoubleMuon_Run2016_backup    .lumi = (5.744+2.573+4.248+4.009+3.101+7.540+8.329+0.210)*1000
MuonEG_Run2016_backup        .lumi = (5.743+2.573+4.248+4.009+3.101+7.540+8.327+0.210)*1000

allSamples_Data25ns = []
##allSamples_Data25ns += [DoubleEG_Run2016B, MuonEG_Run2016B, DoubleMuon_Run2016B]#, SingleElectron_Run2016B, SingleMuon_Run2016B]
#allSamples_Data25ns += [DoubleEG_Run2016B_backup, MuonEG_Run2016B_backup, DoubleMuon_Run2016B_backup]#, SingleElectron_Run2016B_backup, SingleMuon_Run2016B_backup]
#allSamples_Data25ns += [DoubleEG_Run2016BCD_backup, MuonEG_Run2016BCD_backup, DoubleMuon_Run2016BCD_backup]#, SingleElectron_Run2016BCD_backup, SingleMuon_Run2016BCD_backup]

allSamples_Data25ns += [DoubleMuon_Run2016BCD_backup,    DoubleEG_Run2016BCD_backup,    MuonEG_Run2016BCD_backup]
allSamples_Data25ns += [DoubleMuon_Run2016BCDEFG_backup, DoubleEG_Run2016BCDEFG_backup, MuonEG_Run2016BCDEFG_backup]
allSamples_Data25ns += [DoubleMuon_Run2016_backup, DoubleEG_Run2016_backup, MuonEG_Run2016_backup]

for s in allSamples_Data25ns:
  s.color   = ROOT.kBlack
  s.isData  = True

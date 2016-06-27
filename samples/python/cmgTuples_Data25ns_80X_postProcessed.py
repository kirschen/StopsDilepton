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
    postProcessing_directory = "postProcessed_80X/dilep"

logger.info("Loading data samples from directory %s", os.path.join(data_directory, postProcessing_directory))

dirs = {}
dirs['DoubleEG']       = ["DoubleEG_Run2016B_PromptReco_v2"]
dirs['DoubleMuon']     = ["DoubleMuon_Run2016B_PromptReco_v2"]
dirs['MuonEG']         = ["MuonEG_Run2016B_PromptReco_v2"]
#dirs['SingleElectron'] = ["SingleElectron_Run2016B_PromptReco"]
#dirs['SingleMuon']     = ["SingleMuon_Run2016B_PromptReco"]

for key in dirs:
  dirs[key] = [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]]

DoubleEG_Run2016B       = Sample.fromDirectory(name="DoubleEG_Run2016B",       treeName="Events", texName="DoubleEG (Run2016B)",       directory=dirs["DoubleEG"])
DoubleMuon_Run2016B     = Sample.fromDirectory(name="DoubleMuon_Run2016B",     treeName="Events", texName="DoubleMuon (Run2016B)",     directory=dirs["DoubleMuon"])
MuonEG_Run2016B         = Sample.fromDirectory(name="MuonEG_Run2016B",         treeName="Events", texName="MuonEG (Run2016B)",         directory=dirs["MuonEG"])
#SingleElectron_Run2016B = Sample.fromDirectory(name="SingleElectron_Run2016B", treeName="Events", texName="SingleElectron (Run2016B)", directory=dirs["SingleElectron"])
#SingleMuon_Run2016B     = Sample.fromDirectory(name="SingleMuon_Run2016B",     treeName="Events", texName="SingleMuon (Run2016B)",     directory=dirs["SingleMuon"])

DoubleEG_Run2016B      .lumi = 1000*(3.997)
DoubleMuon_Run2016B    .lumi = 1000*(3.997)
MuonEG_Run2016B        .lumi = 1000*(3.997)
#SingleElectron_Run2016B.lumi =  1000*(2.165)
#SingleMuon_Run2016B    .lumi =  1000*(2.165)

allSamples_Data25ns = [DoubleEG_Run2016B, MuonEG_Run2016B, DoubleMuon_Run2016B]#, SingleElectron_Run2016B, SingleMuon_Run2016B]
for s in allSamples_Data25ns:
  s.color   = ROOT.kBlack
  s.isData  = True

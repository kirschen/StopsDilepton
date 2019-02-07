import copy, os, sys
from RootTools.core.Sample import Sample 
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

# Data directory
try:    data_directory = sys.modules['__main__'].data_directory
except: from StopsDilepton.tools.user import data_directory

# Take post processing directory if defined in main module
try:    postProcessing_directory = sys.modules['__main__'].postProcessing_directory
except: postProcessing_directory = 'stops_2018_nano_v7/dilep'

logger.info("Loading data samples from directory %s", os.path.join(data_directory, postProcessing_directory))

dirs = {}
for (run, version) in [('A',''), ('B',''), ('C',''), ('D','')]:
    runTag = 'Run2018' + run + '_17Sep2018' + version
    dirs["EGamma_Run2018"           + run + version ] = ["EGamma_"            + runTag ]
    dirs["DoubleMuon_Run2018"       + run + version ] = ["DoubleMuon_"        + runTag ]
    dirs["MuonEG_Run2018"           + run + version ] = ["MuonEG_"            + runTag ]
    dirs["SingleMuon_Run2018"       + run + version ] = ["SingleMuon_"        + runTag ]

def merge(pd, totalRunName, listOfRuns):
    dirs[pd + '_' + totalRunName] = []
    for run in listOfRuns: dirs[pd + '_' + totalRunName].extend(dirs[pd + '_' + run])

for pd in ['MuonEG', 'DoubleMuon', 'EGamma', 'SingleMuon']:
    merge(pd, 'Run2018',    ['Run2018A', 'Run2018B', 'Run2018C', 'Run2018D'])

for key in dirs:
    dirs[key] = [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]]


def getSample(pd, runName, lumi):
    sample      = Sample.fromDirectory(name=(pd + '_' + runName), treeName="Events", texName=(pd + ' (' + runName + ')'), directory=dirs[pd + '_' + runName])
    sample.lumi = lumi
    return sample

EGamma_Run2018                  = getSample('EGamma',           'Run2018',       ((59.97)*1000))
DoubleMuon_Run2018              = getSample('DoubleMuon',       'Run2018',       ((59.97)*1000))
MuonEG_Run2018                  = getSample('MuonEG',           'Run2018',       ((59.97)*1000))
SingleMuon_Run2018              = getSample('SingleMuon',       'Run2018',       ((59.97)*1000))


allSamples_Data25ns = []
allSamples_Data25ns += [MuonEG_Run2018, EGamma_Run2018, DoubleMuon_Run2018, SingleMuon_Run2018]

Run2018 = Sample.combine("Run2018", [MuonEG_Run2018, EGamma_Run2018, DoubleMuon_Run2018, SingleMuon_Run2018], texName = "Data")
Run2018.lumi = (59.97)*1000

for s in allSamples_Data25ns:
  s.color   = ROOT.kBlack
  s.isData  = True



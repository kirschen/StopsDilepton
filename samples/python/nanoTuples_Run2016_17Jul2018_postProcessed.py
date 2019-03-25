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
except: postProcessing_directory = 'stops_2016_nano_v2/dilep'

logger.info("Loading data samples from directory %s", os.path.join(data_directory, postProcessing_directory))

dirs = {}
for (run, version) in [('B','_ver2'),('C',''),('D',''),('E',''),('F',''),('G',''),('H','')]: # no event that passes json in B_ver1
    runTag = 'Run2016' + run + '_17Jul2018' + version
    dirs["DoubleEG_Run2016"         + run + version ] = ["DoubleEG_"          + runTag ]
    dirs["DoubleMuon_Run2016"       + run + version ] = ["DoubleMuon_"        + runTag ]
    #dirs["SingleElectron_Run2016"   + run + version ] = ["SingleElectron_"    + runTag ]
    #dirs["SingleMuon_Run2016"       + run + version ] = ["SingleMuon_"        + runTag ]
    dirs["MuonEG_Run2016"           + run + version ] = ["MuonEG_"            + runTag ]

def merge(pd, totalRunName, listOfRuns):
    dirs[pd + '_' + totalRunName] = []
    for run in listOfRuns: dirs[pd + '_' + totalRunName].extend(dirs[pd + '_' + run])

for pd in ['MuonEG', 'DoubleMuon', 'DoubleEG']:
    merge(pd, 'Run2016BCD',    ['Run2016B_ver2', 'Run2016C', 'Run2016D'])
    merge(pd, 'Run2016BCDEFG', ['Run2016BCD', 'Run2016E', 'Run2016F', 'Run2016G'])
    merge(pd, 'Run2016',       ['Run2016BCDEFG', 'Run2016H'])

for key in dirs:
    dirs[key] = [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]]


def getSample(pd, runName, lumi):
    sample      = Sample.fromDirectory(name=(pd + '_' + runName), treeName="Events", texName=(pd + ' (' + runName + ')'), directory=dirs[pd + '_' + runName])
    sample.lumi = lumi
    return sample

DoubleEG_Run2016                = getSample('DoubleEG',         'Run2016',       (35.9)*1000)
DoubleMuon_Run2016              = getSample('DoubleMuon',       'Run2016',       (35.9)*1000)
#SingleElectron_Run2016          = getSample('SingleElectron',   'Run2016',      (35.9)*1000)
#SingleMuon_Run2016              = getSample('SingleMuon',       'Run2016',      (35.9)*1000)
MuonEG_Run2016                  = getSample('MuonEG',           'Run2016',       (35.9)*1000)

allSamples_Data25ns = []
allSamples_Data25ns += [MuonEG_Run2016, DoubleEG_Run2016, DoubleMuon_Run2016]

Run2016 = Sample.combine("Run2016", [MuonEG_Run2016, DoubleEG_Run2016, DoubleMuon_Run2016], texName = "Data")
Run2016.lumi = (35.9)*1000

for s in allSamples_Data25ns:
  s.color   = ROOT.kBlack
  s.isData  = True



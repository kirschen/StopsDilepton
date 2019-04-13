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
except: postProcessing_directory = 'stops_2017_nano_v2/dilep'

logger.info("Loading data samples from directory %s", os.path.join(data_directory, postProcessing_directory))

dirs = {}
for (run, version) in [('B',''),('C',''),('D',''),('E',''),('F','')]:
    runTag = 'Run2017' + run + '_31Mar2018' + version
    dirs["DoubleEG_Run2017"         + run + version ] = ["DoubleEG_"          + runTag ]
    dirs["DoubleMuon_Run2017"       + run + version ] = ["DoubleMuon_"        + runTag ]
    dirs["MuonEG_Run2017"           + run + version ] = ["MuonEG_"            + runTag ]
    dirs["SingleMuon_Run2017"       + run + version ] = ["SingleMuon_"        + runTag ]
    dirs["SingleElectron_Run2017"   + run + version ] = ["SingleElectron_"    + runTag ]

def merge(pd, totalRunName, listOfRuns):
    dirs[pd + '_' + totalRunName] = []
    for run in listOfRuns: dirs[pd + '_' + totalRunName].extend(dirs[pd + '_' + run])

for pd in ['MuonEG', 'DoubleMuon', 'DoubleEG', 'SingleElectron', 'SingleMuon']:
    merge(pd, 'Run2017',    ['Run2017B', 'Run2017C', 'Run2017D', 'Run2017E', 'Run2017F'])
    merge(pd, 'Run2017CDE', ['Run2017C', 'Run2017D', 'Run2017E'])

for key in dirs:
    dirs[key] = [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]]

def getSample(pd, runName, lumi):
    sample      = Sample.fromDirectory(name=(pd + '_' + runName), treeName="Events", texName=(pd + ' (' + runName + ')'), directory=dirs[pd + '_' + runName])
    sample.lumi = lumi
    return sample

DoubleEG_Run2017                = getSample('DoubleEG',         'Run2017',       (41.9)*1000)
DoubleEG_Run2017B               = getSample('DoubleEG',         'Run2017B',       (41.9)*1000)
DoubleEG_Run2017CDE             = getSample('DoubleEG',         'Run2017CDE',       (41.9)*1000)
DoubleEG_Run2017F               = getSample('DoubleEG',         'Run2017F',       (41.9)*1000)

DoubleMuon_Run2017              = getSample('DoubleMuon',       'Run2017',       (41.9)*1000)
DoubleMuon_Run2017B             = getSample('DoubleMuon',       'Run2017B',       (41.9)*1000)
DoubleMuon_Run2017CDE           = getSample('DoubleMuon',       'Run2017CDE',       (41.9)*1000)
DoubleMuon_Run2017F             = getSample('DoubleMuon',       'Run2017F',       (41.9)*1000)

MuonEG_Run2017                  = getSample('MuonEG',           'Run2017',       (41.9)*1000)
MuonEG_Run2017B                 = getSample('MuonEG',           'Run2017B',       (41.9)*1000)
MuonEG_Run2017CDE               = getSample('MuonEG',           'Run2017CDE',       (41.9)*1000)
MuonEG_Run2017F                 = getSample('MuonEG',           'Run2017F',       (41.9)*1000)

SingleMuon_Run2017              = getSample('SingleMuon',       'Run2017',       (41.9)*1000)
SingleMuon_Run2017B             = getSample('SingleMuon',       'Run2017B',       (41.9)*1000)
SingleMuon_Run2017CDE           = getSample('SingleMuon',       'Run2017CDE',       (41.9)*1000)
SingleMuon_Run2017F             = getSample('SingleMuon',       'Run2017F',       (41.9)*1000)

SingleElectron_Run2017          = getSample('SingleElectron',   'Run2017',       (41.9)*1000)
SingleElectron_Run2017B         = getSample('SingleElectron',   'Run2017B',       (41.9)*1000)
SingleElectron_Run2017CDE       = getSample('SingleElectron',   'Run2017CDE',       (41.9)*1000)
SingleElectron_Run2017F         = getSample('SingleElectron',   'Run2017F',       (41.9)*1000)


allSamples_Data25ns = []
allSamples_Data25ns += [MuonEG_Run2017, DoubleEG_Run2017, DoubleMuon_Run2017, SingleElectron_Run2017, SingleMuon_Run2017]

Run2017 = Sample.combine("Run2017", [MuonEG_Run2017, DoubleEG_Run2017, DoubleMuon_Run2017, SingleMuon_Run2017, SingleMuon_Run2017], texName = "Data")
Run2017B = Sample.combine("Run2017", [MuonEG_Run2017B, DoubleEG_Run2017B, DoubleMuon_Run2017B, SingleElectron_Run2017B, SingleMuon_Run2017B], texName = "Data")
Run2017CDE = Sample.combine("Run2017", [MuonEG_Run2017CDE, DoubleEG_Run2017CDE, DoubleMuon_Run2017CDE, SingleElectron_Run2017CDE, SingleMuon_Run2017CDE], texName = "Data")
Run2017F = Sample.combine("Run2017", [MuonEG_Run2017F, DoubleEG_Run2017F, DoubleMuon_Run2017F, SingleElectron_Run2017F, SingleMuon_Run2017F], texName = "Data")

Run2017.lumi = (41.9)*1000

allSamples_Data25ns += [Run2017, Run2017B, Run2017CDE, Run2017F]

for s in allSamples_Data25ns:
  s.color   = ROOT.kBlack
  s.isData  = True



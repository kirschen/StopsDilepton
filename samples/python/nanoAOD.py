from RootTools.core.standard import *
from RootTools.fwlite.FWLiteSample import *

hephy = 'root://hephyse.oeaw.ac.at//dpm/oeaw.ac.at/home/cms/'
cache = "/afs/hephy.at/data/dspitzbart01/StopsDilepton/nanoCache.sql"

sampleMap = {}

sampleMap['DoubleMuon_Run2016B_05Feb2018_ver1']  = Sample.fromFiles("DoubleMuon_Run2016B_05Feb2018_ver1",    FWLiteSample.fromDAS("DoubleMuon_Run2016B_05Feb2018_ver1", "/DoubleMuon/Run2016B-05Feb2018_ver1-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016B_05Feb2018_ver2']  = Sample.fromFiles("DoubleMuon_Run2016B_05Feb2018_ver2",    FWLiteSample.fromDAS("DoubleMuon_Run2016B_05Feb2018_ver2", "/DoubleMuon/Run2016B-05Feb2018_ver2-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016C_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016C_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016C_05Feb2018", "/DoubleMuon/Run2016C-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016D_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016D_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016D_05Feb2018", "/DoubleMuon/Run2016D-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016E_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016E_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016E_05Feb2018", "/DoubleMuon/Run2016E-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016F_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016F_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016F_05Feb2018", "/DoubleMuon/Run2016F-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016G_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016G_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016G_05Feb2018", "/DoubleMuon/Run2016G-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016H_05Feb2018_ver2']  = Sample.fromFiles("DoubleMuon_Run2016H_05Feb2018_ver2",    FWLiteSample.fromDAS("DoubleMuon_Run2016H_05Feb2018_ver2", "/DoubleMuon/Run2016H-05Feb2018_ver2-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016H_05Feb2018_ver3']  = Sample.fromFiles("DoubleMuon_Run2016H_05Feb2018_ver3",    FWLiteSample.fromDAS("DoubleMuon_Run2016H_05Feb2018_ver3", "/DoubleMuon/Run2016H-05Feb2018_ver3-v1/NANOAOD", prefix = hephy, dbFile=cache).files)

#DoubleMuon_Run2016 = [DoubleMuon_Run2016B_05Feb2018_ver1,DoubleMuon_Run2016B_05Feb2018_ver2,DoubleMuon_Run2016C_05Feb2018,DoubleMuon_Run2016D_05Feb2018,DoubleMuon_Run2016E_05Feb2018,DoubleMuon_Run2016F_05Feb2018,DoubleMuon_Run2016G_05Feb2018,DoubleMuon_Run2016H_05Feb2018_ver2,DoubleMuon_Run2016H_05Feb2018_ver3]

for s in sampleMap.keys():
    sampleMap[s].isData = True


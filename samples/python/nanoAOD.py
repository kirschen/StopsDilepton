from RootTools.core.standard import *
from RootTools.fwlite.FWLiteSample import *

hephy = 'root://hephyse.oeaw.ac.at//dpm/oeaw.ac.at/home/cms/'
cache = "/afs/hephy.at/data/dspitzbart01/StopsDilepton/nanoCache.sql"

sampleMap = {}

## 2016 ##

sampleMap['DoubleMuon_Run2016B_05Feb2018_ver1']  = Sample.fromFiles("DoubleMuon_Run2016B_05Feb2018_ver1",    FWLiteSample.fromDAS("DoubleMuon_Run2016B_05Feb2018_ver1", "/DoubleMuon/Run2016B-05Feb2018_ver1-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016B_05Feb2018_ver2']  = Sample.fromFiles("DoubleMuon_Run2016B_05Feb2018_ver2",    FWLiteSample.fromDAS("DoubleMuon_Run2016B_05Feb2018_ver2", "/DoubleMuon/Run2016B-05Feb2018_ver2-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016C_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016C_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016C_05Feb2018",      "/DoubleMuon/Run2016C-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016D_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016D_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016D_05Feb2018",      "/DoubleMuon/Run2016D-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016E_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016E_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016E_05Feb2018",      "/DoubleMuon/Run2016E-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016F_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016F_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016F_05Feb2018",      "/DoubleMuon/Run2016F-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016G_05Feb2018']       = Sample.fromFiles("DoubleMuon_Run2016G_05Feb2018",         FWLiteSample.fromDAS("DoubleMuon_Run2016G_05Feb2018",      "/DoubleMuon/Run2016G-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016H_05Feb2018_ver2']  = Sample.fromFiles("DoubleMuon_Run2016H_05Feb2018_ver2",    FWLiteSample.fromDAS("DoubleMuon_Run2016H_05Feb2018_ver2", "/DoubleMuon/Run2016H-05Feb2018_ver2-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2016H_05Feb2018_ver3']  = Sample.fromFiles("DoubleMuon_Run2016H_05Feb2018_ver3",    FWLiteSample.fromDAS("DoubleMuon_Run2016H_05Feb2018_ver3", "/DoubleMuon/Run2016H-05Feb2018_ver3-v1/NANOAOD", prefix = hephy, dbFile=cache).files)

sampleMap['MuonEG_Run2016B_05Feb2018_ver1']  = Sample.fromFiles("MuonEG_Run2016B_05Feb2018_ver1",    FWLiteSample.fromDAS("MuonEG_Run2016B_05Feb2018_ver1", "/MuonEG/Run2016B-05Feb2018_ver1-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2016B_05Feb2018_ver2']  = Sample.fromFiles("MuonEG_Run2016B_05Feb2018_ver2",    FWLiteSample.fromDAS("MuonEG_Run2016B_05Feb2018_ver2", "/MuonEG/Run2016B-05Feb2018_ver2-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2016C_05Feb2018']       = Sample.fromFiles("MuonEG_Run2016C_05Feb2018",         FWLiteSample.fromDAS("MuonEG_Run2016C_05Feb2018",      "/MuonEG/Run2016C-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2016D_05Feb2018']       = Sample.fromFiles("MuonEG_Run2016D_05Feb2018",         FWLiteSample.fromDAS("MuonEG_Run2016D_05Feb2018",      "/MuonEG/Run2016D-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2016E_05Feb2018']       = Sample.fromFiles("MuonEG_Run2016E_05Feb2018",         FWLiteSample.fromDAS("MuonEG_Run2016E_05Feb2018",      "/MuonEG/Run2016E-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2016F_05Feb2018']       = Sample.fromFiles("MuonEG_Run2016F_05Feb2018",         FWLiteSample.fromDAS("MuonEG_Run2016F_05Feb2018",      "/MuonEG/Run2016F-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2016G_05Feb2018']       = Sample.fromFiles("MuonEG_Run2016G_05Feb2018",         FWLiteSample.fromDAS("MuonEG_Run2016G_05Feb2018",      "/MuonEG/Run2016G-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2016H_05Feb2018_ver2']  = Sample.fromFiles("MuonEG_Run2016H_05Feb2018_ver2",    FWLiteSample.fromDAS("MuonEG_Run2016H_05Feb2018_ver2", "/MuonEG/Run2016H-05Feb2018_ver2-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2016H_05Feb2018_ver3']  = Sample.fromFiles("MuonEG_Run2016H_05Feb2018_ver3",    FWLiteSample.fromDAS("MuonEG_Run2016H_05Feb2018_ver3", "/MuonEG/Run2016H-05Feb2018_ver3-v1/NANOAOD", prefix = hephy, dbFile=cache).files)

sampleMap['DoubleEG_Run2016B_05Feb2018_ver1']  = Sample.fromFiles("DoubleEG_Run2016B_05Feb2018_ver1",    FWLiteSample.fromDAS("DoubleEG_Run2016B_05Feb2018_ver1", "/DoubleEG/Run2016B-05Feb2018_ver1-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2016B_05Feb2018_ver2']  = Sample.fromFiles("DoubleEG_Run2016B_05Feb2018_ver2",    FWLiteSample.fromDAS("DoubleEG_Run2016B_05Feb2018_ver2", "/DoubleEG/Run2016B-05Feb2018_ver2-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2016C_05Feb2018']       = Sample.fromFiles("DoubleEG_Run2016C_05Feb2018",         FWLiteSample.fromDAS("DoubleEG_Run2016C_05Feb2018",      "/DoubleEG/Run2016C-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2016D_05Feb2018']       = Sample.fromFiles("DoubleEG_Run2016D_05Feb2018",         FWLiteSample.fromDAS("DoubleEG_Run2016D_05Feb2018",      "/DoubleEG/Run2016D-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2016E_05Feb2018']       = Sample.fromFiles("DoubleEG_Run2016E_05Feb2018",         FWLiteSample.fromDAS("DoubleEG_Run2016E_05Feb2018",      "/DoubleEG/Run2016E-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2016F_05Feb2018']       = Sample.fromFiles("DoubleEG_Run2016F_05Feb2018",         FWLiteSample.fromDAS("DoubleEG_Run2016F_05Feb2018",      "/DoubleEG/Run2016F-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2016G_05Feb2018']       = Sample.fromFiles("DoubleEG_Run2016G_05Feb2018",         FWLiteSample.fromDAS("DoubleEG_Run2016G_05Feb2018",      "/DoubleEG/Run2016G-05Feb2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2016H_05Feb2018_ver2']  = Sample.fromFiles("DoubleEG_Run2016H_05Feb2018_ver2",    FWLiteSample.fromDAS("DoubleEG_Run2016H_05Feb2018_ver2", "/DoubleEG/Run2016H-05Feb2018_ver2-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2016H_05Feb2018_ver3']  = Sample.fromFiles("DoubleEG_Run2016H_05Feb2018_ver3",    FWLiteSample.fromDAS("DoubleEG_Run2016H_05Feb2018_ver3", "/DoubleEG/Run2016H-05Feb2018_ver3-v1/NANOAOD", prefix = hephy, dbFile=cache).files)

## 2017 ##

sampleMap['DoubleMuon_Run2017B_31Mar2018']  = Sample.fromFiles("DoubleMuon_Run2017B_31Mar2018", FWLiteSample.fromDAS("DoubleMuon_Run2017B_31Mar2018",   "/DoubleMuon/Run2017B-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2017C_31Mar2018']  = Sample.fromFiles("DoubleMuon_Run2017C_31Mar2018", FWLiteSample.fromDAS("DoubleMuon_Run2017C_31Mar2018",   "/DoubleMuon/Run2017C-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2017D_31Mar2018']  = Sample.fromFiles("DoubleMuon_Run2017D_31Mar2018", FWLiteSample.fromDAS("DoubleMuon_Run2017D_31Mar2018",   "/DoubleMuon/Run2017D-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
#sampleMap['DoubleMuon_Run2017E_31Mar2018']  = Sample.fromFiles("DoubleMuon_Run2017E_31Mar2018", FWLiteSample.fromDAS("DoubleMuon_Run2017E_31Mar2018",   "/DoubleMuon/Run2017E-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleMuon_Run2017F_31Mar2018']  = Sample.fromFiles("DoubleMuon_Run2017F_31Mar2018", FWLiteSample.fromDAS("DoubleMuon_Run2017F_31Mar2018",   "/DoubleMuon/Run2017F-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)

sampleMap['MuonEG_Run2017B_31Mar2018']  = Sample.fromFiles("MuonEG_Run2017B_31Mar2018", FWLiteSample.fromDAS("MuonEG_Run2017B_31Mar2018",   "/MuonEG/Run2017B-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2017C_31Mar2018']  = Sample.fromFiles("MuonEG_Run2017C_31Mar2018", FWLiteSample.fromDAS("MuonEG_Run2017C_31Mar2018",   "/MuonEG/Run2017C-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2017D_31Mar2018']  = Sample.fromFiles("MuonEG_Run2017D_31Mar2018", FWLiteSample.fromDAS("MuonEG_Run2017D_31Mar2018",   "/MuonEG/Run2017D-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2017E_31Mar2018']  = Sample.fromFiles("MuonEG_Run2017E_31Mar2018", FWLiteSample.fromDAS("MuonEG_Run2017E_31Mar2018",   "/MuonEG/Run2017E-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['MuonEG_Run2017F_31Mar2018']  = Sample.fromFiles("MuonEG_Run2017F_31Mar2018", FWLiteSample.fromDAS("MuonEG_Run2017F_31Mar2018",   "/MuonEG/Run2017F-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)

sampleMap['DoubleEG_Run2017B_31Mar2018']  = Sample.fromFiles("DoubleEG_Run2017B_31Mar2018", FWLiteSample.fromDAS("DoubleEG_Run2017B_31Mar2018",   "/DoubleEG/Run2017B-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2017C_31Mar2018']  = Sample.fromFiles("DoubleEG_Run2017C_31Mar2018", FWLiteSample.fromDAS("DoubleEG_Run2017C_31Mar2018",   "/DoubleEG/Run2017C-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2017D_31Mar2018']  = Sample.fromFiles("DoubleEG_Run2017D_31Mar2018", FWLiteSample.fromDAS("DoubleEG_Run2017D_31Mar2018",   "/DoubleEG/Run2017D-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2017E_31Mar2018']  = Sample.fromFiles("DoubleEG_Run2017E_31Mar2018", FWLiteSample.fromDAS("DoubleEG_Run2017E_31Mar2018",   "/DoubleEG/Run2017E-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)
sampleMap['DoubleEG_Run2017F_31Mar2018']  = Sample.fromFiles("DoubleEG_Run2017F_31Mar2018", FWLiteSample.fromDAS("DoubleEG_Run2017F_31Mar2018",   "/DoubleEG/Run2017F-31Mar2018-v1/NANOAOD", prefix = hephy, dbFile=cache).files)

## 2018 ##


#DoubleMuon_Run2016 = [DoubleMuon_Run2016B_05Feb2018_ver1,DoubleMuon_Run2016B_05Feb2018_ver2,DoubleMuon_Run2016C_05Feb2018,DoubleMuon_Run2016D_05Feb2018,DoubleMuon_Run2016E_05Feb2018,DoubleMuon_Run2016F_05Feb2018,DoubleMuon_Run2016G_05Feb2018,DoubleMuon_Run2016H_05Feb2018_ver2,DoubleMuon_Run2016H_05Feb2018_ver3]

for s in sampleMap.keys():
    sampleMap[s].isData = True


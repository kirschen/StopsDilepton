from RootTools.core.standard import *
from RootTools.fwlite.FWLiteSample import *

# Logging
import logging
logger = logging.getLogger(__name__)

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

baseDir = "/dpm/oeaw.ac.at/home/cms/store/user/dspitzba/nanoAOD/2018_v3/"

sampleMap['DoubleMuon_Run2018A_PromptReco_v1']  = Sample.fromDPMDirectory("DoubleMuon_Run2018A_PromptReco_v1",  baseDir+"DoubleMuon/crab_Run2018A-PromptReco-v1_2018_v3/180607_150517/0000")
sampleMap['DoubleMuon_Run2018A_PromptReco_v2']  = Sample.fromDPMDirectory("DoubleMuon_Run2018A_PromptReco_v2",  baseDir+"DoubleMuon/crab_Run2018A-PromptReco-v2_2018_v3/180607_150537/0000")
sampleMap['DoubleMuon_Run2018A_PromptReco_v3']  = Sample.fromDPMDirectory("DoubleMuon_Run2018A_PromptReco_v3",  baseDir+"DoubleMuon/crab_Run2018A-PromptReco-v3_2018_v3/180607_150559/0000")

sampleMap['DoubleMuon_Run2018B_PromptReco_v1']  = Sample.fromDPMDirectory("DoubleMuon_Run2018B_PromptReco_v1",  baseDir+"DoubleMuon/crab_Run2018B-PromptReco-v1_2018_v3/180712_081910/0000")
sampleMap['DoubleMuon_Run2018B_PromptReco_v2']  = Sample.fromDPMDirectory("DoubleMuon_Run2018B_PromptReco_v2",  baseDir+"DoubleMuon/crab_Run2018B-PromptReco-v2_2018_v3/180712_081933/0000")
sampleMap['DoubleMuon_Run2018C_PromptReco_v1']  = Sample.fromDPMDirectory("DoubleMuon_Run2018C_PromptReco_v1",  baseDir+"DoubleMuon/crab_Run2018C-PromptReco-v1_2018_v3/180712_081954/0000")


sampleMap['MuonEG_Run2018A_PromptReco_v1']      = Sample.fromDPMDirectory("MuonEG_Run2018A_PromptReco_v1",      baseDir+"MuonEG/crab_Run2018A-PromptReco-v1_2018_v3/180607_150722/0000")
sampleMap['MuonEG_Run2018A_PromptReco_v2']      = Sample.fromDPMDirectory("MuonEG_Run2018A_PromptReco_v2",      baseDir+"MuonEG/crab_Run2018A-PromptReco-v2_2018_v3/180607_150742/0000")
sampleMap['MuonEG_Run2018A_PromptReco_v3']      = Sample.fromDPMDirectory("MuonEG_Run2018A_PromptReco_v3",      baseDir+"MuonEG/crab_Run2018A-PromptReco-v3_2018_v3/180607_150803/0000")

sampleMap['EGamma_Run2018A_PromptReco_v1']      = Sample.fromDPMDirectory("EGamma_Run2018A_PromptReco_v1",      baseDir+"EGamma/crab_Run2018A-PromptReco-v1_2018_v3/180607_150620/0000")
sampleMap['EGamma_Run2018A_PromptReco_v2']      = Sample.fromDPMDirectory("EGamma_Run2018A_PromptReco_v2",      baseDir+"EGamma/crab_Run2018A-PromptReco-v2_2018_v3/180607_150640/0000")
sampleMap['EGamma_Run2018A_PromptReco_v3']      = Sample.fromDPMDirectory("EGamma_Run2018A_PromptReco_v3",      baseDir+"EGamma/crab_Run2018A-PromptReco-v3_2018_v3/180607_150701/0000")

# HEM RelVals

baseDir = "/dpm/oeaw.ac.at/home/cms/store/user/dspitzba/nanoAOD/2018_v4/"

sampleMap['DoubleMuon_Run2018B_Prompt_HEmiss_v1_RelVal']    = Sample.fromDPMDirectory("DoubleMuon_Run2018B_Prompt_HEmiss_v1_RelVal", baseDir+"DoubleMuon/crab_CMSSW_10_1_7-101X_dataRun2_Prompt_HEmiss_v1_RelVal_doubMu2018B-v1_2018_v4/180713_094017/0000")
sampleMap['DoubleMuon_Run2018B_Prompt_v11_RelVal']          = Sample.fromDPMDirectory("DoubleMuon_Run2018B_Prompt_v11_RelVal",       baseDir+"DoubleMuon/crab_CMSSW_10_1_7-101X_dataRun2_Prompt_v11_RelVal_doubMu2018B-v1_2018_v4/180713_093957/0000")


#DoubleMuon_Run2016 = [DoubleMuon_Run2016B_05Feb2018_ver1,DoubleMuon_Run2016B_05Feb2018_ver2,DoubleMuon_Run2016C_05Feb2018,DoubleMuon_Run2016D_05Feb2018,DoubleMuon_Run2016E_05Feb2018,DoubleMuon_Run2016F_05Feb2018,DoubleMuon_Run2016G_05Feb2018,DoubleMuon_Run2016H_05Feb2018_ver2,DoubleMuon_Run2016H_05Feb2018_ver3]

for s in sampleMap.keys():
    sampleMap[s].isData = True


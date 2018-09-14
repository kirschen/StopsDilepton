import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT


## these should go somewhere else
dbFile = '/afs/hephy.at/data/dspitzbart01/nanoAOD/DB_Run2018.sql'

# specify a local directory if you want to create (and afterwards automatically use) a local copy of the sample, otherwise use the grid.

## DoubleMuon
DoubleMuon_Run2018A_PromptReco_v1  = Sample.nanoAODfromDAS('DoubleMuon_Run2018A_PromptReco_v1',   '/DoubleMuon/dspitzba-crab_Run2018A-PromptReco-v1_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
DoubleMuon_Run2018A_PromptReco_v2  = Sample.nanoAODfromDAS('DoubleMuon_Run2018A_PromptReco_v2',   '/DoubleMuon/dspitzba-crab_Run2018A-PromptReco-v2_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
DoubleMuon_Run2018A_PromptReco_v3  = Sample.nanoAODfromDAS('DoubleMuon_Run2018A_PromptReco_v3',   '/DoubleMuon/dspitzba-crab_Run2018A-PromptReco-v3_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
DoubleMuon_Run2018B_PromptReco_v1  = Sample.nanoAODfromDAS('DoubleMuon_Run2018B_PromptReco_v1',   '/DoubleMuon/dspitzba-crab_Run2018B-PromptReco-v1_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
DoubleMuon_Run2018B_PromptReco_v2  = Sample.nanoAODfromDAS('DoubleMuon_Run2018B_PromptReco_v2',   '/DoubleMuon/dspitzba-crab_Run2018B-PromptReco-v2_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
DoubleMuon_Run2018C_PromptReco_v1  = Sample.nanoAODfromDAS('DoubleMuon_Run2018C_PromptReco_v1',   '/DoubleMuon/dspitzba-crab_Run2018C-PromptReco-v1_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
DoubleMuon_Run2018C_PromptReco_v2  = Sample.nanoAODfromDAS('DoubleMuon_Run2018C_PromptReco_v2',   '/DoubleMuon/dspitzba-crab_Run2018C-PromptReco-v2_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
DoubleMuon_Run2018C_PromptReco_v3  = Sample.nanoAODfromDAS('DoubleMuon_Run2018C_PromptReco_v3',   '/DoubleMuon/dspitzba-crab_Run2018C-PromptReco-v3_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')

DoubleMuon_Run2018 = [\
    DoubleMuon_Run2018A_PromptReco_v1,
    DoubleMuon_Run2018A_PromptReco_v2,
    DoubleMuon_Run2018A_PromptReco_v3,
    DoubleMuon_Run2018B_PromptReco_v1,
    DoubleMuon_Run2018B_PromptReco_v2,
    DoubleMuon_Run2018C_PromptReco_v1,
    DoubleMuon_Run2018C_PromptReco_v2,
    DoubleMuon_Run2018C_PromptReco_v3,
    ]

### MuonEG
MuonEG_Run2018A_PromptReco_v1  = Sample.nanoAODfromDAS('MuonEG_Run2018A_PromptReco_v1',   '/MuonEG/dspitzba-crab_Run2018A-PromptReco-v1_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
MuonEG_Run2018A_PromptReco_v2  = Sample.nanoAODfromDAS('MuonEG_Run2018A_PromptReco_v2',   '/MuonEG/dspitzba-crab_Run2018A-PromptReco-v2_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
MuonEG_Run2018A_PromptReco_v3  = Sample.nanoAODfromDAS('MuonEG_Run2018A_PromptReco_v3',   '/MuonEG/dspitzba-crab_Run2018A-PromptReco-v3_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
MuonEG_Run2018B_PromptReco_v1  = Sample.nanoAODfromDAS('MuonEG_Run2018B_PromptReco_v1',   '/MuonEG/dspitzba-crab_Run2018B-PromptReco-v1_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
MuonEG_Run2018B_PromptReco_v2  = Sample.nanoAODfromDAS('MuonEG_Run2018B_PromptReco_v2',   '/MuonEG/dspitzba-crab_Run2018B-PromptReco-v2_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
MuonEG_Run2018C_PromptReco_v1  = Sample.nanoAODfromDAS('MuonEG_Run2018C_PromptReco_v1',   '/MuonEG/dspitzba-crab_Run2018C-PromptReco-v1_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
MuonEG_Run2018C_PromptReco_v2  = Sample.nanoAODfromDAS('MuonEG_Run2018C_PromptReco_v2',   '/MuonEG/dspitzba-crab_Run2018C-PromptReco-v2_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
MuonEG_Run2018C_PromptReco_v3  = Sample.nanoAODfromDAS('MuonEG_Run2018C_PromptReco_v3',   '/MuonEG/dspitzba-crab_Run2018C-PromptReco-v3_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')

MuonEG_Run2018 = [\
    MuonEG_Run2018A_PromptReco_v1,
    MuonEG_Run2018A_PromptReco_v2,
    MuonEG_Run2018A_PromptReco_v3,
    MuonEG_Run2018B_PromptReco_v1,
    MuonEG_Run2018B_PromptReco_v2,
    MuonEG_Run2018C_PromptReco_v1,
    MuonEG_Run2018C_PromptReco_v2,
    MuonEG_Run2018C_PromptReco_v3,
    ]

### DoubleEG
EGamma_Run2018A_PromptReco_v1  = Sample.nanoAODfromDAS('EGamma_Run2018A_PromptReco_v1',   '/EGamma/dspitzba-crab_Run2018A-PromptReco-v1_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
EGamma_Run2018A_PromptReco_v2  = Sample.nanoAODfromDAS('EGamma_Run2018A_PromptReco_v2',   '/EGamma/dspitzba-crab_Run2018A-PromptReco-v2_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
EGamma_Run2018A_PromptReco_v3  = Sample.nanoAODfromDAS('EGamma_Run2018A_PromptReco_v3',   '/EGamma/dspitzba-crab_Run2018A-PromptReco-v3_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
EGamma_Run2018B_PromptReco_v1  = Sample.nanoAODfromDAS('EGamma_Run2018B_PromptReco_v1',   '/EGamma/dspitzba-crab_Run2018B-PromptReco-v1_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
EGamma_Run2018B_PromptReco_v2  = Sample.nanoAODfromDAS('EGamma_Run2018B_PromptReco_v2',   '/EGamma/dspitzba-crab_Run2018B-PromptReco-v2_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
EGamma_Run2018C_PromptReco_v1  = Sample.nanoAODfromDAS('EGamma_Run2018C_PromptReco_v1',   '/EGamma/dspitzba-crab_Run2018C-PromptReco-v1_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
EGamma_Run2018C_PromptReco_v2  = Sample.nanoAODfromDAS('EGamma_Run2018C_PromptReco_v2',   '/EGamma/dspitzba-crab_Run2018C-PromptReco-v2_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')
EGamma_Run2018C_PromptReco_v3  = Sample.nanoAODfromDAS('EGamma_Run2018C_PromptReco_v3',   '/EGamma/dspitzba-crab_Run2018C-PromptReco-v3_2018_v4-0b0a778885ba11c3c06e0633f7ebaf56/USER', dbFile=dbFile, instance='phys03')

EGamma_Run2018 = [\
    EGamma_Run2018A_PromptReco_v1,
    EGamma_Run2018A_PromptReco_v2,
    EGamma_Run2018A_PromptReco_v3,
    EGamma_Run2018B_PromptReco_v1,
    EGamma_Run2018B_PromptReco_v2,
    EGamma_Run2018C_PromptReco_v1,
    EGamma_Run2018C_PromptReco_v2,
    EGamma_Run2018C_PromptReco_v3,
    ]

    
allSamples = DoubleMuon_Run2018 + MuonEG_Run2018 + EGamma_Run2018

for s in allSamples:
    s.isData = True


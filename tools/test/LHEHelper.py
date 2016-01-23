import FWCore.ParameterSet.Config as cms
process = cms.Process("test")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10) )
process.source = cms.Source(
    'PoolSource',
#    fileNames = cms.untracked.vstring('root://eoscms.cern.ch//store/mc/RunIISpring15DR74/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/Asympt50ns_MCRUN2_74_V9A-v2/60000/001C7571-0511-E511-9B8E-549F35AE4FAF.root')
    fileNames = cms.untracked.vstring('root://xrootd.unl.edu//store/mc/RunIISpring15DR74/TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/Asympt25ns_MCRUN2_74_V9-v2/20000/5E2A0DB9-E52F-E511-A294-782BCB407B74.root')
    )

# Load the standard set of configuration modules
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

#from Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff import *
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag

#  process.GlobalTag.globaltag = '74X_dataRun2_Prompt_v1'
process.GlobalTag.globaltag = 'MCRUN2_74_V9'
process.load('LHEHelper_cff')
#process.out = cms.OutputModule("PoolOutputModule",
#     #verbose = cms.untracked.bool(True),
#     fileName = cms.untracked.string('histo.root'),
#     outputCommands = cms.untracked.vstring('drop *', 'keep *_*PFCandTupelizer*_*_*', 'keep *_*CaloTowersTupelizer*_*_*')
#)


#
# RUN!
#
process.p = cms.Path(
  process.LHEHelper
#  process.CaloTowersTupelizer
)


#process.outpath = cms.EndPath(process.out)


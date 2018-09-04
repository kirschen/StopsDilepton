from RootTools.core.standard import *
from RootTools.fwlite.FWLiteSample import *

# Logging
import logging
logger = logging.getLogger(__name__)

hephy = 'root://hephyse.oeaw.ac.at//dpm/oeaw.ac.at/home/cms/'
dbFile = '/afs/hephy.at/data/dspitzbart01/nanoAOD/DB_FastSim_Spring16_v2.sql'
baseDir = "/dpm/oeaw.ac.at/home/cms/store/user/dspitzba/nanoAOD/"

SMS_T2tt_mStop_400to1200 = Sample.fromDPMDirectory("SMS_T2tt_mStop_400to1200",  baseDir+"80X_FS_v1/SMS-T2tt_mStop-400to1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_RunIISpring16MiniAODv2-PUSpring16Fast_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1_80X_FS_v1/180815_193944/0000")

SMS_T8bbllnunu_XCha0p5_XSlep0p05    = Sample.nanoAODfromDAS("SMS_T8bbllnunu_XCha0p5_XSlep0p05", "/SMS-T8bbllnunu_XCha0p5_XSlep0p05_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/dspitzba-crab_RunIISummer16MiniAODv2-PUSummer16Fast_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1_80X_FS_v1-19989c43757f6bd6f30d3a68ea9b6591/USER", instance = 'phys03', dbFile=dbFile, xSection=1 )

SMS_T8bbllnunu_XCha0p5_XSlep0p5     = Sample.nanoAODfromDAS("SMS_T8bbllnunu_XCha0p5_XSlep0p5", "/SMS-T8bbllnunu_XCha0p5_XSlep0p5_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/dspitzba-crab_RunIISummer16MiniAODv2-PUSummer16Fast_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1_80X_FS_v1-19989c43757f6bd6f30d3a68ea9b6591/USER", instance = 'phys03', dbFile=dbFile, xSection=1 )
SMS_T8bbllnunu_XCha0p5_XSlep0p5_mN1_700_1000 = Sample.nanoAODfromDAS("SMS_T8bbllnunu_XCha0p5_XSlep0p5_mN1_700_1000", "/SMS-T8bbllnunu_XCha0p5_XSlep0p5_mN1_700_1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/dspitzba-crab_RunIISummer16MiniAODv2-PUSummer16Fast_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1_80X_FS_v1-19989c43757f6bd6f30d3a68ea9b6591/USER", instance = 'phys03', dbFile=dbFile, xSection=1 )

# not yet ready
SMS_T8bbllnunu_XCha0p5_XSlep0p95    = Sample.nanoAODfromDAS("SMS_T8bbllnunu_XCha0p5_XSlep0p95", "/SMS-T8bbllnunu_XCha0p5_XSlep0p95_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/dspitzba-crab_RunIISummer16MiniAODv2-PUSummer16Fast_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1_80X_FS_v1-19989c43757f6bd6f30d3a68ea9b6591/USER", instance = 'phys03', dbFile=dbFile, xSection=1 )
SMS_T8bbllnunu_XCha0p5_XSlep0p95_mN1_700_1300 = Sample.nanoAODfromDAS("SMS_T8bbllnunu_XCha0p5_XSlep0p95_mN1_700_1300", "/SMS-T8bbllnunu_XCha0p5_XSlep0p95_mN1_700_1300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/dspitzba-crab_RunIISummer16MiniAODv2-PUSummer16Fast_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1_80X_FS_v1-19989c43757f6bd6f30d3a68ea9b6591/USER", instance = 'phys03', dbFile=dbFile, xSection=1 )

signals = [
    SMS_T2tt_mStop_400to1200,
    SMS_T8bbllnunu_XCha0p5_XSlep0p05,
    SMS_T8bbllnunu_XCha0p5_XSlep0p5,
    SMS_T8bbllnunu_XCha0p5_XSlep0p5_mN1_700_1000,
    SMS_T8bbllnunu_XCha0p5_XSlep0p95,
    SMS_T8bbllnunu_XCha0p5_XSlep0p95_mN1_700_1300,
    ]


allSamples = signals


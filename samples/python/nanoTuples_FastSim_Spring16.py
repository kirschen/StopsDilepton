from RootTools.core.standard import *
from RootTools.fwlite.FWLiteSample import *

# Logging
import logging
logger = logging.getLogger(__name__)

hephy = 'root://hephyse.oeaw.ac.at//dpm/oeaw.ac.at/home/cms/'
dbFile = '/afs/hephy.at/data/dspitzbart01/nanoAOD/DB_FastSim_Spring16.sql'
baseDir = "/dpm/oeaw.ac.at/home/cms/store/user/dspitzba/nanoAOD/"

SMS_T2tt_mStop_400to1200 = Sample.fromDPMDirectory("SMS_T2tt_mStop_400to1200",  baseDir+"80X_FS_v1/SMS-T2tt_mStop-400to1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_RunIISpring16MiniAODv2-PUSpring16Fast_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1_80X_FS_v1/180815_193944/0000")

T2tt = [
    SMS_T2tt_mStop_400to1200,
    ]


allSamples = T2tt


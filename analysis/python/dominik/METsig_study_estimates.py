#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--noMultiThreading",      dest="noMultiThreading",      default = False,             action="store_true", help="noMultiThreading?")
parser.add_option("--selectEstimator",       dest="selectEstimator",       default=None,                action="store",      help="select estimator?")
parser.add_option("--selectRegion",          dest="selectRegion",          default=None, type="int",    action="store",      help="select region?")
parser.add_option('--logLevel',              dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
parser.add_option("--useGenMet",             dest="useGenMet",             default=False,               action='store_true', help="use genMET instead of recoMET, used for signal studies")
parser.add_option("--MET",                   dest="MET",                   default=0., type="float",    action='store',      help="Minimum value for MET")
parser.add_option("--METsig",                dest="METsig",                default=0., type="float",    action='store',      help="Minimum value for MET significance")

(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import channels, allChannels, trilepChannels
from StopsDilepton.analysis.estimators   import *
from StopsDilepton.analysis.regions      import regionsO, noRegions, regionsNoMET

from StopsDilepton.analysis.Setup import Setup


#define samples
#Background
data_directory = '/afs/hephy.at/data/dspitzbart01/nanoTuples/'
postProcessing_directory = 'stops_2016_nano_v2/dilep'
from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *

oSetup = Setup()

setup = oSetup.sysClone(parameters={"metMin":options.MET, "metSigMin":options.METsig})

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger('INFO', logFile = None )

from StopsDilepton.analysis.regions import getRegionsMet
allRegions =  getRegionsMet(mt2llThresholds = [ 140, -1 ], mt2blblThresholds = [0, -1], metThresholds = [0, -1]) # can be refined for future studies

estimators = estimatorList(setup)
allEstimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])

print setup.defaultCacheDir()

if options.selectEstimator.startswith('T2tt'):
    sample = next((s for s in allSignals_FS if s.name == options.selectEstimator), None)
    if sample:
        estimate = MCBasedEstimate(name=options.selectEstimator, sample={channel:sample for channel in channels+trilepChannels}, cacheDir=setup.defaultCacheDir())
    else:
        logger.info('Could not find sample for signal %s', options.selectEstimator)
        raise NotImplementedError
    
else:
    estimate = next((e for e in allEstimators if e.name == options.selectEstimator), None)

estimate.initCache(setup.defaultCacheDir())

for r in allRegions:
    for channel in ['SF','all']:
        res = estimate.cachedEstimate(r, channel, setup, save=True)

        logger.info('Estimate: %s', res.val)



#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--skipIfCachefileExists", dest="skipIfCachefileExists", default = False,             action="store_true", help="skipIfCachefileExists?")
parser.add_option("--noMultiThreading",      dest="noMultiThreading",      default = False,             action="store_true", help="noMultiThreading?")
parser.add_option("--selectEstimator",       dest="selectEstimator",       default=None,                action="store",      help="select estimator?")
parser.add_option("--selectRegion",          dest="selectRegion",          default=None, type="int",    action="store",      help="select region?")
parser.add_option("--metSigMin",             dest="metSigMin",             default=5,    type="int",    action="store",      help="metSigMin?")
parser.add_option("--metMin",                dest="metMin",                default=80,   type="int",    action="store",      help="metMin?")
parser.add_option('--logLevel',              dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import channels, allChannels
from StopsDilepton.analysis.estimators   import setup, allEstimators
from StopsDilepton.analysis.regions      import regions80X, superRegion, superRegion140

setup.parameters['metMin']    = options.metMin
setup.parameters['metSigMin'] = options.metSigMin

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

allRegions = set(regions80X + superRegion + superRegion140)

estimators = [e for e in allEstimators if e.name == options.selectEstimator or not options.selectEstimator]
isFastSim = False

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
if options.selectEstimator == "DM":
  from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
  estimators = [ MCBasedEstimate(name=s.name, sample={channel:s for channel in allChannels}) for s in signals_TTDM ]
  for e in estimators: e.isSignal = True

elif options.selectEstimator == "T2tt":
  from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
  estimators = [ MCBasedEstimate(name=s.name, sample={channel:s for channel in allChannels}) for s in signals_T2tt ]
  for e in estimators: e.isSignal = True
  isFastSim = True
  setup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']}, isSignal=True)


setup.verbose=True

def wrapper(args):
        r,channel,setup = args
        res = estimate.cachedEstimate(r, channel, setup, save=True)
        return (estimate.uniqueKey(r, channel, setup), res )


for estimate in estimators:
    if options.skipIfCachefileExists and estimate.cache.cacheFileLoaded:
	print "Cache file %s was loaded -> Skipping."%estimate.cache.filename
	continue

    estimate.initCache(setup.defaultCacheDir())

    jobs=[]
    for channel in channels:
	for (i, r) in enumerate(allRegions):
	    if options.selectRegion is not None and options.selectRegion != i: continue
	    jobs.append((r, channel, setup))
	    if estimate.isSignal: jobs.extend(estimate.getSigSysJobs(r, channel, setup, isFastSim))
	    else:                 jobs.extend(estimate.getBkgSysJobs(r, channel, setup))

    if options.noMultiThreading: 
	results = map(wrapper, jobs)
    else:
	from multiprocessing import Pool
	pool = Pool(processes=8)
	results = pool.map(wrapper, jobs)
	pool.close()
	pool.join()

    for channel in ['SF','all']:
	for (i, r) in enumerate(allRegions):
	    if options.selectRegion is not None and options.selectRegion != i: continue
	    estimate.cachedEstimate(r, channel, setup, save=True)
	    if estimate.isSignal: map(lambda args:estimate.cachedEstimate(*args, save=True), estimate.getSigSysJobs(r, channel, setup, isFastSim))
	    else:                 map(lambda args:estimate.cachedEstimate(*args, save=True), estimate.getBkgSysJobs(r, channel, setup))

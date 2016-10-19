#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--noMultiThreading",      dest="noMultiThreading",      default = False,             action="store_true", help="noMultiThreading?")
parser.add_option("--selectEstimator",       dest="selectEstimator",       default=None,                action="store",      help="select estimator?")
parser.add_option("--selectRegion",          dest="selectRegion",          default=None, type="int",    action="store",      help="select region?")
parser.add_option('--logLevel',              dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import channels, allChannels
from StopsDilepton.analysis.estimators   import setup, allEstimators
from StopsDilepton.analysis.regions      import regions80X, superRegion, superRegion140, regions80X_2D


# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )

allRegions = regions80X + superRegion + superRegion140 + regions80X_2D #This cannot be a set!!! No ordering in a set, enumerate changes!!

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
allEstimators += [ MCBasedEstimate(name=s.name, sample={channel:s for channel in allChannels}) for s in signals_TTbarDM + signals_T2tt ]


# Select estimate
estimate = next((e for e in allEstimators if e.name == options.selectEstimator), None)
if not estimate:
  logger.warn(options.selectEstimator + " not known")
  exit(0)


if estimate.name.count('T2tt') or estimate.name.count('TTbarDM'): estimate.isSignal = True

isFastSim = estimate.name.count('T2tt')
if isFastSim:
  setup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF']})

setup.verbose=True

def wrapper(args):
        r,channel,setup = args
        res = estimate.cachedEstimate(r, channel, setup, save=True)
        return (estimate.uniqueKey(r, channel, setup), res )

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

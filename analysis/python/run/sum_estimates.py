#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--logLevel',              dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import allChannels
from StopsDilepton.analysis.estimators import setup, constructEstimatorList
from StopsDilepton.analysis.regions import reducedRegionsNew, superRegion, superRegion140
from StopsDilepton.analysis.Cache import Cache
import os

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )


# These are the ones we are going to sum
estimators = constructEstimatorList(["TTJets","TTZ","DY", 'other-detailed'])

regions = set(reducedRegionsNew + superRegion + superRegion140)

for e in estimators:
    e.initCache(setup.defaultCacheDir())

sumCache = Cache(os.path.join(setup.defaultCacheDir(), 'sum.pkl'), verbosity=2)

for c in ["EE","MuMu","EMu","all"]:
  for r in regions:
    for r, c, s in estimators[0].getBkgSysJobs(r, c, setup):
      res = sum(e.cachedEstimate(r, c, s, save=False) for e in estimators)
      sumCache.add(estimators[0].uniqueKey(r, c, s), res, save=True)

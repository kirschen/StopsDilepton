#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--logLevel',              dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])
parser.add_option("--estimates",             dest="estimates",             default='mc',                action='store',      choices=["mc","dd"],     help="mc estimators or data-driven estimators?")
(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import allChannels, channels
from StopsDilepton.analysis.estimators import setup, constructEstimatorList
from StopsDilepton.analysis.regions import regions80X, superRegion, superRegion140
from StopsDilepton.analysis.Cache import Cache
import os

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(options.logLevel, logFile = None )


# These are the ones we are going to sum
if   options.estimates == "mc": estimators = constructEstimatorList(["TTJets","TTZ","DY", 'other-detailed'])
elif options.estimates == "dd": estimators = constructEstimatorList(["TTJets-DD","TTZ-DD-Top16009","DY-DD", 'other-detailed'])

regions = set(regions80X + superRegion + superRegion140)

for e in estimators:
    e.initCache(setup.defaultCacheDir())

sumCache = Cache(os.path.join(setup.defaultCacheDir(), 'sum_dd.pkl' if options.estimates == "dd" else 'sum.pkl'), verbosity=2)

for c in allChannels:
  for r in regions:
    for r, c, s in estimators[0].getBkgSysJobs(r, c, setup) + [(r, c, setup)]:
      res = sum(e.cachedEstimate(r, c, s, save=False) for e in estimators)
      sumCache.add(estimators[0].uniqueKey(r, c, s), res, save=True)

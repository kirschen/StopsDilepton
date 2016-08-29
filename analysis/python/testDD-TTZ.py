#!/usr/bin/env python
from StopsDilepton.analysis.Region import Region
from StopsDilepton.analysis.estimators import setup
from StopsDilepton.analysis.DataDrivenTTZEstimate import DataDrivenTTZEstimate

import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )
setup.verbose = True

estimateTTZ = DataDrivenTTZEstimate(name='TTZ-DD', cacheDir=None)

regionTTZ = Region('dl_mt2ll', (0,-1))

for channel, sample in setup.sample['Data'].iteritems():
    res = estimateTTZ.cachedEstimate(regionTTZ, channel, setup)
    print "\n Result in ", channel," for estimate ", estimateTTZ.name, regionTTZ,":", res#, 'jer',jer, 'jec', jec

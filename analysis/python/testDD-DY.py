#!/usr/bin/env python
from StopsDilepton.analysis.Region import Region
from StopsDilepton.analysis.estimators import setup, DataDrivenDYEstimate
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
from StopsDilepton.analysis.regions import regions80X
import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )


estimateDY = DataDrivenDYEstimate(name='DY-DD', cacheDir=None, controlRegion=Region('dl_mt2ll', (100,-1)))

for channel, sample in setup.sample['Data'].iteritems():
  for r in [Region('dl_mt2ll', (100,-1))]:
    res = estimateDY.cachedEstimate(r,channel,setup)
    print "\n Result in ", channel," for estimate ", estimateDY.name, r,":", res#, 'jer',jer, 'jec', jec

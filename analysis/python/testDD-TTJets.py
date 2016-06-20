#!/usr/bin/env python
from StopsDilepton.analysis.regions import reducedRegionsNew
from StopsDilepton.analysis.estimators import setup
from StopsDilepton.analysis.DataDrivenTTJetsEstimate import DataDrivenTTJetsEstimate
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )

estimate = DataDrivenTTJetsEstimate(name='TTJets-DD', controlRegion=reducedRegionsNew[0], cacheDir=None)

for region in reducedRegionsNew:
  for channel, sample in setup.sample['Data'].iteritems():
    res = estimate.cachedEstimate(region, channel, setup)

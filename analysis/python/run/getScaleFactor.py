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
estimateDY.initCache(setup.defaultCacheDir())

modifiers = [ {},
              {'reweight':['reweightPUUp']},
              {'reweight':['reweightPUDown']},
              {'reweight':['reweightTopPt']},
 #            {'selectionModifier':'JERUp'},
 #            {'selectionModifier':'JERDown'},
              {'selectionModifier':'JECVUp'},
              {'selectionModifier':'JECVDown'},
#             {'reweight':['reweightLeptonFastSimSFUp']},
#             {'reweight':['reweightLeptonFastSimSFDown']},
#             {'reweight':['reweightBTag_SF']},
#             {'reweight':['reweightBTag_SF_b_Down']},
            ]

selections = [ "met50" ]

for selection in selections:
  if selection == "met50": setup.parameters['metMin'] = 50
  for channel in ['MuMu']:  # is the same for EE
    for r in [Region('dl_mt2ll', (100,-1))]:  # also the same in each applied region because we use a controlRegion
      for modifier in modifiers:
	scaleFactor = estimateDY._estimate(r, channel, setup.sysClone(modifier), returnScaleFactor=True)
	print "DY scalefactor: " + str(scaleFactor) + "     (" + str(modifier) + ")"

from math import sqrt
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator
from StopsDilepton.analysis.u_float import u_float

# Logging
import logging
logger = logging.getLogger(__name__)

class DataDrivenDYEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(DataDrivenDYEstimate, self).__init__(name, cacheDir=cacheDir)

    #Concrete implementation of abstract method 'estimate' as defined in Systematic
    def _estimate(self, region, channel, setup):

        #Sum of all channels for 'all'
        if channel=='all':
            estimate     = sum([ self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE', 'EMu']])

        #MC based for 'EMu'
        elif channel=='EMu':
            weight       = setup.weightString()
            preSelection = setup.preselection('MC', zWindow='allZ', channel=channel)
            cut          = "&&".join([region.cutString(setup.sys['selectionModifier']), preSelection['cut'] ])
            estimate     = setup.lumi[channel]/1000.*u_float(**setup.sample['DY'][channel].getYieldFromDraw(selectionString = cut, weightString=weight))

        #Data driven for EE and MuMu
        else:
            weight       = setup.weightString()

            cut_offZ_1b     = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=channel, zWindow = 'offZ', **setup.defaultParameters(update={'nBTags':(1,-1)}))['cut']])
            cut_onZ_0b      = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=channel, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(0,0 )}))['cut']])
            cut_data_onZ_0b = "&&".join([region.cutString(),                               setup.selection('Data', channel=channel, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(0,0 )}))['cut']])

            # Calculate ratio (offZ,1b)/(onZ,0b)
            yield_offZ_1b = u_float(**setup.sample['DY'][channel].getYieldFromDraw(  selectionString = cut_offZ_1b,     weightString=weight))
            yield_onZ_0b  = u_float(**setup.sample['DY'][channel].getYieldFromDraw(  selectionString = cut_onZ_0b,      weightString=weight))
            R             = yield_offZ_1b/yield_onZ_0b if yield_onZ_0b > 0 else 0

            # Calculate data-other onZ for 0 b-jets region
            yield_data    = u_float(**setup.sample['Data'][channel].getYieldFromDraw(selectionString = cut_data_onZ_0b, weightString="("+str(setup.rescaleDataLumi(channel)) + ")"))
            yield_other   = sum(u_float(**setup.sample[s][channel].getYieldFromDraw( selectionString = cut_onZ_0b,      weightString=weight)) for s in ['TTJets' , 'TTZ' , 'other'])
            normRegYield  = yield_data - yield_other

            # Calculate DY estimate in 1 b-jet region
            estimate      = R*normRegYield

            logger.info("yield_offZ_1b: " + str(yield_offZ_1b))
            logger.info("yield_onZ_0b:  " + str(yield_onZ_0b))
            logger.info("R:             " + str(R))
            logger.info("yield_data:    " + str(yield_data))
            logger.info("yield_other:   " + str(yield_other))
            if normRegYield < 0 and yield_data > 0: logger.warn("Negative normalization region yield: " + str(normRegYield))

	logger.info('Estimate for DY in ' + channel + ' channel: ' + str(estimate) + (" (negative estimated being replaced by 0)" if estimate < 0 else ""))
	return estimate if estimate > 0 else u_float(0, 0)

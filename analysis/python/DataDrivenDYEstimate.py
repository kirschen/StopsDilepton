from math import sqrt
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator
from StopsDilepton.analysis.u_float import u_float

# Logging
import logging
logger = logging.getLogger(__name__)

class DataDrivenDYEstimate(SystematicEstimator):
    def __init__(self, name, controlRegion=None, combineChannels = True, cacheDir=None):
        super(DataDrivenDYEstimate, self).__init__(name, cacheDir=cacheDir)
        self.controlRegion   = controlRegion
        self.combineChannels = combineChannels

    #Concrete implementation of abstract method 'estimate' as defined in Systematic
    def _estimate(self, region, channel, setup, returnScaleFactor = False):

        #Sum of all channels for 'all'
        if channel=='all':
            estimate     = sum([ self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE', 'EMu']])

        elif channel=='SF':
            estimate     = sum([ self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE']])


        #MC based for 'EMu'
        elif channel=='EMu':
            weight       = setup.weightString()
            preSelection = setup.preselection('MC', zWindow='allZ', channel=channel)
            cut          = "&&".join([region.cutString(setup.sys['selectionModifier']), preSelection['cut'] ])
            estimate     = setup.lumi[channel]/1000.*u_float(**setup.sample['DY'][channel].getYieldFromDraw(selectionString = cut, weightString=weight))

        #Data driven for EE and MuMu (calculate for data luminosity)
        else:
            weight       = setup.weightString()
            normRegion   = self.controlRegion if self.controlRegion else region


            # Calculate data-other onZ for 0 b-jets region in normalization region
            channels = ['EE','MuMu'] if self.combineChannels else [channel]

	    cut_onZ_0b      = {}
	    cut_data_onZ_0b = {}
            for c in channels:
	      cut_onZ_0b[c]      = "&&".join([normRegion.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=c, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(0,0 ), 'dPhiJetMet': 0, 'metMin': 50}))['cut']])
	      cut_data_onZ_0b[c] = "&&".join([normRegion.cutString(),                               setup.selection('Data', channel=c, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(0,0 ), 'dPhiJetMet': 0, 'metMin': 50}))['cut']])

            yield_data    = sum(self.yieldFromCache(setup, 'Data',   c, cut_data_onZ_0b[c], "(1)")                         for c in channels)
            yield_onZ_0b  = sum(self.yieldFromCache(setup, 'DY',     c, cut_onZ_0b[c],      weight)*setup.dataLumi[c]/1000 for c in channels)
            yield_other   = sum(self.yieldFromCache(setup, s,        c, cut_onZ_0b[c],      weight)*setup.dataLumi[c]/1000 for c in channels for s in ['TTJets' , 'TTZ' , 'other'])
            scaleFactor   = (yield_data - yield_other)/yield_onZ_0b if yield_onZ_0b > 0 else 0

            # To make this table in the getScaleFactor script
            if returnScaleFactor:
              yields = {i: sum(self.yieldFromCache(setup, i, c, cut_onZ_0b[c], weight)*setup.dataLumi[c]/1000 for c in channels) for i in ['DY', 'TTJets', 'TTZ', 'TTX', 'multiBoson']}
              return (yields, yield_data, scaleFactor)

            if yield_data < yield_other: logger.warn("yield other > yield data in DY control region " + str(normRegion))
            if yield_onZ_0b <=0 :        logger.warn("Zero or negative yield for onZ 0b DY MC in control region " + str(normRegion))

            # Calculate DY estimate in 1 b-jet region (and scale back to MC lumi)
            cut_offZ_1b = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('MC', channel=channel, zWindow = 'offZ', **setup.defaultParameters(update={'nBTags':(1,-1)}))['cut']])

            yield_offZ_1b = self.yieldFromCache(setup, 'DY', c, cut_offZ_1b, weight)*setup.lumi[channel]/1000
            estimate      = yield_offZ_1b*scaleFactor

            logger.info("DY scale factor in " + str(region) + ", channel " + channel + ": " + str(scaleFactor))

	logger.info('Estimate for DY in ' + channel + ' channel' + (' (lumi=' + str(setup.lumi[channel]) + '/pb)' if (channel != "all" and channel != "SF") else "") + ': ' + str(estimate) + (" (negative estimated being replaced by 0)" if estimate < 0 else ""))
	return estimate if estimate > 0 else u_float(0, 0)

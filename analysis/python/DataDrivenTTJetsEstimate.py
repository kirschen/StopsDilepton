from math import sqrt
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator
from StopsDilepton.analysis.u_float import u_float

# Logging
import logging
logger = logging.getLogger(__name__)

class DataDrivenTTJetsEstimate(SystematicEstimator):
    def __init__(self, name, controlRegion, cacheDir=None):
        super(DataDrivenTTJetsEstimate, self).__init__(name, cacheDir=cacheDir)
        self.controlRegion = controlRegion

        # Because we are going to reuse a lot of yields which otherwise will be terribly slow
        self.helperCacheName = os.path.join('.', 'helperCache.pkl')
        self.helperCache     = Cache(self.helperCacheName, verbosity=2)

    # Should move this function somehwere more generally
    def yieldFromCache(self, setup, sample, c, selectionString, weightString):
        s = (sample, c, selectionString, weightString)
        if self.helperCache.contains(s) and self.useCache:
          return self.helperCache.get(s)
        else:
	  yieldFromDraw = u_float(**setup.sample[sample][c].getYieldFromDraw(selectionString, weightString))
          self.helperCache.add(s, yieldFromDraw, save=True)
	  return yieldFromDraw

    #Concrete implementation of abstract method 'estimate' as defined in Systematic
    def _estimate(self, region, channel, setup):

        #Sum of all channels for 'all'
        if channel=='all':
            estimate     = sum([ self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE', 'EMu']])

        else:
            weight       = setup.weightString()
            cut_MC_SR    = "&&".join([            region.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=channel, zWindow = 'offZ', **setup.defaultParameters())['cut']])
            cut_MC_CR    = "&&".join([self.controlRegion.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=channel, zWindow = 'offZ', **setup.defaultParameters())['cut']])
            cut_data_CR  = "&&".join([self.controlRegion.cutString(setup.sys['selectionModifier']), setup.selection('Data', channel=channel, zWindow = 'offZ', **setup.defaultParameters())['cut']])

            # Calculate yields for CR
            yield_data    = self.yieldFromCache(setup, 'Data',   channel, cut_data_CR, "(1)")
            yield_ttjets  = self.yieldFromCache(setup, 'TTJets', channel, cut_MC_CR,   weight)*setup.dataLumi[channel]/1000
            yield_other   = self.yieldFromCache(setup, s,        channel, cut_MC_CR,   weight) for s in ['DY' , 'TTZ' , 'other'])*setup.dataLumi[channel]/1000

            sr_ttjets     = self.yieldFromCache(setup, 'TTJets', channel, cut_MC_SR,   weight)*setup.dataLumi[channel]/1000

            normRegYield  = yield_data - yield_other
            normalization = normRegYield/yield_ttjets if yield_ttjets > 0 else 0
            estimate      = normalization*sr_ttjets

            logger.info("Calculating data-driven TTJets normalization in channel " + channel + " using lumi " + str(setup.dataLumi[channel]) + ":")
            logger.info("yield ttjets:              " + str(yield_ttjets))
            logger.info("yield data:                " + str(yield_data))
            logger.info("yield other:               " + str(yield_other))
            logger.info("yield (data-other):        " + str(normRegYield))
            logger.info("normalization:             " + str(normalization))
            if normRegYield < 0 and yield_data > 0: logger.warn("Negative normalization region yield!")

	return normalization

	logger.info('Estimate for TTJets in ' + channel + ' channel' + (' (lumi=' + str(setup.lumi[channel]) + '/pb)' if channel != "all" else "") + ': ' + str(estimate) + (" (negative estimated being replaced by 0)" if estimate < 0 else ""))
	return estimate if estimate > 0 else u_float(0, 0)

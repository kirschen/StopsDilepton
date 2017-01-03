from math import sqrt
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator
from StopsDilepton.analysis.u_float import u_float
from StopsDilepton.tools.user import analysis_results
import os

# Logging
import logging
logger = logging.getLogger(__name__)

class DataDrivenTTJetsEstimate(SystematicEstimator):
    def __init__(self, name, controlRegion, cacheDir=None):
        super(DataDrivenTTJetsEstimate, self).__init__(name, cacheDir=cacheDir)
        self.controlRegion = controlRegion

    #Concrete implementation of abstract method 'estimate' as defined in Systematic
    def _estimate(self, region, channel, setup):

        #Sum of all channels for 'all'
        if channel=='all':
            estimate     = sum([ self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE', 'EMu']])

        elif channel=='SF':
            estimate     = sum([ self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE']])

        else:
            weight       = setup.weightString()
            cut_MC_SR    = "&&".join([            region.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=channel, **setup.defaultParameters())['cut']])
            cut_MC_CR    = "&&".join([self.controlRegion.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=channel, **setup.defaultParameters())['cut']])
            cut_data_CR  = "&&".join([self.controlRegion.cutString(),                               setup.selection('Data', channel=channel, **setup.defaultParameters())['cut']])

            # Calculate yields for CR (normalized to data lumi)
            yield_data    = self.yieldFromCache(setup, 'Data',   channel, cut_data_CR, "(1)")
            yield_ttjets  = self.yieldFromCache(setup, 'TTJets', channel, cut_MC_CR,   weight)*setup.dataLumi[channel]/1000
            yield_other   = sum(self.yieldFromCache(setup, s,    channel, cut_MC_CR,   weight) for s in ['DY' , 'TTZ' , 'multiBoson','other'])*setup.dataLumi[channel]/1000

            # The ttjets yield in the signal regions
            sr_ttjets     = self.yieldFromCache(setup, 'TTJets', channel, cut_MC_SR,   weight)*setup.lumi[channel]/1000

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

	logger.info('Estimate for TTJets in ' + channel + ' channel' + (' (lumi=' + str(setup.lumi[channel]) + '/pb)' if (channel != "all" and channel != "SF") else "") + ': ' + str(estimate) + (" (negative estimated being replaced by 0)" if estimate < 0 else ""))
	return estimate if estimate > 0 else u_float(0, 0)

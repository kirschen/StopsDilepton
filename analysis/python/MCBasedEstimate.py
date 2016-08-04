# Logging
import logging
logger = logging.getLogger(__name__)

from StopsDilepton.analysis.Region import Region
from StopsDilepton.analysis.u_float import u_float
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator

class MCBasedEstimate(SystematicEstimator):
    def __init__(self, name, sample, cacheDir=None):
        super(MCBasedEstimate, self).__init__(name, cacheDir=cacheDir)
        self.sample=sample
        self.isSignal=False

    def _estimate(self, region, channel, setup):

        ''' Concrete implementation of abstract method 'estimate' as defined in Systematic
        '''

        logger.debug( "MC prediction for %s channel %s" %(self.name, channel) )

        if channel=='all':
            # 'all' is the total of all contributions
            return sum([self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE', 'EMu']])

        elif channel=='SF':
            # 'all' is the total of all contributions
            return sum([self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE']])

        else:

            # Important! We use 'allZ' (mll>20) in case of EMu 
            zWindow= 'allZ' if channel=='EMu' else 'offZ'

            preSelection = setup.preselection('MC', zWindow=zWindow, channel=channel, isSignal=self.isSignal)
            cut = "&&".join([region.cutString(setup.sys['selectionModifier']), preSelection['cut']])
            weight = preSelection['weightStr']

            logger.debug( "Using cut %s and weight %s"%(cut, weight) )

            return setup.lumi[channel]/1000.*u_float(**self.sample[channel].getYieldFromDraw(selectionString = cut, weightString = weight) )

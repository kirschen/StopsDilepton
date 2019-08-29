# Logging
import logging
logger = logging.getLogger(__name__)

from StopsDilepton.analysis.Region import Region
from StopsDilepton.tools.u_float import u_float
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator

class SumEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(SumEstimate, self).__init__(name, cacheDir=cacheDir)

    def _estimate(self, region, channel, setup):
        if channel=='all':
            # 'all' is the total of all contributions
            return sum([self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE', 'EMu']])

        elif channel=='SF':
            # 'all' is the total of all contributions
            return sum([self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE']])

        else:
            raise NotImplementedError("Run sum_estimates.py first")

jmeVariations = ["JER", "JERUp", "JERDown", "JECUp", "JECDown"]

# Standard imports
import os
import abc
from math import sqrt
import json

# StopsDilepton
from StopsDilepton.analysis.Cache import Cache

# Logging
import logging
logger = logging.getLogger(__name__)

class SystematicEstimator:
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, cacheDir=None):
        self.name = name
        self.initCache(cacheDir)

    def initCache(self, cacheDir):
        if cacheDir:
            self.cacheDir=cacheDir
            cacheFileName = os.path.join(cacheDir, self.name+'.pkl')
            if not os.path.exists(os.path.dirname(cacheFileName)):
                os.makedirs(os.path.dirname(cacheFileName))
            self.cache = Cache(cacheFileName, verbosity=1)
        else:
            self.cache=None

    def uniqueKey(self, region, channel, setup):
        return region, channel, json.dumps(setup.sys, sort_keys=True), json.dumps(setup.parameters, sort_keys=True), json.dumps(setup.lumi, sort_keys=True)

    def cachedEstimate(self, region, channel, setup, save=True):
        key =  self.uniqueKey(region, channel, setup)
        if self.cache and self.cache.contains(key):
            res = self.cache.get(key)
            logger.info( "Loading cached %s result for %r : %r"%(self.name, key, res) )
            return res
        elif self.cache:
            logger.info( "Adding cached %s result for %r"%(self.name, key) )
            estimate = self._estimate( region, channel, setup)
            return self.cache.add( key, estimate, save=save)
        else:
            return self._estimate( region, channel, setup)

    @abc.abstractmethod
    def _estimate(self, region, channel, setup):
        '''Estimate yield in 'region' using setup'''
        return

    def PUSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightPUUp']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightPUDown']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up,down)

    def topPtSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightTopPt']}))
        return abs(0.5*(up-ref)/ref) if ref > 0 else up

    def JERSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'JERUp'}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'JERDown'}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def JECSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'JECUp'}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'JECDown'}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def leptonFSSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonFastSimSF']}))
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonFastSimSFUp']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonFastSimSFDown']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def btaggingSFbSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF']}))
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Up']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Down']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def btaggingSFlSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF']}))
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Up']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Down']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def btaggingSFFSSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF']}))
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_FS_Up']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_FS_Down']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def getBkgSysJobs(self, region, channel, setup):
        l = [
            (region, channel, setup.sysClone({'reweight':['reweightPUUp']})),
            (region, channel, setup.sysClone({'reweight':['reweightPUDown']})),

            (region, channel, setup.sysClone({'reweight':['reweightTopPt']})),

            (region, channel, setup.sysClone({'selectionModifier':'JERUp'})),
            (region, channel, setup.sysClone({'selectionModifier':'JERDown'})),

            (region, channel, setup.sysClone({'selectionModifier':'JECUp'})),
            (region, channel, setup.sysClone({'selectionModifier':'JECDown'})),


            (region, channel, setup.sysClone({'reweight':['reweightBTag_SF']})),
            (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Up']})),
            (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Down']})),
            (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Up']})),
            (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Down']})),

        ]
        return l

    def getSigSysJobs(self, region, channel, setup, isFastSim = False):
        l = self.getBkgSysJobs(region = region, channel = channel, setup = setup)
        if isFastSim:
            l.extend( [\
                (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_FS_Up']})),
                (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_FS_Down']})),
                (region, channel, setup.sysClone({'reweight':['reweightLeptonFastSimSF']})),
                (region, channel, setup.sysClone({'reweight':['reweightLeptonFastSimSFUp']})),
                (region, channel, setup.sysClone({'reweight':['reweightLeptonFastSimSFDown']})),
            ] )
        return l

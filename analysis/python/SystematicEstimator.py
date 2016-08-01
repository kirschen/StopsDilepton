jmeVariations = ["JER", "JERUp", "JERDown", "JECUp", "JECDown","JECVUp","JECVDown"]

# Standard imports
import os
import abc
from math import sqrt
import json

# StopsDilepton
from StopsDilepton.analysis.Cache import Cache
from StopsDilepton.analysis.u_float import u_float
from StopsDilepton.analysis.SetupHelpers import channels

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
            self.cacheDir       = cacheDir
            if not os.path.exists(cacheDir): os.makedirs(cacheDir)

            cacheFileName       = os.path.join(cacheDir, self.name+'.pkl')
            helperCacheFileName = os.path.join(cacheDir, self.name+'_helper.pkl')

            self.cache       = Cache(cacheFileName,       verbosity=1)
            self.helperCache = Cache(helperCacheFileName, verbosity=1) if self.name.count('DD') else None
        else:
            self.cache=None
            self.helperCache=None

    # For the datadriven subclasses which often need the same getYieldFromDraw we write those yields to a cache
    def yieldFromCache(self, setup, sample, c, selectionString, weightString):
        s = (sample, c, selectionString, weightString)
        if self.helperCache and self.helperCache.contains(s):
          return self.helperCache.get(s)
        else:
	  yieldFromDraw = u_float(**setup.sample[sample][c].getYieldFromDraw(selectionString, weightString))
          if self.helperCache: self.helperCache.add(s, yieldFromDraw, save=True)
	  return yieldFromDraw


    def uniqueKey(self, region, channel, setup):
        return region, channel, json.dumps(setup.sys, sort_keys=True), json.dumps(setup.parameters, sort_keys=True), json.dumps(setup.lumi, sort_keys=True)

    def cachedEstimate(self, region, channel, setup, save=True, overwrite=False):
        key =  self.uniqueKey(region, channel, setup)
        if (self.cache and self.cache.contains(key)) and not overwrite:
            res = self.cache.get(key)
            logger.info( "Loading cached %s result for %r : %r"%(self.name, key, res) )
        elif self.cache:
            logger.info( "Calculating %s result for %r"%(self.name, key) )
            estimate = self._estimate( region, channel, setup)
            res = self.cache.add( key, estimate, save=save)
            logger.info( "Adding cached %s result for %r : %r" %(self.name, key, estimate) )
        else:
            res = self._estimate( region, channel, setup)
        return res if res > 0 else u_float(0,0)

    @abc.abstractmethod
    def _estimate(self, region, channel, setup):
        '''Estimate yield in 'region' using setup'''
        return

    def PUSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightPU12fbUp']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightPU12fbDown']}))
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
        up   = self.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'JECVUp'}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'JECVDown'}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def leptonFSSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonFastSimSF']}))
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonFastSimSFUp']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonFastSimSFDown']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def btaggingSFbSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Up']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Down']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def btaggingSFlSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Up']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Down']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def btaggingSFFSSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_FS_Up']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_FS_Down']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def leptonSFSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonSFUp']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonSFDown']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)

    def triggerSystematic(self, region, channel, setup):
        ref  = self.cachedEstimate(region, channel, setup)
        up   = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightDilepTriggerBackupUp']}))
        down = self.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightDilepTriggerBackupDown']}))
        return abs(0.5*(up-down)/ref) if ref > 0 else max(up, down)


    def getBkgSysJobs(self, region, channel, setup):
        l = [
            (region, channel, setup.sysClone({'reweight':['reweightPU12fbUp']})),
            (region, channel, setup.sysClone({'reweight':['reweightPU12fbDown']})),

            (region, channel, setup.sysClone({'reweight':['reweightTopPt']})),

            (region, channel, setup.sysClone({'selectionModifier':'JERUp'})),
            (region, channel, setup.sysClone({'selectionModifier':'JERDown'})),

            (region, channel, setup.sysClone({'selectionModifier':'JECUp'})),
            (region, channel, setup.sysClone({'selectionModifier':'JECDown'})),
            (region, channel, setup.sysClone({'selectionModifier':'JECVUp'})),
            (region, channel, setup.sysClone({'selectionModifier':'JECVDown'})),

            (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Up']})),
            (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Down']})),
            (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Up']})),
            (region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Down']})),

            (region, channel, setup.sysClone({'reweight':['reweightLeptonSFDown']})),
            (region, channel, setup.sysClone({'reweight':['reweightLeptonSFUp']})),

            (region, channel, setup.sysClone({'reweight':['reweightDilepTriggerDown']})),
            (region, channel, setup.sysClone({'reweight':['reweightDilepTriggerUp']})),
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

    def getTexName(self, channel, rootTex=True):
        try:
          name = self.texName
        except:
	  try:
	    name = self.sample[channel].texName
	  except:
	    try:
	      texNames = [self.sample[c].texName for c in channels]		# If all, only take texName if it is the same for all channels
	      if texNames.count(texNames[0]) == len(texNames):
		name = texNames[0]
	      else:
		name = self.name
	    except:
	      name = self.name
	if not rootTex: name = "$" + name.replace('#','\\') + "$" # Make it tex format
	return name

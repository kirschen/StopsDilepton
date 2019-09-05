# Logging
import logging
import os
import json
logger = logging.getLogger(__name__)

from StopsDilepton.analysis.Region import Region
from StopsDilepton.tools.u_float import u_float
from StopsDilepton.analysis.Cache import Cache
from StopsDilepton.analysis.SetupHelpers import channels, trilepChannels

class DataObservation():
    def __init__(self, name, sample, cacheDir=None):
        self.name = name
        self.sample=sample
        self.initCache(cacheDir)

    def initCache(self, cacheDir):
        if cacheDir:
            self.cacheDir=cacheDir
            cacheFileName = os.path.join(cacheDir, self.name)
            if not os.path.exists(os.path.dirname(cacheFileName)):
                os.makedirs(os.path.dirname(cacheFileName))
            self.cache = Cache(cacheFileName, verbosity=1)
        else:
            self.cache=None

    def uniqueKey(self, region, channel, setup):
        ## this is used in MCBasedEstimate
        ##return '_'.join([str(region), channel, json.dumps(sysForKey, sort_keys=True).replace('"TEMP"',reweightKey), json.dumps(setup.parameters, sort_keys=True), json.dumps(setup.lumi, sort_keys=True)])
        if hasattr(setup, 'blinding'): return str(region), channel, json.dumps(setup.sys, sort_keys=True), json.dumps(setup.parameters, sort_keys=True), json.dumps(setup.lumi, sort_keys=True), setup.blinding
        else:                          return str(region), channel, json.dumps(setup.sys, sort_keys=True), json.dumps(setup.parameters, sort_keys=True), json.dumps(setup.lumi, sort_keys=True)

    # alias for cachedObservation to make it easier to call the same function as for the mc's
    def cachedEstimate(self, region, channel, setup, save=True, overwrite=False):
        return self.cachedObservation(region, channel, setup, overwrite=overwrite)

    def cachedObservation(self, region, channel, setup, save=True, overwrite=False):
        key =  self.uniqueKey(region, channel, setup)
        if self.cache and self.cache.contains(key) and not overwrite and not (channel == 'SF' or channel == 'all'):
            res = self.cache.get(key)
            logger.debug( "Loading cached %s result for %r : %r"%(self.name, key, res) )
            return res
        elif self.cache:
            logger.debug( "Adding cached %s result for %r"%(self.name, key) )
            return self.cache.add( key, self.observation( region, channel, setup, overwrite), overwrite=True)
        else:
            return self.observation( region, channel, setup, overwrite)

    def observation(self, region, channel, setup, overwrite):

        if channel=='all':
            return sum([self.cachedEstimate(region, c, setup, overwrite=overwrite) for c in (trilepChannels if setup.parameters['triLep'] else channels)])

        if channel=='SF':
            return sum([self.cachedObservation(region, c, setup, overwrite=overwrite) for c in ['MuMu', 'EE']])

        else:
            preSelection = setup.preselection('Data', channel=channel)
            cut = "&&".join([region.cutString(setup.sys['selectionModifier']), preSelection['cut']])

            logger.debug( "Using cut %s"% cut )

            if hasattr(setup, 'blinding') and setup.blinding: weight = 'weight*' + setup.blinding
            else:                                             weight = 'weight'
            return u_float(**self.sample.getYieldFromDraw(selectionString = cut, weightString = weight) )

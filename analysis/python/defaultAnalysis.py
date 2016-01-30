from Setup import Setup
setup = Setup()

#define analysis regions
from StopsDilepton.analysis.regions import regions1D, regions3D
regions =  regions3D

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.analysis.DataDrivenDYEstimate import DataDrivenDYEstimate
from StopsDilepton.analysis.DataDrivenTTZEstimate import DataDrivenTTZEstimate
#from collections import OrderedDict
bkgEstimators = [
      #DataDrivenDYEstimate(name='DY-DD', cacheDir=setup.cacheDir),
      #DataDrivenTTZEstimate(name='TTZ-DD', cacheDir=setup.cacheDir),

      MCBasedEstimate(name='DY',          sample=setup.sample['DY'],     cacheDir = None ),#setup.defaultCacheDir()),
      MCBasedEstimate(name='TTJets',      sample=setup.sample['TTJets'], cacheDir = None ),#setup.defaultCacheDir()),
      MCBasedEstimate(name='TTZ',         sample=setup.sample['TTZ'],    cacheDir = None ),#setup.defaultCacheDir()),
      MCBasedEstimate(name='other',       sample=setup.sample['other'],  cacheDir = None ),#setup.defaultCacheDir()),
]

nList = [e.name for e in bkgEstimators]
assert len(list(set(nList))) == len(nList), "Names of bkgEstimators are not unique: %s"%",".join(nList)

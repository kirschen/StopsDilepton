from Setup import Setup, otherEWKComponents
setup = Setup()

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
#from collections import OrderedDict
bkgEstimators = [
      MCBasedEstimate(name='TTZ',         sample=setup.sample['TTZ'],    cacheDir = None ),#setup.defaultCacheDir()),
      MCBasedEstimate(name='TTJets',      sample=setup.sample['TTJets'], cacheDir = None ),#setup.defaultCacheDir()),
      MCBasedEstimate(name='DY',          sample=setup.sample['DY'],     cacheDir = None ),#setup.defaultCacheDir()),
      MCBasedEstimate(name='other',       sample=setup.sample['other'],  cacheDir = None ),#setup.defaultCacheDir()),
]
nList = [e.name for e in bkgEstimators]
assert len(list(set(nList))) == len(nList), "Names of bkgEstimators are not unique: %s"%",".join(nList)


from SetupHelpers import channels 
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_postProcessed import *
bkgEstimators_detailed = [
      MCBasedEstimate(name='TTZ',         sample=setup.sample['TTZ'],    cacheDir = None ),#setup.defaultCacheDir()),
      MCBasedEstimate(name='TTJets',      sample=setup.sample['TTJets'], cacheDir = None ),#setup.defaultCacheDir()),
      MCBasedEstimate(name='DY',          sample=setup.sample['DY'],     cacheDir = None ),#setup.defaultCacheDir()),
]
bkgEstimators_detailed += [  MCBasedEstimate(name=comp.name,  sample={c:comp for c in channels},  cacheDir = None ) for comp in otherEWKComponents ]

bkgEstimators_detailed.append(  MCBasedEstimate(name="QCD", sample= {'MuMu': QCD_Mu5, 'EE': QCD_EMbcToE, 'EMu': QCD_Mu5EMbcToE} ) )



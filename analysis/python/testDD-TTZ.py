from StopsDilepton.analysis.Region import Region
from StopsDilepton.analysis.defaultAnalysis import setup

#Always taking data lumi
setup.lumi = {channel:setup.sample['Data'][channel]['lumi'] for channel in setup.sample['Data'].keys()}
setup.loadChains()

from StopsDilepton.analysis.DataDrivenTTZEstimate import DataDrivenTTZEstimate
setup.verbose = True

estimateTTZ = DataDrivenTTZEstimate(name='TTZ-DD', cacheDir=None)

regionTTZ = Region('dl_mt2ll', (0,-1))

for channel in ['MuMu']:
  res = estimateTTZ.cachedEstimate(regionTTZ,channel,setup)
  print "\n Result in ", channel," for estimate ", estimateTTZ.name, regionTTZ,":", res#, 'jer',jer, 'jec', jec

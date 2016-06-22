from StopsDilepton.analysis.Region import Region

#Put all sets of regions that are used in the analysis, closure, tables, etc.

def getRegionsFromThresholds(var, vals):
    return [Region(var, (vals[i], vals[i+1])) for i in range(len(vals)-1)]+[Region(var, (vals[-1], -1))]

regions1D = getRegionsFromThresholds('dl_mt2ll', [140, 240])

def getRegions3D(mt2llThresholds, mt2blblThresholds, mt2bbThresholds):
  regions_mt2ll   = getRegionsFromThresholds('dl_mt2ll',   mt2llThresholds)
  regions_mt2bb   = getRegionsFromThresholds('dl_mt2bb',   mt2bbThresholds)
  regions_mt2blbl = getRegionsFromThresholds('dl_mt2blbl', mt2blblThresholds)

  regions3D = []
  for r1 in regions_mt2ll:
    for r3 in regions_mt2blbl:
      for r2 in regions_mt2bb:
        regions3D.append(r1+r2+r3)

  return regions3D
    


defaultRegions     = getRegions3D( mt2llThresholds = [0, 140, 240],   mt2blblThresholds = [0, 100, 200], mt2bbThresholds  = [70,170, 270])
reducedRegionsA    = getRegions3D( mt2llThresholds = [0, 140, 240],   mt2blblThresholds = [0, 100, 200], mt2bbThresholds  = [70,170])
reducedRegionsB    = getRegions3D( mt2llThresholds = [0, 140, 240],   mt2blblThresholds = [0, 100],      mt2bbThresholds  = [70,170, 270])
reducedRegionsAB   = getRegions3D( mt2llThresholds = [0, 140, 240],   mt2blblThresholds = [0, 100],      mt2bbThresholds  = [70,170])

reducedRegionsNew  = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2bb", (0, -1)) + Region("dl_mt2blbl", (0, -1))] # whole mt2ll < 100 as control region
reducedRegionsNew += getRegions3D( mt2llThresholds = [100, 140, 240], mt2blblThresholds = [0, 100, 200], mt2bbThresholds  = [70,170])

reducedRegionsC    = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2bb", (0, -1)) + Region("dl_mt2blbl", (0, -1))] # whole mt2ll < 100 as control region
reducedRegionsC   += getRegions3D( mt2llThresholds = [100, 140, 240], mt2blblThresholds = [0, 150], mt2bbThresholds  = [70,170])

superRegion        = getRegions3D( mt2llThresholds = [0, 100], mt2blblThresholds = [0], mt2bbThresholds = [70] ) # control region is mt2ll < 100, super regions is mt2ll > 100

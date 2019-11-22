from StopsDilepton.analysis.Region import Region

#Put all sets of regions that are used in the analysis, closure, tables, etc.

def getRegionsFromThresholds(var, vals, gtLastThreshold = True):
    return [Region(var, (vals[i], vals[i+1])) for i in range(len(vals)-1)]

regions1D = getRegionsFromThresholds('dl_mt2ll', [140, 240, -1])

def getRegions2D(varOne, varOneThresholds, varTwo, varTwoThresholds):
    regions_varOne  = getRegionsFromThresholds(varOne,  varOneThresholds)
    regions_varTwo  = getRegionsFromThresholds(varTwo, varTwoThresholds)

    regions2D = []
    for r1 in regions_varOne:
        for r2 in regions_varTwo:
            regions2D.append(r1+r2)

    return regions2D

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

def getRegionsMet(mt2llThresholds, mt2blblThresholds, metThresholds):
  regions_mt2ll   = getRegionsFromThresholds('dl_mt2ll',   mt2llThresholds)
  regions_mt2blbl = getRegionsFromThresholds('dl_mt2blbl', mt2blblThresholds)
  regions_met     = getRegionsFromThresholds('MET_pt',     metThresholds)

  regions3D = []
  for r1 in regions_mt2ll:
    for r2 in regions_mt2blbl:
      for r3 in regions_met:
        regions3D.append(r1+r2+r3)

  return regions3D
 
def getRegionsMetSig(mt2llThresholds, mt2blblThresholds, metsigThresholds):
    regions_mt2ll = getRegionsFromThresholds('dl_mt2ll', mt2llThresholds)
    regions_mt2blbl = getRegionsFromThresholds('dl_mt2blbl', mt2blblThresholds)
    regions_metsig = getRegionsFromThresholds('MET_significance', metsigThresholds)
    
    regions3D = []
    for r1 in regions_mt2ll:
        for r2 in regions_mt2blbl:
            for r3 in regions_metsig:
                regions3D.append(r1+r2+r3)
    
    return regions3D


regions2016     = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, 200, -1]) + [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]

regionsLegacy        = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (12, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 12, 50, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 12, -1] )
highMT2blblregions   = getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 100, 200, -1], metsigThresholds = [ 12, 50, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 12, -1] )

regionsLegacytest1   = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (12, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100], metsigThresholds = [ 12, 100, -1] )  + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 200, -1], metsigThresholds = [ 12, 100, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 12, -1] )

noRegions = [Region("dl_mt2ll", (0, -1))] 
regionsNoMET = getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [0, -1])

regionsAgg = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + [Region("dl_mt2ll", (100, 140)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (200, -1))] + [Region("dl_mt2ll", (140, 240)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (200, -1))]

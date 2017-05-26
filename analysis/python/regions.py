from StopsDilepton.analysis.Region import Region

#Put all sets of regions that are used in the analysis, closure, tables, etc.

def getRegionsFromThresholds(var, vals, gtLastThreshold = True):
    return [Region(var, (vals[i], vals[i+1])) for i in range(len(vals)-1)]

regions1D = getRegionsFromThresholds('dl_mt2ll', [140, 240, -1])

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
    


defaultRegions     = getRegions3D( mt2llThresholds = [0, 140, 240, -1], mt2blblThresholds = [0, 100, 200, -1], mt2bbThresholds  = [70,170, 270, -1])

# whole mt2ll < 100 GeV as control region
reducedRegionsNew  = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2bb", (0, -1)) + Region("dl_mt2blbl", (0, -1))] # whole mt2ll < 100 as control region
reducedRegionsNew += getRegions3D( mt2llThresholds = [100, 140, 240, -1], mt2blblThresholds = [0, 100, 200], mt2bbThresholds  = [70,170, -1])

# definition of super regions
superRegion        = getRegions3D( mt2llThresholds = [0, 100, -1],      mt2blblThresholds = [0, -1], mt2bbThresholds = [70, -1] ) # control region is mt2ll < 100, super regions is mt2ll > 100
superRegion140     = getRegions3D( mt2llThresholds = [0, 100, 140, -1], mt2blblThresholds = [0, -1], mt2bbThresholds = [70, -1] ) # control region is mt2ll < 100, super regions is mt2ll > 140

# same as reducedRegionsNew, but with collapsed hith mt2ll > 240 GeV region
regions80X         = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2bb", (0, -1)) + Region("dl_mt2blbl", (0, -1))]
regions80X        += getRegions3D( mt2llThresholds = [100, 140, 240], mt2blblThresholds = [0, 100, 200,-1], mt2bbThresholds  = [70,170,-1])
regions80X        += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2bb", (0, -1)) + Region("dl_mt2blbl", (0, -1))]

# same as reducedRegionsNew, but with collapsed hith mt2ll > 240 GeV region and without Mt2bb
def getRegions2D(mt2llThresholds, mt2blblThresholds):
  regions_mt2ll   = getRegionsFromThresholds('dl_mt2ll',   mt2llThresholds)
  regions_mt2blbl = getRegionsFromThresholds('dl_mt2blbl', mt2blblThresholds)

  regions2D = []
  for r1 in regions_mt2ll:
    for r3 in regions_mt2blbl:
        regions2D.append(r1+r3)

  return regions2D

regions80X_2D         = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1))]
regions80X_2D        += getRegions2D( mt2llThresholds = [100, 140, 240], mt2blblThresholds = [0, 100, 200,-1])
regions80X_2D        += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1))]



def getRegionsMet(mt2llThresholds, mt2blblThresholds, metThresholds):
  regions_mt2ll   = getRegionsFromThresholds('dl_mt2ll',   mt2llThresholds)
  regions_mt2blbl = getRegionsFromThresholds('dl_mt2blbl', mt2blblThresholds)
  regions_met     = getRegionsFromThresholds('met_pt',     metThresholds)

  regions3D = []
  for r1 in regions_mt2ll:
    for r2 in regions_mt2blbl:
      for r3 in regions_met:
        regions3D.append(r1+r2+r3)

  return regions3D
 


regionsA = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [80, -1])
regionsB = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [100, -1])
regionsC = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [120, -1])
regionsD = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))]  + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [80, 140, 200, -1])
regionsE = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))]  + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, -1])
regionsF = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (120, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [120, -1])
regionsG = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))]  + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, 140, 200, -1])
regionsH = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (100, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [100, 200, 300, -1])
regionsI = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [200, -1])
regionsJ = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [300, -1])
regionsK = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [140, -1])
regionsL = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [160, -1])
regionsM = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [180, -1])
regionsN = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [220, -1])
regionsO = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, 200, -1])
regionsP = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 180, -1], metThresholds = [80, 200, -1])
regionsQ = getRegionsMet(mt2llThresholds = [ 0, 100, 140, -1], mt2blblThresholds = [0, -1], metThresholds = [80, -1])
regionsR = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0,  -1], metThresholds = [80, 200, -1])
regionsS = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, 200, -1])

regionsAgg = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + [Region("dl_mt2ll", (100, 140)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (200, -1))] + [Region("dl_mt2ll", (140, 240)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (200, -1))]

regionsDM1 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, -1])
regionsDM2 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [80, -1])
regionsDM3 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + [Region("dl_mt2ll", (100, -1)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))]
regionsDM4 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, -1], mt2blblThresholds = [0, -1], metThresholds = [80, -1])
regionsDM5 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [80, 200, -1])
regionsDM6 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, -1], mt2blblThresholds = [0, -1], metThresholds = [80, 200, -1])
regionsDM7 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, -1], mt2blblThresholds = [0, -1], metThresholds = [80, 120, 170, -1])

regionsDM = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (50, -1))] + [Region("dl_mt2ll", (100, 140)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (50, -1))] + [Region("dl_mt2ll", (140, -1)) + Region("dl_mt2blbl", (0, -1)) + Region("met_pt", (50, -1))]

regionsA += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsB += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (100, -1))]
regionsC += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (120, -1))]
regionsD += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsE += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsF += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (120, -1))]
regionsG += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsH += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (100, -1))]
regionsI += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (200, -1))]
regionsJ += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (300, -1))]
regionsK += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (140, -1))]
regionsL += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (160, -1))]
regionsM += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (180, -1))]
regionsN += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (220, -1))]
regionsO += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsP += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsR += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsS += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsAgg += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsDM1 += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsDM2 += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]
regionsDM5 += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('met_pt', (80, -1))]

noRegions = [Region("dl_mt2ll", (0, -1)) + Region("dl_mt2bb", (0, -1)) + Region("met_pt", (0, -1))] # For TTZ CR 

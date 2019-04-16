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
    


defaultRegions     = getRegions3D( mt2llThresholds = [0, 140, 240, -1], mt2blblThresholds = [0, 100, 200, -1], mt2bbThresholds  = [70,170, 270, -1])


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


regionsA = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [80, -1])
regionsB = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [100, -1])
regionsC = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [120, -1])
regionsD = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))]  + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [80, 140, 200, -1])
regionsE = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))]  + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, -1])
regionsF = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (120, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [120, -1])
regionsG = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))]  + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, 140, 200, -1])
regionsH = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (100, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [100, 200, 300, -1])
regionsI = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [200, -1])
regionsJ = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [300, -1])
regionsK = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [140, -1])
regionsL = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [160, -1])
regionsM = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [180, -1])
regionsN = getRegionsMet( mt2llThresholds = [ 0, 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [220, -1])
regionsO = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, 200, -1])
regionsP = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 180, -1], metThresholds = [80, 200, -1])
regionsQ = getRegionsMet(mt2llThresholds = [ 0, 100, 140, -1], mt2blblThresholds = [0, -1], metThresholds = [80, -1])
regionsR = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0,  -1], metThresholds = [80, 200, -1])
regionsS = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, 200, -1])

regionsT_1 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 20, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_2 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (9, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 9, 20, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 9, -1] )
regionsT_3 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (10, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 10, 20, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 10, -1] )
regionsT_4 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (11, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 11, 20, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 11, -1] )
regionsT_5 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (12, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 12, 20, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 12, -1] )
regionsT_6 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (13, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 13, 20, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 13, -1] )
regionsT_7 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (14, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 14, 20, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 14, -1] )
regionsT_8 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (15, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 15, 20, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 15, -1] )
regionsT_9 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 21, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_10 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 22, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_11 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 23, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_12 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 24, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_13 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 25, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_14 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 26, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_15 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 27, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_16 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 28, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_17 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 29, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsT_18 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, 30, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )


regionsU_1 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (8, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 8, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 8, -1] )
regionsU_2 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (9, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 9, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 9, -1] )
regionsU_3 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (10, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 10, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 10, -1] )
regionsU_4 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (11, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 11, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 11, -1] )
regionsU_5 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (12, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 12, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 12, -1] )
regionsU_6 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (13, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 13, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 13, -1] )
regionsU_7 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (14, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 14, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 14, -1] )
regionsU_8 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (15, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 15, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 15, -1] )
regionsU_9 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (16, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 16, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 16, -1] )
regionsU_10 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (17, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 17, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 17, -1] )
regionsU_11 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (18, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 18, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 18, -1] )
regionsU_12 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (19, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 19, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 19, -1] )
regionsU_13 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_significance", (20, -1))] + getRegionsMetSig( mt2llThresholds = [ 100, 140, 240 ], mt2blblThresholds = [ 0, 100, 200, -1], metsigThresholds = [ 20, -1] ) + getRegionsMetSig( mt2llThresholds = [ 240, -1 ], mt2blblThresholds = [ 0, -1], metsigThresholds = [ 20, -1] )



regionsAgg = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + [Region("dl_mt2ll", (100, 140)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (200, -1))] + [Region("dl_mt2ll", (140, 240)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (200, -1))]

regionsDM1 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [80, -1])
regionsDM2 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [80, -1])
regionsDM3 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + [Region("dl_mt2ll", (100, -1)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))]
regionsDM4 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, -1], mt2blblThresholds = [0, -1], metThresholds = [80, -1])
regionsDM5 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, -1], metThresholds = [80, 200, -1])
regionsDM6 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, -1], mt2blblThresholds = [0, -1], metThresholds = [80, 200, -1])
regionsDM7 = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (80, -1))] + getRegionsMet(mt2llThresholds = [ 100, -1], mt2blblThresholds = [0, -1], metThresholds = [80, 120, 170, -1])

regionsDM = [Region("dl_mt2ll", (0, 100)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (50, -1))] + [Region("dl_mt2ll", (100, 140)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (50, -1))] + [Region("dl_mt2ll", (140, -1)) + Region("dl_mt2blbl", (0, -1)) + Region("MET_pt", (50, -1))]

regionsA += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsB += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (100, -1))]
regionsC += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (120, -1))]
regionsD += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsE += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsF += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (120, -1))]
regionsG += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsH += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (100, -1))]
regionsI += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (200, -1))]
regionsJ += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (300, -1))]
regionsK += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (140, -1))]
regionsL += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (160, -1))]
regionsM += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (180, -1))]
regionsN += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (220, -1))]
regionsO += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsP += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsR += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsS += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsAgg += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsDM1 += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsDM2 += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]
regionsDM5 += [Region("dl_mt2ll", (240, -1)) + Region("dl_mt2blbl", (0, -1)) + Region('MET_pt', (80, -1))]

noRegions = [Region("dl_mt2ll", (0, -1)) + Region("dl_mt2bb", (0, -1)) + Region("MET_pt", (0, -1))] # For TTZ CR 
regionsNoMET = getRegionsMet(mt2llThresholds = [ 100, 140, 240], mt2blblThresholds = [0, 100, 200, -1], metThresholds = [0, -1])

from StopsDilepton.analysis.Region import Region

#Put all sets of regions that are used in the analysis, closure, tables, etc.

def getRegionsFromThresholds(var, vals):
    return [Region(var, (vals[i], vals[i+1])) for i in range(len(vals)-1)]+[Region(var, (vals[-1], -1))]

regions1D = getRegionsFromThresholds('dl_mt2ll', [140, 240])

mt2llThresholds  = [0, 140, 240]
mt2blblThresholds= [0, 100, 200]
mt2bbThresholds  = [70,170, 270]

regions_mt2ll = getRegionsFromThresholds('dl_mt2ll', mt2llThresholds)
regions_mt2bb = getRegionsFromThresholds('dl_mt2bb', mt2bbThresholds)
regions_mt2blbl = getRegionsFromThresholds('dl_mt2blbl', mt2blblThresholds)

regions3D = []
for r1 in regions_mt2ll:
    for r2 in regions_mt2bb:
        for r3 in regions_mt2blbl:
            regions3D.append(r1+r2+r3)

normReg = regions3D[0]
regions3D = regions3D[1:]
#{'name':'dl_mt2ll',   'thresholds':[0,100,200]},
#{'name':'dl_mt2blbl', 'thresholds':[0,100,200]},
#{'name':'dl_mt2bb',   'thresholds':[70,170,270]},

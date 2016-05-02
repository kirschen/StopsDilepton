from StopsDilepton.tools.objectSelection import getGenPartsAll

def getGenPtZ(r):
  genparts = getGenPartsAll(r)
  for g in genparts:								# Type 0: no photon
    if g['pdgId'] != 23:        continue					# pdgId == 22 for photons
    if g['status'] != 62:	continue					# status 62 is last gencopy before it decays into ll/nunu
    return g['pt']
  return float('nan')

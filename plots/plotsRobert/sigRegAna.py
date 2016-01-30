import ROOT
from math import sqrt, exp
#helpers
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_postProcessed import *
from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain, getChain
from StopsDilepton.tools.localInfo import plotDir
#Define chains for signals and backgrounds

import pickle
#prefix = "rectangularGrid_dl_mt2ll_dl_mt2blbl_dl_mt2bb"
#prefix = "3D_step50_noDPhiJetMET"
#prefix = '3D_step50_noDPhiJetMET_dl_mt2ll_dl_mt2bb'
#prefix = '3D_step50_noDPhiJetMET_dl_mt2ll_dl_mt2blbl'
#prefix = '3D_step50_noDPhiJetMET_dl_mt2bb_dl_mt2blbl'

#prefix ='optimized_dl_mt2bb_dl_mt2blbl_dl_mt2ll'
#prefix ='optimized_dl_mt2blbl_dl_mt2ll_dl_mt2bb'
prefix ='optimized_dl_mt2ll_dl_mt2bb_dl_mt2blbl'

regions = pickle.load(file('/afs/hephy.at/data/rschoefbeck01/StopsDilepton/regions/'+prefix+'.pkl'))

def sOverB(s,b):
    if b>0:
        return s/b
    else:
        return 0.
def sOverSqrtB(s,b):
    if b>0:
        return s/sqrt(b)
    else:
        return 0.

def maxFOM(r, fom=sOverB):
    return  max([fom(r['sigYields'][s], r['bkgYield']) for s in r['sigYields'].keys()])

goodRegions = filter(lambda r:maxFOM(r, fom=sOverSqrtB)>0.2, regions)
#goodRegions = filter(lambda r:r['bkgYield']>0, regions )
#goodRegions = regions

def getRegionsWithCuts(regions_, cuts_):
    res=[]
    for r in regions_:
        toAdd=True
        for c in cuts_:
            if c not in r['cuts']:
                toAdd=False
                break
        if toAdd:res.append(r)
    return res

def getCutsFromRegions(regions_, var_=None):
    res=[]
    for r in regions_:
        for c in r['cuts']:
            if c not in res:
                if not var_ or c['name']==var_:
                    res.append(c)
    return res

allVars = []
for c in getCutsFromRegions(goodRegions):
    if c['name'] not in allVars:
        allVars.append(c['name'])

def listRecursive(vars=allVars, regions=goodRegions, requiredCuts=[]):
    subRegions = getRegionsWithCuts(regions,  requiredCuts)
    if len(vars)>0:
        var = vars[0]
        remainingVars = vars[1:]
        cuts = getCutsFromRegions(subRegions, var)
#    print "At:", var, "remaining", remainingVars, "looping over",cuts,subRegions, var
        for c in reversed(cuts):
#      print "Looping", c
            listRecursive(remainingVars,  subRegions, requiredCuts+[c])
    else:
        assert len(subRegions)==1,  "Regions not unique!"
        r = subRegions[0]
        print ", ".join([c['name']+":"+str(c['cut']) for c in r['cuts']])

listRecursive()

from StopsDilepton.tools.cardFileWriter import cardFileWriter
c = cardFileWriter.cardFileWriter()
c.defWidth=20
c.precision=6
c.unique=False

limit={}
signals = goodRegions[0]['sigYields'].keys()
for s in reversed(signals):
    c.reset()
    for i, r in enumerate(goodRegions):
        c.addBin('Bin'+str(i), ['bkg'], 'Bin'+str(i))
        bkg = r['bkgYield']
        sig = r['sigYields'][s]
        c.specifyObservation('Bin'+str(i), int(bkg))
        c.specifyExpectation('Bin'+str(i), 'bkg', bkg)
        c.specifyExpectation('Bin'+str(i), 'signal', sig)

    c.addUncertainty('Lumi', 'lnN')
    c.specifyFlatUncertainty('Lumi', 1.2)
#  c.addUncertainty('Systematic', 'lnN')
#  c.specifyFlatUncertainty('Systematic', 1.01)
    c.writeToFile(s+'.txt')
    limit[s] = c.calcLimit()

print prefix
print " ".join(signals)
print [limit[s]['0.500'] for s in signals]

#[3.984375, 10.40625, 8.15625, 1.7265625]
#[3.984375, 10.40625, 8.15625, 1.7265625]
#[3.984375, 10.28125, 7.53125, 1.7265625]


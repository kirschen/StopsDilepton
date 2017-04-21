from StopsDilepton.analysis.MCBasedEstimate              import MCBasedEstimate
from StopsDilepton.analysis.DataDrivenDYEstimate         import DataDrivenDYEstimate
from StopsDilepton.analysis.DataDrivenMultiBosonEstimate import DataDrivenMultiBosonEstimate
from StopsDilepton.analysis.DataDrivenTTZEstimate        import DataDrivenTTZEstimate
from StopsDilepton.analysis.DataDrivenTTJetsEstimate     import DataDrivenTTJetsEstimate
from SetupHelpers import channels 
from Setup import Setup, otherEWKComponents
from StopsDilepton.analysis.Region import Region
setup = Setup()

estimators = {}

# Data-driven estimators
#estimators['DY-DD']           = [DataDrivenDYEstimate( name='DY-DD',         controlRegion=Region('dl_mt2ll', (100,-1)))]
#estimators['multiBoson-DD']   = [DataDrivenMultiBosonEstimate( name='multiBoson-DD', controlRegion=Region('dl_mt2ll', (100,-1)), estimateDY=estimators['DY-DD'][0])]
#estimators['TTZ-DD']          = [DataDrivenTTZEstimate(name='TTZ-DD')]
#estimators['TTZ-DD-Top16009'] = [DataDrivenTTZEstimate(name='TTZ-DD-Top16009', useTop16009=True)]
estimators['TTJets-DD']       = [DataDrivenTTJetsEstimate(name='TTJets-DD', controlRegion=Region('dl_mt2ll', (0,100)))]

#estimators['DY-DD'][0].texName           = "DY"
#estimators['TTZ-DD'][0].texName          = "t#bar{t}Z"
#estimators['TTZ-DD-Top16009'][0].texName = "t#bar{t}Z"
estimators['TTJets-DD'][0].texName       = "t#bar{t}/single-t"
#estimators['multiBoson-DD'][0].texName   = "diboson/triboson"

# main MC based estimators
for mc in ['DY','TTJets','TTZ','multiBoson','other','TTXNoZ','Top_gaussian','Top_nongaussian','Top_fakes']:
  estimators[mc] = [MCBasedEstimate(name=mc, sample=setup.sample[mc])]

# detailed MC based estimators (used for plotting so leave out the small ones)
#estimators['other-detailed']  = [ MCBasedEstimate(name=comp.name, sample={c:comp for c in channels}) for comp in [multiBoson,  TTXNoZ] ]
# estimators['other-detailed'] += [ MCBasedEstimate(name="QCD", sample= {'MuMu': QCD_Mu5, 'EE': QCD_EMbcToE, 'EMu': QCD_Mu5EMbcToE}) ]



# check if all estimators have unique name
estimatorNames = [e.name for eList in estimators.values() for e in eList]
assert len(set(estimatorNames)) == len(estimatorNames), "Names of bkgEstimators are not unique: %s"%",".join(estimatorNames)



# constuct estimator lists
def constructEstimatorList(eList):
  estimatorList = []
  for e in eList:
    estimatorList += estimators[e]
  return estimatorList

allEstimators = constructEstimatorList(estimators.keys())

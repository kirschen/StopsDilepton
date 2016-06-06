from StopsDilepton.analysis.MCBasedEstimate       import MCBasedEstimate
from StopsDilepton.analysis.DataDrivenDYEstimate  import DataDrivenDYEstimate
from StopsDilepton.analysis.DataDrivenTTZEstimate import DataDrivenTTZEstimate
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_postProcessed import *
from SetupHelpers import channels 
from Setup import Setup, otherEWKComponents
setup = Setup()

estimators = {}

# Data-driven estimators
estimators['DY-DD']           = [DataDrivenDYEstimate( name='DY-DD')]
estimators['TTZ-DD']          = [DataDrivenTTZEstimate(name='TTZ-DD')]
estimators['TTZ-DD-Top16009'] = [DataDrivenTTZEstimate(name='TTZ-DD-Top16009', useTop16009=True)]

# main MC based estimators
for mc in ['DY','TTJets','TTZ','other']:
  estimators[mc] = [MCBasedEstimate(name=mc, sample=setup.sample[mc])]

# detailed MC based estimators
estimators['other-detailed']  = [ MCBasedEstimate(name=comp.name, sample={c:comp for c in channels}) for comp in otherEWKComponents ]
estimators['other-detailed'] += [ MCBasedEstimate(name="QCD", sample= {'MuMu': QCD_Mu5, 'EE': QCD_EMbcToE, 'EMu': QCD_Mu5EMbcToE}) ]



# check if all estimators have unique name
estimatorNames = [e.name for eList in estimators.values() for e in eList]
assert len(set(estimatorNames)) == len(estimatorNames), "Names of bkgEstimators are not unique: %s"%",".join(estimatorNames)



# constuct estimator lists
def constructEstimatorList(mcList):
  estimatorList = []
  for mc in mcList:
    estimatorList += estimators[mc]
  return estimatorList

#defaultAnalysisEstimators = constructEstimatorList(['DY-DD','TTZ-DD','TTJets','other'])
mcAnalysisEstimators      = constructEstimatorList(['DY',   'TTZ',   'TTJets','other'])
mcDetailedEstimators      = constructEstimatorList(['DY',   'TTZ',   'TTJets','other-detailed'])
allEstimators             = constructEstimatorList(estimators.keys())

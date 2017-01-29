#
# Trilepton selections for TTZ CR
#
from StopsDilepton.tools.objectSelection import muonSelectorString,eleSelectorString
def getLeptonString(nMu, nE):
  return muonSelectorString(ptCut=10, relIso03 = 0.12) + "==" + str(nMu) + "&&" + eleSelectorString(ptCut=10, eleId = 3, relIso03=0.12) + "==" + str(nE)

def getPtThresholdString(firstPt, secondPt, thirdPt):
    return "&&".join([muonSelectorString(ptCut=firstPt,  relIso03=0.12) + "+" + eleSelectorString(ptCut=firstPt,  relIso03=0.12) + ">=1",
                      muonSelectorString(ptCut=secondPt, relIso03=0.12) + "+" + eleSelectorString(ptCut=secondPt, relIso03=0.12) + ">=2",
                      muonSelectorString(ptCut=thirdPt,  relIso03=0.12) + "+" + eleSelectorString(ptCut=thirdPt,  relIso03=0.12) + ">=2"])

def getTrilepSelection(mode, higherPtCuts = False):
  if   mode=="3mu":   return "&&".join([getLeptonString(3, 0), getPtThresholdString(40, 20, 20) if higherPtCuts else getPtThresholdString(40, 20, 10)])
  elif mode=="2mu1e": return "&&".join([getLeptonString(2, 1), getPtThresholdString(40, 20, 20) if higherPtCuts else getPtThresholdString(40, 20, 10)])
  elif mode=="2e1mu": return "&&".join([getLeptonString(1, 2), getPtThresholdString(40, 20, 20) if higherPtCuts else getPtThresholdString(40, 20, 10)])
  elif mode=="3e":    return "&&".join([getLeptonString(0, 3), getPtThresholdString(40, 20, 20) if higherPtCuts else getPtThresholdString(40, 20, 10)])

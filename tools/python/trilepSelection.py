#
# Trilepton selections for TTZ CR
#

'Sum$(lep_pt>20&&abs(lep_eta)<2.4&&lep_pfRelIso03_all<0.12)>2&&l1_pt>40&&l2_pt>20'




from StopsDilepton.tools.objectSelection import muonSelectorString,eleSelectorString
def getLeptonString(nMu, nE):
  return "Sum$(lep_pt>10&&abs(lep_eta)<2.4&&lep_pfRelIso03_all<0.12&&abs(lep_pdgId)==13)==" + str(nMu) + "&&" + "Sum$(lep_pt>10&&abs(lep_eta)<2.4&&lep_pfRelIso03_all<0.12&&abs(lep_pdgId)==11)==" + str(nE)

def getPtThresholdString(firstPt, secondPt, thirdPt):
    return "(l1_pt>%s&&l1_relIso03<0.12) && (l2_pt>%s&&l2_relIso03<0.12) && Sum$(lep_pt>%s&&abs(lep_eta)<2.4&&lep_pfRelIso03_all<0.12)>2"%(firstPt,secondPt,thirdPt)

def getTrilepSelection(mode):
  if   mode=="3mu":   return "&&".join([getLeptonString(3, 0), getPtThresholdString(40, 20, 20) ])
  elif mode=="2mu1e": return "&&".join([getLeptonString(2, 1), getPtThresholdString(40, 20, 20) ])
  elif mode=="2e1mu": return "&&".join([getLeptonString(1, 2), getPtThresholdString(40, 20, 20) ])
  elif mode=="3e":    return "&&".join([getLeptonString(0, 3), getPtThresholdString(40, 20, 20) ])

import ROOT
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.analysis.u_float import u_float
import os
from math import sqrt

keys_mu  = [("TnP_NUM_MediumID_DENOM_generalTracks_VAR_map_pt_eta.root", "SF"),
            ("TnP_NUM_TightIP2D_DENOM_MediumID_VAR_map_pt_eta.root",     "SF"),
            ("TnP_NUM_TightIP3D_DENOM_MediumID_VAR_map_pt_eta.root",     "SF"),
            ("ratio_NUM_RelIsoVTight_DENOM_MediumID_VAR_map_pt_eta_v2.root","pt_abseta_ratio")]

keys_ele = [("scaleFactors.root", "GsfElectronToCutBasedStopsDilepton"),
            ("scaleFactors.root", "CutBasedStopsDileptonToRelIso012")]

class leptonSF:
    def __init__(self):
        self.dataDir = "$CMSSW_BASE/src/StopsDilepton/tools/data/leptonSFData"

        self.mu  = [getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, file)), key) for (file, key) in keys_mu]
        self.ele = [getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, file)), key) for (file, key) in keys_ele]
        for effMap in self.mu + self.ele: assert effMap

    def getPartialSF(self, effMap, pt, eta):
	sf  = effMap.GetBinContent(effMap.GetXaxis().FindBin(pt), effMap.GetYaxis().FindBin(abs(eta)))
	err = effMap.GetBinError(  effMap.GetXaxis().FindBin(pt), effMap.GetYaxis().FindBin(abs(eta)))
        return u_float(sf, err)

    def mult(self, list):
        res = list[0]
        for i in list[1:]: res = res*i
        return res

    def getSF(self, pdgId, pt, eta, sigma=0):
        if abs(pdgId)==13:   
          if pt >= 120: pt = 119 # last bin is valid to infinity
          sf = self.mult([self.getPartialSF(effMap, pt, eta) for effMap in self.mu])
        elif abs(pdgId)==11:
          if pt >= 200: pt = 199 # last bin is valid to infinity
          sf = self.mult([self.getPartialSF(effMap, pt, eta) for effMap in self.ele])
        else: 
          raise Exception("Lepton SF for PdgId %i not known"%pdgId)

        return (1+sf.sigma*sigma)*sf.val

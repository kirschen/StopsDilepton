'''
Material from https://twiki.cern.ch/twiki/bin/view/CMS/SUSLeptonSF#Scale_Factors_for_2018_Data
- relIso SFs missing
- muon SFs for 2018 missing
- old muon SFs for 2016

'''

import ROOT
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.analysis.u_float import u_float
import os
from math import sqrt


class leptonSF:
    def __init__(self, year):

        # default assumptions
        self.mu_x_is_pt  = True
        self.mu_abs_eta  = True
        self.ele_x_is_pt = False
        self.ele_abs_eta = False

        if year == 2016:
            keys_mu  = [("MuonRun2016_MediumID.root", "SF")]
            keys_ele = [("ElectronScaleFactors_Run2016.root", "Run2016_CutBasedTightNoIso94XV2")]
        elif year == 2017:
            keys_mu  = [("MuonRun2017BCDEF_SF_ID.root", "NUM_MediumID_DEN_genTracks_pt_abseta")]
            keys_ele = [("ElectronScaleFactors_Run2017.root", "Run2017_CutBasedTightNoIso94XV2")]
        elif year == 2018:
            keys_mu  = [("MuonRun2018_MediumID.root", "SF2D")]
            self.mu_x_is_pt = False # for the 2018 histo, pt and eta are reversed!
            keys_ele = [("ElectronScaleFactors_Run2018.root", "Run2018_CutBasedTightNoIso94XV2")]
        
        self.dataDir = "$CMSSW_BASE/src/StopsDilepton/tools/data/leptonSFData"

        self.mu  = [getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, file)), key) for (file, key) in keys_mu]
        self.ele = [getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, file)), key) for (file, key) in keys_ele]
        for effMap in self.mu + self.ele: assert effMap

    def getPartialSF(self, effMap, pt, eta):

        bin_x, bin_y = effMap.GetXaxis().FindBin(pt), effMap.GetYaxis().FindBin(eta)
        sf  = effMap.GetBinContent(bin_x, bin_y)
        err = effMap.GetBinError  (bin_x, bin_y)
        return u_float(sf, err)

    def mult(self, list):
        res = list[0]
        for i in list[1:]: res = res*i
        return res

    def getSF(self, pdgId, pt, eta, sigma=0):
        # protection for the abs(eta)=2.4 case
        if eta >= 2.4:  eta = 2.39
        if eta <= -2.4: eta = -2.39

        if abs(pdgId)==13:   
          if pt >= 120: pt = 119 # last bin is valid to infinity
          eta_ = abs(eta) if self.mu_abs_eta else eta
          sf   = self.mult([ self.getPartialSF(effMap, pt, eta_) if self.mu_x_is_pt else self.getPartialSF(effMap, eta_, pt) for effMap in self.mu])
          sf.sigma = 0.03 # Recommendation for Moriond17
        elif abs(pdgId)==11:
          if pt >= 500: pt = 499 # last bin is valid to infinity
          eta_ = abs(eta) if self.ele_abs_eta else eta
          sf   = self.mult([self.getPartialSF(effMap, pt, eta_) if self.ele_x_is_pt else self.getPartialSF(effMap, eta_, pt) for effMap in self.ele]) # eta/pt are intentionally mixed up because the 2D hists are the other way around... don't even ask
        else: 
          raise Exception("Lepton SF for PdgId %i not known"%pdgId)

        return (1+sf.sigma*sigma)*sf.val

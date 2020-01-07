'''
Lepton Full/Fast SF SUS 2016-18
Material from https://twiki.cern.ch/twiki/bin/view/CMS/SUSLeptonSF
'''

import ROOT
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.tools.u_float import u_float
import os
from math import sqrt

class leptonFastSimSF:
    def __init__(self, year):

        # default assumptions
        self.mu_x_is_pt  = True
        self.mu_abs_eta  = True
        self.mu_max_pt   = 120
        self.ele_x_is_pt = True
        self.ele_abs_eta = True
        self.ele_max_pt  = 200

        if year == 2016:
            self.mu_max_pt   = 200
            keys_mu  = [("2016_FastSim_sf_mu_mediumID.root", "histo2D"),
                        ("2016_FastSim_sf_mu_mediumID_mini02.root", "histo2D")]
            keys_ele = [("2016_FastSim_sf_el_mediumCB.root", "histo2D"),
                        ("2016_FastSim_sf_el_mini01.root", "histo2D") ]
        elif year == 2017:
            self.mu_max_pt   = 500
            keys_mu  = [("2017_FastSim_detailed_mu_full_fast_sf_17.root", "miniIso02_MediumId_sf"),]
                       # ("", "")]
            self.ele_x_is_pt = False 
            self.ele_abs_eta = False 
            self.ele_max_pt  = 500
            keys_ele = [("2017_FastSim_detailed_ele_full_fast_sf_17.root", "CutBasedMediumNoIso94XV2_sf"),]
                       # ("2017_FastSim_detailed_ele_full_fast_sf_17.root", "")]
        elif year == 2018:
            keys_mu  = [("2018_FastSim_detailed_mu_full_fast_sf_18.root", "miniIso02_MediumId_sf"),]
                       # ("", "")]
            self.ele_x_is_pt = False 
            self.ele_abs_eta = False 
            self.ele_max_pt  = 500
            keys_ele = [("2018_FastSim_detailed_ele_full_fast_sf_18.root", "CutBasedMediumNoIso94XV2_sf"),
                        ("fastSimSF_2018.root", "eff_pt_eta")]
        
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

    def getSF(self, pdgId, pt, eta):
        # protection for the abs(eta)=2.4 case
        if eta >= 2.4:  eta = 2.39
        if eta <= -2.4: eta = -2.39

        if abs(pdgId)==13:   
          if pt >= self.mu_max_pt: pt = self.mu_max_pt-1 # last bin is valid to infinity
          eta_ = abs(eta) if self.mu_abs_eta else eta
          sf   = self.mult([ self.getPartialSF(effMap, pt, eta_) if self.mu_x_is_pt else self.getPartialSF(effMap, eta_, pt) for effMap in self.mu])
          #sf.sigma = 0.03 # Recommendation for Moriond17
        elif abs(pdgId)==11:
          if pt >= self.ele_max_pt: pt = self.ele_max_pt-1 # last bin is valid to infinity
          eta_ = abs(eta) if self.ele_abs_eta else eta
          sf   = self.mult([self.getPartialSF(effMap, pt, eta_) if self.ele_x_is_pt else self.getPartialSF(effMap, eta_, pt) for effMap in self.ele])
        else: 
          raise Exception("Lepton SF for PdgId %i not known"%pdgId)

        return sf.val, (1-sf.sigma)*sf.val, (1+sf.sigma)*sf.val 

if __name__ == "__main__":
    sf_2016 = leptonFastSimSF( year = 2016 )
    sf_2017 = leptonFastSimSF( year = 2017 )
    sf_2018 = leptonFastSimSF( year = 2018 )

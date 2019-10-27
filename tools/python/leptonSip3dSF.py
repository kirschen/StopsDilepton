'''
Lepton SF SUS 2016-18
Material from https://twiki.cern.ch/twiki/bin/view/CMS/SUSLeptonSF
'''

import ROOT
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.tools.u_float import u_float
import os
from math import sqrt

class leptonSip3dSF:
    def __init__(self, year):

        # default assumptions
        self.mu_x_is_pt  = None 
        self.mu_abs_eta  = None
        self.mu_max_pt   = None
        self.ele_x_is_pt = False
        self.ele_abs_eta = False
        self.ele_max_pt  = 200

        if   year == 2016:
            keys_mu  = []
            keys_ele = [("2016_effRatio_dataMC_trailing_ele_sip3Dlt4.root", "eff_num_trailing_ele_sip3Dlt4_data_16f8bdfe_ee41_4983_96db_f4619d91fcb0_clone"),
                         ]
        elif year == 2017:
            keys_mu  = []
            keys_ele = [("2017_effRatio_dataMC_trailing_ele_sip3Dlt4.root", "eff_num_trailing_ele_sip3Dlt4_data_ae79fb2d_b05d_4a82_8492_5e473de41ba3_clone"),
                        ]
        elif year == 2018:
            keys_mu  = [] 
            keys_ele = [("2018_effRatio_dataMC_trailing_ele_sip3Dlt4.root", "eff_num_trailing_ele_sip3Dlt4_data_2b6e3ced_f085_4bac_b2b0_bba16b6fb8ea_clone"),
                        ]
        
        self.dataDir = "$CMSSW_BASE/src/StopsDilepton/tools/data/leptonSFData"

        self.mu  = []
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
          return 1.0, 1.0, 1.0 # so far we only have extra ele SF 
        elif abs(pdgId)==11:
          if pt >= self.ele_max_pt: pt = self.ele_max_pt-1 # last bin is valid to infinity
          eta_ = abs(eta) if self.ele_abs_eta else eta
          sf   = self.mult([self.getPartialSF(effMap, pt, eta_) if self.ele_x_is_pt else self.getPartialSF(effMap, eta_, pt) for effMap in self.ele])
        else: 
          raise Exception("Lepton SF for PdgId %i not known"%pdgId)

        return sf.val, (1-sf.sigma)*sf.val, (1+sf.sigma)*sf.val 

if __name__ == "__main__":
    sf_2016 = leptonSip3dSF( year = 2016 )
    sf_2017 = leptonSip3dSF( year = 2017 )
    sf_2018 = leptonSip3dSF( year = 2018 )

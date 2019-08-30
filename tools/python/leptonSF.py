'''
Lepton SF SUS 2016-18
Material from https://twiki.cern.ch/twiki/bin/view/CMS/SUSLeptonSF
'''

import ROOT
from StopsDilepton.tools.helpers import getObjFromFile
from StopsDilepton.tools.u_float import u_float
import os
from math import sqrt

class leptonSF:
    def __init__(self, year):

        # default assumptions
        self.mu_x_is_pt  = True
        self.mu_abs_eta  = True
        self.mu_max_pt   = 120
        self.ele_x_is_pt = True
        self.ele_abs_eta = True
        self.ele_max_pt  = 200

        if   year == 2016:
            keys_mu  = [ ("2016_TnP_NUM_MediumID_DENOM_generalTracks_VAR_map_pt_eta.root",  "SF"),
                         ("2016_TnP_NUM_MiniIsoTight_DENOM_MediumID_VAR_map_pt_eta.root",   "SF")]
            keys_ele = [ ("2016_electrons_scaleFactors.root",       "GsfElectronToCutBasedSpring15T"),
                         ("2016_electrons_scaleFactors.root",       "MVAVLooseElectronToMini2") ]
        elif year == 2017:
            keys_mu  = [("2017_Muons_RunBCDEF_SF_ID.root",         "NUM_MediumID_DEN_genTracks_pt_abseta"),
                        ("2017_Muon_MiniIso02_vs_Medium_SF.root",  "TnP_MC_NUM_MiniIso02Cut_DEN_MediumID_PAR_pt_eta")]
            self.ele_x_is_pt = False 
            self.ele_abs_eta = False 
            self.ele_max_pt  = 500
            keys_ele = [("2017_ElectronScaleFactors_Run2017.root", "Run2017_CutBasedTightNoIso94XV2"),
                        ("2017_ElectronScaleFactors_Run2017.root", "Run2017_MVAVLooseTightIP2DMini")]
        elif year == 2018:
            keys_mu  = [("2018_Muon_RunABCD_SF_ID.root",           "NUM_MediumID_DEN_TrackerMuons_pt_abseta"),
                        ("2017_Muon_MiniIso02_vs_Medium_SF.root",  "TnP_MC_NUM_MiniIso02Cut_DEN_MediumID_PAR_pt_eta")] # 2017 Iso SF are recommended
            self.ele_x_is_pt = False 
            self.ele_abs_eta = False 
            self.ele_max_pt  = 500
            keys_ele = [("2018_ElectronScaleFactors_Run2018.root", "Run2018_CutBasedTightNoIso94XV2"),
                        ("2018_ElectronScaleFactors_Run2018.root", "Run2018_Mini")]
        
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
    sf_2016 = leptonSF( year = 2016 )
    sf_2017 = leptonSF( year = 2017 )
    sf_2018 = leptonSF( year = 2018 )

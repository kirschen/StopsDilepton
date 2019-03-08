import ROOT
from StopsDilepton.tools.helpers import getObjFromFile
import os

basedir = "$CMSSW_BASE/src/StopsDilepton/tools/data/triggerEff/"

#OR of all backput triggers


class triggerEfficiency:
    def __init__(self, year):

        if year == 2016:
            ee_trigger_SF   = basedir+'Run2016_HLT_ee_measuredInMET_v1.root'
            mue_trigger_SF  = basedir+'Run2016_HLT_muEle_measuredInMET_v1.root'
            mumu_trigger_SF = basedir+'Run2016_HLT_mm_measuredInMET_v1.root'
        elif year == 2017:
            ee_trigger_SF   = basedir+'Run2017_HLT_ee_measuredInMET_v1.root'
            mue_trigger_SF  = basedir+'Run2017_HLT_muEle_measuredInMET_v1.root'
            mumu_trigger_SF = basedir+'Run2017_HLT_mm_measuredInMET_v1.root'
        elif year == 2018:
            ee_trigger_SF   = basedir+'Run2018_HLT_ee_measuredInMET_v1.root'
            mue_trigger_SF  = basedir+'Run2018_HLT_muEle_measuredInMET_v1.root'
            mumu_trigger_SF = basedir+'Run2018_HLT_mm_measuredInMET_v1.root'

        self.mumu_highEta   = getObjFromFile(os.path.expandvars(mumu_trigger_SF),   "eff_pt1_pt2_highEta1")
        self.mumu_lowEta    = getObjFromFile(os.path.expandvars(mumu_trigger_SF),   "eff_pt1_pt2_lowEta1")
        self.ee_highEta     = getObjFromFile(os.path.expandvars(ee_trigger_SF),     "eff_pt1_pt2_highEta1")
        self.ee_lowEta      = getObjFromFile(os.path.expandvars(ee_trigger_SF),     "eff_pt1_pt2_lowEta1")
        self.mue_highEta    = getObjFromFile(os.path.expandvars(mue_trigger_SF),    "eff_pt1_pt2_highEta1")
        self.mue_lowEta     = getObjFromFile(os.path.expandvars(mue_trigger_SF),    "eff_pt1_pt2_lowEta1")

        h_ = [self.mumu_highEta, self.mumu_lowEta, self.ee_highEta, self.ee_lowEta, self.mue_highEta, self.mue_lowEta]
        assert False not in [bool(x) for x in h_], "Could not load trigger SF: %r"%h_

        self.ptMax = self.mumu_highEta.GetXaxis().GetXmax()

    def __getSF(self, map_, pt1, pt2):
        if pt1>self.ptMax: pt1=self.ptMax - 1 
        if pt2>self.ptMax: pt2=self.ptMax - 1 
        val = map_.GetBinContent( map_.FindBin(pt1, pt2) )
        valErr = map_.GetBinError( map_.FindBin(pt1, pt2) )
        return (val, valErr)

    def getSF(self, pt1, eta1, pdgId1, pt2, eta2, pdgId2):

        if pt1<pt2:
            raise ValueError ( "Sort leptons wrt pt." )
#            pt1, eta1, pdgId1, pt2, eta2, pdgId2 = pt2, eta2, pdgId2, pt1, eta1, pdgId1

        #Split in low/high eta of leading lepton for both, ee and mumu channel 
        if abs(pdgId1)==abs(pdgId2)==13:
            if abs(eta1)<1.5:
                return self.__getSF(self.mumu_lowEta, pt1, pt2)
            else:
                return self.__getSF(self.mumu_highEta, pt1, pt2)
        elif abs(pdgId1)==abs(pdgId2)==11:
            if abs(eta1)<1.5:
                return self.__getSF(self.ee_lowEta, pt1, pt2)
            else:
                return self.__getSF(self.ee_highEta, pt1, pt2)
        #Split in low/high eta of muon for emu channel 
        elif abs(pdgId1)==13 and abs(pdgId2)==11:
            if abs(eta1)<1.5: 
                return self.__getSF(self.mue_lowEta, pt1, pt2)
            else:
                return self.__getSF(self.mue_highEta, pt1, pt2)
        elif abs(pdgId1)==11 and abs(pdgId2)==13:
            if abs(eta1)<1.5: 
                return self.__getSF(self.mue_lowEta, pt1, pt2)
            else:
                return self.__getSF(self.mue_highEta, pt1, pt2)
        raise ValueError( "Did not find trigger SF for pt1 %3.2f eta %3.2f pdgId1 %i pt2 %3.2f eta2 %3.2f pdgId2 %i"%( pt1, eta1, pdgId1, pt2, eta2, pdgId2 ) )
        


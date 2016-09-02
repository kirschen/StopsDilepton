import ROOT
from StopsDilepton.tools.helpers import getObjFromFile
import os

#https://twiki.cern.ch/twiki/bin/view/CMS/SUSLeptonSFMC#How_to_retrieve_SF_and_stat_unce

muSFFile = "sf_mu_stop"
eleSFFile = "sf_el_stop"

class leptonFastSimSF:
    def __init__(self):
        self.dataDir = "$CMSSW_BASE/src/StopsDilepton/tools/data/leptonFastSimSFData"
        muFileName = os.path.join(self.dataDir, muSFFile+'.root')
        eleFileName = os.path.join(self.dataDir, eleSFFile+'.root')

        self.mu2D = getObjFromFile(os.path.expandvars(muFileName), "histo2D")
        assert self.mu2D, "Could not load 'histo2D' from %s"%os.path.expandvars(muFileName)
        self.ele2D = getObjFromFile(os.path.expandvars(eleFileName), "histo2D")
        assert self.ele2D, "Could not load 'histo2D' from %s"%os.path.expandvars(eleFileName)
        print "Loaded lepton SF file for muons:     %s"%muFileName
        print "Loaded lepton SF file for electrons: %s"%eleFileName
#    print self.mu2D, os.path.expandvars(muFileName)
#    print self.ele2D, os.path.expandvars(eleFileName)

    def get2DSFUnc(self, pdgId, pt):
        if abs(pdgId)==13:
            return 0.01
        elif abs(pdgId)==11:
            return 0.05
        else:
            raise Exception("FastSim SF Unc for PdgId %i not known"%pdgId)

    def get2DSF(self, pdgId, pt, eta, nvtx, sigma=0):
        if abs(pdgId)==13:
            res = (1+self.get2DSFUnc(pdgId, pt)*sigma)*self.mu2D.GetBinContent(self.mu2D.GetXaxis().FindBin(pt), self.mu2D.GetYaxis().FindBin(abs(eta)))
        elif abs(pdgId)==11:
            res = (1+self.get2DSFUnc(pdgId, pt)*sigma)*self.ele2D.GetBinContent(self.ele2D.GetXaxis().FindBin(pt), self.ele2D.GetYaxis().FindBin(abs(eta)))
        else:
            raise Exception("FastSim SF for PdgId %i not known"%pdgId)
        if res==0: res=1 #no SF for |eta|>2.19 for electrons?
        return res

#fastSimSF = FastSimSF()
#print fastSimSF.get2DSF(11, 1000,0,20), fastSimSF.get2DSF(13, 1000,0,20)

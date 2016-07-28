import ROOT
from StopsDilepton.tools.helpers import getObjFromFile
import os

#https://twiki.cern.ch/twiki/bin/view/CMS/SUSLeptonSFMC#How_to_retrieve_SF_and_stat_unce

muSFFile = "sf_mu_mediumID_mini02"
eleSFFile = "sf_el_tight_mini01" #FIXME!!! This is not quite appropriate but there are no mRelIso 0.2 ele SF

class leptonFastSimSF:
    def __init__(self):
        self.dataDir = "$CMSSW_BASE/src/StopsDilepton/tools/data/leptonFastSimSFData"
        muFileName = os.path.join(self.dataDir, muSFFile+'.root')
        eleFileName = os.path.join(self.dataDir, eleSFFile+'.root')

        self.mu3D = getObjFromFile(os.path.expandvars(muFileName), "histo3D")
        assert self.mu3D, "Could not load 'histo3D' from %s"%os.path.expandvars(muFileName)
        self.ele3D = getObjFromFile(os.path.expandvars(eleFileName), "histo3D")
        assert self.ele3D, "Could not load 'histo3D' from %s"%os.path.expandvars(eleFileName)
        print "Loaded lepton SF file for muons:     %s"%muFileName
        print "Loaded lepton SF file for electrons: %s"%eleFileName
#    print self.mu3D, os.path.expandvars(muFileName)
#    print self.ele3D, os.path.expandvars(eleFileName)

    def get3DSFUnc(self, pdgId, pt):
        if abs(pdgId)==13:
            return 0.01
        elif abs(pdgId)==11:
            return 0.05
        else:
            raise Exception("FastSim SF Unc for PdgId %i not known"%pdgId)

    def get3DSF(self, pdgId, pt, eta, nvtx, sigma=0):
        if abs(pdgId)==13:
            res = (1+self.get3DSFUnc(pdgId, pt)*sigma)*self.mu3D.GetBinContent(self.mu3D.GetXaxis().FindBin(pt), self.mu3D.GetYaxis().FindBin(abs(eta)), self.mu3D.GetZaxis().FindBin(nvtx))
        elif abs(pdgId)==11:
            res = (1+self.get3DSFUnc(pdgId, pt)*sigma)*self.ele3D.GetBinContent(self.ele3D.GetXaxis().FindBin(pt), self.ele3D.GetYaxis().FindBin(abs(eta)), self.ele3D.GetZaxis().FindBin(nvtx))
        else:
            raise Exception("FastSim SF for PdgId %i not known"%pdgId)
        if res==0: res=1 #no SF for |eta|>2.19 for electrons?
        return res

#fastSimSF = FastSimSF()
#print fastSimSF.get3DSF(11, 1000,0,20), fastSimSF.get3DSF(13, 1000,0,20)

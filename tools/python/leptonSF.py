import ROOT
from StopsDilepton.tools.helpers import getObjFromFile
import os
from math import sqrt

file_muId     = "TnP_MuonID_NUM_MediumID_DENOM_generalTracks_VAR_map_pt_eta.root"
file_muIso    = "TnP_MuonID_NUM_MultiIsoVT_DENOM_MediumID_VAR_map_pt_eta.root"
file_eleId    = "scaleFactors.root"
file_eleIso   = "scaleFactors.root"

key_muId      = "pt_abseta_PLOT_pair_probeMultiplicity_bin0"
key_muIso     = "pt_abseta_PLOT_pair_probeMultiplicity_bin0_&_Medium2016_pass"
key_eleId     = "GsfElectronToTight"
key_eleIso    = "CutBasedTightElectronToMultiIsoVT"

class leptonSF:
    def __init__(self):
        self.dataDir = "$CMSSW_BASE/src/StopsDilepton/tools/data/leptonSFData"

        self.muId   = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, file_muId)),   key_muId)
        self.muIso  = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, file_muIso)),  key_muIso)
        self.eleId  = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, file_eleId)),  key_eleId)
        self.eleIso = getObjFromFile(os.path.expandvars(os.path.join(self.dataDir, file_eleIso)), key_eleIso)
        assert self.muId
        assert self.muIso
        assert self.eleId
        assert self.eleIso

    def getSF(self, pdgId, pt, eta, sigma=0):
        if abs(pdgId)==13: 
	  sf_id      = self.muId.GetBinContent( self.muId.GetXaxis().FindBin(pt),  self.muId.GetYaxis().FindBin(abs(eta)))
	  sf_id_err  = self.muId.GetBinError(   self.muId.GetXaxis().FindBin(pt),  self.muId.GetYaxis().FindBin(abs(eta)))
	  sf_iso     = self.muIso.GetBinContent(self.muIso.GetXaxis().FindBin(pt), self.muIso.GetYaxis().FindBin(abs(eta)))
	  sf_iso_err = self.muIso.GetBinError(  self.muIso.GetXaxis().FindBin(pt), self.muIso.GetYaxis().FindBin(abs(eta)))
        elif abs(pdgId)==11:
          if pt >= 200: pt = 199 # last bin is valid to infinity
	  sf_id      = self.eleId.GetBinContent( self.eleId.GetXaxis().FindBin(pt),  self.eleId.GetYaxis().FindBin(abs(eta)))
	  sf_id_err  = self.eleId.GetBinError(   self.eleId.GetXaxis().FindBin(pt),  self.eleId.GetYaxis().FindBin(abs(eta)))
	  sf_iso     = self.eleIso.GetBinContent(self.eleIso.GetXaxis().FindBin(pt), self.eleIso.GetYaxis().FindBin(abs(eta)))
	  sf_iso_err = self.eleIso.GetBinError(  self.eleIso.GetXaxis().FindBin(pt), self.eleIso.GetYaxis().FindBin(abs(eta)))
        else:
            raise Exception("FastSim SF for PdgId %i not known"%pdgId)

        sf         = sf_id*sf_iso
        sf_err     = sqrt(sf_id_err*sf_id_err + sf_iso_err*sf_iso_err)

        return (1+sf_err*sigma)*sf

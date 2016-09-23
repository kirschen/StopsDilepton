''' Interface to Optimass M2 variables
'''
import ROOT, array

# Optimass include path and library
ROOT.gSystem.AddIncludePath(" -I$CMSSW_BASE/src/OptiMass-v1.0.3/include/alm_base/ ");
ROOT.gSystem.AddIncludePath(" -I$CMSSW_BASE/src/OptiMass-v1.0.3/model/dict_src/ ");
ROOT.gSystem.AddLinkedLibs("$CMSSW_BASE/src/OptiMass-v1.0.3/lib/libOptiMass.a")

# Compile model file and wrapper
ROOT.gROOT.ProcessLine(".L $CMSSW_BASE/src/OptiMass-v1.0.3/model/dict_src/TTbar_AB.cpp+")
ROOT.gROOT.ProcessLine(".L $CMSSW_BASE/src/StopsDilepton/tools/scripts/m2Wrapper.cpp+")

from math import pi, sqrt, cos, sin

class m2Calculator:

    def __init__(self):
        self.m2Wrapper = ROOT.m2Wrapper()
        self.leptonMass = 0.
        self.bjetMass = 0.
        self.reset()
        self.verbose = False

    def reset(self):
        self.met=None
        self.lepton1=None
        self.lepton2=None
        self.bjet1=None
        self.bjet2=None

#Setters
    def setMet(self, pt, phi):
        self.met = ROOT.TVector2(pt*cos(phi), pt*sin(phi))
    def setLepton1(self, pt1, eta1, phi1):
        self.lepton1 = ROOT.TLorentzVector()
        self.lepton1.SetPtEtaPhiM(pt1, eta1, phi1, self.leptonMass)
    def setLepton2(self, pt2, eta2, phi2):
        self.lepton2 = ROOT.TLorentzVector()
        self.lepton2.SetPtEtaPhiM(pt2, eta2, phi2, self.leptonMass)
    def setLeptons(self, pt1, eta1, phi1, pt2, eta2, phi2):
        self.setLepton1(pt1,eta1,phi1)
        self.setLepton2(pt2,eta2,phi2)
    def setBJet1(self, pt1, eta1, phi1):
        self.bjet1 = ROOT.TLorentzVector()
        self.bjet1.SetPtEtaPhiM(pt1, eta1, phi1, self.bjetMass)
    def setBJet2(self, pt2, eta2, phi2):
        self.bjet2 = ROOT.TLorentzVector()
        self.bjet2.SetPtEtaPhiM(pt2, eta2, phi2, self.bjetMass)
    def setBJets(self, pt1, eta1, phi1, pt2, eta2, phi2):
        self.setBJet1(pt1,eta1,phi1)
        self.setBJet2(pt2,eta2,phi2)

#M2CC
    def m2CC(self):
        # Check inputs
        assert self.met and self.lepton1 and self.lepton2 and self.bjet1 and self.bjet2, "Incomplete specification, need met/lepton1/lepton2/bjet1/bjet2"

        # control verbosity
        self.m2Wrapper.verbose = self.verbose

        # set log level to warnings to suppress Minuit2 
        errorLevel = ROOT.gErrorIgnoreLevel
        ROOT.gErrorIgnoreLevel = 1001

        # Calculate result
        result = self.m2Wrapper.calcM2( self.lepton1, self.lepton2, self.bjet1, self.bjet2, self.met, ROOT.m2Wrapper.M2CC )

        # reset logLevel
        ROOT.gErrorIgnoreLevel = errorLevel

        return result        

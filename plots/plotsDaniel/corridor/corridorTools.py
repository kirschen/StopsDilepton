import ROOT
import os
import numpy as np
import math
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module



class corridorTools(Module):

    def __init__(self):
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("nGenElectrons", "I")
        self.out.branch("nGenElectrons_reconstructed", "I")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def isGoodMuon(self, muon):
        if muon.pt > 20 and muon.mediumId and abs(muon.eta)<2.4 and muon.pfRelIso03_all < 0.2:
            return True
        else:
            return False

    def isGoodElectron(self, electron):
        if electron.pt > 20 and electron.cutBased >= 4 and abs(electron.eta) < 2.4 and electron.pfRelIso03_all < 0.15 and electron.sip3d < 4.0 and abs(electron.dxy) < 0.05 and abs(electron.dz) < 0.1:
            return True
        else:
            return False

    def findBestZcandidate(self, leptons):
        mZ = 91.2
        inds = range(len(leptons))
        vecs = [ ROOT.TLorentzVector() for i in inds ]
        for i, v in enumerate(vecs):
            v.SetPtEtaPhiM(leptons[i].pt, leptons[i].eta, leptons[i].phi, 0.)
        dlMasses = [((vecs[comb[0]] + vecs[comb[1]]).M(), comb[0], comb[1])  for comb in itertools.combinations(inds, 2) if leptons[comb[0]].pdgId*leptons[comb[1]].pdgId < 0 and abs(leptons[comb[0]].pdgId) == abs(leptons[comb[1]].pdgId) ]
        return min(dlMasses, key=lambda (m,i1,i2):abs(m-mZ)) if len(dlMasses)>0 else (float('nan'), -1, -1)

    def deltaPhi(self, phi1, phi2):
        dphi = phi2-phi1
        if  dphi > math.pi:
            dphi -= 2.0*math.pi
        if dphi <= -math.pi:
            dphi += 2.0*math.pi
        return abs(dphi)

    def deltaR2(self, l1, l2):
        return self.deltaPhi(l1.phi, l2.phi)**2 + (l1.eta - l2.eta)**2

    def deltaR(self, l1, l2):
        return math.sqrt(self.deltaR2(l1,l2))

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        muons       = Collection(event, "Muon")
        electrons   = Collection(event, "Electron")
        jets        = Collection(event, "Jet")
        genParts    = Collection(event, "GenPart")

        nGenElectrons = 0
        nGenElectrons_reconstructed = 0

        for part in genParts:
            if abs(part.pdgId)==11 and part.status==23 and part.pt>10 and part.pt<50 and abs(part.eta) < 2.4:
                nGenElectrons += 1
                for ele in electrons:
                    if self.deltaR(ele, part) < 0.4:
                        nGenElectrons_reconstructed += 1

        

        self.out.fillBranch("nGenElectrons", nGenElectrons)
        self.out.fillBranch("nGenElectrons_reconstructed", nGenElectrons_reconstructed)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

tools = lambda : corridorTools( )


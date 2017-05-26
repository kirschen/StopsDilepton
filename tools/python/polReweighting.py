import math
import ROOT

def getPolWeights(r):
    tl1     = ROOT.TLorentzVector()
    tl2     = ROOT.TLorentzVector()
    tt1     = ROOT.TLorentzVector()
    tt2     = ROOT.TLorentzVector()
    tst1    = ROOT.TLorentzVector()
    tst2    = ROOT.TLorentzVector()
    
    bV1 = ROOT.TVector3()
    bV2 = ROOT.TVector3()
    
    w_pol_L = 1.
    w_pol_R = 1.
    
    genParts = []
    for i, pdgId in enumerate(r.genPartAll_pdgId):
        # get the stop 4 vectors
        if pdgId == 1000022:
            if r.genPartAll_status[i] in [1,23] and r.genPartAll_motherId[i] == 1000006:
                j = r.genPartAll_motherIndex1[i] # get the mother
                tst1.SetPtEtaPhiM(r.genPartAll_pt[j], r.genPartAll_eta[j], r.genPartAll_phi[j], r.genPartAll_mass[j])
            if r.genPartAll_status[i] in [1,23] and r.genPartAll_motherId[i] == -1000006:
                j = r.genPartAll_motherIndex1[i] # get the mother
                tst2.SetPtEtaPhiM(r.genPartAll_pt[j], r.genPartAll_eta[j], r.genPartAll_phi[j], r.genPartAll_mass[j])
        
        # get the top and lepton/quark 4-vectors
        if abs(pdgId) in range(1,7) + range(11,17):
            if abs(r.genPartAll_motherId[i]) == 24 and (r.genPartAll_status[i] in [1,22,23]):
                mIndex = r.genPartAll_motherIndex1[i]
                gmIndex = r.genPartAll_motherIndex1[mIndex]

                if r.genPartAll_grandmotherId[i] != r.genPartAll_motherId[i]:
                    matched = True
                    gmIndex = r.genPartAll_motherIndex1[mIndex]
                else:
                    matched = False

                while not matched:
                    if not abs(r.genPartAll_pdgId[gmIndex]) == 6:
                        gmIndex = r.genPartAll_motherIndex1[gmIndex]
                    else:
                        matched = True

                #print 'Lepton properties', r.genPartAll_pdgId[i], r.genPartAll_pt[i], r.genPartAll_eta[i], r.genPartAll_phi[i], r.genPartAll_mass[i]
                #print 'Top properties', r.genPartAll_pdgId[gmIndex], r.genPartAll_pt[gmIndex], r.genPartAll_eta[gmIndex], r.genPartAll_phi[gmIndex], r.genPartAll_mass[gmIndex]

                if r.genPartAll_pdgId[gmIndex]*r.genPartAll_pdgId[i] < 0:
                    if r.genPartAll_pdgId[gmIndex] == 6:
                        tt1.SetPtEtaPhiM(r.genPartAll_pt[gmIndex], r.genPartAll_eta[gmIndex], r.genPartAll_phi[gmIndex], r.genPartAll_mass[gmIndex])
                        tl1.SetPtEtaPhiM(r.genPartAll_pt[i], r.genPartAll_eta[i], r.genPartAll_phi[i], r.genPartAll_mass[i])
                    if r.genPartAll_pdgId[gmIndex] == -6:
                        tt2.SetPtEtaPhiM(r.genPartAll_pt[gmIndex], r.genPartAll_eta[gmIndex], r.genPartAll_phi[gmIndex], r.genPartAll_mass[gmIndex])
                        tl2.SetPtEtaPhiM(r.genPartAll_pt[i], r.genPartAll_eta[i], r.genPartAll_phi[i], r.genPartAll_mass[i])

    bV1.SetXYZ(-tst1.Px()/tst1.Energy(), -tst1.Py()/tst1.Energy(), -tst1.Pz()/tst1.Energy())
    bV2.SetXYZ(-tst2.Px()/tst2.Energy(), -tst2.Py()/tst2.Energy(), -tst2.Pz()/tst2.Energy())
    tt1.Boost(bV1)
    tt2.Boost(bV2)
    tl1.Boost(bV1)
    tl2.Boost(bV2)
    
    if tt1.P() > 0 and tl1.P() > 0:
        costh       = ( tt1.Px()*tl1.Px() + tt1.Py()*tl1.Py()+ tt1.Pz()*tl1.Pz() ) / ( tt1.P() * tl1.P() )
        weight_L    = ( tt1.Energy() + tt1.P() ) * ( 1-costh )
        weight_R    = ( tt1.Energy() - tt1.P() ) * ( 1+costh )
        w_pol_L    *= 2*weight_L / (weight_R+weight_L)
        w_pol_R    *= 2*weight_R / (weight_R+weight_L)

    if tt2.P() > 0 and tl2.P() > 0:
        costh       = ( tt2.Px()*tl2.Px() + tt2.Py()*tl2.Py()+ tt2.Pz()*tl2.Pz() ) / ( tt2.P() * tl2.P() )
        weight_L    = ( tt2.Energy() + tt2.P() ) * ( 1-costh )
        weight_R    = ( tt2.Energy() - tt2.P() ) * ( 1+costh )
        w_pol_L    *= 2*weight_L / (weight_R+weight_L)
        w_pol_R    *= 2*weight_R / (weight_R+weight_L)
    
    return w_pol_L, w_pol_R

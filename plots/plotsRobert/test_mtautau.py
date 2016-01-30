import ROOT
from StopsDilepton.tools.mtautau import mtautau
from math import cos, sin, sqrt, pi

def scaleMomentum(v, scale):
    res=v.Clone()
    res.SetXYZM(scale * res.X(), scale * res.Y(), scale * res.Z(), res.M())
    return res

tau_m = 0.
Z_m = 91.2

tau_phi=pi/4
tau_eta=1.
tau_pt = sqrt((Z_m**2/4. - tau_m**2)/cos(tau_phi)**2)

frac_neu1 = 0.3 #fraction of momentum carried by neutrino1
frac_neu2 = 0.7 #fraction of momentum carried by neutrino2

tau1_p = ROOT.TLorentzVector()
tau1_p.SetPtEtaPhiM(tau_pt, tau_eta, tau_phi, tau_m)
tau2_p = ROOT.TLorentzVector()
tau2_p.SetPtEtaPhiM(tau_pt, tau_eta, pi-tau_phi, tau_m)

print "Check Z-mass (2 taus) %f" % (tau1_p + tau2_p).M()

lepton_1 = scaleMomentum(tau1_p, 1-frac_neu1)
lepton_2 = scaleMomentum(tau2_p, 1-frac_neu2)
neu_1 = scaleMomentum(tau1_p, frac_neu1)
neu_2 = scaleMomentum(tau2_p, frac_neu2)

print "Check Z-mass (2 leptons, two neutrinos) %f" % (lepton_1+neu_1+lepton_2+neu_2).M()

met = neu_1+neu_2

res = mtautau(met.Pt(), met.Phi(), lepton_1.Pt(), lepton_1.Eta(), lepton_1.Phi(),  lepton_2.Pt(), lepton_2.Eta(), lepton_2.Phi(), tauMass = 0., retAll=True )
print res

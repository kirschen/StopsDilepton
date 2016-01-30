from math import sin, cos, sqrt
import ROOT
def mtautau(met, metphi, l1pt, l1eta, l1phi, l2pt, l2eta, l2phi, tauMass=1.777,retAll=False):
    """
      1. assume leptonic tau decay and neutrinos and lepton agree
      neutrino_{1,2} = alpha_{1,2}*lepton_{1,2}
      2. Use this to calculate neutrino momenta from MET measurements
      alpha_1*lepton_1+alpha_2*lepton_2=ETmiss
      3. compute parent mass:
      ((alpha_1+1)*lepton_1 + (alpha_2+1)*lepton_2).mass()
    """
    l1px, l1py = l1pt*cos(l1phi), l1pt*sin(l1phi)
    l2px, l2py = l2pt*cos(l2phi), l2pt*sin(l2phi)
    mex, mey = met*cos(metphi), met*sin(metphi)

    den = (l1px*l2py-l1py*l2px)
    if den!=0:
        alpha_1 = (mex*l2py-mey*l2px)/den
        alpha_2 = (mey*l1px-mex*l1py)/den
    else:
        return float('nan')

    tau1 = ROOT.TLorentzVector()
    tau1.SetPtEtaPhiM((1+alpha_1)*l1pt, l1eta, l1phi, tauMass)
    tau2 = ROOT.TLorentzVector()
    tau2.SetPtEtaPhiM((1+alpha_2)*l2pt, l2eta, l2phi, tauMass)
    if retAll:
        return (tau1+tau2).M(), alpha_1,alpha_2
    else:
        return (tau1+tau2).M()

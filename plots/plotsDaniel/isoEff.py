import ROOT,pickle
import time
from math import pi, sqrt

from StopsDilepton.samples.heppy_dpm_samples import mc_heppy_mapper
from StopsDilepton.samples.heppy_dpm_samples import T2tt_heppy_mapper
from StopsDilepton.samples.heppy_dpm_samples import data_heppy_mapper
from StopsDilepton.samples.heppy_dpm_samples import ttbarDM_heppy_mapper

from StopsDilepton.tools.cutInterpreter import cutInterpreter
from StopsDilepton.analysis.u_float import u_float


def deltaPhi(phi1, phi2):
  dphi = phi2-phi1
  if  dphi > pi:
      dphi -= 2.0*pi
  if dphi <= -pi:
      dphi += 2.0*pi
  return abs(dphi)
def deltaR2(l1, l2):
  return deltaPhi(l1['phi'], l2['phi'])**2 + (l1['eta'] - l2['eta'])**2
def deltaR(l1, l2):
  return sqrt(deltaR2(l1,l2))

mc = mc_heppy_mapper
mc_samples = mc.heppy_sample_names

#tt = mc_heppy_mapper.from_heppy_samplename('VVTo2L2Nu')
tt = mc_heppy_mapper.from_heppy_samplename('TTLep_pow_ext')

presel = "Sum$(LepGood_pt>20&&abs(LepGood_eta)<2.4)>0"

njetBins = ["nCMGjet01","nCMGjet23", "nCMGjet45", "nCMGjet6p"]
HTBins = ["htCMG0to200", "htCMG200to400", "htCMG400"]
METBins = ["met0to80","met80to140","met140to240","met240"]

allBins = njetBins + HTBins + METBins

isoEffs = {}

for b in allBins:
  isoEffs[b] = {}
  cut = presel + '&&'
  cut += cutInterpreter.cutString(b)
  
  print cut
  
  tt.chain.Draw(">>eList", cut)
  
  elist = ROOT.gDirectory.Get("eList")
  number_events = elist.GetN()
  
  #number_events = int(1e3)
  num_mu    = 0
  num_ele   = 0
  denom_mu  = 0
  denom_ele = 0
  print "Working on %i events"%(number_events)
  
  for i in range(number_events):
    tt.chain.GetEntry(elist.GetEntry(i))
    if i%10000==0: print 'Done with %i'%(i)
    # reco
    recoLep_pt        = [l for l in tt.chain.LepGood_pt]
    recoLep_phi       = [l for l in tt.chain.LepGood_phi]
    recoLep_eta       = [l for l in tt.chain.LepGood_eta]
    recoLep_relIso03  = [l for l in tt.chain.LepGood_relIso03]
    recoLep_match     = [l for l in tt.chain.LepGood_mcMatchAny]
    recoLep_pdg       = [l for l in tt.chain.LepGood_pdgId]
    recoLep = []
    for i,pt in enumerate(recoLep_pt):
      lep = {
        'pt':recoLep_pt[i],
        'phi':recoLep_phi[i],
        'eta':recoLep_eta[i],
        'iso':recoLep_relIso03[i],
        'match':recoLep_match[i],
        'pdg':recoLep_pdg[i]}
      recoLep.append(lep)
    
    # gen
    genLep_pt        = [l for l in tt.chain.genLep_pt]
    genLep_phi       = [l for l in tt.chain.genLep_phi]
    genLep_eta       = [l for l in tt.chain.genLep_eta]
    genLep_pdg       = [l for l in tt.chain.genLep_pdgId]
    genLep = []
    for i,pt in enumerate(genLep_pt):
      lep = {
        'pt': genLep_pt[i],
        'phi':genLep_phi[i],
        'eta':genLep_eta[i],
        'pdg':genLep_pdg[i]}
      genLep.append(lep)
    
    for gl in genLep:
      if gl['pt']>20 and abs(gl['eta'])<2.4:
        #if abs(gl['pdg']) == 13: denom_mu += 1
        #elif abs(gl['pdg']) == 11: denom_ele += 1
        matched = False
        for rl in recoLep:
          dr = deltaR(rl, gl)
          if dr<0.4:
            #print "match between rl and gl", rl, gl, dr
            if rl['iso'] < 0.12:
              if abs(rl['pdg']) == 13: num_mu += 1
              elif abs(rl['pdg']) == 11: num_ele += 1
            if abs(rl['pdg']) == 13: denom_mu += 1
            elif abs(rl['pdg']) == 11: denom_ele += 1
            matched = True
            break
        #if not matched: print "No match for", rl, genLep
  
  num_mu    = u_float(num_mu,     sqrt(num_mu))
  denom_mu  = u_float(denom_mu,   sqrt(denom_mu))
  num_ele   = u_float(num_ele,    sqrt(num_ele))
  denom_ele = u_float(denom_ele,  sqrt(denom_ele))

  isoEffs[b]['mu']  = num_mu/denom_mu
  isoEffs[b]['ele'] = num_ele/denom_ele
  print "Isolation efficiency for muons is", num_mu/denom_mu
  print "Isolation efficiency for electrons is", num_ele/denom_ele
  pickle.dump(isoEffs, file('/afs/hephy.at/data/dspitzbart01/StopsDilepton/isoEfficiency/isoEff_ttlep_pow.pkl','w'))

print "Overwriting pkl file"
pickle.dump(isoEffs, file('/afs/hephy.at/data/dspitzbart01/StopsDilepton/isoEfficiency/isoEff_ttlep_pow.pkl','w'))


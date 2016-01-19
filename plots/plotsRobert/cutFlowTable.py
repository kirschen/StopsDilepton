import ROOT

from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_1l_postProcessed import *

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain, getChain
from StopsDilepton.tools.localInfo import plotDir

small = False

#Define chains for signals and backgrounds
samples = [
  DY_HT_LO, TTJets_Lep, TTZ, TTXNoZ, singleTop, WJetsToLNu_HT, diBoson, triBoson, QCD_Mu5EMbcToE, T2tt_450_0 
]
DY_HT_LO['name']    = "DY (LO)" 
TTJets_Lep['name']  = "TT+Jets (MG)" 
TTZ['name'] =         "TT+Z" 
TTXNoZ['name'] =      "TT+X"
singleTop['name'] =   "single top"
WJetsToLNu_HT['name'] ="W+Jets" 
diBoson['name'] =      "diBoson" 
triBoson['name'] =     "triboson"
QCD_Mu5EMbcToE ['name'] = " QCD"
for s in samples:
  s['chain'] = getChain(s,histname='', maxN=-1 if not small else 1)

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWP = multiIsoLepString('VT', ('l1_index','l2_index'))

cuts=[
 ("==2 leptons", "nGoodMuons+nGoodElectrons==2"),
 ("opposite sign","isOS==1"),
 ("m(ll)>20", "dl_mass>20"), 
 ("|m(ll) - mZ|>15 for SF","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"), 
 (">=2 jets", "(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2"), 
 (">=1 b-tags (CSVv2)", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1"), 
 ("MET>80", "met_pt>80"), 
 ("MET/sqrt(HT)>5", "met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>5"), 
 ("dPhi(Jet_1,2|MET)>0.25", "cos(met_phi-Jet_phi[0])<cos(0.25)&&cos(met_phi-Jet_phi[1])<cos(0.25)"), 
 ("MT2(ll) > 140", "dl_mt2ll>140"), 
# ("multiIso VT", multiIsoWP), 
# ("MT2(ll) > 240", "dl_mt2ll>240"), 
  ]

#lumiFac=10
#print 30*" "+ "".join([ "%13s"%s['name'] for s in samples ] )
#for i in range(len(cuts)):
#  r=[]
#  for s in samples:
#    selection = "&&".join(c[1] for c in cuts[:i+1])
#    if selection=="":selection="(1)"
##    print selection
#    y = lumiFac*getYieldFromChain(s['chain'], selection, 'weightPU')
#    n = getYieldFromChain(s['chain'], selection, '(1)')
#    r.append(y)
#  print "%30s"%cuts[i][0]+ "".join([ " %12.1f"%r[j] for j in range(len(r))] )

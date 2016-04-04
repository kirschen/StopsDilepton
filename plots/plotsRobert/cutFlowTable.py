import ROOT

from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_2l_postProcessed import *
#from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_1l_postProcessed import *

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain

small = False

#Define chains for signals and backgrounds
samples = [
#    DY_HT_LO, TTJets_Lep, TTZ, TTXNoZ, singleTop, WJetsToLNu_HT, diBoson, triBoson, QCD_Mu5EMbcToE, T2tt_450_0
#    DY_HT_LO, TTJets_Lep, TTZ, TTXNoZ, singleTop, diBoson, triBoson, QCD_Mu5EMbcToE
   Sample.fromDirectory(name="TTJets_Lep",       treeName="Events", isData=False, color=7,              texName="t#bar{t} + Jets (lep)",     directory=['/scratch/rschoefbeck/cmgTuples/postProcessed_Fall15_mAODv2/dilep/TTJets_DiLepton_ext/']) 
]

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWP = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])


cuts=[
  ("==2 leptons", "nGoodMuons+nGoodElectrons==2"),
  ("opposite sign","isOS==1"),
  ("m(ll)>20", "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"),
  (">=2 jets", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
  (">=1 b-tags (CSVv2)", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
  ("MET>80", "met_pt>80"),
  ("MET/sqrt(HT)>5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
  ("dPhi(JetGood_1,2|MET)>0.25", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
  ("MT2(ll) > 140", "dl_mt2ll>140"),
  ("multiIso M(Mu), T(Ele)", multiIsoWP),
# ("relIso04<0.12", relIso04sm12Cut),

# ("MT2(ll) > 240", "dl_mt2ll>240"),
    ]

lumiFac=10
print 30*" "+ "".join([ "%13s"%s.name for s in samples ] )
for i in reversed(range(len(cuts))):
    r=[]
    for s in samples:
        selection = "&&".join(c[1] for c in cuts[:i+1])
        if selection=="":selection="(1)"
        y = lumiFac*getYieldFromChain(s.chain, selection, 'weight')
        n = getYieldFromChain(s.chain, selection, '(1)')
        r.append(y)
    print "%30s"%cuts[i][0]+ "".join([ " %12.1f"%r[j] for j in range(len(r))] )

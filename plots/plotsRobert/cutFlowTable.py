import ROOT

from RootTools.core.standard import *

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger('INFO', logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger('INFO', logFile = None )

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain

#make samples
data_directory = "/afs/hephy.at/data/rschoefbeck01/cmgTuples/" 
postProcessing_directory = "postProcessed_Fall15_v3/dilep/" 
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_2l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
maxN = -1
s1 =  Sample.fromFiles(name="T2tt_450_0", treeName="Events", isData=False, color=ROOT.kBlack, texName="T2tt(450,0)", files=['/afs/hephy.at/data/rschoefbeck01/cmgTuples/postProcessed_Fall15_v3/dilep/T2tt/T2tt_450_0.root'], maxN = maxN)
s2 =  Sample.fromFiles(name="T2tt_450_0", treeName="Events", isData=False, color=ROOT.kBlack, texName="T2tt(450,0)", files=['/afs/hephy.at/data/rschoefbeck01/cmgTuples/postProcessed_Fall15_mAODv2/dilepTiny/T2tt/T2tt_450_0.root'], maxN = maxN)

#Define chains for signals and backgrounds
samples = [
#    DY_HT_LO, TTJets_Lep, TTZ, TTXNoZ, singleTop, diBoson, WZZ, QCD_Mu5EMbcToE, 
#    TTbarDMJets_pseudoscalar_Mchi1_Mphi10,
#    TTbarDMJets_pseudoscalar_Mchi10_Mphi100
s1,
s2, 
# Sample.fromDirectory(name="TTJets_Lep", treeName="Events", isData=False, color=7, texName="t#bar{t} + Jets (lep)", directory=['/scratch/rschoefbeck/cmgTuples/fromTom/postProcessed_Fall15_mAODv2/dilep/TTJets_DiLepton_comb/'], maxN = maxN) 
]
QCD_Mu5EMbcToE.name = 'QCD'
#TTbarDMJets_pseudoscalar_Mchi1_Mphi10.name = "10/1"
#TTbarDMJets_pseudoscalar_Mchi10_Mphi100.name = "100/10"
from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWPVTVT = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
#multiIsoWPMT = multiIsoLepString('M','T', ('l1_index','l2_index'))
#relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])

if maxN>0:
    for s in samples:
        s.reduceFiles( to = 1 )

cuts=[
  ("==2 leptons", "nGoodMuons+nGoodElectrons==2"),
#  ("multiIso VT(Mu), VT(Ele)", multiIsoWPVTVT),
  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
  ("opposite sign","isOS==1"),
  ("m(ll)>20", "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"),
  (">=2 jets", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
  (">=1 b-tags (CSVv2)", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
  ("MET>80", "met_pt>80"),
  ("MET/sqrt(HT)>5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
  ("dPhi(JetGood_1,2|MET)>0.25", "cos(met_phi-JetGood_phi[0])<cos(0.25)&&cos(met_phi-JetGood_phi[1])<cos(0.25)"),
  ("MT2(ll) > 140", "dl_mt2ll>140"),
#  ("multiIso M(Mu), T(Ele)", multiIsoWPMT),
#  ("filterCut", "Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter" ),
# ("relIso04<0.12", relIso04sm12Cut),

# ("MT2(ll) > 240", "dl_mt2ll>240"),
    ]

lumiFac=10
print 30*" "+ "".join([ "%13s"%s.name for s in samples ] )
for i in reversed(range(len(cuts))):
#for i in range(len(cuts)):
    r=[]
    for s in samples:
        selection = "&&".join(c[1] for c in cuts[:i+1])
        if selection=="":selection="(1)"
        y = lumiFac*getYieldFromChain(s.chain, selection, 'weight')
        n = getYieldFromChain(s.chain, selection, '(1)')
        r.append(y)
    print "%30s"%cuts[i][0]+ "".join([ " %12.1f"%r[j] for j in range(len(r))] )

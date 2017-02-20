import ROOT, pickle, os
from StopsDilepton.tools.btagEfficiency import *
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *

from StopsDilepton.tools.helpers import getChain, getChunks

# get MC truth efficiencies for a specific sample
def getBTagMCTruthEfficiencies(c, cut="(1)"):
    mceff = {}
    for ptBin in ptBins:
        mceff[tuple(ptBin)] = {}
        for etaBin in etaBins:
            mceff[tuple(ptBin)][tuple(etaBin)] = {}
            etaCut = "abs(JetGood_eta)>"+str(etaBin[0])+"&&abs(JetGood_eta)<"+str(etaBin[1])
            ptCut = "abs(JetGood_pt)>"+str(ptBin[0])
            if ptBin[1]>0:
                ptCut += "&&abs(JetGood_pt)<"+str(ptBin[1])
            c.Draw("(JetGood_btagCSV>0.8484)>>hbQuark(100,-1,2)",cut+"&&JetGood_id>0&&abs(JetGood_hadronFlavour)==5&&                     "+etaCut+"&&"+ptCut)
            c.Draw("(JetGood_btagCSV>0.8484)>>hcQuark(100,-1,2)",cut+"&&JetGood_id>0&&abs(JetGood_hadronFlavour)==4&&                     "+etaCut+"&&"+ptCut)
            c.Draw("(JetGood_btagCSV>0.8484)>>hOther(100,-1,2)" ,cut+"&&JetGood_id>0&&(abs(JetGood_hadronFlavour) < 4  || abs(JetGood_hadronFlavour) > 5)&&  "+etaCut+"&&"+ptCut)
            hbQuark = ROOT.gDirectory.Get("hbQuark")
            hcQuark = ROOT.gDirectory.Get("hcQuark")
            hOther = ROOT.gDirectory.Get("hOther")
            mceff[tuple(ptBin)][tuple(etaBin)]["b"]     = hbQuark.GetMean()
            mceff[tuple(ptBin)][tuple(etaBin)]["c"]     = hcQuark.GetMean()
            mceff[tuple(ptBin)][tuple(etaBin)]["other"] = hOther.GetMean()
            print "Eta",etaBin,etaCut,"Pt",ptBin,ptCut,"Found b/c/other", mceff[tuple(ptBin)][tuple(etaBin)]["b"], mceff[tuple(ptBin)][tuple(etaBin)]["c"], mceff[tuple(ptBin)][tuple(etaBin)]["other"]
            del hbQuark, hcQuark, hOther
    return mceff

#for sample in [TTJets, TTJets_Lep]:
#for sample in [ TTJets_DiLepton, TTJets]:
#c = getChain(getChunks(TTJets_DiLepton)[0] + getChunks(TTJets_DiLepton_ext)[0], treeName="tree")
c = Top_pow.chain
res=  getBTagMCTruthEfficiencies(c,
    #cut="(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2&&Sum$(LepGood_pt>20&&abs(LepGood_eta)<2.4)>=2"
    cut="nJetGood>=2&&l1_pt>20&&l2_pt>20"
)
print "Efficiencies:"
print res
pickle.dump(res, \
    file(os.path.expandvars('$CMSSW_BASE/src/StopsDilepton/tools/data/btagEfficiencyData/TTJets_pow_2j_2l.pkl'), 'w')
)

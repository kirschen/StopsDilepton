import ROOT
from RootTools.core.standard import *

c = ROOT.TChain("Events")

for d in [\
    "DYJetsToLL_M50_HT70to100",
    "DYJetsToLL_M50_HT100to200_ext",
    "DYJetsToLL_M50_HT200to400_comb",
    "DYJetsToLL_M50_HT400to600_comb",
    "DYJetsToLL_M50_HT600to800",
    "DYJetsToLL_M50_HT800to1200",
    "DYJetsToLL_M50_HT1200to2500",
    "DYJetsToLL_M50_HT2500toInf",
    ]:
        c.Add("/afs/hephy.at/data/cms06/nanoTuples/stops_2016_nano_v0p23/dilep/%s/*.root"%d)
        #c.Add("/afs/hephy.at/data/cms06/nanoTuples/stops_2016_nano_v0p23/dilep/%s/*_0.root"%d)

from Analysis.Tools.metFilters            import getFilterCut
from StopsDilepton.tools.cutInterpreter  import cutInterpreter
cutString = "&&".join( [cutInterpreter.cutString( "POGMetSig12-lepSel-njet2p-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1"),  "nGoodMuons+nGoodElectrons==2&&isOS&&(isEE||isMuMu)" , getFilterCut(isData=False, year=2016)] )

c.Draw("nBTag>>h0(3,0,3)", "36.9*weight*reweightHEM*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF*(Sum$(GenJet_pt>40&&abs(GenJet_eta)<2.4&&abs(GenJet_hadronFlavour)==5)==0)*%s"%cutString)
c.Draw("nBTag>>h1(3,0,3)", "36.9*weight*reweightHEM*reweightDilepTrigger*reweightLeptonSF*reweightBTag_SF*reweightLeptonTrackingSF*(Sum$(GenJet_pt>40&&abs(GenJet_eta)<2.4&&abs(GenJet_hadronFlavour)==5)>=1)*%s"%cutString)

ROOT.h0.style = styles.lineStyle(ROOT.kBlue)
ROOT.h1.style = styles.lineStyle(ROOT.kRed)


ROOT.h0.legendText =  "nGenB=0"
ROOT.h1.legendText = "nGenB#geq 1"


plotting.draw( Plot.fromHisto("nBTag", histos = [[ROOT.h0, ROOT.h1]], texX="nBTag(reco)", texY="Number of events"),
            plot_directory = "/afs/hephy.at/user/r/rschoefbeck/www/etc/"
    )

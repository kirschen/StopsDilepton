import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/useNiceColorPalette.C")
ROOT.setTDRStyle()
if type(ROOT.tdrStyle)!=type(ROOT.gStyle):
    del ROOT.tdrStyle
    ROOT.setTDRStyle()
ROOT.useNiceColorPalette(255)
ROOT.tdrStyle.SetPadRightMargin(0.15)

from math import *
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, getJets
from StopsDilepton.tools.localInfo import *

#preselection: MET>50, HT>100, n_bjets>=2
preselection = 'abs(dl_mass-91.2)>15.&&(isMuMu)&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)>=0&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2'

reduceStat = 1

from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data50ns_1l_postProcessed import *

#load all the samples
samples = [TTJets_50ns, DoubleMuon_Run2015B]
#signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]

#get the TChains for each sample
for s in samples:
    s['chain'] = getChain(s,histname="")

#plots
plots = [\
    {'name':'mt2ll_vs_mt2bb',   'varX':'dl_mt2ll', 'varY':'dl_mt2bb', 'binning': [25,25,275,25,25,275], 'histo':{}},
    {'name':'mt2ll_vs_mt2blbl', 'varX':'dl_mt2ll', 'varY':'dl_mt2blbl', 'binning': [25,25,275,25,25,275], 'histo':{}},
    {'name':'mt2blbl_vs_mt2bb', 'varX':'dl_mt2blbl', 'varY':'dl_mt2bb', 'binning': [25,25,275,25,25,275], 'histo':{}},
]

#make plot in each sample:
for s in samples:
    for p in plots:
        p['histo'][s['name']] = ROOT.TH2F("met_"+s["name"], "met_"+s["name"], *(p['binning']))
        s["chain"].Draw(p['varY']+":"+p['varX']+'>>'+p['histo'][s['name']].GetName(), preselection)
#  print "Looping over %s" % s["name"]
#  eList = getEList(chain, preselection)
#  nEvents = eList.GetN()/reduceStat
#  print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)
#  for ev in range(nEvents):
#    if ev%10000==0:print "At %i/%i"%(ev,nEvents)
#    chain.GetEntry(eList.GetEntry(ev))
#    #event weight (L= 4fb^-1)
#    weight = reduceStat*getVarValue(chain, "weight")
#    #MET
#
#  del eList

#Some coloring

for p in plots:
    #Make a stack for samples
    for s in samples:
        c1 = ROOT.TCanvas()
        p['histo'][s['name']].Draw("COLZ")
        c1.SetLogz()
        c1.Print(plotDir+"/"+s['name']+'_'+p["name"]+".png")
        print s['name'], p["name"], p['histo'][s['name']].GetCorrelationFactor()

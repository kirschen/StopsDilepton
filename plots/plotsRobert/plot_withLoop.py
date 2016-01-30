import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
import array

from StopsDilepton.tools.mtautau import mtautau as mtautau_
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.localInfo import *

#preselection: MET>50, HT>100, n_bjets>=2
#Once we decided in HT definition and b-tag WP we add those variables to the tuple.
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2

#preselection = 'met_pt>40&&Sum$((Jet_pt)*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>100&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)==2&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'
preselection = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>2&&Sum$(LepGood_pt>20)>=2'
#preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)==2&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>2&&Sum$(LepGood_pt>20)>=2'
prefix="def"
#prefix="mt2ll-120"
reduceStat = 1
lumiScale = 42/4000.

#load all the samples
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data50ns_1l_postProcessed import *

#backgrounds = [TTJets_50ns, WJetsToLNu_50ns, diBosons_50ns, singleTop_50ns, DY_50ns]#, QCD]
backgrounds = [TTJets_50ns, diBosons_50ns, singleTop_50ns, DY_50ns]#, QCD]
for b in backgrounds:
    b['isData']=False
#backgrounds = [TTJets_25ns, DY_25ns, singleTop_25ns, diBosons_25ns, WJetsHTToLNu_25ns]#, QCD]

data = DoubleMuon_Run2015B
data['isData']=True
signals = [] #SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]


#get the TChains for each sample
for s in backgrounds+signals+[data]:
    s['chain'] = getChain(s,histname="")

#plots
plots = {\
    'met': {'title':'#slash{E}_{T} (GeV)', 'name':'met', 'binning': [26,0,520], 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'mt2ll', 'binning': [26,0,520], 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': [26,0,520], 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': [26,0,520], 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': [35,0,35], 'histo':{}},
    'mtautau_zoomed': {'title':'M_{#tau#tau} (GeV)', 'name':'mtautau_zoomed', 'binning': [50,0,200], 'histo':{}},
    'mtautau': {'title':'M_{#tau#tau} (GeV)', 'name':'mtautau', 'binning': [50,0,2000], 'histo':{}},
    'alpha0': {'title':'#alpha_{0}', 'name':'alpha0', 'binning': [50,-10,10], 'histo':{}},
    'alpha1': {'title':'#alpha_{1}', 'name':'alpha1', 'binning': [50,-10,10], 'histo':{}},
}


#make plot in each sample:
for s in backgrounds+signals+[data]:
    for pk in plots.keys():
        plots[pk]['histo'][s['name']] = ROOT.TH1F("met_"+s["name"], "met_"+s["name"], *(plots[pk]['binning']))

    chain = s["chain"]
    print "Looping over %s" % s["name"]
    eList = getEList(chain, preselection)
    nEvents = eList.GetN()/reduceStat
    print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)
    for ev in range(nEvents):
        if ev%10000==0:print "At %i/%i"%(ev,nEvents)
        chain.GetEntry(eList.GetEntry(ev))
        mt2Calc.reset()
        weight = reduceStat*getVarValue(chain, "weight")*lumiScale if not s['isData'] else 1
        met = getVarValue(chain, "met_pt")
        plots['met']['histo'][s["name"]].Fill(met, weight)
        metPhi = getVarValue(chain, "met_phi")
        leptons = filter(lambda l: looseMuID(l) or looseEleID(l), getLeptons(chain))
        if len(leptons)==2 and leptons[0]['pdgId']*leptons[1]['pdgId']<0 and abs(leptons[0]['pdgId'])==abs(leptons[1]['pdgId']): #OSSF choice
            l0pt, l0eta, l0phi = leptons[0]['pt'],  leptons[0]['eta'],  leptons[0]['phi']
            l1pt, l1eta, l1phi = leptons[1]['pt'],  leptons[1]['eta'],  leptons[1]['phi']
            mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
            if  mll>20 and abs(mll-91.2)<15:
                jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
                bjets = filter(lambda j:j['btagCSV']>0.890, jets)
                if len(bjets)==2:
                    mt2Calc.setMet(met,metPhi)
                    mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
                    mt2ll = mt2Calc.mt2ll()
#          if mt2ll>120:
                    if True:
                        plots['mt2ll']['histo'][s["name"]].Fill(mt2ll, weight)
                        ht = sum([j['pt'] for j in jets])
                        plots['kinMetSig']['histo'][s["name"]].Fill(met/sqrt(ht), weight)
                        mt2Calc.setBJets(bjets[0]['pt'], bjets[0]['eta'], bjets[0]['phi'], bjets[1]['pt'], bjets[1]['eta'], bjets[1]['phi'])
                        mt2bb   = mt2Calc.mt2bb()
                        mt2blbl = mt2Calc.mt2blbl()
                        plots['mt2bb']['histo'][s["name"]].Fill(mt2bb, weight)
                        plots['mt2blbl']['histo'][s["name"]].Fill(mt2blbl, weight)
                        mtautau, alpha_0, alpha_1 = mtautau_(met,metPhi, l0pt, l0eta, l0phi, l1pt, l1eta, l1phi, retAll=True)
                        plots['mtautau']['histo'][s["name"]].Fill(mtautau, weight)
                        plots['mtautau_zoomed']['histo'][s["name"]].Fill(mtautau, weight)
                        plots['alpha0']['histo'][s["name"]].Fill(alpha_0, weight)
                        plots['alpha1']['histo'][s["name"]].Fill(alpha_1, weight)
#
#        else:
#          print "Preselection and b-jet selection inconsistent"

    del eList

#Some coloring
TTJets_50ns["color"]=ROOT.kRed
TTJets_25ns["color"]=ROOT.kRed
WJetsHTToLNu_25ns["color"]=ROOT.kGreen
#TTVH["color"]=ROOT.kMagenta
diBosons_50ns["color"]=ROOT.kMagenta
diBosons_25ns["color"]=ROOT.kMagenta
singleTop_50ns["color"]=ROOT.kOrange
singleTop_25ns["color"]=ROOT.kOrange
DY_50ns["color"]=ROOT.kBlue
DY_25ns["color"]=ROOT.kBlue

for pk in plots.keys():
    #Make a stack for backgrounds
    l=ROOT.TLegend(0.6,0.6,1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    bkg_stack = ROOT.THStack("bkgs","bkgs")
    for b in reversed(backgrounds):
        plots[pk]['histo'][b['name']].SetFillColor(b["color"])
        plots[pk]['histo'][b['name']].SetMarkerColor(b["color"])
        plots[pk]['histo'][b['name']].SetMarkerSize(0)
#    plots[pk]['histo'][b['name']].GetYaxis().SetRangeUser(10**-2.5, 2*plots[pk]['histo'][b['name']].GetMaximum())
        bkg_stack.Add(plots[pk]['histo'][b['name']],"h")
        l.AddEntry(plots[pk]['histo'][b['name']], b["name"])
    #Plot!
    c1 = ROOT.TCanvas()
    bkg_stack.SetMaximum(2*bkg_stack.GetMaximum())
    bkg_stack.SetMinimum(10**-1.5)
    bkg_stack.Draw('e')
    bkg_stack.GetXaxis().SetTitle(plots[pk]['title'])
    binning = plots[pk]['binning']
    bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (binning[2]-binning[1])/binning[0]) )
    c1.SetLogy()

    plots[pk]['histo'][data['name']].Draw('hsame')
#  signal = "SMS_T2tt_2J_mStop650_mLSP325"#May chose different signal here
#  signalPlot = plots[pk]['histo'][signal].Clone()
#  signalPlot.Scale(100)
#  signalPlot.Draw("same")
#  l.AddEntry(signalPlot, signal+" x 100")
    l.Draw()
    c1.Print(plotDir+"/"+prefix+'_'+plots[pk]["name"]+".png")

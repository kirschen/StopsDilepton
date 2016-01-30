import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.texHelpers import latexmaker
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, ele_ID_eta, getGenParts
from StopsDilepton.tools.localInfo import *

#preselection: MET>50, HT>100, n_bjets>=2
#Once we decided in HT definition and b-tag WP we add those variables to the tuple.
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw

highestCSV = False
highestPT  = True

if highestCSV and not highestPT:
    preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'
if highestPT and not highestCSV:
    preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)>=1&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'

reduceStat = 1

#load all the samples
from StopsDilepton.samples.cmgTuplesPostProcessed_PHYS14 import *
#backgrounds = [WJetsHTToLNu, TTH, TTW, TTZ, DY, singleTop, TTJets]#, QCD]
backgrounds = [TTH, TTW, TTZ]
signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]

#get the TChains for each sample
for s in backgrounds+signals:
    s['chain'] = getChain(s,histname="")

#binning
mllbinning = [25,25,275]
mt2llbinning = [25,0,275]
mt2bbbinning = [25,0,550]
mt2blblbinning = [25,0,550]
njetsbinning = [15,0,15]
nbjetsbinning = [10,0,10]

#make plot in each sample:
plots = {\
    'mumu':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    },
    'ee':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    },
    'emu':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    },
}

#adding SF
plotsSF = {\
    'SF':{\
    'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
    'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    },
}

for s in backgrounds+signals:
    #1D
    for pk in plots.keys():
        for plot in plots[pk].keys():
            plots[pk][plot]['histo'][s["name"]] = ROOT.TH1F(plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, *plots[pk][plot]['binning'])

    chain = s["chain"]
    #Using Event loop
    #get EList after preselection
    print "Looping over %s" % s["name"]
    eList = getEList(chain, preselection)
    nEvents = eList.GetN()/reduceStat
    print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)
    for ev in range(nEvents):
        if ev%10000==0:print "At %i/%i"%(ev,nEvents)
        chain.GetEntry(eList.GetEntry(ev))
        mt2Calc.reset()
        #event weight (L= 4fb^-1)
        weight = reduceStat*getVarValue(chain, "weight")
        #MET
        met = getVarValue(chain, "met_pt")
        metPhi = getVarValue(chain, "met_phi")
        #jetpt
        leadingjetpt = getVarValue(chain, "Jet_pt",0)
        subleadingjetpt = getVarValue(chain, "Jet_pt",1)
        #Leptons
        allLeptons = getLeptons(chain)
        muons = filter(looseMuID, allLeptons)
        electrons = filter(looseEleID, allLeptons)
        #GENinfo
        genparticles = getGenParts(chain)

        #SF and OF channels
        leptons = {\
            'mu':   {'name': 'mumu', 'file': muons},
            'e':   {'name': 'ee', 'file': electrons},
            'emu': {'name': 'emu', 'file': [electrons,muons]},
            }
        for lep in leptons.keys():
            twoleptons = False
            #Same Flavor
            if lep != 'emu':
                if len(leptons[lep]['file'])==2 and leptons[lep]['file'][0]['pdgId']*leptons[lep]['file'][1]['pdgId']<0:
                    #genmatching(leptons[lep]['file'][0],genparticles)
                    twoleptons = True
                    l0pt, l0eta, l0phi = leptons[lep]['file'][0]['pt'],  leptons[lep]['file'][0]['eta'],  leptons[lep]['file'][0]['phi']
                    l1pt, l1eta, l1phi = leptons[lep]['file'][1]['pt'],  leptons[lep]['file'][1]['eta'],  leptons[lep]['file'][1]['phi']
                    leadingleptonpt = l0pt
                    subleadingleptonpt = l1pt
                    mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
                    plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
                    zveto = True
            #Opposite Flavor
            if lep == 'emu':
                if len(leptons[lep]['file'][0])==1 and len(leptons[lep]['file'][1])==1 and leptons[lep]['file'][0][0]['pdgId']*leptons[lep]['file'][1][0]['pdgId']<0:
                    twoleptons = True
                    l0pt, l0eta, l0phi = leptons[lep]['file'][0][0]['pt'],  leptons[lep]['file'][0][0]['eta'],  leptons[lep]['file'][0][0]['phi']
                    l1pt, l1eta, l1phi = leptons[lep]['file'][1][0]['pt'],  leptons[lep]['file'][1][0]['eta'],  leptons[lep]['file'][1][0]['phi']
                    mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
                    plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
                    zveto = False
            if (twoleptons and mll>20 and not zveto) or (twoleptons and mll > 20 and zveto and abs(mll-91.2)>15):
                mt2Calc.setMet(met,metPhi)
                mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)

                mt2ll = mt2Calc.mt2ll()
                #if mt2ll > 120:
                plots[leptons[lep]['name']]['mt2ll']['histo'][s["name"]].Fill(mt2ll, weight)
                jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
                plots[leptons[lep]['name']]['njets']['histo'][s["name"]].Fill(len(jets),weight)
                #highest CSV
                if highestCSV:
                    bjetsCSV = sorted(jets,key=lambda j:j['btagCSV'])
                    plots[leptons[lep]['name']]['nbjets']['histo'][s["name"]].Fill(len(bjetsCSV),weight)
                    mt2Calc.setBJets(bjetsCSV[-1]['pt'], bjetsCSV[-1]['eta'], bjetsCSV[-1]['phi'], bjetsCSV[-2]['pt'], bjetsCSV[-2]['eta'], bjetsCSV[-2]['phi'])
                if highestPT:
                    bjetspt = filter(lambda j:j['btagCSV']>0.814, jets)
                    nobjets = filter(lambda j:j['btagCSV']<0.814, jets)
                    plots[leptons[lep]['name']]['nbjets']['histo'][s["name"]].Fill(len(bjetspt),weight)
                    if len(bjetspt)>=2:
                        mt2Calc.setBJets(bjetspt[0]['pt'], bjetspt[0]['eta'], bjetspt[0]['phi'], bjetspt[1]['pt'], bjetspt[1]['eta'], bjetspt[1]['phi'])
                    if len(bjetspt)==1:
                        mt2Calc.setBJets(bjetspt[0]['pt'], bjetspt[0]['eta'], bjetspt[0]['phi'], nobjets[0]['pt'], nobjets[0]['eta'], nobjets[0]['phi'])

                #higest pt
                mt2bb   = mt2Calc.mt2bb()
                mt2blbl = mt2Calc.mt2blbl()
                plots[leptons[lep]['name']]['mt2bb']['histo'][s["name"]].Fill(mt2bb, weight)
                plots[leptons[lep]['name']]['mt2blbl']['histo'][s["name"]].Fill(mt2blbl, weight)
    del eList


#Some coloring
TTJets["color"]=ROOT.kRed
WJetsHTToLNu["color"]=ROOT.kGreen
TTH["color"]=ROOT.kMagenta
TTW["color"]=ROOT.kMagenta-3
TTZ["color"]=ROOT.kMagenta-6
singleTop["color"]=ROOT.kOrange
DY["color"]=ROOT.kBlue

#Plotvariables
signal = {'path': ["SMS_T2tt_2J_mStop425_mLSP325","SMS_T2tt_2J_mStop500_mLSP325","SMS_T2tt_2J_mStop650_mLSP325","SMS_T2tt_2J_mStop850_mLSP100"], 'name': ["T2tt(425,325)","T2tt(500,325)","T2tt(650,325)","T2tt(850,100)"]}
yminimum = 10**-0.5
legendtextsize = 0.032
signalscaling = 100

draw1D = True

if draw1D:

    for pk in plots.keys():
        for plot in plots[pk].keys():
        #Make a stack for backgrounds
            l=ROOT.TLegend(0.6,0.6,1.0,1.0)
            l.SetFillColor(0)
            l.SetShadowColor(ROOT.kWhite)
            l.SetBorderSize(1)
            l.SetTextSize(legendtextsize)
            bkg_stack = ROOT.THStack("bkgs","bkgs")
            for b in backgrounds:
                plots[pk][plot]['histo'][b["name"]].SetFillColor(b["color"])
                plots[pk][plot]['histo'][b["name"]].SetMarkerColor(b["color"])
                plots[pk][plot]['histo'][b["name"]].SetMarkerSize(0)
                bkg_stack.Add(plots[pk][plot]['histo'][b["name"]],"h")
                l.AddEntry(plots[pk][plot]['histo'][b["name"]], b["name"])

        #Plot!
            c1 = ROOT.TCanvas()
            bkg_stack.SetMaximum(2*bkg_stack.GetMaximum())
            bkg_stack.SetMinimum(yminimum)
            bkg_stack.Draw()
            bkg_stack.GetXaxis().SetTitle(plots[pk][plot]['title'])
            bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (plots[pk][plot]['binning'][2]-plots[pk][plot]['binning'][1])/plots[pk][plot]['binning'][0]) )
            c1.SetLogy()
            signalPlot_1 = plots[pk][plot]['histo'][signal['path'][0]].Clone()
            signalPlot_2 = plots[pk][plot]['histo'][signal['path'][2]].Clone()
            signalPlot_1.Scale(signalscaling)
            signalPlot_2.Scale(signalscaling)
            signalPlot_1.SetLineColor(ROOT.kBlack)
            signalPlot_2.SetLineColor(ROOT.kCyan)
            signalPlot_1.SetLineWidth(3)
            signalPlot_2.SetLineWidth(3)
            signalPlot_1.Draw("same")
            signalPlot_2.Draw("same")
            l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
            l.AddEntry(signalPlot_2, signal['name'][1]+" x " + str(signalscaling), "l")
            l.Draw()
            channeltag = ROOT.TPaveText(0.45,0.8,0.59,0.85,"NDC")
            firstlep, secondlep = pk[:len(pk)/2], pk[len(pk)/2:]
            if firstlep == 'mu':
                firstlep = '#' + firstlep
            if secondlep == 'mu':
                secondlep = '#' + secondlep
            channeltag.AddText(firstlep+secondlep)
            channeltag.SetFillColor(ROOT.kWhite)
            channeltag.SetShadowColor(ROOT.kWhite)
            channeltag.Draw()
            if highestCSV and not highestPT:
                c1.Print(plotDir+"/bjetdiscr_CSV/"+plots[pk][plot]['name']+"_"+pk+".png")
            if highestPT and not highestCSV:
                c1.Print(plotDir+"/bjetdiscr_pt/"+plots[pk][plot]['name']+"_"+pk+".png")

    for plot in plotsSF['SF'].keys():
        bkg_stack_SF = ROOT.THStack("bkgs_SF","bkgs_SF")
        l=ROOT.TLegend(0.6,0.6,1.0,1.0)
        l.SetFillColor(0)
        l.SetShadowColor(ROOT.kWhite)
        l.SetBorderSize(1)
        l.SetTextSize(legendtextsize)
        for b in backgrounds:
            bkgforstack = plots['ee'][plot]['histo'][b["name"]]
            bkgforstack.Add(plots['mumu'][plot]['histo'][b["name"]])
            bkg_stack_SF.Add(bkgforstack,"h")
            l.AddEntry(bkgforstack, b["name"])

        c1 = ROOT.TCanvas()
        bkg_stack_SF.SetMaximum(2*bkg_stack.GetMaximum())
        bkg_stack_SF.SetMinimum(yminimum)
        bkg_stack_SF.Draw()
        bkg_stack_SF.GetXaxis().SetTitle(plotsSF['SF'][plot]['title'])
        bkg_stack_SF.GetYaxis().SetTitle("Events / %i GeV"%( (plotsSF['SF'][plot]['binning'][2]-plotsSF['SF'][plot]['binning'][1])/plotsSF['SF'][plot]['binning'][0]) )
        c1.SetLogy()
        signalPlot_1 = plots['ee'][plot]['histo'][signal['path'][0]].Clone()
        signalPlot_1.Add(plots['mumu'][plot]['histo'][signal['path'][0]])
        signalPlot_2 = plots['ee'][plot]['histo'][signal['path'][2]].Clone()
        signalPlot_2.Add(plots['mumu'][plot]['histo'][signal['path'][2]])
        signalPlot_1.Scale(signalscaling)
        signalPlot_2.Scale(signalscaling)
        signalPlot_1.SetLineColor(ROOT.kBlack)
        signalPlot_2.SetLineColor(ROOT.kCyan)
        signalPlot_1.SetLineWidth(3)
        signalPlot_2.SetLineWidth(3)
        signalPlot_1.Draw("same")
        signalPlot_2.Draw("same")
        l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
        l.AddEntry(signalPlot_2, signal['name'][1]+" x " + str(signalscaling), "l")
        l.Draw()
        channeltag = ROOT.TPaveText(0.45,0.8,0.59,0.85,"NDC")
        channeltag.AddText("SF")
        channeltag.SetFillColor(ROOT.kWhite)
        channeltag.SetShadowColor(ROOT.kWhite)
        channeltag.Draw()
        if highestCSV and not highestPT:
            c1.Print(plotDir+"/bjetdiscr_CSV/"+plotsSF['SF'][plot]['name']+"_SF.png")
        if highestPT and not highestCSV:
            c1.Print(plotDir+"/bjetdiscr_pt/"+plotsSF['SF'][plot]['name']+"_SF.png")


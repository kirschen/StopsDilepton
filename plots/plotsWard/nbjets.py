import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, deltaPhi
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, getGenParts
from StopsDilepton.tools.user import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()


#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True
makedraw2D = False
makelatextables = False #Ignore this if you're not Ward
mt2llcuts = {'80':80., '100':100., '110':110, '120':120., '130':130., '140':140., '150':150.} #make plots named mt2llwithcutat..... I.E. lines 134-136
metcut = '40'     #USED IN LINE 28
luminosity = 42.    #USED IN LINES 345-346

#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#See here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = "met_pt>40&&Sum$(LepGood_pt>20)>=2"

#######################################################
#                 load all the samples                #
#######################################################
#from StopsDilepton.samples.cmgTuplesPostProcessed_PHYS14 import *
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
backgrounds = [diBosons_50ns,WJetsToLNu_50ns,singleTop_50ns,QCDMu_50ns,DYHT_50ns,TTJets_50ns]
#backgrounds = [singleTop_50ns,DY_50ns,TTJets_50ns]
signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
data = [DoubleEG_50ns,DoubleMuon_50ns,MuonEG_50ns]

#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals+data:
    s['chain'] = getChain(s,histname="")

#######################################################
#           define binning of 1D histograms           #
#######################################################
njetsbinning = [15,0,15]
nbjetsbinning = [10,0,10]

#######################################################
#             make plot in each sample:               #
#######################################################
plots = {\
    'mumu':{\
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    },
    'ee':{\
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    },
    'emu':{\
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    },
}


#######################################################
#            Start filling in the histograms          #
#######################################################
for s in backgrounds+signals+data:
    #construct 1D histograms
    for pk in plots.keys():
        for plot in plots[pk].keys():
            plots[pk][plot]['histo'][s["name"]] = ROOT.TH1F(plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, *plots[pk][plot]['binning'])
            plots[pk][plot]['histo'][s["name"]].Sumw2()

    chain = s["chain"]

    chain.SetBranchStatus("*",0)
    chain.SetBranchStatus("met_pt",1)
    chain.SetBranchStatus("met_phi",1)
    chain.SetBranchStatus("Jet_pt",1)
    chain.SetBranchStatus("Jet_eta",1)
    chain.SetBranchStatus("Jet_id",1)
    chain.SetBranchStatus("Jet_btagCSV",1)
    chain.SetBranchStatus("LepGood_pt",1)
    chain.SetBranchStatus("LepGood_eta",1)
    chain.SetBranchStatus("LepGood_phi",1)
    chain.SetBranchStatus("LepGood_charge",1)
    chain.SetBranchStatus("LepGood_dxy",1)
    chain.SetBranchStatus("LepGood_dz",1)
    chain.SetBranchStatus("LepGood_relIso03",1)
    chain.SetBranchStatus("LepGood_tightId",1)
    chain.SetBranchStatus("LepGood_pdgId",1)
    chain.SetBranchStatus("LepGood_mediumMuonId",1)
    chain.SetBranchStatus("LepGood_miniRelIso",1)
    chain.SetBranchStatus("LepGood_sip3d",1)
    chain.SetBranchStatus("LepGood_mvaIdPhys14",1)
    chain.SetBranchStatus("LepGood_convVeto",1)
    chain.SetBranchStatus("LepGood_lostHits",1)
    chain.SetBranchStatus("Jet_eta",1)
    chain.SetBranchStatus("Jet_pt",1)
    chain.SetBranchStatus("Jet_phi",1)
    chain.SetBranchStatus("Jet_btagCMVA",1)
    chain.SetBranchStatus("Jet_btagCSV",1)
    chain.SetBranchStatus("Jet_id",1)
    chain.SetBranchStatus("weight",1)
    if s not in data:
        chain.SetBranchStatus("genWeight",1)
        chain.SetBranchStatus("Jet_mcMatchFlav",1)
        chain.SetBranchStatus("xsec",1)
        chain.SetBranchStatus("Jet_partonId",1)

    #Using Event loop
    #get EList after preselection
    print '\n', "Looping over %s" % s["name"]
    eList = getEList(chain, preselection)
    nEvents = eList.GetN()/reduceStat
    print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)

    for ev in range(nEvents):

        increment = 50
        if nEvents>increment and ev%(nEvents/increment)==0:
            sys.stdout.write('\r' + "=" * (ev / (nEvents/increment)) +  " " * ((nEvents - ev)/ (nEvents/increment)) + "]" +  str(round((ev+1) / (float(nEvents)/100),2)) + "%")
            sys.stdout.flush()
            sys.stdout.write('\r')
        chain.GetEntry(eList.GetEntry(ev))
        mt2Calc.reset()
        #event weight (L= 4fb^-1)
        weight = reduceStat*getVarValue(chain, "weight")

        if s not in data: weight = weight*(luminosity/4000.)

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
                    zveto = True
            #Opposite Flavor
            if lep == 'emu':
                if len(leptons[lep]['file'][0])==1 and len(leptons[lep]['file'][1])==1 and leptons[lep]['file'][0][0]['pdgId']*leptons[lep]['file'][1][0]['pdgId']<0:
                    twoleptons = True
                    l0pt, l0eta, l0phi = leptons[lep]['file'][0][0]['pt'],  leptons[lep]['file'][0][0]['eta'],  leptons[lep]['file'][0][0]['phi']
                    l1pt, l1eta, l1phi = leptons[lep]['file'][1][0]['pt'],  leptons[lep]['file'][1][0]['eta'],  leptons[lep]['file'][1][0]['phi']
                    if l1pt > l0pt :
                        leadingleptonpt = l1pt
                        subleadingleptonpt = l0pt
                    else:
                        leadingleptonpt = l0pt
                        subleadingleptonpt = l1pt
                    mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
                    zveto = False
            if (twoleptons and mll>20 and not zveto) or (twoleptons and mll > 20 and zveto and abs(mll-91.2)>15):
                jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
                ht = sum([j['pt'] for j in jets])
                PhiMetJet1 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",0))
                PhiMetJet2 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",1))

                bjetspt = filter(lambda j:j['btagCSV']>0.814, jets)
                nobjets = filter(lambda j:j['btagCSV']<=0.814, jets)
                plots[leptons[lep]['name']]['nbjets']['histo'][s["name"]].Fill(len(bjetspt),weight)
                plots[leptons[lep]['name']]['njets']['histo'][s["name"]].Fill(len(jets),weight)
    del eList


#######################################################
#             Drawing done here                       #
#######################################################
#Some coloring

TTJets_50ns["color"]=7
DYHT_50ns["color"]=8
QCDMu_50ns["color"]=46
singleTop_50ns["color"]=40
diBosons_50ns["color"]=ROOT.kOrange
WJetsToLNu_50ns['color']=ROOT.kRed-10
#Plotvariables
signal = {'path': ["SMS_T2tt_2J_mStop425_mLSP325","SMS_T2tt_2J_mStop500_mLSP325","SMS_T2tt_2J_mStop650_mLSP325","SMS_T2tt_2J_mStop850_mLSP100"], 'name': ["T2tt(425,325)","T2tt(500,325)","T2tt(650,325)","T2tt(850,100)"]}
yminimum = 0.1
ymaximum = 30
legendtextsize = 0.028
signalscaling = 100
histopad =  [0.01, 0.2, 0.99, 0.99]
datamcpad = [0.01, 0.08, 0.99, 0.3]

if makedraw1D:

    for pk in plots.keys():
        for plot in plots[pk].keys():
            #Make a stack for backgrounds
            l=ROOT.TLegend(0.6,0.5,0.99,1.0)
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
            datahist = plots[pk][plot]['histo'][data[0]["name"]].Clone()
            for d in data[1:]:
                datahist.Add(plots[pk][plot]['histo'][d["name"]])
            datahist.SetMarkerColor(ROOT.kBlack)
            #Plot!
            c1 = ROOT.TCanvas()
            bkg_stack.SetMaximum(ymaximum*bkg_stack.GetMaximum())
            bkg_stack.SetMinimum(yminimum)
            bkg_stack.Draw()
            bkg_stack.GetXaxis().SetTitle(plots[pk][plot]['title'])
            bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (plots[pk][plot]['binning'][2]-plots[pk][plot]['binning'][1])/plots[pk][plot]['binning'][0]) )
            c1.SetLogy()
            signalPlot_1 = plots[pk][plot]['histo'][signal['path'][0]].Clone()
            signalPlot_2 = plots[pk][plot]['histo'][signal['path'][1]].Clone()
            signalPlot_3 = plots[pk][plot]['histo'][signal['path'][2]].Clone()
            signalPlot_4 = plots[pk][plot]['histo'][signal['path'][3]].Clone()
            signalPlot_1.Scale(signalscaling)
            signalPlot_2.Scale(signalscaling)
            signalPlot_3.Scale(signalscaling)
            signalPlot_4.Scale(signalscaling)
            signalPlot_1.SetLineColor(ROOT.kRed)
            signalPlot_2.SetLineColor(ROOT.kBlue)
            signalPlot_3.SetLineColor(ROOT.kViolet)
            signalPlot_4.SetLineColor(ROOT.kGray)
            signalPlot_1.SetLineWidth(3)
            signalPlot_2.SetLineWidth(3)
            signalPlot_3.SetLineWidth(3)
            signalPlot_4.SetLineWidth(3)
            signalPlot_1.Draw("HISTsame")
            signalPlot_2.Draw("HISTsame")
            signalPlot_3.Draw("HISTsame")
            signalPlot_4.Draw("HISTsame")
            datahist.Draw("peSAME")
            l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
            l.AddEntry(signalPlot_2, signal['name'][1]+" x " + str(signalscaling), "l")
            l.AddEntry(signalPlot_3, signal['name'][2]+" x " + str(signalscaling), "l")
            l.AddEntry(signalPlot_4, signal['name'][3]+" x " + str(signalscaling), "l")
            l.AddEntry(datahist, "data", "pe")
            l.Draw()
            channeltag = ROOT.TPaveText(0.4,0.75,0.59,0.85,"NDC")
            firstlep, secondlep = pk[:len(pk)/2], pk[len(pk)/2:]
            if firstlep == 'mu':
                firstlep = '#' + firstlep
            if secondlep == 'mu':
                secondlep = '#' + secondlep
            channeltag.AddText(firstlep+secondlep)
            if plots[pk][plot].has_key('tag'):
                print 'Tag found, adding to histogram'
                channeltag.AddText(plots[pk][plot]['tag'])
            channeltag.AddText("lumi: "+str(luminosity)+' pb^{-1}')
            channeltag.SetFillColor(ROOT.kWhite)
            channeltag.SetShadowColor(ROOT.kWhite)
            channeltag.Draw()
            c1.Print(plotDir+"/test/nbjets/"+plots[pk][plot]['name']+"_"+pk+".png")

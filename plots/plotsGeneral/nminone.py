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
reduceStat = 100 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True
makedraw2D = False
makelatextables = False #Ignore this if you're not Ward
metcut = '0'     #USED IN LINE 28
metsignifcut = 7.    #USED IN LINE 401
luminosity = 10000.    #USED IN LINES 345-346
mt2llcut = 0.

#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#See here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
#preselection = 'met_pt>'+metcut+'&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.89)>=1&&Sum$(LepGood_pt>20)==2'
preselection = 'met_pt>'+metcut+'&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=1&&Sum$(LepGood_pt>20)==2'

#######################################################
#                 load all the samples                #
#######################################################
#from StopsDilepton.samples.cmgTuplesPostProcessed_PHYS14 import *
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
backgrounds = [diBosons_50ns,WJetsToLNu_50ns,singleTop_50ns,QCDMu_50ns,DYHT_50ns,TTJets_50ns]
#backgrounds = [singleTop_50ns,DYHT_50ns,TTJets_50ns]
signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
#data = [DoubleEG_50ns,DoubleMuon_50ns,MuonEG_50ns]
data = []

#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals+data:
    s['chain'] = getChain(s,histname="")

#######################################################
#           define binning of 1D histograms           #
#######################################################
mt2llbinning = [25,0,300]
metbinning = [20,0,800]
kinMetSigbinning = [25,0,25]
njetsbinning = [15,0,15]
nbjetsbinning = [10,0,10]
dphibinning = [20,0,pi]

#######################################################
#             make plot in each sample:               #
#######################################################
plots = {\
    'mumu':{\
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV), #jets>=2, #bjets>=1', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2}), #jets>=2, #bjets>=1', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'dPhi': {'title': 'dPhi(MET,jet1|jet2)', 'name': 'dphi', 'binning': dphibinning, 'histo':{}},
    },
    'ee':{\
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV), #jets>=2, #bjets>=1', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2}), #jets>=2, #bjets>=1', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'dPhi': {'title': 'dPhi(MET,jet1|jet2)', 'name': 'dphi', 'binning': dphibinning, 'histo':{}},
    },
    'emu':{\
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV), #jets>=2, #bjets>=1', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2}), #jets>=2, #bjets>=1', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'dPhi': {'title': 'dPhi(MET,jet1|jet2)', 'name': 'dphi', 'binning': dphibinning, 'histo':{}},
    },
}

#######################################################
#          make plots specifically for SF             #
#######################################################
plotsSF = {\
    'SF':{\
    'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
    'met': {'title':'E^{miss}_{T} (GeV), #jets>=2, #bjets>=1', 'name':'MET', 'binning': metbinning, 'histo':{}},
    'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2}), #jets>=2, #bjets>=1', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
    'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
    'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
    'dPhi': {'title': 'dPhi(MET,jet1|jet2)', 'name': 'dphi', 'binning': dphibinning, 'histo':{}},
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
                bjetspt = filter(lambda j:j['btagCSV']>0.89, jets)
                nobjets = filter(lambda j:j['btagCSV']<=0.89, jets)
                PhiMetJet1 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",0))
                PhiMetJet2 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",1))

                if PhiMetJet1 <= PhiMetJet2: PhiMetJet_small = PhiMetJet1
                else:                        PhiMetJet_small = PhiMetJet2

                mt2Calc.setMet(met,metPhi)
                mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)

                mt2ll = mt2Calc.mt2ll()

                if mt2ll > mt2llcut:

                    if met>40:

                        plots[leptons[lep]['name']]['njets']['histo'][s["name"]].Fill(len(jets),weight)
                        plots[leptons[lep]['name']]['nbjets']['histo'][s["name"]].Fill(len(bjetspt),weight)
                        if len(jets)>=2 and len(bjetspt)>=1:
                            plots[leptons[lep]['name']]['mt2ll']['histo'][s["name"]].Fill(mt2ll,weight)
                            plots[leptons[lep]['name']]['kinMetSig']['histo'][s["name"]].Fill(met/sqrt(ht), weight)
                            plots[leptons[lep]['name']]['met']['histo'][s["name"]].Fill(met, weight)
                            plots[leptons[lep]['name']]['dPhi']['histo'][s["name"]].Fill(PhiMetJet_small, weight)

    #Add overflow bin to last bin
    for pk in plots.keys():
        for plot in plots[pk].keys():
            nXbins = plots[pk][plot]['histo'][s['name']].GetNbinsX()
            overflow = plots[pk][plot]['histo'][s['name']].GetBinContent(nXbins+1)
            plots[pk][plot]['histo'][s['name']].AddBinContent(nXbins, overflow)
            plots[pk][plot]['histo'][s['name']].SetBinContent(nXbins+1, 0)
            overflow2 = plots[pk][plot]['histo'][s['name']].GetBinContent(nXbins+1)

    del eList

#print plots['emu']['mt2ll']['histo'][TTJets_50ns['name']].Integral()
#print plots['mumu']['mt2ll']['histo'][TTJets_50ns['name']].Integral()


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
yminimum = 10
ymaximum = 100
legendtextsize = 0.028
signalscaling = 100
histopad =  [0.01, 0.2, 0.99, 0.99]
datamcpad = [0.01, 0.08, 0.99, 0.3]

if makedraw1D:

    for pk in plots.keys():
        for plot in plots[pk].keys():
            #Make a stack for backgrounds
            l=ROOT.TLegend(0.6,0.6,0.99,1.0)
            l.SetFillColor(0)
            l.SetShadowColor(ROOT.kWhite)
            l.SetBorderSize(1)
            l.SetTextSize(legendtextsize)
            bkg_stack = ROOT.THStack("bkgs","bkgs")
            #totalbackground = plots[pk][plot]['histo'][backgrounds[0]["name"]].Clone()
            for b in backgrounds:
                plots[pk][plot]['histo'][b["name"]].SetFillColor(b["color"])
                plots[pk][plot]['histo'][b["name"]].SetMarkerColor(b["color"])
                plots[pk][plot]['histo'][b["name"]].SetMarkerSize(0)
                bkg_stack.Add(plots[pk][plot]['histo'][b["name"]],"h")
                l.AddEntry(plots[pk][plot]['histo'][b["name"]], b["name"])
                #if b != backgrounds[0]: totalbackground.Add(plots[pk][plot]['histo'][b["name"]])
            if len(data)!= 0:datahist = plots[pk][plot]['histo'][data[0]["name"]].Clone()
            for d in data[1:]:
                datahist.Add(plots[pk][plot]['histo'][d["name"]])
            if len(data)!= 0: datahist.SetMarkerColor(ROOT.kBlack)
        #Plot!
            c1 = ROOT.TCanvas()
            #pad1 = ROOT.TPad("","",histopad[0],histopad[1],histopad[2],histopad[3])
            #pad1.Draw()
            #pad1.cd()
            bkg_stack.SetMaximum(ymaximum*bkg_stack.GetMaximum())
            bkg_stack.SetMinimum(yminimum)
            bkg_stack.Draw()
            bkg_stack.GetXaxis().SetTitle(plots[pk][plot]['title'])
            bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (plots[pk][plot]['binning'][2]-plots[pk][plot]['binning'][1])/plots[pk][plot]['binning'][0]) )
            #bkg_stack.GetXaxis().SetLabelSize(0.)
            #pad1.SetLogy()
            c1.SetLogy()
            signalPlot_1 = plots[pk][plot]['histo'][signal['path'][0]].Clone()
            signalPlot_2 = plots[pk][plot]['histo'][signal['path'][2]].Clone()
            signalPlot_1.Scale(signalscaling)
            signalPlot_2.Scale(signalscaling)
            signalPlot_1.SetLineColor(ROOT.kRed)
            signalPlot_2.SetLineColor(ROOT.kBlue)
            signalPlot_1.SetLineWidth(3)
            signalPlot_2.SetLineWidth(3)
            signalPlot_1.Draw("HISTsame")
            signalPlot_2.Draw("HISTsame")
            if len(data)!= 0:datahist.Draw("peSAME")
            l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
            l.AddEntry(signalPlot_2, signal['name'][2]+" x " + str(signalscaling), "l")
            if len(data)!= 0: l.AddEntry(datahist, "data", "pe")
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
            #c1.cd()
            #pad2 = ROOT.TPad("","",datamcpad[0],datamcpad[1],datamcpad[2],datamcpad[3])
            #pad2.SetGrid()
            #pad2.SetBottomMargin(0.4)
            #pad2.Draw()
            #pad2.cd()
            #ratio = datahist.Clone()
            #ratio.Divide(totalbackground)
            #ratio.SetMarkerStyle(20)
            #ratio.SetMarkerSize(0.5)
            #ratio.GetYaxis().SetTitle("Data/Bkg.")
            #ratio.GetXaxis().SetTitle(plots[pk][plot]['title'])
            #ratio.GetXaxis().SetTitleSize(0.2)
            #ratio.GetYaxis().SetTitleSize(0.18)
            #ratio.GetYaxis().SetTitleOffset(0.29)
            #ratio.GetXaxis().SetTitleOffset(0.8)
            #ratio.GetYaxis().SetLabelSize(0.1)
            #ratio.GetXaxis().SetLabelSize(0.18)
            #ratio.Draw("pe")
            #c1.cd()
            c1.Print(plotDir+"/test/nminone/"+plots[pk][plot]['name']+"_"+pk+"_mt2llcut_"+str(mt2llcut)+".png")

    for plot in plotsSF['SF'].keys():
        bkg_stack_SF = ROOT.THStack("bkgs_SF","bkgs_SF")
        l=ROOT.TLegend(0.6,0.6,0.99,1.0)
        l.SetFillColor(0)
        l.SetShadowColor(ROOT.kWhite)
        l.SetBorderSize(1)
        l.SetTextSize(legendtextsize)
        #totalbackground = plots['ee'][plot]['histo'][backgrounds[0]["name"]].Clone()
        #totalbackground.Add(plots['mumu'][plot]['histo'][backgrounds[0]["name"]])
        for b in backgrounds:
            bkgforstack = plots['ee'][plot]['histo'][b["name"]]
            bkgforstack.Add(plots['mumu'][plot]['histo'][b["name"]])
            bkg_stack_SF.Add(bkgforstack,"h")
            l.AddEntry(bkgforstack, b["name"])
            #if b != backgrounds[0]:
            #  totalbackground.Add(plots['ee'][plot]['histo'][b["name"]])
            #  totalbackground.Add(plots['mumu'][plot]['histo'][b["name"]])
        if len(data)!= 0:
            datahist = plots['ee'][plot]['histo'][data[0]["name"]].Clone()
            datahist.Add(plots['mumu'][plot]['histo'][data[0]["name"]])
            for d in data[1:]:
                datahist.Add(plots['ee'][plot]['histo'][d["name"]])
                datahist.Add(plots['mumu'][plot]['histo'][d["name"]])
            datahist.SetMarkerColor(ROOT.kBlack)
        c1 = ROOT.TCanvas()
        #pad1 = ROOT.TPad("","",histopad[0],histopad[1],histopad[2],histopad[3])
        #pad1.Draw()
        #pad1.cd()
        bkg_stack_SF.SetMaximum(ymaximum*bkg_stack_SF.GetMaximum())
        bkg_stack_SF.SetMinimum(yminimum)
        bkg_stack_SF.Draw()
        bkg_stack_SF.GetXaxis().SetTitle(plotsSF['SF'][plot]['title'])
        bkg_stack_SF.GetYaxis().SetTitle("Events / %i GeV"%( (plotsSF['SF'][plot]['binning'][2]-plotsSF['SF'][plot]['binning'][1])/plotsSF['SF'][plot]['binning'][0]) )
        #bkg_stack_SF.GetXaxis().SetLabelSize(0.)
        #pad1.SetLogy()
        c1.SetLogy()
        signalPlot_1 = plots['ee'][plot]['histo'][signal['path'][0]].Clone()
        signalPlot_1.Add(plots['mumu'][plot]['histo'][signal['path'][0]])
        signalPlot_2 = plots['ee'][plot]['histo'][signal['path'][2]].Clone()
        signalPlot_2.Add(plots['mumu'][plot]['histo'][signal['path'][2]])
        signalPlot_1.Scale(signalscaling)
        signalPlot_2.Scale(signalscaling)
        signalPlot_1.SetLineColor(ROOT.kRed)
        signalPlot_2.SetLineColor(ROOT.kBlue)
        signalPlot_1.SetLineWidth(3)
        signalPlot_2.SetLineWidth(3)
        signalPlot_1.Draw("HISTsame")
        signalPlot_2.Draw("HISTsame")
        if len(data)!= 0: datahist.Draw("peSAME")
        l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
        l.AddEntry(signalPlot_2, signal['name'][2]+" x " + str(signalscaling), "l")
        if len(data)!= 0: l.AddEntry(datahist, "data", "pe")
        l.Draw()
        channeltag = ROOT.TPaveText(0.4,0.75,0.59,0.85,"NDC")
        channeltag.AddText("SF")
        if plotsSF['SF'][plot].has_key('tag'):
            print 'Tag found, adding to histogram'
            channeltag.AddText(plots[pk][plot]['tag'])
        channeltag.AddText("lumi: "+str(luminosity)+'pb^{-1}')
        channeltag.SetFillColor(ROOT.kWhite)
        channeltag.SetShadowColor(ROOT.kWhite)
        channeltag.Draw()
        # c1.cd()
        # pad2 = ROOT.TPad("","",datamcpad[0],datamcpad[1],datamcpad[2],datamcpad[3])
        # pad2.SetGrid()
        # pad2.SetBottomMargin(0.4)
        # pad2.Draw()
        # pad2.cd()
        # ratio = datahist.Clone()
        # ratio.Divide(totalbackground)
        # ratio.SetMarkerStyle(20)
        # ratio.SetMarkerSize(0.5)
        # ratio.GetYaxis().SetTitle("Data/Bkg.")
        #   #ratio.GetYaxis().SetNdivisions(502)
        # ratio.GetXaxis().SetTitle(plots[pk][plot]['title'])
        # ratio.GetXaxis().SetTitleSize(0.2)
        # ratio.GetYaxis().SetTitleSize(0.18)
        # ratio.GetYaxis().SetTitleOffset(0.29)
        # ratio.GetXaxis().SetTitleOffset(0.8)
        # ratio.GetYaxis().SetLabelSize(0.1)
        # ratio.GetXaxis().SetLabelSize(0.18)
        # ratio.Draw("pe")
        # c1.cd()
        c1.Print(plotDir+"/test/nminone/"+plotsSF['SF'][plot]['name']+"_SF_mt2llcut"+str(mt2llcut)+".png")

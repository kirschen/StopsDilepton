import ROOT, glob
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy as n

from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()

from math import *
from StopsDilepton.tools.helpers import getChain,getWeight,getVarValue, getEList
from StopsDilepton.tools.localInfo import *
from datetime import datetime
from StopsDilepton.tools.puReweighting import getReweightingFunction
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, getGenParts, getGoodLeptons, getGoodElectrons, getGoodMuons, getGoodJets

import collections

#puReweightingFunc = getReweightingFunction(era="doubleMu_onZ_isOS_1500pb_nVert_reweight")
#puReweighting = lambda c:puReweightingFunc(getVarValue(c, "nVert"))


import sys

start = datetime.now()
print '\n','\n', "Starting code",'\n','\n'

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *


#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 100 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True
makeTexFile = True
mt2llcutscaling = False
noscaling = False

#btagcoeff          = 0.89
btagcoeff          = 0.605
njetscut           = [">="+str(sys.argv[1]),str(sys.argv[1])+'m']
nbjetscut          = [">="+str(sys.argv[2]),str(sys.argv[2])+'m']


presel_njet        = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)'+njetscut[0]
presel_nbjet       = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>'+str(btagcoeff)+')'+nbjetscut[0]
presel_nlep        = '(nGoodElectrons+nGoodMuons)>=2&&Sum$(LepGood_pt>10)>=2'
presel_triggers    = '(HLT_mumuIso||HLT_ee_DZ||HLT_mue)'

luminosity = DoubleMuon_Run2015D["lumi"]

datacut = "(Flag_HBHENoiseFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter&&weight>0)"

preselection = presel_njet+'&&'+presel_nbjet+'&&'+presel_nlep+'&&'+presel_triggers

exec('sample=['+sys.argv[3]+']')

#backgrounds = [DY_HT_LO,TTJets,WJetsToLNu,singleTop,QCD_Mu5,TTZ,TTW,TZQ,TTH,diBoson]
#backgrounds = [TTZ]

#######################################################
#            get the TChains for each sample          #
#######################################################
for s in sample:
    s['chain'] = getChain(s,histname="")

mt2llbinning = [15,0,300]
mllbinning = [50,0,150]
metbinning = [30,0,300]
zptbinning = [50,0,300]
lepptbinning = [40,0,400]
njetsbinning = [10,0,10]
nbjetsbinning = [10,0,10]


ListOfDataEvents = []


plots = {\
    '2l':{\
        #'dl_mt2ll_onZ':{'title':'MT2ll (GeV)', 'name':'MT2ll_2l_onZ', 'binning': mt2llbinning, 'histo':{'totalbkg':0.,}}, #offZ mt2ll doesn't make sense
        'dl_mass_onZ':{'title':'M_{ll} (GeV)', 'name':'Mll_2l_onZ', 'binning': mllbinning, 'histo':{'totalbkg':0.,}},
        'dl_mass_offZ':{'title':'M_{ll} (GeV)', 'name':'Mll_2l_offZ', 'binning': mllbinning, 'histo':{'totalbkg':0.,}},
        'met_pt_onZ':{'title':'MET (GeV)', 'name':'MET_2l_onZ', 'binning': metbinning, 'histo':{'totalbkg':0.,}},
        'met_pt_offZ':{'title':'MET (GeV)', 'name':'MET_2l_offZ', 'binning': metbinning, 'histo':{'totalbkg':0.,}},
        'Z_pt_onZ':{'title':'p_{T} Z (GeV)', 'name':'ZpT_2l_onZ', 'binning': zptbinning, 'histo':{'totalbkg':0.,}},
        'Z_pt_offZ':{'title':'p_{T} Z (GeV)', 'name':'ZpT_2l_offZ', 'binning': zptbinning, 'histo':{'totalbkg':0.,}},
        'l1_pt_onZ':{'title':'p_{T} lep1 (GeV)', 'name':'lep1_2l_onZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l1_pt_offZ':{'title':'p_{T} lep1 (GeV)', 'name':'lep1_2l_offZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l2_pt_onZ':{'title':'p_{T} lep2 (GeV)', 'name':'lep2_2l_onZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l2_pt_offZ':{'title':'p_{T} lep2 (GeV)', 'name':'lep2_2l_offZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'njets_onZ':{'title':'njets', 'name':'njets_2l_onZ', 'binning': njetsbinning, 'histo':{'totalbkg':0.,}},
        'njets_offZ':{'title':'njets', 'name':'njets_2l_offZ', 'binning': njetsbinning, 'histo':{'totalbkg':0.,}},
        'nbjets_onZ':{'title':'nbjets', 'name':'nbjets_2l_onZ', 'binning': nbjetsbinning, 'histo':{'totalbkg':0.,}},
        'nbjets_offZ':{'title':'nbjets', 'name':'nbjets_2l_offZ', 'binning': nbjetsbinning, 'histo':{'totalbkg':0.,}},
        },
    '3l':{\
        #'dl_mt2ll_onZ':{'title':'MT2ll (GeV)', 'name':'MT2ll_3l_onZ', 'binning': mt2llbinning, 'histo':{'totalbkg':0.,}}, #offZ mt2ll doesn't make sense
        'dl_mass_onZ':{'title':'M_{ll} (GeV)', 'name':'Mll_3l_onZ', 'binning': mllbinning, 'histo':{'totalbkg':0.,}},
        'dl_mass_offZ':{'title':'M_{ll} (GeV)', 'name':'Mll_3l_offZ', 'binning': mllbinning, 'histo':{'totalbkg':0.,}},
        'met_pt_onZ':{'title':'MET (GeV)', 'name':'MET_3l_onZ', 'binning': metbinning, 'histo':{'totalbkg':0.,}},
        'met_pt_offZ':{'title':'MET (GeV)', 'name':'MET_3l_offZ', 'binning': metbinning, 'histo':{'totalbkg':0.,}},
        'Z_pt_onZ':{'title':'p_{T} Z (GeV)', 'name':'ZpT_3l_onZ', 'binning': zptbinning, 'histo':{'totalbkg':0.,}},
        'Z_pt_offZ':{'title':'p_{T} Z (GeV)', 'name':'ZpT_3l_offZ', 'binning': zptbinning, 'histo':{'totalbkg':0.,}},
        'l1_pt_onZ':{'title':'p_{T} lep1 (GeV)', 'name':'lep1_3l_onZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l1_pt_offZ':{'title':'p_{T} lep1 (GeV)', 'name':'lep1_3l_offZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l2_pt_onZ':{'title':'p_{T} lep2 (GeV)', 'name':'lep2_3l_onZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l2_pt_offZ':{'title':'p_{T} lep2 (GeV)', 'name':'lep2_3l_offZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l3_pt_onZ':{'title':'p_{T} lep3 (GeV)', 'name':'lep3_3l_onZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l3_pt_offZ':{'title':'p_{T} lep3 (GeV)', 'name':'lep3_3l_offZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'njets_onZ':{'title':'njets', 'name':'njets_3l_onZ', 'binning': njetsbinning, 'histo':{'totalbkg':0.,}},
        'njets_offZ':{'title':'njets', 'name':'njets_3l_offZ', 'binning': njetsbinning, 'histo':{'totalbkg':0.,}},
        'nbjets_onZ':{'title':'nbjets', 'name':'nbjets_3l_onZ', 'binning': nbjetsbinning, 'histo':{'totalbkg':0.,}},
        'nbjets_offZ':{'title':'nbjets', 'name':'nbjets_3l_offZ', 'binning': nbjetsbinning, 'histo':{'totalbkg':0.,}},
        },
    '4l':{\
        #'dl_mt2ll_onZ':{'title':'MT2ll (GeV)', 'name':'MT2ll_4l_onZ', 'binning': mt2llbinning, 'histo':{'totalbkg':0.,}}, #offZ mt2ll doesn't make sense
        'dl_mass_onZ':{'title':'M_{ll} (GeV)', 'name':'Mll_4l_onZ', 'binning': mllbinning, 'histo':{'totalbkg':0.,}},
        'dl_mass_offZ':{'title':'M_{ll} (GeV)', 'name':'Mll_4l_offZ', 'binning': mllbinning, 'histo':{'totalbkg':0.,}},
        'met_pt_onZ':{'title':'MET (GeV)', 'name':'MET_4l_onZ', 'binning': metbinning, 'histo':{'totalbkg':0.,}},
        'met_pt_offZ':{'title':'MET (GeV)', 'name':'MET_4l_offZ', 'binning': metbinning, 'histo':{'totalbkg':0.,}},
        'Z_pt_onZ':{'title':'p_{T} Z (GeV)', 'name':'ZpT_4l_onZ', 'binning': zptbinning, 'histo':{'totalbkg':0.,}},
        'Z_pt_offZ':{'title':'p_{T} Z (GeV)', 'name':'ZpT_4l_offZ', 'binning': zptbinning, 'histo':{'totalbkg':0.,}},
        'l1_pt_onZ':{'title':'p_{T} lep1 (GeV)', 'name':'lep1_4l_onZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l1_pt_offZ':{'title':'p_{T} lep1 (GeV)', 'name':'lep1_4l_offZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l2_pt_onZ':{'title':'p_{T} lep2 (GeV)', 'name':'lep2_4l_onZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l2_pt_offZ':{'title':'p_{T} lep2 (GeV)', 'name':'lep2_4l_offZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l3_pt_onZ':{'title':'p_{T} lep3 (GeV)', 'name':'lep3_4l_onZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l3_pt_offZ':{'title':'p_{T} lep3 (GeV)', 'name':'lep3_4l_offZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l4_pt_onZ':{'title':'p_{T} lep4 (GeV)', 'name':'lep4_4l_onZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'l4_pt_offZ':{'title':'p_{T} lep4 (GeV)', 'name':'lep4_4l_offZ', 'binning': lepptbinning, 'histo':{'totalbkg':0.,}},
        'njets_onZ':{'title':'njets', 'name':'njets_4l_onZ', 'binning': njetsbinning, 'histo':{'totalbkg':0.,}},
        'njets_offZ':{'title':'njets', 'name':'njets_4l_offZ', 'binning': njetsbinning, 'histo':{'totalbkg':0.,}},
        'nbjets_onZ':{'title':'nbjets', 'name':'nbjets_4l_onZ', 'binning': nbjetsbinning, 'histo':{'totalbkg':0.,}},
        'nbjets_offZ':{'title':'nbjets', 'name':'nbjets_4l_offZ', 'binning': nbjetsbinning, 'histo':{'totalbkg':0.,}},
        },
    }


#######################################################
#            Start filling in the histograms          #
#######################################################
for s in sample:
    #construct 1D histograms
    for lepton in plots.keys():
        for plot in plots[lepton].keys():
                plots[lepton][plot]['histo'][s["name"]] = ROOT.TH1D(plots[lepton][plot]['name']+"_"+s["name"], plots[lepton][plot]['name']+"_"+s["name"], *plots[lepton][plot]['binning'])
                plots[lepton][plot]['histo'][s["name"]].Sumw2()

    chain = s["chain"]

    if (s == DoubleMuon_Run2015D):
        eList =  getEList(chain, preselection+'&&'+datacut+'&&HLT_mumuIso')
    elif (s == DoubleEG_Run2015D):
        eList =  getEList(chain, preselection+'&&'+datacut+'&&HLT_ee_DZ')
    elif (s == MuonEG_Run2015D):
        eList =  getEList(chain, preselection+'&&'+datacut+'&&HLT_mue')
    else:
        eList = getEList(chain, preselection)

    nEvents = eList.GetN()/reduceStat
    print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)

      #start event loop
    for ev in range(nEvents):

        ##################################
        #        Processing output       #
        ##################################
        increment = 50
        if nEvents>increment and ev%(nEvents/increment)==0:
            sys.stdout.write('\r' + "=" * (ev / (nEvents/increment)) +  " " * ((nEvents - ev)/ (nEvents/increment)) + "]" +  str(round((ev+1) / (float(nEvents)/100),2)) + "%")
            sys.stdout.flush()
            sys.stdout.write('\r')
        chain.GetEntry(eList.GetEntry(ev))

        #No double counting in data samples
        if getVarValue(chain, "evt") in ListOfDataEvents:
            continue
        else:
            ListOfDataEvents.append(getVarValue(chain, "evt"))

        weight = reduceStat*getVarValue(chain, "weight")*(luminosity/1000.) if not s['isData'] else 1

        #leptons
        electrons = getGoodElectrons(chain)
        muons = getGoodMuons(chain)
        leptons = getGoodLeptons(chain,10)

        #mt2ll for 2l
        mt2ll = getVarValue(chain,"dl_mt2ll")

        #met
        met = getVarValue(chain,'met_pt')

        #jets
        jets =  getGoodJets(chain)
        bjets = filter(lambda j:j['btagCSV']>btagcoeff, jets)
        nobjets = filter(lambda j:j['btagCSV']<=btagcoeff, jets)


        zleptons = []
        ttleptons = []

        #Find two leptons that are from a Z boson. If no lepton is found mZ = 999999.
        mZ = 9999999.
        Z_pt = 9999999.
        for Lep1 in range(len(leptons)-1):
            l1 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(leptons[Lep1]['pt'], leptons[Lep1]['eta'], leptons[Lep1]['phi'], 0)
            for Lep2 in range(Lep1+1,len(leptons)):
                if (leptons[Lep1]['pdgId']*leptons[Lep2]['pdgId'] < 0):
                    if (abs(leptons[Lep1]['pdgId']) == abs(leptons[Lep2]['pdgId'])):
                        l2 = ROOT.TLorentzVector()
                        l2.SetPtEtaPhiM(leptons[Lep2]['pt'], leptons[Lep2]['eta'], leptons[Lep2]['phi'], 0)
                        diLep = l1+l2
                        if (abs(diLep.M()-91.2) < abs(mZ-91.2)):
                            mZ = diLep.M()
                            Z_pt = diLep.Pt()
                            zleptons = [leptons[Lep1],leptons[Lep2]]


        if abs(mZ - 91.2) < 15: #there is a dilepton pair from a Z
            if len(leptons)==2:
                plots['2l']['dl_mass_onZ']['histo'][s["name"]].Fill(mZ,weight)
                plots['2l']['Z_pt_onZ']['histo'][s["name"]].Fill(Z_pt,weight)
                plots['2l']['l1_pt_onZ']['histo'][s['name']].Fill(leptons[0]['pt'],weight)
                plots['2l']['l2_pt_onZ']['histo'][s['name']].Fill(leptons[1]['pt'],weight)
                plots['2l']['njets_onZ']['histo'][s['name']].Fill(len(jets),weight)
                plots['2l']['nbjets_onZ']['histo'][s['name']].Fill(len(bjets),weight)
                plots['2l']['met_pt_onZ']['histo'][s['name']].Fill(met,weight)
            elif len(leptons)==3:
                #mt2Calc.reset()
                plots['3l']['dl_mass_onZ']['histo'][s["name"]].Fill(mZ,weight)
                plots['3l']['Z_pt_onZ']['histo'][s["name"]].Fill(Z_pt,weight)
                plots['3l']['l1_pt_onZ']['histo'][s['name']].Fill(leptons[0]['pt'],weight)
                plots['3l']['l2_pt_onZ']['histo'][s['name']].Fill(leptons[1]['pt'],weight)
                plots['3l']['l3_pt_onZ']['histo'][s['name']].Fill(leptons[2]['pt'],weight)
                plots['3l']['njets_onZ']['histo'][s['name']].Fill(len(jets),weight)
                plots['3l']['nbjets_onZ']['histo'][s['name']].Fill(len(bjets),weight)
                plots['3l']['met_pt_onZ']['histo'][s['name']].Fill(met,weight)
            elif len(leptons)==4:
                #mt2Calc.reset()
                #print len(ttleptons), len(zleptons), ttleptons[0]['pt'],ttleptons[1]['pt'],zleptons[0]['pt'],zleptons[1]['pt']
                #mt2Calc.setLeptons(???)
                plots['4l']['dl_mass_onZ']['histo'][s["name"]].Fill(mZ,weight)
                plots['4l']['Z_pt_onZ']['histo'][s["name"]].Fill(Z_pt,weight)
                plots['4l']['l1_pt_onZ']['histo'][s['name']].Fill(leptons[0]['pt'],weight)
                plots['4l']['l2_pt_onZ']['histo'][s['name']].Fill(leptons[1]['pt'],weight)
                plots['4l']['l3_pt_onZ']['histo'][s['name']].Fill(leptons[2]['pt'],weight)
                plots['4l']['l4_pt_onZ']['histo'][s['name']].Fill(leptons[3]['pt'],weight)
                plots['4l']['njets_onZ']['histo'][s['name']].Fill(len(jets),weight)
                plots['4l']['nbjets_onZ']['histo'][s['name']].Fill(len(bjets),weight)
                plots['4l']['met_pt_onZ']['histo'][s['name']].Fill(met,weight)
        else:
            if len(leptons)==2:
                plots['2l']['dl_mass_offZ']['histo'][s["name"]].Fill(mZ,weight)
                plots['2l']['Z_pt_offZ']['histo'][s["name"]].Fill(Z_pt,weight)
                plots['2l']['l1_pt_offZ']['histo'][s['name']].Fill(leptons[0]['pt'],weight)
                plots['2l']['l2_pt_offZ']['histo'][s['name']].Fill(leptons[1]['pt'],weight)
                plots['2l']['njets_offZ']['histo'][s['name']].Fill(len(jets),weight)
                plots['2l']['nbjets_offZ']['histo'][s['name']].Fill(len(bjets),weight)
                plots['2l']['met_pt_offZ']['histo'][s['name']].Fill(met,weight)
            elif len(leptons)==3:
                plots['3l']['dl_mass_offZ']['histo'][s["name"]].Fill(mZ,weight)
                plots['3l']['Z_pt_offZ']['histo'][s["name"]].Fill(Z_pt,weight)
                plots['3l']['l1_pt_offZ']['histo'][s['name']].Fill(leptons[0]['pt'],weight)
                plots['3l']['l2_pt_offZ']['histo'][s['name']].Fill(leptons[1]['pt'],weight)
                plots['3l']['l3_pt_offZ']['histo'][s['name']].Fill(leptons[2]['pt'],weight)
                plots['3l']['njets_offZ']['histo'][s['name']].Fill(len(jets),weight)
                plots['3l']['nbjets_offZ']['histo'][s['name']].Fill(len(bjets),weight)
                plots['3l']['met_pt_offZ']['histo'][s['name']].Fill(met,weight)
            elif len(leptons)==4:
                plots['4l']['dl_mass_offZ']['histo'][s["name"]].Fill(mZ,weight)
                plots['4l']['Z_pt_offZ']['histo'][s["name"]].Fill(Z_pt,weight)
                plots['4l']['l1_pt_offZ']['histo'][s['name']].Fill(leptons[0]['pt'],weight)
                plots['4l']['l2_pt_offZ']['histo'][s['name']].Fill(leptons[1]['pt'],weight)
                plots['4l']['l3_pt_offZ']['histo'][s['name']].Fill(leptons[2]['pt'],weight)
                plots['4l']['l4_pt_offZ']['histo'][s['name']].Fill(leptons[3]['pt'],weight)
                plots['4l']['njets_offZ']['histo'][s['name']].Fill(len(jets),weight)
                plots['4l']['nbjets_offZ']['histo'][s['name']].Fill(len(bjets),weight)
                plots['4l']['met_pt_offZ']['histo'][s['name']].Fill(met,weight)


    #overflow
    for lepton in plots.keys():
        for plot in plots[lepton].keys():
            nbinsx        = plots[lepton][plot]['histo'][s['name']].GetNbinsX()
            lastbin       = plots[lepton][plot]['histo'][s['name']].GetBinContent(nbinsx)
            error         = plots[lepton][plot]['histo'][s['name']].GetBinError(nbinsx)
            overflowbin   = plots[lepton][plot]['histo'][s['name']].GetBinContent(nbinsx+1)
            overflowerror = plots[lepton][plot]['histo'][s['name']].GetBinError(nbinsx+1)
            plots[lepton][plot]['histo'][s['name']].SetBinContent(nbinsx,lastbin+overflowbin)
            plots[lepton][plot]['histo'][s['name']].SetBinError(nbinsx,sqrt(error**2+overflowerror**2))
            plots[lepton][plot]['histo'][s['name']].SetBinContent(nbinsx+1,0.)
            plots[lepton][plot]['histo'][s['name']].SetBinError(nbinsx+1,0.)
                #Remove bins with negative events
            for i in range(nbinsx):
                if plots[lepton][plot]['histo'][s['name']].GetBinContent(i+1) < 0: plots[lepton][plot]['histo'][s['name']].SetBinContent(i+1,0.)


processtime = datetime.now()
print "Time to process chains: ", processtime - start


#######################################################
#             Output text file                        #
#######################################################

for lepton in plots.keys():
    for s in sample:
        rootfilepath = "./OutputRootFiles/"+lepton+'_njet_'+njetscut[1]+'_nbjet_'+nbjetscut[1]+'/data/' if s['isData'] else "./OutputRootFiles/"+lepton+'_njet_'+njetscut[1]+'_nbjet_'+nbjetscut[1]+'/backgrounds/'
        if not os.path.exists(rootfilepath): os.makedirs(rootfilepath)
        rootfile = ROOT.TFile(rootfilepath+s['name']+".root","recreate")
        for plot in plots[lepton].keys():
            plots[lepton][plot]['histo'][s['name']].Write()
        rootfile.Close()

makeplotstime = datetime.now()

print '\n','\n', "Total time processing: ", makeplotstime-start


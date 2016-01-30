import ROOT
from ROOT import TTree, TFile, AddressOf, gROOT
from array import array
import numpy as n

from math import *
import array

## This is a test

from StopsDilepton.tools.mtautau import mtautau as mtautau_
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, deltaPhi
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.localInfo import *

#preselection: MET>50, HT>100, n_bjets>=2
#Once we decided in HT definition and b-tag WP we add those variables to the tuple.
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2

#preselectionMC = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=0&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=0&&Sum$(LepGood_pt>20)>=2'
preselectionMC = 'met_pt>80 && Sum$(Jet_pt>30 && abs(Jet_eta)<2.4 && Jet_id && Jet_btagCSV>0.890)>=1 && Sum$(Jet_pt>30 && abs(Jet_eta)<2.4 && Jet_id)>=2 && Sum$(LepGood_pt>20)>=2'
preselectionData = preselectionMC+'&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter&&Flag_HBHENoiseFilterMinZeroPatched'
prefix="def"
reduceStat = 1
lumiScale = 1.

#load all the samples
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *

#backgrounds = [diBosons_25ns,WJetsToLNu_25ns,singleTop_25ns,QCDMu_25ns, DYHT_25ns, DY_25ns, TTX_25ns, TTLep_25ns]
backgrounds = [TTLep_25ns]

for b in backgrounds:
    b['isData']=0

signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
#signals = [SMS_T2tt_2J_mStop425_mLSP325]

for s in signals:
    s['isData']=0

data = [DoubleEG_25ns,DoubleMuon_25ns,MuonEG_25ns]
for d in data:
    d['isData']=1

#get the TChains for each sample
for s in backgrounds+signals+data:
    s['chain'] = getChain(s,histname="")

#for s in backgrounds+signals+data:
for s in backgrounds+signals:

	fout = TFile(s["name"]+'.root','RECREATE')
	t = TTree('anaTree','Tree of variables')

	MET                   = n.zeros(1, dtype=float)
	METPhi                = n.zeros(1, dtype=float)
	METSqrtHT             = n.zeros(1, dtype=float)
	ptLeadingJet          = n.zeros(1, dtype=float)
	ptSubLeadingJet       = n.zeros(1, dtype=float)
	ptLeadingBJet         = n.zeros(1, dtype=float)
	etaLeadingBJet        = n.zeros(1, dtype=float)
	etaLeadingJet         = n.zeros(1, dtype=float)
	etaSubLeadingJet      = n.zeros(1, dtype=float)
	phiLeadingJet         = n.zeros(1, dtype=float)
	phiSubLeadingJet      = n.zeros(1, dtype=float)
	ptLeadingLepton       = n.zeros(1, dtype=float)
	ptSubLeadingLepton    = n.zeros(1, dtype=float)
	mt2ll                 = n.zeros(1, dtype=float)
	mt2bb                 = n.zeros(1, dtype=float)
	mt2blbl               = n.zeros(1, dtype=float)
	HT                    = n.zeros(1, dtype=float)
	dileptonInvariantMass = n.zeros(1, dtype=float)
	xsecWeight            = n.zeros(1, dtype=float)
	pileupWeight          = n.zeros(1, dtype=float)
	mindPhiMetJet12       = n.zeros(1, dtype=float)
	nbjets                = n.zeros(1, dtype=int)
	njets                 = n.zeros(1, dtype=int)
	nleptons              = n.zeros(1, dtype=int)
	nVertices             = n.zeros(1, dtype=int)
	isMC                  = n.zeros(1, dtype=int)
	isElecElec            = n.zeros(1, dtype=int)
	isMuonMuon            = n.zeros(1, dtype=int)
	isMuonElec            = n.zeros(1, dtype=int)
	EventNumber           = n.zeros(1, dtype=int)
	Process               = bytearray(200)

	lepton1 = ROOT.TLorentzVector()
	lepton2 = ROOT.TLorentzVector()
	jet1 = ROOT.TLorentzVector()
	jet2 = ROOT.TLorentzVector()
	bjet1 = ROOT.TLorentzVector()
	bjet2 = ROOT.TLorentzVector()

	t.Branch("MET", MET, "MET/D")
	t.Branch("METPhi", METPhi, "METPhi/D")
	t.Branch("METSqrtHT", METSqrtHT, "METSqrtHT/D")
	t.Branch("ptLeadingJet", ptLeadingJet, "ptLeadingJet/D")
	t.Branch("ptLeadingBJet", ptLeadingBJet, "ptLeadingBJet/D")
	t.Branch("etaLeadingBJet", etaLeadingBJet, "etaLeadingBJet/D")
	t.Branch("ptSubLeadingJet", ptSubLeadingJet, "ptSubLeadingJet/D")
	t.Branch("etaLeadingJet", etaLeadingJet, "etaLeadingJet/D")
	t.Branch("etaSubLeadingJet", etaSubLeadingJet, "etaSubLeadingJet/D")
	t.Branch("phiLeadingJet", phiLeadingJet, "phiLeadingJet/D")
	t.Branch("phiSubLeadingJet", phiSubLeadingJet, "phiSubLeadingJet/D")
	t.Branch("ptLeadingLepton", ptLeadingLepton, "ptLeadingLepton/D")
	t.Branch("ptSubLeadingLepton", ptSubLeadingLepton, "ptSubLeadingLepton/D")
	t.Branch("mt2ll", mt2ll, "mt2ll/D")
	t.Branch("mt2bb", mt2bb, "mt2bb/D")
	t.Branch("mt2blbl", mt2blbl, "mt2blbl/D")
	t.Branch("HT", HT, "HT/D")
	t.Branch("dileptonInvariantMass", dileptonInvariantMass, "dileptonInvariantMass/D")
	t.Branch("xsecWeight", xsecWeight, "xsecWeight/D")
	t.Branch("pileupWeight", pileupWeight, "pileupWeight/D")
	t.Branch("mindPhiMetJet12", mindPhiMetJet12, "mindPhiMetJet12/D")
	t.Branch("nbjets", nbjets, "nbjets/I")
	t.Branch("njets", njets, "njets/I")
	t.Branch("nleptons", nleptons, "nleptons/I")
	t.Branch("nVertices", nVertices, "nVertices/I")
	t.Branch("isMC", isMC, "isMC/I")
	t.Branch("isElecElec", isElecElec, "isElecElec/I")
	t.Branch("isMuonMuon", isMuonMuon, "isMuonMuon/I")
	t.Branch("isMuonElec", isMuonElec, "isMuonElec/I")
	t.Branch("EventNumber", EventNumber, "EventNumber/I")
	t.Branch("LeadingLepton","TLorentzVector",lepton1)
	t.Branch("SubLeadingLepton","TLorentzVector",lepton2)
	t.Branch('Process', Process, 'Process[200]/C')


	chain = s["chain"]

	if s['isData']==0:
		eList = getEList(chain, preselectionMC)
		nEvents = eList.GetN()/reduceStat
		print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselectionMC,nEvents)

	else:
		eList = getEList(chain, preselectionData)
		nEvents = eList.GetN()/reduceStat
		print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselectionData,nEvents)


	for ev in range(nEvents):

		if ev%10000==0:print "At %i/%i"%(ev,nEvents)
		chain.GetEntry(eList.GetEntry(ev))

		mt2Calc.reset()
		weight = reduceStat*getVarValue(chain, "weight")*lumiScale if not s['isData'] else 1

		met = getVarValue(chain, "met_pt")
		metPhi = getVarValue(chain, "met_phi")
		metEta = getVarValue(chain, "met_eta")
		EventNumber[0] = getVarValue(chain, "evt")
		mt2ll[0] = 0
		mt2bb[0] = 0
		mt2blbl[0] = 0
		MET[0] = met
		METPhi[0] = metPhi
		xsecWeight[0] = weight
		isMC[0] = 1-s['isData']
		isElecElec[0] = 0
		isMuonMuon[0] = 0
		isMuonElec[0] = 0
		if not s["name"].find("SMS"):
			pileupWeight[0] = getVarValue(chain,"puWeight")

		trigger = 0

		if s['isData'] == 1:
			triggerMuMu = getVarValue(chain,"HLT_mumuIso")
			triggerEleEle = getVarValue(chain,"HLT_ee_DZ")
			triggerMuEle = getVarValue(chain,"HLT_mue")

		if s['isData'] == 0:
			trigger = 1
		if not s["name"].find("DoubleEG") and triggerEleEle :
			trigger = 1
			isElecElec[0] = 1
		if not s["name"].find("DoubleEG") and triggerEleEle==0 :
			trigger = 0
			isElecElec[0] = 1
		if not s["name"].find("DoubleMuon") and triggerMuMu :
			trigger = 1
			isMuonMuon[0] = 1
		if not s["name"].find("DoubleMuon") and triggerMuMu==0 :
			trigger = 0
			isMuonMuon[0] = 1
		if not s["name"].find("MuonEG") and triggerMuEle :
			trigger = 1
			isMuonElec[0] = 1
		if not s["name"].find("MuonEG") and triggerMuEle==0 :
			trigger = 0
			isMuonElec[0] = 1


		leptons = filter(lambda l: looseMuID(l) or looseEleID(l), getLeptons(chain))
		jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
		bjets = filter(lambda j:j['btagCSV']>0.890, jets)

		nbjets[0] = len(bjets)
		njets[0] = len(jets)
		nleptons[0] = len(leptons)
		Process[:200] = s["name"]
		HT[0] = sum([j['pt'] for j in jets])
		METSqrtHT[0] = met/HT[0]
		ptLeadingBJet[0] = bjets[0]['pt']
		etaLeadingBJet[0] = bjets[0]['eta']

		PhiMetJet1 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",0))
		PhiMetJet2 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",1))

		if PhiMetJet1 <= PhiMetJet2: PhiMetJet_small = PhiMetJet1
		else:                        PhiMetJet_small = PhiMetJet2

		mindPhiMetJet12[0] = PhiMetJet_small


		ptLeadingJet[0] = getVarValue(chain, "Jet_pt",0)
		ptSubLeadingJet[0] = getVarValue(chain, "Jet_pt",1)
		etaLeadingJet[0] = getVarValue(chain, "Jet_eta",0)
		etaSubLeadingJet[0] = getVarValue(chain, "Jet_eta",1)
		phiLeadingJet[0] = getVarValue(chain, "Jet_phi",0)
		phiSubLeadingJet[0] = getVarValue(chain, "Jet_phi",1)


		if len(leptons)>=2 and leptons[0]['pdgId']*leptons[1]['pdgId']<0:
		
			## OF SF choice
			if leptons[0]['pdgId']+leptons[1]['pdgId']==0 and abs(leptons[0]['pdgId'])==11:
				isElecElec[0] = 1
			if leptons[0]['pdgId']+leptons[1]['pdgId']==0 and abs(leptons[0]['pdgId'])==13:
				isMuonMuon[0] = 1
			if abs(leptons[0]['pdgId'])+abs(leptons[1]['pdgId'])==24:
				isMuonElec[0] = 1


			l0pt, l0eta, l0phi, l0mass = leptons[0]['pt'],  leptons[0]['eta'],  leptons[0]['phi'],  leptons[0]['mass']
			l1pt, l1eta, l1phi, l1mass = leptons[1]['pt'],  leptons[1]['eta'],  leptons[1]['phi'],  leptons[1]['mass']

			mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))

			dileptonInvariantMass[0] = mll
			ptLeadingLepton[0] = l0pt
			ptSubLeadingLepton[0] = l1pt

			lepton1.SetPtEtaPhiM(l0pt, l0eta, l0phi, l0mass)
			lepton2.SetPtEtaPhiM(l1pt, l1eta, l1phi, l1mass)

			l0pt, l0eta, l0phi, l0mass = leptons[0]['pt'],  leptons[0]['eta'],  leptons[0]['phi'],  leptons[0]['mass']

		mt2Calc.setMet(met,metPhi)
		#mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
		#mt2ll[0] = mt2Calc.mt2ll()
		mt2ll[0] = getVarValue(chain, "dl_mt2ll")

		if len(bjets)>=2:
			mt2Calc.setBJets(bjets[0]['pt'], bjets[0]['eta'], bjets[0]['phi'], bjets[1]['pt'], bjets[1]['eta'], bjets[1]['phi'])
			#mt2bb[0]   = mt2Calc.mt2bb()
			#mt2blbl[0] = mt2Calc.mt2blbl()
			mt2bb[0]   = getVarValue(chain, "dl_mt2bb")
			mt2blbl[0] = getVarValue(chain, "dl_mt2blbl")
		

		if dileptonInvariantMass[0] > 20 and nbjets[0] >0 and nleptons[0]==2 and njets[0] > 1 and MET[0] > 80 and mindPhiMetJet12[0] > 0.25 and MET[0]/sqrt(HT[0]) > 5:
#		if mll>20 and njets[0] > 0 and nleptons[0]==2 and trigger==1:

			t.Fill()


	del eList

	fout.Write()
	fout.Close()


# move to outdir
outdir = "ntuples"
os.system("mv DoubleMuon.root "+outdir+"/DoubleMuon.root")
os.system("mv DoubleEG.root "+outdir+"/DoubleElec.root")
os.system("mv MuonEG.root "+outdir+"/MuonElec.root")
os.system("mv SMS_T2tt_2J_mStop425_mLSP325.root "+outdir+"/T2ttS425N325.root")
os.system("mv SMS_T2tt_2J_mStop500_mLSP325.root "+outdir+"/T2ttS500N325.root")
os.system("mv SMS_T2tt_2J_mStop650_mLSP325.root "+outdir+"/T2ttS650N325.root")
os.system("mv SMS_T2tt_2J_mStop850_mLSP100.root "+outdir+"/T2ttS850N100.root")
os.system("mv DrellYan* "+outdir)
os.system("mv QCD_Mu.root "+outdir+"/QCDMu.root")
os.system("mv WW+WZ+ZZ.root "+outdir+"/DiBosons.root")
os.system("mv W+Jets.root "+outdir+"/WJets.root")
os.system("mv singletop.root "+outdir+"/singleTop.root")
os.system("mv tt+Jets2L2Nu.root "+outdir+"/TTJets2L2Nu.root")
os.system("mv TTX.root "+outdir+"/TTX.root")

import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
import array
from StopsDilepton.tools.user import plotDir
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getGoodLeptons, default_muon_selector, default_ele_selector, getJets, leptonVars, jetVars
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.user import *

reduceStat = 1
lumiScale = 10.

#load all the samples
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *

#ttjets = TTJets_Lep
#ttjets['name']="TTLep_1l2l"
ttjets = TTJets
ttjets['name']="TTJetsNLO"
ttjets['chain'] = getChain(ttjets,histname="")
#prefix = "mRelIso01"
prefix="mAODv2"
#others={'name':'ST/VV/TTX', 'chain':getChain([WJetsToLNu,DY,singleTop,TTX,diBoson], histname="")}

#samples = [ttjets, others]
samples = [ttjets]

cuts=[
  ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
  ("njet2", "(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2"),
  ("nbtag1", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1"),
  ("mll20", "dl_mass>20"),
  ("met80", "met_pt>80"),
  ("metSig5", "met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>5"),
  ("dPhiJet0-dPhiJet1", "cos(met_phi-Jet_phi[0])<cos(0.25)&&cos(met_phi-Jet_phi[1])<cos(0.25)"),
  ("isOS","isOS==1"),
  ("SFZVeto","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"),
# ("mRelIso01", "LepGood_miniRelIso[l1_index]<0.1&&LepGood_miniRelIso[l2_index]<0.1")
    ]
preselection = "&&".join([c[1] for c in cuts])

plots = {\
    'mt2ll_reco':               {'label':'reco',               'color':ROOT.kBlack, 'title':'M_{T2ll} (GeV)', 'binning': [315/15,0,315], 'histo':{}},
    'mt2ll_puppi':              {'label':'puppi',              'color':ROOT.kPink, 'title':'M_{T2ll} (GeV)', 'binning': [315/15,0,315], 'histo':{}},
    'mt2ll_genMetPt':           {'label':'met: genPt',         'color':ROOT.kRed, 'title':'M_{T2ll} (GeV)', 'binning': [315/15,0,315], 'histo':{}},
    'mt2ll_genMetPhi':          {'label':'met: genPhi',        'color':ROOT.kBlue, 'title':'M_{T2ll} (GeV)', 'binning': [315/15,0,315], 'histo':{}},
    'mt2ll_genMet':             {'label':'met: genMet',        'color':ROOT.kGreen, 'title':'M_{T2ll} (GeV)', 'binning': [315/15,0,315], 'histo':{}},
    'mt2ll_metJetCorr':         {'label':'met: gen-jet corr.', 'color':ROOT.kMagenta, 'title':'M_{T2ll} (GeV)', 'binning': [315/15,0,315], 'histo':{}},
    'mt2ll_LepGenMatch':        {'label':'lep: genMatch',      'color':ROOT.kCyan, 'title':'M_{T2ll} (GeV)', 'binning': [315/15,0,315], 'histo':{}},
    'mt2ll_LepGenPt':           {'label':'lep: genPt',         'color':ROOT.kViolet, 'title':'M_{T2ll} (GeV)', 'binning': [315/15,0,315], 'histo':{}},
    'mt2ll_LepGenPt_genMet':    {'label':'gen lep + gen Met',  'color':ROOT.kOrange, 'title':'M_{T2ll} (GeV)', 'binning': [315/15,0,315], 'histo':{}},
#  'mt2ll_LepGenPtPhi':        {'label':'lep: genLep', 'title':'M_{T2ll} (GeV)', 'binning': [21,0,420], 'histo':{}},
#  'mt2bb': {'title':'M_{T2ll} (GeV)', 'name':'mt2ll', 'binning': [18,60,420], 'histo':{}},
#  'mt2blbl': {'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': [21,0,420], 'histo':{}},
}

#plots = {\
#  'mt2ll_reco':               {'label':'reco',               'color':ROOT.kBlack, 'title':'M_{T2ll} (GeV)', 'binning': [28,70,140], 'histo':{}},
#  'mt2ll_puppi':              {'label':'puppi',              'color':ROOT.kPink, 'title':'M_{T2ll} (GeV)', 'binning': [28,70,140], 'histo':{}},
#  'mt2ll_genMetPt':           {'label':'met: genPt',         'color':ROOT.kRed, 'title':'M_{T2ll} (GeV)', 'binning': [28,70,140], 'histo':{}},
#  'mt2ll_genMetPhi':          {'label':'met: genPhi',        'color':ROOT.kBlue, 'title':'M_{T2ll} (GeV)', 'binning': [28,70,140], 'histo':{}},
#  'mt2ll_genMet':             {'label':'met: genMet',        'color':ROOT.kGreen, 'title':'M_{T2ll} (GeV)', 'binning': [28,70,140], 'histo':{}},
#  'mt2ll_metJetCorr':         {'label':'met: gen-jet corr.', 'color':ROOT.kMagenta, 'title':'M_{T2ll} (GeV)', 'binning': [28,70,140], 'histo':{}},
#  'mt2ll_LepGenMatch':        {'label':'lep: genMatch',      'color':ROOT.kCyan, 'title':'M_{T2ll} (GeV)', 'binning': [28,70,140], 'histo':{}},
#  'mt2ll_LepGenPt':           {'label':'lep: genPt',         'color':ROOT.kViolet, 'title':'M_{T2ll} (GeV)', 'binning': [28,70,140], 'histo':{}},
#  'mt2ll_LepGenPt_genMet':    {'label':'gen lep + gen Met',  'color':ROOT.kOrange, 'title':'M_{T2ll} (GeV)', 'binning': [28,70,140], 'histo':{}},
#}

#make plot in each sample:
for sample in samples:
    for pk in plots.keys():
        plots[pk]['histo'][sample['name']] = ROOT.TH1F("plot_"+sample["name"], "plot_"+sample["name"], *(plots[pk]['binning']))
        plots[pk]['histo'][sample['name']].SetLineColor(plots[pk]['color'])
        plots[pk]['histo'][sample['name']].SetMarkerColor(plots[pk]['color'])
        plots[pk]['histo'][sample['name']].SetMarkerSize(0)

    chain = sample["chain"]
    print "Looping over %s" % sample["name"]
    eList = getEList(chain, preselection)
    nEvents = eList.GetN()/reduceStat
    print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),sample["name"],preselection,nEvents)
    for ev in range(nEvents):
        if ev%10000==0:print "At %i/%i"%(ev,nEvents)
        chain.GetEntry(eList.GetEntry(ev))
        mt2Calc.reset()
        weight = reduceStat*getVarValue(chain, "weight")*lumiScale
        met = getVarValue(chain, "met_pt")
        metPhi = getVarValue(chain, "met_phi")
        puppiMet = getVarValue(chain, "puppiMet_pt")
        puppiMetPhi = getVarValue(chain, "puppiMet_phi")
        genMet = getVarValue(chain, "met_genPt")
        genMetPhi = getVarValue(chain, "met_genPhi")
        leptons = getGoodLeptons(chain, leptonVars+['mcMatchId', 'mcMatchAny', 'mcPt'])
        l0GenPt, l0HasMatch, l0pt, l0eta, l0phi = leptons[0]['mcPt'],  abs(leptons[0]['mcMatchId'])==6, leptons[0]['pt'],  leptons[0]['eta'],  leptons[0]['phi']
        l1GenPt, l1HasMatch, l1pt, l1eta, l1phi = leptons[1]['mcPt'],  abs(leptons[1]['mcMatchId'])==6, leptons[1]['pt'],  leptons[1]['eta'],  leptons[1]['phi']
        mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain, jetVars+['mcPt', 'mcMatchId', 'mcFlavour']))
    #  bjets = filter(lambda j:j['btagCSV']>0.890, jets)
    #  print len(leptons), len(bjets), mll
        mt2Calc.setMet(met,metPhi)
        mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
        mt2ll = mt2Calc.mt2ll()
        plots['mt2ll_reco']['histo'][sample["name"]].Fill(mt2ll, weight)

        mt2Calc.setMet(puppiMet,puppiMetPhi)
        mt2ll = mt2Calc.mt2ll()
        plots['mt2ll_puppi']['histo'][sample["name"]].Fill(mt2ll, weight)

        mt2Calc.setMet(genMet,metPhi)
        mt2ll_genMetPt = mt2Calc.mt2ll()
        plots['mt2ll_genMetPt']['histo'][sample["name"]].Fill(mt2ll_genMetPt, weight)

        mt2Calc.setMet(met,genMetPhi)
        mt2ll_genMetPhi = mt2Calc.mt2ll()
        plots['mt2ll_genMetPhi']['histo'][sample["name"]].Fill(mt2ll_genMetPhi, weight)

        mt2Calc.setMet(genMet,genMetPhi)
        mt2ll_genMet = mt2Calc.mt2ll()
        plots['mt2ll_genMet']['histo'][sample["name"]].Fill(mt2ll_genMet, weight)

        sx, sy = 0., 0.
        for jet in jets:
            sx+= cos(jet['phi'])*(-jet['pt']+jet['mcPt'])
            sy+= sin(jet['phi'])*(-jet['pt']+jet['mcPt'])
        metCorrPt  = sqrt((met*cos(metPhi)-sx)**2 + (met*sin(metPhi)-sy)**2)
        metCorrPhi = atan2(met*sin(metPhi)-sy, met*cos(metPhi)-sx)
        mt2Calc.setMet(metCorrPt,metCorrPhi)
        mt2ll_metJetCorr = mt2Calc.mt2ll()
        plots['mt2ll_metJetCorr']['histo'][sample["name"]].Fill(mt2ll_metJetCorr, weight)

        if l0HasMatch and l1HasMatch:
            plots['mt2ll_LepGenMatch']['histo'][sample["name"]].Fill(mt2ll, weight)

            mt2Calc.setMet(met,metPhi)
            mt2Calc.setLeptons(l0GenPt, l0eta, l0phi, l1GenPt, l1eta, l1phi)
            mt2ll_LepGenPt = mt2Calc.mt2ll()
            plots['mt2ll_LepGenPt']['histo'][sample["name"]].Fill(mt2ll_LepGenPt, weight)

            mt2Calc.setMet(genMet,genMetPhi)
            mt2ll_LepGenPt_genMet = mt2Calc.mt2ll()
            plots['mt2ll_LepGenPt_genMet']['histo'][sample["name"]].Fill(mt2ll_LepGenPt_genMet, weight)

    del eList

plotList=[
['all', ['mt2ll_reco',
'mt2ll_genMetPt',
'mt2ll_genMetPhi',
'mt2ll_genMet',
'mt2ll_metJetCorr',
'mt2ll_LepGenMatch',
'mt2ll_LepGenPt',
'mt2ll_LepGenPt_genMet']],

['gen1', ['mt2ll_reco',
'mt2ll_genMet',
'mt2ll_LepGenPt_genMet']],

['puppi', ['mt2ll_reco',
'mt2ll_genMet',
'mt2ll_LepGenPt_genMet',
'mt2ll_puppi']],

['gen2', ['mt2ll_reco',
'mt2ll_genMet',
'mt2ll_metJetCorr']],

['genMet',['mt2ll_reco',
'mt2ll_genMetPt',
'mt2ll_genMetPhi',
'mt2ll_genMet']],

['genLep',['mt2ll_reco',
'mt2ll_LepGenMatch',
'mt2ll_LepGenPt',
'mt2ll_LepGenPt_genMet']]
]

#for pk in plots.keys():
#Make a stack for backgrounds
for name, keys in plotList:
    l=ROOT.TLegend(0.6,1.0-0.05*len(keys),1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    first = True
    opt="h"
    c1 = ROOT.TCanvas()
    for pk in keys:
        plots[pk]['histo'][ttjets['name']].Draw(opt)
        plots[pk]['histo'][ttjets['name']].GetXaxis().SetTitle(plots[pk]["title"])
        l.AddEntry(plots[pk]['histo'][ttjets['name']], plots[pk]["label"])
        if first:
            first=False
            opt=opt+"same"
#  plots['mt2ll_reco']['histo'][others['name']].GetXaxis().SetTitle(plots[pk]["title"])
#  plots['mt2ll_reco']['histo'][others['name']].SetLineStyle(ROOT.kDashed)
#  plots['mt2ll_reco']['histo'][others['name']].SetLineColor(ROOT.kBlack)
#  plots['mt2ll_reco']['histo'][others['name']].Draw(opt)
#  l.AddEntry(plots['mt2ll_reco']['histo'][others['name']], others['name'])
    l.Draw()
    c1.SetLogy()
    c1.Print(plotDir+"/png2L/"+prefix+"_"+ttjets['name']+'_mt2ll_'+name+'_tail.png')

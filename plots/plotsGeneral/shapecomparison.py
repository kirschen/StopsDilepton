import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, ele_ID_eta, getGenParts
from StopsDilepton.tools.user import *

#preselection: MET>50, HT>100, n_bjets>=2
#Once we decided in HT definition and b-tag WP we add those variables to the tuple.
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>2&&Sum$(LepGood_pt>20)>=2'

reduceStat = 1

#load all the samples
from StopsDilepton.samples.cmgTuplesPostProcessed_PHYS14 import *
backgrounds = [DY]

#get the TChains for each sample
for s in backgrounds:
    s['chain'] = getChain(s,histname="")


mt2llbinning = [25,0,275]

#make plot in each sample:
plots = {\
    'mumu':{\
        'mt2llonZ_bjets0': {'title':'M_{T2ll} (GeV)', 'name':'MT2llonZ_bjets0', 'binning': mt2llbinning, 'histo':{}},
        'mt2llonZ_bjets1up': {'title':'M_{T2ll} (GeV)', 'name':'MT2llonZ_bjets1up', 'binning': mt2llbinning, 'histo':{}},
        'mt2lloffZ_bjets0': {'title':'M_{T2ll} (GeV)', 'name':'MT2lloffZ_bjets0', 'binning': mt2llbinning, 'histo':{}},
        'mt2lloffZ_bjets1up': {'title':'M_{T2ll} (GeV)', 'name':'MT2lloffZ_bjets1up', 'binning': mt2llbinning, 'histo':{}},
    },
    'ee':{\
        'mt2llonZ_bjets0': {'title':'M_{T2ll} (GeV)', 'name':'MT2llonZ_bjets0', 'binning': mt2llbinning, 'histo':{}},
        'mt2llonZ_bjets1up': {'title':'M_{T2ll} (GeV)', 'name':'MT2llonZ_bjets1up', 'binning': mt2llbinning, 'histo':{}},
        'mt2lloffZ_bjets0': {'title':'M_{T2ll} (GeV)', 'name':'MT2lloffZ_bjets0', 'binning': mt2llbinning, 'histo':{}},
        'mt2lloffZ_bjets1up': {'title':'M_{T2ll} (GeV)', 'name':'MT2lloffZ_bjets1up', 'binning': mt2llbinning, 'histo':{}},
    },
}

#adding SF
plotsSF = {\
    'SF':{\
        'mt2llonZ_bjets0': {'title':'M_{T2ll} (GeV)', 'name':'MT2llonZ_bjets0', 'binning': mt2llbinning, 'histo':{}},
        'mt2llonZ_bjets1up': {'title':'M_{T2ll} (GeV)', 'name':'MT2llonZ_bjets1up', 'binning': mt2llbinning, 'histo':{}},
        'mt2lloffZ_bjets0': {'title':'M_{T2ll} (GeV)', 'name':'MT2lloffZ_bjets0', 'binning': mt2llbinning, 'histo':{}},
        'mt2lloffZ_bjets1up': {'title':'M_{T2ll} (GeV)', 'name':'MT2lloffZ_bjets1up', 'binning': mt2llbinning, 'histo':{}},
    },
}

for s in backgrounds:
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
        #Leptons
        allLeptons = getLeptons(chain)
        muons = filter(looseMuID, allLeptons)
        electrons = filter(looseEleID, allLeptons)

        #SF and OF channels
        leptons = {\
            'mu':   {'name': 'mumu', 'file': muons},
            'e':   {'name': 'ee', 'file': electrons},
            }
        for lep in leptons.keys():
            twoleptons = False
            #Same Flavor
            if len(leptons[lep]['file'])==2 and leptons[lep]['file'][0]['pdgId']*leptons[lep]['file'][1]['pdgId']<0:
                    #genmatching(leptons[lep]['file'][0],genparticles)
                twoleptons = True
                l0pt, l0eta, l0phi = leptons[lep]['file'][0]['pt'],  leptons[lep]['file'][0]['eta'],  leptons[lep]['file'][0]['phi']
                l1pt, l1eta, l1phi = leptons[lep]['file'][1]['pt'],  leptons[lep]['file'][1]['eta'],  leptons[lep]['file'][1]['phi']
                mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
            if twoleptons and mll > 20:
                mt2Calc.setMet(met,metPhi)
                mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
                mt2ll = mt2Calc.mt2ll()
                jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
                bjets = filter(lambda j:j['btagCSV']>0.814, jets)
                if (len(bjets)==0):
                    if(abs(mll-91.2)<15):
                        plots[leptons[lep]['name']]['mt2llonZ_bjets0']['histo'][s["name"]].Fill(mt2ll, weight)
                    else:
                        plots[leptons[lep]['name']]['mt2lloffZ_bjets0']['histo'][s["name"]].Fill(mt2ll, weight)
                if (len(bjets)>0):
                    if (abs(mll-91.2)<15):
                        plots[leptons[lep]['name']]['mt2llonZ_bjets1up']['histo'][s["name"]].Fill(mt2ll, weight)
                    else:
                        plots[leptons[lep]['name']]['mt2lloffZ_bjets1up']['histo'][s["name"]].Fill(mt2ll, weight)
    del eList


legendtextsize = 0.032

for pk in plots.keys():
    l=ROOT.TLegend(0.6,0.6,1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    l.SetTextSize(legendtextsize)

        #Plot!
    c1 = ROOT.TCanvas()
    mt2llonZ_bjets0 = plots[pk]['mt2llonZ_bjets0']['histo']["DY"]
    mt2llonZ_bjets1up = plots[pk]['mt2llonZ_bjets1up']['histo']["DY"]
    mt2lloffZ_bjets0 = plots[pk]['mt2lloffZ_bjets0']['histo']["DY"]
    mt2lloffZ_bjets1up = plots[pk]['mt2lloffZ_bjets1up']['histo']["DY"]

    mt2llonZ_bjets0.Scale(1./mt2llonZ_bjets0.Integral())
    mt2llonZ_bjets1up.Scale(1./mt2llonZ_bjets1up.Integral())
    mt2lloffZ_bjets0.Scale(1./mt2lloffZ_bjets0.Integral())
    mt2lloffZ_bjets1up.Scale(1./mt2lloffZ_bjets1up.Integral())

    mt2llonZ_bjets0.SetLineColor(1)
    mt2llonZ_bjets1up.SetLineColor(2)
    mt2lloffZ_bjets0.SetLineColor(3)
    mt2lloffZ_bjets1up.SetLineColor(4)

    mt2llonZ_bjets0.SetLineWidth(2)
    mt2llonZ_bjets1up.SetLineWidth(2)
    mt2lloffZ_bjets0.SetLineWidth(2)
    mt2lloffZ_bjets1up.SetLineWidth(2)

    l.AddEntry(mt2llonZ_bjets0, "On Z, b=0", "l")
    l.AddEntry(mt2llonZ_bjets1up, "On Z, b#geq1", "l")
    l.AddEntry(mt2lloffZ_bjets0, "Off Z, b=0", "l")
    l.AddEntry(mt2lloffZ_bjets1up, "Off Z, b#geq1", "l")

    mt2llonZ_bjets0.Draw()
    mt2llonZ_bjets0.GetXaxis().SetTitle(plots[pk]['mt2llonZ_bjets0']['title'])
    c1.SetLogy()
    mt2llonZ_bjets1up.Draw("same")
    mt2lloffZ_bjets0.Draw("same")
    mt2lloffZ_bjets1up.Draw("same")
    l.Draw()
    channeltag = ROOT.TPaveText(0.45,0.7,0.59,0.85,"NDC")
    firstlep, secondlep = pk[:len(pk)/2], pk[len(pk)/2:]
    if firstlep == 'mu':
        firstlep = '#' + firstlep
    if secondlep == 'mu':
        secondlep = '#' + secondlep
    channeltag.AddText(firstlep+secondlep)
    channeltag.AddText(DY['name'])
    channeltag.SetFillColor(ROOT.kWhite)
    channeltag.SetShadowColor(ROOT.kWhite)
    channeltag.Draw()
    c1.Print(plotDir+"/test2/m2tllcomparison_"+pk+".png")


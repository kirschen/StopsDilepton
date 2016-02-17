import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
import array, operator
from StopsDilepton.tools.user import plotDir
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, deltaR, getObjFromFile
from StopsDilepton.tools.objectSelection import getGenPartsAll, getGoodLeptons, getLeptons, looseMuID, looseEleID, getJets, leptonVars, jetVars, getGoodTaus
from StopsDilepton.tools.genParticleTools import getDaughters, descendDecay, decaysTo, printDecay
from StopsDilepton.tools.mt2Calculator import mt2Calculator
from StopsDilepton.tools.pdgToName import pdgToName
mt2Calc = mt2Calculator()
from StopsDilepton.tools.user import *

reduceStat = 1
lumiScale = 10.
lepPdgs = [11,13,15]
nuPdgs = [12,14,16]

#load all the samples
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *
small = False
maxN=3 if small else -1
ttjets = TTJets_Lep
ttjets['name']="TTLep_1l2l"
ttjets['chain'] = getChain(ttjets,histname="", maxN=maxN)
prefix="mAODv2"
#others={'name':'ST/VV/TTX', 'chain':getChain([WJetsToLNu,DY,singleTop,TTX,diBoson], histname="")}

samples=[TTJets_Lep]

##vetoed by patched CSC

def vecPtSum(objs, subtract=[]):
    px = sum([o['pt']*cos(o['phi']) for o in objs])
    py = sum([o['pt']*sin(o['phi']) for o in objs])
    px -= sum([o['pt']*cos(o['phi']) for o in subtract])
    py -= sum([o['pt']*sin(o['phi']) for o in subtract])
    return sqrt(px**2+py**2)
def bold(s):
    return '\033[1m'+s+'\033[0m'

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
  ("tauVeto","Sum$(TauGood_pt>20 && abs(TauGood_eta)<2.4 && TauGood_idDecayModeNewDMs>=1 && TauGood_idCI3hit>=1 && TauGood_idAntiMu>=1 && TauGood_idAntiE>=1)==0"),
  ("mRelIso01", "LepGood_miniRelIso[l1_index]<0.1&&LepGood_miniRelIso[l2_index]<0.1"),
  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
  ("ecalDeadCellTPFilter", "(!(run==1&&lumi==45896&&evt==38047218))&&(!(run==1&&lumi==24231&&evt==20087421))&&(!(run==1&&lumi==63423&&evt==52577001))&&(!(run==1&&lumi==87234&&evt==72316782))&&(!(run==1&&lumi==30168&&evt==25009164))"),
#("evt","evt==847303"),#lepton from a jet?
#("evt", "evt==24638863") #fake lepton?
#("evt","evt==3916824")
#("evt","evt==5439514")#jet mism and photon radiation?
("evt","evt==22105179") #electron from top???
#("evt","evt==12255583")
#("evt","evt==72477272")
#("evt","evt==32462388")
#("evt","evt==18695814")
# ("evt","evt==6960642"), #high pt nu
# ("evt","evt==7955897"), #700GeV genMet
#("evt","evt==67750352"), #ele from hadron
#("evt","evt==24638863"),#lep-mism 490.78
#("evt","evt==7955897"),#lep-mism 312.65 (matched to l from -24,24)
#("evt","evt==68529377")# muon with large pt error

    ]
#prefix+="_tauVeto_mRelIso01_looseLepVeto"
preselection = "&&".join([c[1] for c in cuts])

#ttjets['chain'].Scan('Sum$(abs(genPartAll_pdgId)==11&&abs(genPartAll_motherId)==24):Sum$(abs(genPartAll_pdgId)==13&&abs(genPartAll_motherId)==24):Sum$(abs(genPartAll_pdgId)==15&&abs(genPartAll_motherId)==24)', 'isEMu==1&&dl_mt2ll>140&&'+preselection)
#ttjets['chain'].Scan('genPartAll_pdgId:genPartAll_motherId:genPartAll_pt:genPartAll_phi:genPartAll_eta:LepGood_pt:LepGood_eta:LepGood_phi', 'abs(genPartAll_pdgId)==13&&isMuMu==1&&dl_mt2ll>140&&'+preselection)


def dRMatch(coll, dR=0.4, checkPdgId=False):
    def match(l):
        for o in coll:
            if deltaR(l,o)<dR and (l['pdgId']==o['pdgId'] or not checkPdgId): return True
        return False
    return match



for s in samples:
#  for pk in plots.keys():
#    plots[pk]['histo'][s['name']] = ROOT.TH1F("met_"+s["name"], "met_"+s["name"], *(plots[pk]['binning']))

    chain = s["chain"]
    print "Looping over %s" % s["name"]
    eList = getEList(chain, preselection+"&&dl_mt2ll>140")
    nEvents = eList.GetN()/reduceStat
    print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)
    ntot=0
    counterReco={}
    counterRecoGen={}
    counterRecoGen_muMatched={}
    counterRecoGen_eleMatched={}
    counterRecoGen_allMatched={}
    counterRecoGen_oneMuMatchedToB={}
    counterRecoGen_oneEleMatchedToB={}
    counterRecoGen_oneMuMatchedToTau={}
    counterRecoGen_oneEleMatchedToTau={}
    counterRecoGen_recoTau={}
    counterRecoGen_recoMatchedTau={}
    counterRecoGen_looseMu={}
    counterRecoGen_looseEle={}
    counterRecofake_fakeMet50={}
    counterRecofake_fakeMet100={}
    counterRecofake_fakeMet200={}
    counterRecoGen_failRelIso03={}
    badMuonCandidates={}
    badElectronCandidates={}
    for mode in ["isMuMu", "isEE", "isEMu"]:
        counterReco[mode]=0
        counterRecoGen[mode]={}
        counterRecoGen_muMatched[mode]={}
        counterRecoGen_eleMatched[mode]={}
        counterRecoGen_allMatched[mode]={}
        counterRecoGen_oneMuMatchedToB[mode]={}
        counterRecoGen_oneEleMatchedToB[mode]={}
        counterRecoGen_oneMuMatchedToTau[mode]={}
        counterRecoGen_oneEleMatchedToTau[mode]={}
        counterRecoGen_recoTau[mode]={}
        counterRecoGen_recoMatchedTau[mode]={}
        counterRecoGen_looseMu[mode]={}
        counterRecoGen_looseEle[mode]={}
        counterRecofake_fakeMet50[mode]={}
        counterRecofake_fakeMet100[mode]={}
        counterRecofake_fakeMet200[mode]={}
        counterRecoGen_failRelIso03[mode]={}
        badMuonCandidates[mode]=[]
        badElectronCandidates[mode]=[]
    for ev in range(nEvents):
        ntot+=1
        if ev%10000==0:print "At %i/%i"%(ev,nEvents)
        chain.GetEntry(eList.GetEntry(ev))
        mt2Calc.reset()
        weight = reduceStat*getVarValue(chain, "weight")*lumiScale if not s['isData'] else 1
        mt2ll = getVarValue(chain, "dl_mt2ll")
        met = getVarValue(chain, "met_pt")
        metPhi = getVarValue(chain, "met_phi")
        genMet = getVarValue(chain, "met_genPt")
        genMetPhi = getVarValue(chain, "met_genPhi")
        deltaMet = sqrt((met*cos(metPhi)-genMet*cos(genMetPhi))**2+(met*sin(metPhi)-genMet*sin(genMetPhi))**2)
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))

        allLeptons = getLeptons(chain, collVars=leptonVars+['mcMatchId','mcMatchAny','mcMatchTau','mcPt','ip3d', 'relIso03', 'relIso04', 'jetPtRatiov1', 'jetPtRelv1', 'jetPtRelv2', 'jetPtRatiov2', 'jetBTagCSV', 'jetDR'])
        leptons = filter(lambda l: looseMuID(l) or looseEleID(l), allLeptons)

#LepGood_mcMatchId Match to source from hard scatter (pdgId of heaviest particle in chain, 25 for H, 6 for t, 23/24 for W/Z), zero if non-prompt or fake for Leptons after the preselection
#LepGood_mcMatchAny  Match to any final state leptons: 0 if unmatched, 1 if light flavour (including prompt), 4 if charm, 5 if bottom for Leptons after the preselection
#LepGood_mcMatchTau True if the leptons comes from a tau for Leptons after the preselection

#    for l in leptons:
#      if (l['mcMatchAny']==0 and (not (l['mcMatchId']==0))) or ( (not l['mcMatchAny']==0) and (l['mcMatchId']==0)):
#        print "Match?",l

#RECO
        looseMu = filter(lambda l: abs(l['pdgId'])==13 and l['miniRelIso']<0.4 and l['pt']>15, allLeptons)
        looseEle= filter(lambda l: abs(l['pdgId'])==11 and l['miniRelIso']<0.4 and l['pt']>15, allLeptons)
        mu      = filter(lambda l: abs(l['pdgId'])==13, leptons)
        ele     = filter(lambda l: abs(l['pdgId'])==11, leptons)
        tau     = getGoodTaus(chain)

#RECO mathes
        muMatched   = filter(lambda l: abs(l['mcMatchAny'])==1, mu)
        eleMatched  = filter(lambda l: abs(l['mcMatchAny'])==1, ele)
        tauMatched  = filter(lambda l: abs(l['mcMatchId'])>=1, tau)
#GEN
        genParts = getGenPartsAll(chain)
        status1MuEle        =   filter(lambda p: abs(p['pdgId']) in [11,13] and p['status']==1 and p['pt']>10, genParts)
        genLeptons          =   [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId']) in [24] and abs(p['pdgId']) in lepPdgs, genParts)]
        genLeptonsFromTau   =   [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId']) in [15] and abs(p['pdgId']) in lepPdgs, genParts)]
        genNeutrinosFromW   =   [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId']) ==24 and abs(p['pdgId']) in nuPdgs, genParts)]
        genNeutrinosFromTau =   [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId']) ==15 and abs(p['pdgId']) in nuPdgs, genParts)]
        otherNeutrinos      =   [descendDecay(q, genParts) for q in filter(lambda p: abs(p['pdgId']) in nuPdgs, genParts) if not descendDecay(q, genParts) in genNeutrinosFromW+genNeutrinosFromTau]
        genEle =                [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId']) in [24] and abs(p['pdgId'])==11 , genParts)]
        genMu=                  [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId']) in [24] and abs(p['pdgId'])==13 , genParts)]
        genEleFromTau=          [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId']) in [15] and abs(p['pdgId'])==11 , genParts)]
        genMuFromTau=           [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId']) in [15] and abs(p['pdgId'])==13 , genParts)]
        genTau=                 [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==24 and abs(p['pdgId'])==15 , genParts)]
        genTauToE=              [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==24 and abs(p['pdgId'])==15 and decaysTo(p, 11, genParts), genParts)]
        genTauToMu=             [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==24 and abs(p['pdgId'])==15 and decaysTo(p, 13, genParts), genParts)]
        genTauToHad=            [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==24 and abs(p['pdgId'])==15 and not (decaysTo(p, 11, genParts) or decaysTo(p, 13, genParts)), genParts)]
        genNuE =                [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==24 and abs(p['pdgId'])==12 , genParts)]
        genNuMu=                [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==24 and abs(p['pdgId'])==14 , genParts)]
        genNuTau=               [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==24 and abs(p['pdgId'])==16 , genParts)]
        genNuEFromTau =         [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==15 and abs(p['pdgId'])==12 , genParts)]
        genNuMuFromTau=         [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==15 and abs(p['pdgId'])==14 , genParts)]
        genNuTauFromTau=        [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==15 and abs(p['pdgId'])==16 , genParts)]
#    genB   =                [descendDecay(q, genParts) for q in filter(lambda p: abs(p['motherId'])==6 and abs(p['pdgId'])==5 , genParts)]
        genB   =                filter(lambda p: abs(p['motherId'])==6 and abs(p['pdgId'])==5 , genParts)

#Matched
#    muMatchedToB     = filter(lambda l: abs(l['mcMatchAny'])==5 and l['mcMatchId']==0, mu)
#    eleMatchedToB    = filter(lambda l: abs(l['mcMatchAny'])==5 and l['mcMatchId']==0, ele)
#    muMatchedToTau   = filter(lambda l: l['mcMatchTau']>0, mu)
#    eleMatchedToTau  = filter(lambda l: l['mcMatchTau']>0, ele)
        muMatchedToB     = filter(lambda l: dRMatch(genB, dR=0.4)(l), mu)
        eleMatchedToB    = filter(lambda l: dRMatch(genB, dR=0.4)(l), ele)
        muMatchedToTau   = filter(lambda l: dRMatch(genMuFromTau, dR=0.4)(l), mu)
        eleMatchedToTau  = filter(lambda l: dRMatch(genEleFromTau, dR=0.4)(l), ele)

#    for gt in genTau:
#      print "Descending tau..."
#      res = descendDecay(gt, genParts)
#      if res:
#        print "Found lepton %i"%res['pdgId']
#      else:
#        print "Hadronic decay"
#      print "Check genNuE %i genNuMu %i genNuTau %i"%(len(genNuE), len(genNuMu), len(genNuTau))
#      print "  genTau decay:",[p['pdgId'] for p in genParts[gt['daughterIndex1']:gt['daughterIndex2']+1] ]
        for v in ['isMuMu','isEE','isEMu']:
            exec(v+'=getVarValue(chain, "'+v+'")')

        if isMuMu and not len(mu)==2 and len(ele)==0:
            print "Mode isMuMu but found mu/ele %i/%i"%(len(mu),len(ele))
            continue
        if isEE and not len(mu)==0 and len(ele)==2:
            print "Mode isEE but found mu/ele %i/%i"%(len(mu),len(ele))
            continue
        if isEMu and not len(mu)==1 and len(ele)==1:
            print "Mode isEMu but found mu/ele %i/%i"%(len(mu),len(ele))
            continue

        for mode in ["isMuMu", "isEE", "isEMu"]:
            if eval(mode+'==1'):
                counterReco[mode]+=1
                badMuonCandidates[mode].append(mu)
                badElectronCandidates[mode].append(ele)

                gMode="other"
#        print len(genEle),len(genMu),len(genTau),len(genLeptons)
                if    len(genMu)==2 and len(genLeptons)==2: gMode="2Mu"
                elif  len(genMu)==1 and len(genLeptons)==1: gMode="1Mu"
                elif  len(genEle)==2 and len(genLeptons)==2: gMode="2Ele"
                elif  len(genEle)==1 and len(genLeptons)==1: gMode="1Ele"
                elif  len(genMu)==1 and len(genEle)==1 and len(genLeptons)==2: gMode="Ele+Mu"
#        elif  len(genMu)==1 and len(genTau)==1 and len(genLeptons)==2: gMode="Mu+Tau"
#        elif  len(genEle)==1 and len(genTau)==1 and len(genLeptons)==2: gMode="Ele+Tau"
                elif  len(genMu)==1 and len(genTauToE)==1 and len(genLeptons)==2: gMode="Mu+TauToE"
                elif  len(genMu)==1 and len(genTauToMu)==1 and len(genLeptons)==2: gMode="Mu+TauToMu"
                elif  len(genMu)==1 and len(genTauToHad)==1 and len(genLeptons)==2: gMode="Mu+TauToHad"
                elif  len(genEle)==1 and len(genTauToE)==1 and len(genLeptons)==2: gMode="Ele+TauToE"
                elif  len(genEle)==1 and len(genTauToMu)==1 and len(genLeptons)==2: gMode="Ele+TauToMu"
                elif  len(genEle)==1 and len(genTauToHad)==1 and len(genLeptons)==2: gMode="Ele+TauToHad"

                elif  len(genTau)==2 and len(genLeptons)==2: gMode="2Tau"

                if gMode=='other':
                    print len(genLeptons), len(genNeutrinosFromW), len(genNuE), len(genNuMu), len(genNuTau)
                if not counterRecoGen[mode].has_key(gMode):
                    counterRecoGen[mode][gMode]=0
                    counterRecoGen_muMatched[mode][gMode]=0
                    counterRecoGen_eleMatched[mode][gMode]=0
                    counterRecoGen_allMatched[mode][gMode]=0
                    counterRecoGen_oneMuMatchedToB[mode][gMode]=0
                    counterRecoGen_oneEleMatchedToB[mode][gMode]=0
                    counterRecoGen_oneMuMatchedToTau[mode][gMode]=0
                    counterRecoGen_oneEleMatchedToTau[mode][gMode]=0
                    counterRecoGen_recoTau[mode][gMode]=0
                    counterRecoGen_recoMatchedTau[mode][gMode]=0
                    counterRecoGen_looseMu[mode][gMode]=0
                    counterRecoGen_looseEle[mode][gMode]=0
                    counterRecofake_fakeMet50[mode][gMode]=0
                    counterRecofake_fakeMet100[mode][gMode]=0
                    counterRecofake_fakeMet200[mode][gMode]=0
                    counterRecoGen_failRelIso03[mode][gMode]=0
                counterRecoGen[mode][gMode]+=1
                if len(mu)==len(muMatched):counterRecoGen_muMatched[mode][gMode]+=1
                if len(ele)==len(eleMatched):counterRecoGen_eleMatched[mode][gMode]+=1
                if len(mu)==len(muMatched) and len(ele)==len(eleMatched):counterRecoGen_allMatched[mode][gMode]+=1
                if len(muMatchedToB)>0:
                    counterRecoGen_oneMuMatchedToB[mode][gMode]+=1
#          print "Mu matched to b %i:%i:%i"%(getVarValue(chain, "run"), getVarValue(chain, "lumi"), getVarValue(chain, "evt"))
                if len(eleMatchedToB)>0:
                    counterRecoGen_oneEleMatchedToB[mode][gMode]+=1
#          print "Ele matched to b %i:%i:%i"%(getVarValue(chain, "run"), getVarValue(chain, "lumi"), getVarValue(chain, "evt"))
                if len(muMatchedToTau)>0:   counterRecoGen_oneMuMatchedToTau[mode][gMode]+=1
                if len(eleMatchedToTau)>0:   counterRecoGen_oneEleMatchedToTau[mode][gMode]+=1
                if len(tau)>0:   counterRecoGen_recoTau[mode][gMode]+=1
                if len(tauMatched)>0:   counterRecoGen_recoMatchedTau[mode][gMode]+=1
                if len(looseMu)>=3:  counterRecoGen_looseMu[mode][gMode]+=1
                if len(looseEle)>=3:   counterRecoGen_looseEle[mode][gMode]+=1
                leptonsFailRelIso03  = any([l['relIso03']>0.1 for l in leptons])
                leptonsFailRelIso03_012  = any([l['relIso03']>0.12 for l in leptons])
                leptonsFailRelIso04  = any([l['relIso04']>0.1 for l in leptons])
                leptonsFailRelIso04_012  = any([l['relIso04']>0.12 for l in leptons])
                if leptonsFailRelIso03: counterRecoGen_failRelIso03[mode][gMode]+=1
                if deltaMet>50:  counterRecofake_fakeMet50[mode][gMode]+=1
                neutrinoFromWPt = vecPtSum(genNeutrinosFromW)
                neutrinoFromWAndTauPt = vecPtSum(genNeutrinosFromW+genNeutrinosFromTau)
                neutrinoFromTauPt = vecPtSum(genNeutrinosFromTau)

                otherNeutrinoPt = vecPtSum(otherNeutrinos)
                if otherNeutrinoPt>40:
                    neutrinoMotherString = ",".join([pdgToName[p['motherId']] for p in otherNeutrinos if p['pt']>20])
                    if len(neutrinoMotherString)>0:neutrinoMotherString=bold(" high-pt nu")+" from "+neutrinoMotherString
                else:
                      neutrinoMotherString=""
                allNeutrinoPt = vecPtSum(otherNeutrinos+genNeutrinosFromW+genNeutrinosFromTau)
                jets = getJets(ttjets['chain'], jetVars+['mcPt'])
                dx, dy = 0., 0.
                for j in jets:
                    if j['mcPt']>0:
                        dx+=(j['pt']-j['mcPt'])*cos(j['phi'])
                        dy+=(j['pt']-j['mcPt'])*cos(j['phi'])
                jetMismeas = sqrt(dx**2+dy**2)
                if jetMismeas>40:
                    jetMismeasString=bold("jet-mism:")+" %6.2f"%jetMismeas
                else:
                    jetMismeasString=     "jet-mism:"+" %6.2f"%jetMismeas

                print "%6s %12s %20s mt2ll %6.2f d-MET %6.2f met %6.2f genmet %6.2f (W-nu %6.2f tau-nu %6.2f other-nu %6.2f all-nu %6.2f%s)"\
                    %(mode, gMode,  "%2i:%2i:%2i"%(getVarValue(chain, "run"), getVarValue(chain, "lumi"), getVarValue(chain, "evt")), mt2ll, deltaMet, met, genMet, neutrinoFromWPt, neutrinoFromTauPt, otherNeutrinoPt, allNeutrinoPt,neutrinoMotherString)\
                    +jetMismeasString

                lepDMet = vecPtSum(leptons, genLeptons)
                if lepDMet>40:
                    lepStr=bold("lep-mism")
                else:
                    lepStr="lep-mism"

                lepMatched     = filter(lambda l: dRMatch(status1MuEle, dR=0.15, checkPdgId=True)(l), leptons)
                for rl in leptons:
                    gl = filter(lambda l: dRMatch([rl], dR=0.15, checkPdgId=True)(l), status1MuEle )
                    if len(gl)==1:
                        rl['matchMotherPdgId']=gl[0]['motherId']
                mmatch = ",".join([pdgToName[l['matchMotherPdgId']] for l in leptons if l.has_key('matchMotherPdgId')])
                if mmatch!="":mmatch=" (matched to l from "+mmatch+")"
                leptonsFailRelIso03Str = ""
                if leptonsFailRelIso03: leptonsFailRelIso03Str=bold('>=1 lep fails relIso03<0.1!')
                if leptonsFailRelIso03_012: leptonsFailRelIso03Str=bold('>=1 lep fails relIso03<0.12!')
                leptonsFailRelIso04Str = ""
                if leptonsFailRelIso04: leptonsFailRelIso04Str=bold('>=1 lep fails relIso04<0.1!')
                if leptonsFailRelIso04_012: leptonsFailRelIso04Str=bold('>=1 lep fails relIso04<0.12!')
                print " "*41+"lep-m %i %s %6.2f %s. %s %s" %(len(lepMatched),lepStr, lepDMet, mmatch, leptonsFailRelIso03Str, leptonsFailRelIso04Str)
                print
                if deltaMet>100:  counterRecofake_fakeMet100[mode][gMode]+=1
                if deltaMet>200:  counterRecofake_fakeMet200[mode][gMode]+=1

#        print "mode %s genLeps %i genNus %i (%i %i %i) gen/recoLeps/matched Ele:%i/%i/%i Mu:%i/%i/%i Tau:%i"%(mode, len(genLeptons), len(genNeutrinos), len(genNuE), len(genNuMu), len(genNuTau), len(genEle), len(ele), len(eleMatched), len(genMu), len(mu),len(muMatched), len(genTau))
#        if len(eleMatchedToB+muMatchedToB)>0:print "  fromB (tot.: %i) Ele:%i Mu:%i"%(len(eleMatchedToB+muMatchedToB), len(eleMatchedToB), len(muMatchedToB))#, eleMatchedToB, muMatchedToB
#        if len(eleMatchedToTau+muMatchedToTau)>0:print "  fromTau (tot.: %i) Ele:%i Mu:%i"%(len(eleMatchedToTau+muMatchedToTau), len(eleMatchedToTau), len(muMatchedToTau))#,eleMatchedToTau,muMatchedToTau

    print
    for mode in ["isMuMu", "isEE", "isEMu"]:

        print "Reconstructed as %s (%i)"%(mode, counterReco[mode])
        sortedRes = sorted(counterRecoGen[mode].items(), key=operator.itemgetter(1))
        sortedRes.reverse()
        for gMode,n in sortedRes:
            print "  Generated as %s: %i " %(gMode, n)
            print "    all eleMatched: %i"       %counterRecoGen_eleMatched[mode][gMode]
            print "    all muMatched: %i"        %counterRecoGen_muMatched[mode][gMode]
            print "    all lep matched: %i"      %counterRecoGen_allMatched[mode][gMode]
            print "    >=1 match Ele/B: %i"      %counterRecoGen_oneEleMatchedToB[mode][gMode]
            print "    >=1 match Mu/B: %i"       %counterRecoGen_oneMuMatchedToB[mode][gMode]
            print "    >=1 match Ele/Tau: %i"    %counterRecoGen_oneEleMatchedToTau[mode][gMode]
            print "    >=1 match Mu/Tau: %i"     %counterRecoGen_oneMuMatchedToTau[mode][gMode]
            print "    >=1 reco had. tau: %i"     %counterRecoGen_recoTau[mode][gMode]
            print "    >=1 matched reco had. tau: %i"     %counterRecoGen_recoMatchedTau[mode][gMode]
            print "    >=1 extra mu: %i" % counterRecoGen_looseMu[mode][gMode]
            print "    >=1 extra ele: %i" % counterRecoGen_looseEle[mode][gMode]
            print "    >=1 lep. fails relIso03: %i"% counterRecoGen_failRelIso03[mode][gMode]
            print "    >50 fake MET %i"%counterRecofake_fakeMet50[mode][gMode]
            print "    >100 fake MET %i"%counterRecofake_fakeMet100[mode][gMode]
            print "    >200 fake MET %i"%counterRecofake_fakeMet200[mode][gMode]
        print
        print

#for mode in ["isMuMu", "isEE", "isEMu"]:
#  for p in [ 'miniRelIso', 'dxy','dz', 'ip3d', 'jetBTagCSV', 'jetDR', 'jetPtRatiov1', 'jetPtRatiov2', 'jetPtRelv1', 'relIso03', 'relIso04', 'sip3d']: #, 'jetPtRelv2'
#    if not mode=='isEE':
#      c1 = getObjFromFile('/afs/hephy.at/user/r/rschoefbeck/www/png25ns_2l_mAODv2_mcTrig_draw/njet2-nbtag1-met50/LepGood_'+p+'_mu.root','ROOT.c1')
#      h = c1.FindObject("LepGood_"+p+"_mu_DrawString_TTJets_Clone").Clone()
#      h.Reset()
#      for muons in badMuonCandidates[mode]:
#        if len(muons)>0:
#          val = max([abs(m[p]) for m in muons])
#          h.Fill(val)
#      c1.Draw()
#      h.SetLineColor(ROOT.kBlack)
#      h.SetLineStyle(1)
#      h.SetLineWidth(2)
#      h.SetFillStyle(0)
#      h.Draw('histsame')
#      c1.Print('/afs/hephy.at/user/r/rschoefbeck/www/png25ns_2l_mAODv2_mcTrig_draw/njet2-nbtag1-met50/'+prefix+'_LepGood_'+p+'_mu_'+mode+'_overlay.root')
#      c1.Print('/afs/hephy.at/user/r/rschoefbeck/www/png25ns_2l_mAODv2_mcTrig_draw/njet2-nbtag1-met50/'+prefix+'_LepGood_'+p+'_mu_'+mode+'_overlay.png')
#      c1.Print('/afs/hephy.at/user/r/rschoefbeck/www/png25ns_2l_mAODv2_mcTrig_draw/njet2-nbtag1-met50/'+prefix+'_LepGood_'+p+'_mu_'+mode+'_overlay.pdf')
#  for p in [ 'miniRelIso', 'dxy','dz', 'ip3d', 'jetBTagCSV', 'jetDR', 'jetPtRatiov1', 'jetPtRatiov2', 'jetPtRelv1', 'jetPtRelv2', 'relIso03', 'relIso04', 'sip3d', 'convVeto', 'mvaIdSpring15']: #, 'lostHits'
#    if not mode=='isMuMu':
#      c1 = getObjFromFile('/afs/hephy.at/user/r/rschoefbeck/www/png25ns_2l_mAODv2_mcTrig_draw/njet2-nbtag1-met50/LepGood_'+p+'_ele.root','ROOT.c1')
#      h = c1.FindObject("LepGood_"+p+"_ele_DrawString_TTJets_Clone").Clone()
#      h.Reset()
#      for electrons in badElectronCandidates[mode]:
#        if len(electrons)>0:
#          val = max([abs(m[p]) for m in electrons])
#          h.Fill(val)
#      c1.Draw()
#      h.SetLineColor(ROOT.kBlack)
#      h.SetLineStyle(1)
#      h.SetLineWidth(2)
#      h.SetFillStyle(0)
#      h.Draw('histsame')
#      c1.Print('/afs/hephy.at/user/r/rschoefbeck/www/png25ns_2l_mAODv2_mcTrig_draw/njet2-nbtag1-met50/'+prefix+'_LepGood_'+p+'_ele_'+mode+'_overlay.root')
#      c1.Print('/afs/hephy.at/user/r/rschoefbeck/www/png25ns_2l_mAODv2_mcTrig_draw/njet2-nbtag1-met50/'+prefix+'_LepGood_'+p+'_ele_'+mode+'_overlay.png')
#      c1.Print('/afs/hephy.at/user/r/rschoefbeck/www/png25ns_2l_mAODv2_mcTrig_draw/njet2-nbtag1-met50/'+prefix+'_LepGood_'+p+'_ele_'+mode+'_overlay.pdf')

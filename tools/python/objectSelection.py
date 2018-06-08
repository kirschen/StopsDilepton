from StopsDilepton.tools.helpers import mZ, getVarValue, getObjDict
from math import *
import numbers

jetVars = ['eta','pt','phi','btagDeepB', 'btagCSVV2', 'jetId', 'area']

def getJets(c, jetVars=jetVars, jetColl="Jet"):
    return [getObjDict(c, jetColl+'_', jetVars, i) for i in range(int(getVarValue(c, 'n'+jetColl)))]

def jetId(j, ptCut=30, absEtaCut=2.4, ptVar='pt'):
  return j[ptVar]>ptCut and abs(j['eta'])<absEtaCut and j['jetId']

def getGoodJets(c, ptCut=30, absEtaCut=2.4, jetVars=jetVars, jetColl="Jet"):
    return filter(lambda j:jetId(j, ptCut=ptCut, absEtaCut=absEtaCut), getJets(c, jetVars, jetColl=jetColl))

def isBJet(j, tagger = 'DeepCSV', year = 2016):
    if tagger == 'CSVv2':
        if year == 2016:
            # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation80XReReco
            return j['btagCSVV2'] > 0.8484 
        elif year == 2017:
            # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
            return j['btagCSVV2'] > 0.8838 
        else:
            raise (NotImplementedError, "Don't know what cut to use for year %s"%year)
    elif tagger == 'DeepCSV':
        if year == 2016:
            # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation80XReReco
            return j['btagDeepB'] > 0.6324
        elif year == 2017:
            # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
            return j['btagDeepB'] > 0.4941
        else:
            raise (NotImplementedError, "Don't know what cut to use for year %s"%year)

def getGenLeps(c):
    return [getObjDict(c, 'genLep_', ['eta','pt','phi','charge', 'pdgId', 'sourceId'], i) for i in range(int(getVarValue(c, 'ngenLep')))]

def getGenParts(c):
    return [getObjDict(c, 'GenPart_', ['eta','pt','phi','charge', 'pdgId', 'motherId', 'grandmotherId'], i) for i in range(int(getVarValue(c, 'nGenPart')))]

genVars = ['eta','pt','phi','mass','charge', 'status', 'pdgId', 'motherId', 'grandmotherId','nDaughters','daughterIndex1','daughterIndex2','nMothers','motherIndex1','motherIndex2','isPromptHard'] 
def getGenPartsAll(c):
    return [getObjDict(c, 'genPartAll_', genVars, i) for i in range(int(getVarValue(c, 'ngenPartAll')))]

def alwaysTrue(*args, **kwargs):
  return True
def alwaysFalse(*args, **kwargs):
  return False


## MUONS ##
def muonSelector( lepton_selection, year ):
    # tigher isolation applied on analysis level
    if lepton_selection == 'tight':
        def func(l):
            return \
                l["pt"]                 >= 10 \
                and abs(l["eta"])       < 2.4 \
                and l["mediumId"]   >= 1 \
                and l['pfRelIso03_all'] < 0.20 \
                and l["sip3d"]          < 4.0 \
                and abs(l["dxy"])       < 0.05 \
                and abs(l["dz"])        < 0.1

    elif lepton_selection == 'loose':
        def func(l):
            return \
                l["pt"]                 >= 10 \
                and abs(l["eta"])       < 2.4 \
                and l['pfRelIso03_all'] < 0.20 \
                and l["sip3d"]          < 4.0 \
                and abs(l["dxy"])       < 0.05 \
                and abs(l["dz"])        < 0.1


    return func


## ELECTRONS ##
def eleSelector( lepton_selection, year ):
    # tigher isolation applied on analysis level
    if lepton_selection == 'tight':
        def func(l):
            return \
                l["pt"]                 >= 10 \
                and abs(l["eta"])       < 2.4 \
                and l['cutBased']       >= 4 \
                and l['pfRelIso03_all'] < 0.20 \
                and l["convVeto"]       > 0 \
                and l["lostHits"]       == 0 \
                and l["sip3d"]          < 4.0 \
                and abs(l["dxy"])       < 0.05 \
                and abs(l["dz"])        < 0.1

    elif lepton_selection == 'loose':
        def func(l):
            return \
                l["pt"]                 >= 10 \
                and abs(l["eta"])       < 2.4 \
                and l['cutBased']       >= 1 \
                and l['pfRelIso03_all'] < 0.20 \
                and l["convVeto"]       > 0 \
                and l["lostHits"]       == 0 \
                and l["sip3d"]          < 4.0 \
                and abs(l["dxy"])       < 0.05 \
                and abs(l["dz"])        < 0.1

    return func


leptonVars_data = ['eta','etaSc', 'pt','phi','dxy', 'dz','tightId', 'pdgId', 'mediumMuonId', 'miniRelIso', 'relIso03', 'sip3d', 'mvaIdSpring15', 'convVeto', 'lostHits', 'jetPtRelv2', 'jetPtRatiov2', 'eleCutId_Spring2016_25ns_v1_ConvVetoDxyDz']
leptonVars = leptonVars_data + ['mcMatchId','mcMatchAny']

electronVars_data = ['pt','eta','phi','pdgId','cutBased','miniPFRelIso_all','pfRelIso03_all','sip3d','lostHits','convVeto','dxy','dz','charge','deltaEtaSC']
electronVars = electronVars_data + []

muonVars_data = ['pt','eta','phi','pdgId','mediumId','miniPFRelIso_all','pfRelIso03_all','sip3d','dxy','dz','charge']
muonVars = muonVars_data + []

def getLeptons(c, collVars=leptonVars):
    return [getObjDict(c, 'LepGood_', collVars, i) for i in range(int(getVarValue(c, 'nLepGood')))]

def getMuons(c, collVars=muonVars):
    return [getObjDict(c, 'Muon_', collVars, i) for i in range(int(getVarValue(c, 'nMuon')))]
def getElectrons(c, collVars=electronVars):
    return [getObjDict(c, 'Electron_', collVars, i) for i in range(int(getVarValue(c, 'nElectron')))]

def getGoodMuons(c, collVars=muonVars, mu_selector = alwaysFalse):
    return [l for l in getMuons(c, collVars) if mu_selector(l)]

def getGoodElectrons(c, collVars=electronVars, ele_selector = alwaysFalse):
    return [l for l in getElectrons(c, collVars) if ele_selector(l)]


tauVars=['eta','pt','phi','pdgId','charge', 'dxy', 'dz', 'idDecayModeNewDMs', 'idCI3hit', 'idAntiMu','idAntiE','mcMatchId']

def getTaus(c, collVars=tauVars):
    return [getObjDict(c, 'TauGood_', collVars, i) for i in range(int(getVarValue(c, 'nTauGood')))]

def looseTauID(l, ptCut=20, absEtaCut=2.4):
    return \
        l["pt"]>=ptCut\
        and abs(l["eta"])<absEtaCut\
        and l["idDecayModeNewDMs"]>=1\
        and l["idCI3hit"]>=1\
        and l["idAntiMu"]>=1\
        and l["idAntiE"]>=1\

def getGoodTaus(c, collVars=tauVars):
    return [l for l in getTaus(c,collVars=collVars) if looseTauID(l)]

idCutBased={'loose':1 ,'medium':2, 'tight':3}
photonVars=['eta','pt','phi','mass','cutBased']
photonVarsMC = photonVars + ['mcPt']
def getPhotons(c, collVars=photonVars, idLevel='loose'):
    return [getObjDict(c, 'Photon_', collVars, i) for i in range(int(getVarValue(c, 'nPhoton')))]
def getGoodPhotons(c, ptCut=50, idLevel="loose", isData=True, collVars=None):
    if collVars is None: collVars = photonVars if isData else photonVarsMC
    return [p for p in getPhotons(c, collVars) if p['cutBased'] >= idCutBased[idLevel] and p['pt'] > ptCut ]

def getFilterCut(isData=False, isFastSim = False, badMuonFilters = "Summer2016"):
    if isFastSim:
        filterCut            = "Flag_goodVertices"
    else:
        filterCut            = "Flag_goodVertices&&Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_globalTightHalo2016Filter&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter"
        if badMuonFilters == "Moriond2017":
            filterCut += "&&Flag_badChargedHadronSummer2016"
            if isData: filterCut += "&&Flag_badMuonMoriond2017&&Flag_badCloneMuonMoriond2017"
        elif badMuonFilters == "Moriond2017Official":
            filterCut += "&&Flag_badChargedHadronSummer2016"
            if isData: filterCut += "&&Flag_noBadMuons&&!Flag_duplicateMuons"
        elif badMuonFilters == "Summer2016":
            filterCut += "&&Flag_badChargedHadronSummer2016&&Flag_badMuonSummer2016"
        elif badMuonFilters == "Summer2016_pt20":
            filterCut += "&&Flag_badChargedHadronSummer2016&&Flag_badMuonSummer2016_pt20"
        elif badMuonFilters is None or badMuonFilters == "None":
            pass
        elif badMuonFilters == "Moriond2017OnlyClone":
            filterCut += "&&Flag_badChargedHadronSummer2016"
            if isData: filterCut += "&&Flag_badCloneMuonMoriond2017"
        elif badMuonFilters == "Moriond2017OnlyOther":
            filterCut += "&&Flag_badChargedHadronSummer2016"
            if isData: filterCut += "&&Flag_badMuonMoriond2017"
    if isData: filterCut += "&&weight>0"
    return filterCut

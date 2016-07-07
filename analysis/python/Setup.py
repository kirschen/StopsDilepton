#Standard import
import copy

# RootTools
from RootTools.core.standard import *

# Logging
import logging
logger = logging.getLogger(__name__)

#user specific
from StopsDilepton.tools.user import analysis_results

#define samples
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_Fall15_mAODv2_25ns_postProcessed import *

#Choices for specific samples
#DYSample          = DY
DYSample           = DY_HT_LO #LO, HT binned including a low HT bin starting from zero from the inclusive sample
#TTJetsSample      = TTJets #NLO
TTJetsSample       = TTJets_Lep #LO, very large dilep + single lep samples
WJetsSample        = WJetsToLNu #WJetsToLNu_HT
otherEWKComponents = [singleTop, diBoson, triBoson,  TTXNoZ, WJetsSample]
otherEWKBkgs       = Sample.combine("otherBkgs", otherEWKComponents, texName = "other bkgs.")

from StopsDilepton.analysis.SystematicEstimator import jmeVariations
from StopsDilepton.analysis.SetupHelpers import getZCut, channels, allChannels

#to run on data
#lumi = {'EMu': MuonEG_Run2015D.lumi, 'MuMu':DoubleMuon_Run2015D.lumi, 'EE':DoubleEG_Run2015D.lumi}
dataLumi = {'EMu': MuonEG_Run2015D.lumi, 'MuMu':DoubleMuon_Run2015D.lumi, 'EE':DoubleEG_Run2015D.lumi}
#10/fb to run on MC
lumi = {c:10000 for c in channels}

#Define defaults here
zMassRange            = 15
default_mllMin        = 20
default_metMin        = 80
default_metSigMin     = 5
default_dPhiJetMet    = 0.25 # To fix: this only applies to the 2nd jet, the first jet is fixes see below
default_nJets         = (2, -1)   # written as (min, max)
default_nBTags        = (1, -1)
default_leptonCharges = "isOS"
default_useTriggers   = True

filterCutData = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter&&vetoPassed&&jsonPassed&&weight>0)"
filterCutMC   = "(Flag_HBHENoiseIsoFilter&&Flag_HBHENoiseFilter&&Flag_CSCTightHaloFilter&&Flag_goodVertices&&Flag_eeBadScFilter&&Flag_EcalDeadCellTriggerPrimitiveFilter)"

class Setup:
    def __init__(self):
        self.analysis_results = analysis_results
        self.zMassRange       = zMassRange
        self.prefixes         = []
        self.externalCuts     = []

        #Default cuts and requirements. Those three things below are used to determine the key in the cache!
        self.parameters   = {
            'mllMin':        default_mllMin,
            'metMin':        default_metMin,
            'metSigMin':     default_metSigMin,
            'dPhiJetMet':    default_dPhiJetMet,
            'nJets':         default_nJets,
            'nBTags':        default_nBTags,
            'leptonCharges': default_leptonCharges,
            'useTriggers':   default_useTriggers
        }


#       self.sys      = {'weight':'weight', 'reweight':['reweightPU'], 'selectionModifier':None}
        self.sys      = {'weight':'weight', 'reweight':[],             'selectionModifier':None}
        self.lumi     = lumi
        self.dataLumi = dataLumi

        self.sample = {
        'DY':         {c:DYSample     for c in channels},
        'TTJets' :    {c:TTJetsSample for c in channels},
        'TTZ' :       {c:TTZ          for c in channels},
        'other'  :    {'MuMu': Sample.combine('other', [otherEWKBkgs, QCD_Mu5]),
                       'EE':   Sample.combine('other', [otherEWKBkgs,QCD_EMbcToE]),
                       'EMu':  Sample.combine('other', [otherEWKBkgs, QCD_Mu5EMbcToE])},
        'Data'   :    {'MuMu': DoubleMuon_Run2015D,
                       'EE':   DoubleEG_Run2015D,
                       'EMu':  MuonEG_Run2015D},
        }

    def prefix(self):
        return '_'.join(self.prefixes+[self.preselection('MC', zWindow='allZ')['prefix']])

    def defaultCacheDir(self):
        return os.path.join(self.analysis_results, self.prefix(), 'cacheFiles')

    #Clone the setup and optinally modify the systematic variation
    def sysClone(self, sys=None, parameters=None):
        '''Clone setup and change systematic if provided'''

        res            = copy.copy(self)
        res.sys        = copy.deepcopy(self.sys)
        res.parameters = copy.deepcopy(self.parameters)

        if sys:
            for k in sys.keys():
                if k=='reweight':
                    res.sys[k] = list(set(res.sys[k]+sys[k])) #Add with unique elements
                else:
                    res.sys[k] = sys[k] # if sys[k] else res.sys[k]

        if parameters:
            for k in parameters.keys():
                res.parameters[k] = parameters[k]

        return res

    def defaultParameters(self, update={}):
        assert type(update)==type({}), "Update arguments with key arg dictionary. Got this: %r"%update
        res = copy.deepcopy(self.parameters)
        res.update(update)
        return res

    def weightString(self):
        return "*".join([self.sys['weight']] + (self.sys['reweight'] if self.sys['reweight'] else []))

    def preselection(self, dataMC , zWindow, channel='all'):
        '''Get preselection  cutstring.'''
        return self.selection(dataMC, channel = channel, zWindow = zWindow, hadronicSelection = False, **self.parameters)

    def selection(self, dataMC,
			mllMin, metMin, metSigMin, dPhiJetMet,
			nJets, nBTags, leptonCharges, useTriggers,
			channel = 'all', zWindow = 'offZ', hadronicSelection = False):
        '''Define full selection
	   dataMC: 'Data' or 'MC'
	   channel: all, EE, MuMu or EMu
	   zWindow: offZ, onZ, or allZ
	   hadronicSelection: whether to return only the hadronic selection
	'''
        #Consistency checks
        assert dataMC in ['Data','MC'],                                                          "dataMC = Data or MC, got %r."%dataMC
        if self.sys['selectionModifier']: assert self.sys['selectionModifier'] in jmeVariations, "Don't know about systematic variation %r, take one of %s"%(self.sys['selectionModifier'], ",".join(jmeVariations))
        assert not leptonCharges or leptonCharges in ["isOS", "isSS"],                           "Don't understand leptonCharges %r. Should take isOS or isSS."%leptonCharges

        #Postfix for variables (only for MC)
        sysStr="" if (not self.sys['selectionModifier'] or dataMC=='Data') else "_"+self.sys['selectionModifier']

        res={'cuts':[], 'prefixes':[]}

        if leptonCharges and not hadronicSelection:
	    res['cuts'].append(leptonCharges)
	    res['prefixes'].append(leptonCharges)

        if nJets and not (nJets[0]==0 and nJets[1]<0):
            assert nJets[0]>=0 and (nJets[1]>=nJets[0] or nJets[1]<0), "Not a good nJets selection: %r"%nJets
            njetsstr = "nJetGood"+sysStr+">="+str(nJets[0])
            prefix   = "nJets"+str(nJets[0])
            if nJets[1]>=0:
                njetsstr+= "&&"+"nJetGood"+sysStr+"<="+str(nJets[1])
                if nJets[1]!=nJets[0]: prefix+=str(nJets[1])
            else:
                prefix+='p'
            res['cuts'].append(njetsstr)
            res['prefixes'].append(prefix)

        if nBTags and not (nBTags[0]==0 and nBTags[1]<0):
            assert nBTags[0]>=0 and (nBTags[1]>=nBTags[0] or nBTags[1]<0), "Not a good nBTags selection: %r"% nBTags
            nbtstr = "nBTag"+sysStr+">="+str(nBTags[0])
            prefix = "nbtag"+str(nBTags[0])
            if nBTags[1]>=0:
                nbtstr+= "&&nBTag"+sysStr+"<="+str(nBTags[1])
                if nBTags[1]!=nBTags[0]: prefix+=str(nBTags[1])
            else:
                prefix+='p'
            res['cuts'].append(nbtstr)
            res['prefixes'].append(prefix)

        if metMin and metMin>0:
          res['cuts'].append('met_pt'+sysStr+'>='+str(metMin))
          res['prefixes'].append('met'+str(metMin))
        if metSigMin and metSigMin>0:
          res['cuts'].append('metSig'+sysStr+'>='+str(metSigMin))
          res['prefixes'].append('metSig'+str(metSigMin))
        if dPhiJetMet>=0.:
          res['cuts'].append('cos(met_phi'+sysStr+'-JetGood_phi[0])<0.8&&cos(met_phi'+sysStr+'-JetGood_phi[1])<cos('+str(dPhiJetMet)+')')
          res['prefixes'].append('dPhiJet0-dPhiJet')

        if not hadronicSelection:
            if mllMin and mllMin>0:
              res['cuts'].append('dl_mass>='+str(mllMin))
              res['prefixes'].append('mll'+str(mllMin))

            triggerMuMu   = "HLT_mumuIso"
            triggerEleEle = "HLT_ee_DZ"
            triggerMuEle  = "HLT_mue"
            preselMuMu = "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0"
            preselEE   = "isEE==1&&nGoodMuons==0&&nGoodElectrons==2"
            preselEMu  = "isEMu==1&&nGoodMuons==1&&nGoodElectrons==1"

            #Z window
            assert zWindow in ['offZ', 'onZ', 'allZ'], "zWindow must be one of onZ, offZ, allZ. Got %r"%zWindow
            if zWindow in ['onZ', 'offZ']:
                  res['cuts'].append(getZCut(zWindow, self.zMassRange))

            #lepton channel
            assert channel in allChannels, "channel must be one of "+",".join(allChannels)+". Got %r."%channel
            if useTriggers:
                pMuMu = preselMuMu + "&&" + triggerMuMu
                pEE   = preselEE   + "&&" + triggerEleEle
                pEMu  = preselEMu  + "&&" + triggerMuEle
            else:
                pMuMu = preselMuMu
                pEE   = preselEE
                pEMu  = preselEMu

            if channel=="MuMu":  chStr = pMuMu
            elif channel=="EE":  chStr = pEE
            elif channel=="EMu": chStr = pEMu
            elif channel=="all": chStr = "("+pMuMu+'||'+pEE+'||'+pEMu+')'
            res['cuts'].append(chStr)

        if dataMC=='Data': filterCut = filterCutData
        else:              filterCut = filterCutMC
        res['cuts'].append("l1_pt>25")
        res['cuts'].append(filterCut)
        res['cuts'].extend(self.externalCuts)

        return {'cut':"&&".join(res['cuts']), 'prefix':'-'.join(res['prefixes']), 'weightStr': self.weightString()}


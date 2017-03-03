#Standard import
import copy

# RootTools
from RootTools.core.standard import *

# Logging
import logging
logger = logging.getLogger(__name__)

#user specific
from StopsDilepton.tools.user import analysis_results
from StopsDilepton.tools.helpers import getObjFromFile

#define samples
postProcessing_directory = 'postProcessed_80X_v31/dilepTiny'
from StopsDilepton.samples.cmgTuples_Data25ns_80X_03Feb_postProcessed import *
postProcessing_directory = 'postProcessed_80X_v35/dilepTiny'
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *

#Choices for specific samples
#DYSample          = DY
DYSample           = DY_HT_LO #LO, HT binned including a low HT bin starting from zero from the inclusive sample
#TTJetsSample      = TTJets #NLO
#TTJetsSample       = Sample.combine("TTJets", [TTJets_Lep, singleTop], texName = "t#bar{t}/single-t") #LO, very large dilep + single lep samples
TTJetsSample       = Top_pow
otherEWKComponents = [TTXNoZ, WJetsToLNu]
otherEWKBkgs       = Sample.combine("otherBkgs", otherEWKComponents, texName = "other bkgs.")

from StopsDilepton.analysis.SystematicEstimator import jmeVariations, metVariations
from StopsDilepton.analysis.SetupHelpers import getZCut, channels, allChannels, trilepChannels, allTrilepChannels
from StopsDilepton.analysis.fastSimGenMetReplacements import fastSimGenMetReplacements
from StopsDilepton.tools.objectSelection import getFilterCut

#to run on data
dataLumi = {'EMu': MuonEG_Run2016_backup.lumi, 'MuMu':DoubleMuon_Run2016_backup.lumi, 'EE':DoubleEG_Run2016_backup.lumi, '3mu':DoubleMuon_Run2016_backup.lumi, '3e':DoubleEG_Run2016_backup.lumi, '2mu1e':MuonEG_Run2016_backup.lumi, '2e1mu':MuonEG_Run2016_backup.lumi}
#10/fb to run on MC
#lumi = {c:10000 for c in channels}
lumi = dataLumi

#Define defaults here
zMassRange            = 15
default_mllMin        = 20
default_metMin        = 80
default_metSigMin     = 5
default_zWindow       = "offZ"
default_dPhi          = True
default_triLep        = False
default_dPhiInv       = False
default_nJets         = (2, -1)   # written as (min, max)
default_nBTags        = (1, -1)
default_leptonCharges = "isOS"


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
            'zWindow':       default_zWindow,
            'dPhi':          default_dPhi,
            'dPhiInv':       default_dPhiInv,
            'nJets':         default_nJets,
            'nBTags':        default_nBTags,
            'leptonCharges': default_leptonCharges,
            'triLep':        default_triLep,
        }

        self.sys = {'weight':'weight', 'reweight':['reweightPU36fb','reweightDilepTriggerBackup','reweightLeptonSF','reweightTopPt','reweightBTag_SF','reweightLeptonTrackingSF'], 'selectionModifier':None}
        self.lumi     = lumi
        self.dataLumi = dataLumi

        self.sample = {
        'DY':         {c:DYSample     for c in channels+trilepChannels},
        'TTJets' :    {c:TTJetsSample for c in channels+trilepChannels},
        'TTZ' :       {c:TTZ          for c in channels+trilepChannels},
        'multiBoson' :{c:multiBoson   for c in channels+trilepChannels},
        'TTXNoZ' :    {c:TTXNoZ       for c in channels+trilepChannels},
        'other'  :    {c:Sample.combine('other', [otherEWKBkgs]) for c in channels+trilepChannels},
        'Data'   :    {'MuMu':  DoubleMuon_Run2016_backup,
                       'EE':    DoubleEG_Run2016_backup,
                       'EMu':   MuonEG_Run2016_backup,
                       '3mu':   DoubleMuon_Run2016_backup,
                       '3e':    DoubleEG_Run2016_backup,
                       '2mu1e': MuonEG_Run2016_backup,
                       '2e1mu': MuonEG_Run2016_backup},
        }
        
        dataPUHistForSignalPath = "$CMSSW_BASE/src/StopsDilepton/tools/data/puFastSimUncertainty/dataPU.root"
        self.dataPUHistForSignalFile = getObjFromFile(os.path.expandvars(dataPUHistForSignalPath), "data")

    def prefix(self):
        return '_'.join(self.prefixes+[self.preselection('MC')['prefix']])

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
                if k=='remove':
                    for i in sys[k]:
                      res.sys['reweight'].remove(i)
                elif k=='reweight':
                    res.sys[k] = list(set(res.sys[k]+sys[k])) #Add with unique elements
                    for upOrDown in ['Up','Down']:
                      if 'reweightPU36fb'+upOrDown             in res.sys[k]: res.sys[k].remove('reweightPU36fb')
                      if 'reweightDilepTriggerBackup'+upOrDown in res.sys[k]: res.sys[k].remove('reweightDilepTriggerBackup')
                      if 'reweightBTag_SF_b_'+upOrDown         in res.sys[k]: res.sys[k].remove('reweightBTag_SF')
                      if 'reweightBTag_SF_l_'+upOrDown         in res.sys[k]: res.sys[k].remove('reweightBTag_SF')
                      if 'reweightLeptonSF'+upOrDown           in res.sys[k]: res.sys[k].remove('reweightLeptonSF')
                      if 'reweightLeptonFastSimSF'+upOrDown    in res.sys[k]: res.sys[k].remove('reweightLeptonFastSimSF')
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

    def preselection(self, dataMC , channel='all', isFastSim = False):
        '''Get preselection  cutstring.'''
        return self.selection(dataMC, channel = channel, isFastSim = isFastSim, hadronicSelection = False, **self.parameters)

    def selection(self, dataMC,
                        mllMin, metMin, metSigMin, zWindow, dPhi, dPhiInv,
                        nJets, nBTags, leptonCharges, triLep,
                        channel = 'all', hadronicSelection = False,  isFastSim = False):
        '''Define full selection
           dataMC: 'Data' or 'MC'
           channel: all, EE, MuMu or EMu
           zWindow: offZ, onZ, or allZ
           hadronicSelection: whether to return only the hadronic selection
       isFastSim: adjust filter cut etc. for fastsim
        '''
        #Consistency checks
        if self.sys['selectionModifier']:
          assert self.sys['selectionModifier'] in jmeVariations+metVariations+['genMet'] or 'nVert' in self.sys['selectionModifier'], "Don't know about systematic variation %r, take one of %s"%(self.sys['selectionModifier'], ",".join(jmeVariations + ['genMet']))
        assert dataMC in ['Data','MC'],                                                   "dataMC = Data or MC, got %r."%dataMC
        assert not leptonCharges or leptonCharges in ["isOS", "isSS"],                    "Don't understand leptonCharges %r. Should take isOS or isSS."%leptonCharges

        #Postfix for variables (only for MC and if we have a jme variation)
        sysStr = ""
        metStr = ""
        if dataMC == "MC" and self.sys['selectionModifier'] in jmeVariations: sysStr = "_" + self.sys['selectionModifier']
        if dataMC == "MC" and self.sys['selectionModifier'] in metVariations: metStr = "_" + self.sys['selectionModifier']

        res={'cuts':[], 'prefixes':[]}

        if leptonCharges and not hadronicSelection and not triLep:
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
          res['cuts'].append('met_pt'+sysStr+metStr+'>='+str(metMin))
          res['prefixes'].append('met'+str(metMin))
        if metSigMin and metSigMin>0:
          res['cuts'].append('metSig'+sysStr+metStr+'>='+str(metSigMin))
          res['prefixes'].append('metSig'+str(metSigMin))
        if dPhi:
          res['cuts'].append('cos(met_phi'+sysStr+metStr+'-JetGood_phi[0])<0.8&&cos(met_phi'+sysStr+metStr+'-JetGood_phi[1])<cos(0.25)')
          res['prefixes'].append('dPhiJet0-dPhiJet')
        elif dPhiInv:
          res['cuts'].append('!(cos(met_phi'+sysStr+metStr+'-JetGood_phi[0])<0.8&&cos(met_phi'+sysStr+metStr+'-JetGood_phi[1])<cos(0.25))')
          res['prefixes'].append('dPhiInv')

        if not hadronicSelection:
            if mllMin and mllMin>0:
              res['cuts'].append('dl_mass>='+str(mllMin))
              res['prefixes'].append('mll'+str(mllMin))

            if triLep:
              assert channel in allTrilepChannels, "channel must be one of "+",".join(allTrilepChannels)+". Got %r."%channel
              from StopsDilepton.tools.trilepSelection import getTrilepSelection
              if channel =="all": chStr = '(' + '||'.join([getTrilepSelection(c) for c in ['3mu','2mu1e','2e1mu','3e']]) + ')'
              else:               chStr = getTrilepSelection(channel)
              res['cuts'].append(chStr)

              assert zWindow == 'onZ', "zWindow must be onZ for trilep selection"
              res['cuts'].append('abs(mlmZ_mass-91.1876)<10')

            else:

              preselMuMu = "isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0"
              preselEE   = "isEE==1&&nGoodMuons==0&&nGoodElectrons==2"
              preselEMu  = "isEMu==1&&nGoodMuons==1&&nGoodElectrons==1"

              #Z window
              assert zWindow in ['offZ', 'onZ', 'allZ'], "zWindow must be one of onZ, offZ, allZ. Got %r"%zWindow
              if zWindow == 'onZ':                     res['cuts'].append(getZCut(zWindow, self.zMassRange))
              if zWindow == 'offZ' and channel!="EMu": res['cuts'].append(getZCut(zWindow, self.zMassRange))  # Never use offZ when in emu channel, use allZ instead

              #lepton channel
              assert channel in allChannels, "channel must be one of "+",".join(allChannels)+". Got %r."%channel

              if channel=="MuMu":  chStr = preselMuMu
              elif channel=="EE":  chStr = preselEE
              elif channel=="EMu": chStr = preselEMu
              elif channel=="all": chStr = "("+preselMuMu+'||'+preselEE+'||'+preselEMu+')'
              elif channel=="SF":  chStr = "("+preselMuMu+'||'+preselEE+')'

              res['cuts'].append(chStr)

              res['prefixes'].append('looseLeptonVeto')
              res['cuts'].append('Sum$(LepGood_pt>15&&LepGood_relIso03<0.4)==2')

              res['prefixes'].append('relIso0.12')
              res['cuts'].append("l1_relIso03<0.12&&l2_relIso03<0.12")

              res['cuts'].append("l1_pt>25")

        res['cuts'].append(getFilterCut(isData=(dataMC=='Data'), badMuonFilters='Moriond2017Official', isFastSim=isFastSim))
        #res['cuts'].append(getFilterCut(isData=(dataMC=='Data'), isFastSim=isFastSim))
        res['cuts'].extend(self.externalCuts)
        
        if self.sys['selectionModifier']:
            if "nVert" in self.sys['selectionModifier']:
                res['cuts'].append(self.sys['selectionModifier'])
        
        if self.sys['selectionModifier'] == 'genMet':
            res['cuts'] = [ fastSimGenMetReplacements(r) for r in res['cuts'] ]
        return {'cut':"&&".join(res['cuts']), 'prefix':'-'.join(res['prefixes']), 'weightStr': self.weightString()}

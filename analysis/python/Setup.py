from StopsDilepton.tools.localInfo import analysisOutputDir
import copy

#Numerical constants
zMassRange=15

#define samples
from StopsDilepton.samples.helpers import combineSamples
from StopsDilepton.samples.cmgTuples_Data25ns_mAODv2_postProcessed import *
from StopsDilepton.samples.cmgTuples_Spring15_mAODv2_25ns_1l_postProcessed import *

#choices for specific samples
#DYSample      = DY #NLO M10t050 + M50
DYSample      = DY_HT_LO #LO, HT binned including a low HT bin starting from zero from the inclusive sample
#TTJetsSample  = TTJets #NLO
TTJetsSample  = TTJets_Lep #LO, very large dilep + single lep samples
otherEWKBkgs   = combineSamples([singleTop, diBoson, triBoson, TTXNoZ, WJetsToLNu_HT])
otherEWKBkgs['name'] = 'otherBkgs'
otherEWKBkgs['texName'] = 'other bkgs.'

from StopsDilepton.analysis.systematics import jmeVariations
from StopsDilepton.analysis.SetupHelpers import getZCut, loadChain, allChannels

#to run on data
#lumi = {'EMu':MuonEG_Run2015D['lumi'], 'MuMu':DoubleMuon_Run2015D['lumi'], 'EE':DoubleEG_Run2015D['lumi']}
#10/fb to run on MC
lumi = {c:10000 for c in allChannels}

#Define defaults here
default_mllMin = 20
default_metMin = 80
default_metSigMin = 5
default_dPhiJetMet = 0.25
default_nJets = (2, -1)
default_nBTags = (1, -1)
default_leptonCharges = "isOS"
default_useTriggers = True

class Setup:
  def __init__(self):
    self.verbose=False
    self.analysisOutputDir = analysisOutputDir
    self.zMassRange   = zMassRange
    self.prefixes = [] 
    self.externalCuts = [] 

    #Default cuts and requirements. Those three things below are used to determine the key in the cache!
    self.parameters      = {'mllMin':default_mllMin, 'metMin':default_metMin, 'metSigMin':default_metSigMin, 'dPhiJetMet':default_dPhiJetMet, 'nJets': default_nJets, 'nBTags': default_nBTags, 'leptonCharges': default_leptonCharges, 'useTriggers':True}
    self.sys          = {'weight':'weightPU', 'reweight':[], 'selectionModifier':None, 'useBTagWeights':None}
    self.lumi=lumi

    self.sample = {
    'DY':         {c:DYSample for c in allChannels},
    'TTJets' :    {c:TTJetsSample for c in allChannels},
    'TTZ' :       {c:TTZ for c in allChannels},
    'other'  :    {'MuMu':combineSamples([otherEWKBkgs, QCD_Mu5]), 'EE': combineSamples([otherEWKBkgs,QCD_EMbcToE]), 'EMu':combineSamples([otherEWKBkgs, QCD_Mu5EMbcToE]), 
                   'all': combineSamples([otherEWKBkgs, QCD_Mu5EMbcToE])},
    'Data'   :    {'MuMu':DoubleMuon_Run2015D, 'EE': DoubleEG_Run2015D, 'EMu':MuonEG_Run2015D},
    }

  def loadChains(self):
    for s in sum([s.values() for s in self.sample.values()],[]):
      loadChain(s)# if not type(s)==type([]) else [loadChain(t) for t in s]

  def prefix(self):
    return '_'.join(self.prefixes+[self.preselection('MC')['prefix']])

  def defaultCacheDir(self):
    return os.path.join(self.analysisOutputDir, self.prefix(), 'cacheFiles')

  #Clone the setup and optinally modify the systematic variation
  def sysClone(self, sys=None):
    '''Clone setup and change systematic if provided'''
    res     = copy.copy(self)
    res.sys = copy.deepcopy(self.sys)
    if sys:
      for k in sys.keys():
        if k=='reweight':
          res.sys[k]=list(set(res.sys[k]+sys[k])) #Add with unique elements 
#          res.sys[k] = res.sys[k]+sys[k] 
          if len(res.sys[k])!=len(list(set(res.sys[k]))): print "Warning! non-exclusive list of reweights: %s"% ",".join(res.sys['k'])
        else:
          res.sys[k]=sys[k]# if sys[k] else res.sys[k]
    return res

  def defaultParameters(self, update={}):
    assert type(update)==type({}), "Update arguments with key arg dictionary. Got this: %r"%update
    res = copy.deepcopy(self.parameters)
    res.update(update)
    return res
      

  def preselection(self, dataMC , channel='all', zWindow = 'offZ'):
    '''Get preselection  cutstring.'''
    return self.selection(dataMC, channel = channel, zWindow = zWindow, hadronicSelection = False, **self.parameters)

  def selection(self, dataMC,  
                mllMin, metMin, metSigMin, dPhiJetMet, 
                nJets, nBTags, leptonCharges, useTriggers, 
                channel = 'all', zWindow = 'offZ', hadronicSelection = False):
    '''Define full selection
dataMC: 'Data' or 'MC'
channel: EE, MuMu or EMu
zWindow: offZ, onZ, or allZ
hadronicSelection: whether to return only the hadronic selection
 '''
    #Consistency checks
    assert dataMC in ['Data','MC'], "dataMC = Data or MC, got %r."%dataMC
    assert not (dataMC=='Data' and self.sys['selectionModifier']), "Why would you need data preselection with selectionModifier=%r? Should be None."%self.sys['selectionModifier']
    if self.sys['selectionModifier']: assert self.sys['selectionModifier'] in jmeVariations, "Don't know about systematic variation %r, take one of %s"%(self.sys['selectionModifier'], ",".join(jmeVariations))
    assert not leptonCharges or leptonCharges in ["isOS", "isSS"], "Don't understand leptonCharges %r. Should take isOS or isSS."%leptonCharges

    #postfix for variables     
    sysStr="" if not self.sys['selectionModifier'] else "_"+self.sys['selectionModifier']

    res={'cuts':[], 'prefixes':[], 'reweight':self.sys['reweight'] if self.sys['reweight'] else [] }

    if leptonCharges and not hadronicSelection:
     res['cuts'].append(leptonCharges)
     res['prefixes'].append(leptonCharges)

    if nJets and not ( nJets[0]==0 and nJets[1]<0):
      assert nJets[0]>=0 and (nJets[1]>=nJets[0] or nJets[1]<0), "Not a good nJets selection: %r"%nJets
      njetsstr = "nGoodJets"+sysStr+">="+str(nJets[0])
      lstr = "nJets"+str(nJets[0])
      if nJets[1]>=0: 
        njetsstr+= "&&"+"nGoodJets"+sysStr+"<="+str(nJets[1])
        if nJets[1]!=nJets[0]: lstr+=str(nJets[1])
      else:
        lstr+='p'
      res['cuts'].append(njetsstr)
      res['prefixes'].append(lstr)

    if nBTags and not ( nBTags[0]==0 and nBTags[1]<0):
      assert not (self.sys['selectionModifier'] and self.sys['useBTagWeights']), "Can't use both, selectionModifier and useBTagWeights!"
      #btag prefix string
      bPrefix = "nbtag"+str(nBTags[0])
      if nBTags[1]>=0: 
        if nBTags[1]!=nBTags[0]: bPrefix+=str(nBTags[1]) 
      if nBTags[1]<0: bPrefix+='p'
      res['prefixes'].append(bPrefix)
      #if we're using cuts... 
      if not self.sys['useBTagWeights']: 
        assert nBTags[0]>=0 and (nBTags[1]>=nBTags[0] or nBTags[1]<0), "Not a good nBTags selection: %r, useBTagWeights %s"%(nBTags, self.sys['useBTagWeights'])
        nbtstr = "nBTags"+sysStr+">="+str(nBTags[0])
        if nBTags[1]>=0: 
          nbtstr+= "&&nBTags"+sysStr+"<="+str(nBTags[1])
        res['cuts'].append(nbtstr)
      else: #if we're using weights (-> no cuts)
        assert self.sys['useBTagWeights'] in ['MC', 'SF', 'SF_b_Up', 'SF_b_Down', 'SF_l_Up', 'SF_l_Down', 'SF_FS_Up', 'SF_FS_Down'], 'Unknown b-tag weight: %r'%self.sys['useBTagWeights']
        assert nBTags[0]>=0 and (nBTags[1]==nBTags[0] or nBTags[1]<0),    "Not a good nBTags selection: %r, useBTagWeights %s"%(nBTags, self.sys['useBTagWeights'])
        rwstr = "reweightBTag"+str(nBTags[0])
        if nBTags[1]<0: rwstr+='p'
        rwstr += '_'+self.sys['useBTagWeights'] #append b-tag weight
        res['reweight'].append(rwstr)

    if metMin and metMin>0:
     res['cuts'].append('met_pt'+sysStr+'>='+str(metMin))
     res['prefixes'].append('met'+str(metMin))
    if metSigMin and metSigMin>0:
     res['cuts'].append('met_pt'+sysStr+'/sqrt(ht)'+sysStr+'>='+str(metSigMin))
     res['prefixes'].append('metSig'+str(metSigMin))
    if dPhiJetMet>=0.:
     res['cuts'].append('cos(met_phi'+sysStr+'-Jet_phi[0])<cos('+str(dPhiJetMet)+')&&cos(met_phi'+sysStr+'-Jet_phi[1])<cos('+str(dPhiJetMet)+')')
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
#      res['prefixes'] = zWindow + res['prefixes']
      if zWindow in ['onZ', 'offZ']:
         res['cuts'].append(getZCut(zWindow, self.zMassRange))

      #lepton channel
      assert channel in allChannels, "channel must be one of "+",".join(allChannels)+". Got %r."%channel
#      res['prefixes'] = channel + res['prefixes']
      if useTriggers:
        pMuMu = preselMuMu + "&&" + triggerMuMu
        pEE   = preselEE  + "&&" + triggerEleEle 
        pEMu  = preselEMu + "&&" + triggerMuEle
      else:
        pMuMu = preselMuMu 
        pEE   = preselEE  
        pEMu  = preselEMu 
      if channel=="MuMu":
        chStr=pMuMu
      if channel=="EE":
        chStr=pEE
      if channel=="EMu":
        chStr=pEMu
      if channel=="all":
        chStr = "("+pMuMu+'||'+pEE+'||'+pEMu+')'
      res['cuts'].append(chStr) 
    if dataMC=='Data':
      filterCut = "(Flag_HBHENoiseFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter&&weight>0)"
      res['cuts'].append(filterCut)

    res['cuts'].extend(self.externalCuts)

    return {'cut':"&&".join(res['cuts']), 'prefix':'-'.join(res['prefixes']), 'weightStr':"*".join([self.sys['weight']]+res['reweight'])} 


from StopsDilepton.tools.helpers import getYieldFromChain
from math import sqrt
from StopsDilepton.analysis.systematics import SystematicBaseClass
from StopsDilepton.analysis.u_float import u_float
from StopsDilepton.tools.helpers import printHeader
from StopsDilepton.tools.objectSelection import looseMuIDString,looseEleIDString


class DataDrivenTTZEstimate(SystematicBaseClass):
  def __init__(self, name, cacheDir=None):
    super(DataDrivenTTZEstimate, self).__init__(name, cacheDir=cacheDir)
    self.nJets = (4,-1) #jet selection
    self.nLooseBTags = (2,-1) #loose bjet selection
    self.nMediumBTags = (1,-1) #bjet selection
#Concrete implementation of abstract method 'estimate' as defined in Systematic
  def _estimate(self, region, channel, setup):
    printHeader("DD TTZ prediction for '%s' channel %s" %(self.name, channel))

    #Sum of all channels for 'all'
    if channel=='all':
      return sum( [ self.cachedEstimate(region, c, channel, setup) for c in ['MuMu', 'EE', 'EMu'] ] )
    else:
      #Data driven for EE, EMu and  MuMu. 
      preSelection = setup.preselection('MC', channel=channel)

      #check lumi consistency
      assert abs(1.-setup.lumi[channel]/setup.sample['Data'][channel]['lumi'])<0.01, "Lumi specified in setup %f does not match lumi in data sample %f in channel %s"%(setup.lumi[channel], setup.sample['Data'][channel]['lumi'], channel)
      selection_MC_2l = "&&".join([region.cutString(setup.sys['selectionModifier']), preSelection['cut']])
      weight = preSelection['weightStr']
      
      print "weight: ", weight

      yield_MC_2l =  setup.lumi[channel]/1000.*u_float(getYieldFromChain(setup.sample['TTZ'][channel]['chain'], cutString = selection_MC_2l, weight=weight, returnError = True) )
      if setup.verbose: print "yield_MC_2l: %s"%yield_MC_2l 
      
      muonSelection_loosePt = looseMuIDString(ptCut=10)
      electronSelection_loosePt = looseEleIDString(ptCut=10)
      
      #mu_mu_mu
      MuMuMuSelection = "nGoodMuons>=2" + '&&' + muonSelection_loosePt + "==3"
      if setup.parameters['useTriggers']: MuMuMuSelection += '&&HLT_3mu'
      #e_e_e
      EEESelection = "nGoodElectrons>=2" + '&&' + electronSelection_loosePt + "==3"
      if setup.parameters['useTriggers']: EEESelection += '&&HLT_3e'
      #e_e_mu
      EEMuSelection = "(nGoodMuons+nGoodElectrons)>=2" + "&&" + electronSelection_loosePt + "==2&&" + muonSelection_loosePt + "==1" 
      if setup.parameters['useTriggers']: EEMuSelection += '&&HLT_2e1mu'
      #mu_mu_e
      MuMuESelection = "(nGoodMuons+nGoodElectrons)>=2" + "&&" + electronSelection_loosePt + "==1&&" + muonSelection_loosePt + "==2" 
      if setup.parameters['useTriggers']: MuMuESelection += '&&HLT_2mu1e'
      
      MC_hadronSelection    = setup.selection('MC', hadronicSelection = True, 
          **setup.defaultParameters(update={'nJets': self.nJets, 'nBTags':self.nMediumBTags, 'metMin': 0., 'metSigMin':0., 'dPhiJetMet':0. })
        )['cut']
      data_hadronSelection  = setup.selection('Data', hadronicSelection = True, 
          **setup.defaultParameters(update={'nJets': self.nJets, 'nBTags':self.nMediumBTags, 'metMin': 0., 'metSigMin':0., 'dPhiJetMet':0. })
        )['cut']

      #loose bjet selection added here
      MC_hadronSelection += '&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.605)>='+str(self.nLooseBTags[0])
      data_hadronSelection += '&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.605)>='+str(self.nLooseBTags[0])
      if self.nLooseBTags[1]>0:  
        MC_hadronSelection += '&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.605)<='+str(self.nLooseBTags[1])
        data_hadronSelection += '&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.605)<='+str(self.nLooseBTags[1])

      MC_MuMuMu = "&&".join([
        MC_hadronSelection,
        MuMuMuSelection,
        "abs(mlmZ_mass-91.2)<10"
      ])
      MC_EEE = "&&".join([
        MC_hadronSelection,
        EEESelection,
        "abs(mlmZ_mass-91.2)<10"
      ])
      MC_EEMu = "&&".join([
        MC_hadronSelection,
        EEMuSelection,
        "abs(mlmZ_mass-91.2)<10"
      ])
      MC_MuMuE = "&&".join([
        MC_hadronSelection,
        MuMuESelection,
        "abs(mlmZ_mass-91.2)<10"
      ])

      MC_3l = "(("+MC_MuMuMu+")||("+MC_EEE+")||("+MC_EEMu+")||("+MC_MuMuE+"))"
      
      data_MuMuMu = "&&".join([
        data_hadronSelection,
        MuMuMuSelection,
        "abs(mlmZ_mass-91.2)<10"
      ])
      data_EEE = "&&".join([
        data_hadronSelection,
        EEESelection,
        "abs(mlmZ_mass-91.2)<10"
      ])
      data_EEMu = "&&".join([
        data_hadronSelection,
        EEMuSelection,
        "abs(mlmZ_mass-91.2)<10"
      ])
      data_MuMuE = "&&".join([
        data_hadronSelection,
        MuMuESelection,
        "abs(mlmZ_mass-91.2)<10"
      ])


      ######yield_MC_3l computed for ALL channels but lumi changes slightly here depending on channel
      yield_MC_3l = setup.lumi[channel]/1000.*u_float( getYieldFromChain(setup.sample['TTZ'][channel]['chain'], cutString = MC_3l, weight=weight, returnError = True))
      if setup.verbose: print "yield_MC_looseSelection_3l: %s"%yield_MC_3l 
      yield_data_MuMuMu = u_float( getYieldFromChain(setup.sample['Data']['MuMu']['chain'], cutString = data_MuMuMu, weight=weight, returnError = True))
      if setup.verbose: print "yield_data_looseSelection_MuMuMu: %s"%yield_data_MuMuMu
      yield_data_EEE = u_float( getYieldFromChain(setup.sample['Data']['EE']['chain'], cutString = data_EEE, weight=weight, returnError = True))
      if setup.verbose: print "yield_data_looseSelection_EEE: %s"%yield_data_EEE
      yield_data_EMu = u_float( getYieldFromChain(setup.sample['Data']['EMu']['chain'], cutString = "(("+data_MuMuE+')||('+data_EEMu+'))', weight=weight, returnError = True))
      if setup.verbose: print "yield_data_looseSelection_EMu: %s"%yield_data_EMu
      
      yield_data_3l = yield_data_MuMuMu+yield_data_EEE+yield_data_EMu
      if setup.verbose: print "yield_data_3l: %s"%yield_data_3l
      
      #electroweak subtraction
      print "\n Substracting electroweak backgrounds from data: \n"
      yield_other = u_float(0., 0.) 
      for s in ['TTJets' , 'DY', 'other']:
        yield_other+= setup.lumi[channel]/1000.* u_float(getYieldFromChain(setup.sample[s][channel]['chain'], cutString = MC_3l,  weight=weight, returnError=True))
        if setup.verbose: print "yield_looseSelection_other %s added, now: %s"%(s, yield_other)
        
      normRegYield = yield_data_3l - yield_other
      if normRegYield.val<0: print "\n !!!Warning!!! \n Negative normalization region yield data: (%s), MC: (%s) \n"%(yield_data_3l, yield_other)

      print  "normRegYield", normRegYield
      print "\n Control Region predictys ", normRegYield, " TTZ events in data; ", yield_MC_3l, " TTZ events in MC. Ratio ---> ", (normRegYield/yield_MC_3l)
      print "DD-TTZ ---> ", (normRegYield/yield_MC_3l)*yield_MC_2l
      return (normRegYield/yield_MC_3l)*yield_MC_2l
      

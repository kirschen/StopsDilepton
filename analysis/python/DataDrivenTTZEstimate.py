from math import sqrt
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator
from StopsDilepton.analysis.u_float import u_float
from StopsDilepton.tools.objectSelection import looseMuIDString,looseEleIDString
#from StopsDilepton.tools.helpers import printHeader

# Logging
import logging
logger = logging.getLogger(__name__)

def getLooseLeptonString(nMu, nE):
    return looseMuIDString(ptCut=10) + "==" + str(nMu) + "&&" + looseEleIDString(ptCut=10) + "==" + str(nE)

def getLeptonString(nMu, nE):
    # Only good leptons or also loose?
    # return "nGoodMuons==" + str(nMu) + "&&nGoodElectrons==" + str(nE)
    return getLooseLeptonString(nMu, nE)

def getPtThresholdString(firstPt, secondPt, thirdPt):
    return "(Sum$(LepGood_pt>" + str(firstPt) + ")>=1&&Sum$(LepGood_pt>" + str(secondPt) + ")>=2&&Sum$(LepGood_pt>" + str(thirdPt) + ")>=3)"

class DataDrivenTTZEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(DataDrivenTTZEstimate, self).__init__(name, cacheDir=cacheDir)
        self.nJets        = (4,-1) # jet selection (min, max)
        self.nLooseBTags  = (2,-1) # loose bjet selection (min, max)
        self.nMediumBTags = (1,-1) # bjet selection (min, max)

        self.useTop16009       = True
        self.ratioTop16009     = 1.27 #
        self.sysErrTop16009    = (-0.17, +0.20)
        self.statErrTop16009   = (-0.37, +0.42)

    #Concrete implementation of abstract method 'estimate' as defined in Systematic
    def _estimate(self, region, channel, setup):

        #Sum of all channels for 'all'
        if channel=='all':
            return sum( [ self.cachedEstimate(region, c, channel, setup) for c in ['MuMu', 'EE', 'EMu'] ] )
        else:
            #Data driven for EE, EMu and  MuMu.
            zWindow= 'allZ' if channel=='EMu' else 'offZ'
            preSelection = setup.preselection('MC', zWindow=zWindow, channel=channel)

            #check lumi consistency
            MC_2l = "&&".join([region.cutString(setup.sys['selectionModifier']), preSelection['cut']])
            weight = preSelection['weightStr']
            logger.debug("weight: %s", weight)

            yield_MC_2l =  setup.lumi[channel]/1000.*u_float(**setup.sample['TTZ'][channel].getYieldFromDraw(selectionString = MC_2l, weightString=weight))
            if setup.verbose: print "yield_MC_2l: %s"%yield_MC_2l

            if self.useTop16009:
              sysError  = max((abs(x) for x in self.sysErrTop16009))    # not sure yet to handle assymetric errors
              statError = max((abs(x) for x in self.statErrTop16009))
              error     = sqrt(sysError*sysError+statError*statError)
	      return u_float(self.ratioTop16009, error)*yield_MC_2l
            else:
	      # pt leptons > 30, 20, 10 GeV
	      useTrigger      = False # setup.parameters['useTriggers'] # better not to use three lepton triggers, seems to be too inefficient
	      mumumuSelection = "&&".join([getLeptonString(3, 0), getPtThresholdString(30, 20, 10)]) + ("&&HLT_3mu"   if useTrigger else "")
	      mumueSelection  = "&&".join([getLeptonString(2, 1), getPtThresholdString(30, 20, 10)]) + ("&&HLT_2mu1e" if useTrigger else "") 
	      mueeSelection   = "&&".join([getLeptonString(1, 2), getPtThresholdString(30, 20, 10)]) + ("&&HLT_2e1mu" if useTrigger else "")
	      eeeSelection    = "&&".join([getLeptonString(0, 3), getPtThresholdString(30, 20, 10)]) + ("&&HLT_3e"    if useTrigger else "")
	      lllSelection    = "((" + ")||(".join([mumumuSelection, mumueSelection, mueeSelection, eeeSelection]) + "))"

	      bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890))"
	      bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.605))"
	      zMassSelection  = "abs(mlmZ_mass-91.1876)<10"

	      # Start from base hadronic selection and add loose b-tag and Z-mass requirement
	      selection       = {}
	      for dataOrMC in ["Data", "MC"]:
		selection[dataOrMC]  = setup.selection(dataOrMC, hadronicSelection = True, **setup.defaultParameters(update={'nJets': self.nJets, 'nBTags':self.nMediumBTags, 'metMin': 0., 'metSigMin':0., 'dPhiJetMet':0. }))['cut']
		selection[dataOrMC] += "&&" + bJetSelectionL+">="+str(self.nLooseBTags[0])
		selection[dataOrMC] += "&&" + zMassSelection 


	      MC_3l       = lllSelection    + "&&" + selection["MC"]
	      data_mumumu = mumumuSelection + "&&" + selection["Data"]
	      data_mumue  = mumueSelection  + "&&" + selection["Data"]
	      data_muee   = mueeSelection   + "&&" + selection["Data"]
	      data_eee    = eeeSelection    + "&&" + selection["Data"]

	      # Calculate yields (take together)
	      yield_ttZ_2l      = setup.lumi[channel]/1000.*u_float(**setup.sample['TTZ'][channel].getYieldFromDraw(selectionString = MC_2l,                                 weightString=weight))
	      yield_ttZ_3l      = setup.lumi[channel]/1000.*u_float(**setup.sample['TTZ'][channel].getYieldFromDraw(selectionString = MC_3l,                                 weightString=weight))
	      yield_data_mumumu =                           u_float(**setup.sample['Data']['MuMu'].getYieldFromDraw(selectionString = data_mumumu,                           weightString=weight))
	      yield_data_eee    =                           u_float(**setup.sample['Data']['EE'].getYieldFromDraw(  selectionString = data_eee,                              weightString=weight))
	      yield_data_mue    =                           u_float(**setup.sample['Data']['EMu'].getYieldFromDraw( selectionString = "(("+data_mumue+')||('+data_muee+'))', weightString=weight))
	      yield_data_3l     = yield_data_mumumu + yield_data_mue + yield_data_eee

	      #electroweak subtraction
	      yield_other = u_float(0., 0.)
	      for s in ['TTJets' , 'DY', 'other']:
		  yield_other+= setup.lumi[channel]/1000.* u_float(**setup.sample[s][channel].getYieldFromDraw(selectionString = MC_3l,  weightString=weight))

	      yield_ttZ_data = yield_data_3l - yield_other

	      if yield_ttZ_data/yield_ttZ_3l<0: logger.warn("Data-driven estimate is negative!")
	      logger.info("Control region predictions: ")
	      logger.info("  data:        " + str(yield_data_3l))
	      logger.info("  MC other:    " + str(yield_other))
	      logger.info("  TTZ (MC):    " + str(yield_ttZ_3l))
	      logger.info("  TTZ (data):  " + str(yield_ttZ_data))
	      logger.info("  TTZ (ratio): " + str(yield_ttZ_data/yield_ttZ_3l))
	      return (yield_ttZ_data/yield_ttZ_3l)*yield_MC_2l

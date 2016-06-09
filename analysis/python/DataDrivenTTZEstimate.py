import os
from math import sqrt
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator
from StopsDilepton.analysis.u_float import u_float
from StopsDilepton.tools.objectSelection import muonSelectorString,eleSelectorString
from StopsDilepton.analysis.Cache        import Cache

# Logging
import logging
logger = logging.getLogger(__name__)

def getLooseLeptonString(nMu, nE):
    raise NotImplementedError( "Tom, please check carefully" )
    return muonSelectorString(ptCut=10) + "==" + str(nMu) + "&&" + eleSelectorString(ptCut=10) + "==" + str(nE)

def getLeptonString(nMu, nE):
    # Only good leptons or also loose?
    # return "nGoodMuons==" + str(nMu) + "&&nGoodElectrons==" + str(nE)
    return getLooseLeptonString(nMu, nE)

def getPtThresholdString(firstPt, secondPt, thirdPt):
    return "(Sum$(LepGood_pt>" + str(firstPt) + ")>=1&&Sum$(LepGood_pt>" + str(secondPt) + ")>=2&&Sum$(LepGood_pt>" + str(thirdPt) + ")>=3)"

class DataDrivenTTZEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None, useTop16009=False):
        super(DataDrivenTTZEstimate, self).__init__(name, cacheDir=cacheDir)
        self.nJets        = (3,-1) # jet selection (min, max)
        self.nLooseBTags  = (2,-1) # loose bjet selection (min, max)
        self.nMediumBTags = (0,-1) # bjet selection (min, max)

        self.useTop16009       = useTop16009
        self.ratioTop16009     = 1.27 #
        self.sysErrTop16009    = (-0.17, +0.20)
        self.statErrTop16009   = (-0.37, +0.42)

        # Because we are going to reuse a lot of yields which otherwise will be terribly slow
        self.helperCacheName = os.path.join('.', 'helperCache.pkl')
        self.helperCache     = Cache(self.helperCacheName, verbosity=2)

    def yieldFromCache(self, setup, sample, channel, selectionString, weightString):
        s = (sample, channel, selectionString, weightString)
        if self.helperCache.contains(s):
          return self.helperCache.get(s)
        else:
	  yieldFromDraw = u_float(**setup.sample[sample][channel].getYieldFromDraw(selectionString, weightString))
          self.helperCache.add(s, yieldFromDraw, save=True)
	  return yieldFromDraw

    #Concrete implementation of abstract method 'estimate' as defined in Systematic
    def _estimate(self, region, channel, setup):
        logger.info("Data-driven TTZ estimate for region " + str(region) + " in channel " + channel + " and setup " + str(setup.sys) + ":")

        #Sum of all channels for 'all'
        if channel=='all':
            estimate = sum([self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE', 'EMu']])

        else:
            zWindow= 'allZ' if channel=='EMu' else 'offZ'
            preSelection = setup.preselection('MC', zWindow=zWindow, channel=channel)

            MC_2l = "&&".join([region.cutString(setup.sys['selectionModifier']), preSelection['cut']])
            weight = setup.weightString()
            logger.info("weight: %s", weight)

            yield_ttZ_2l = setup.lumi[channel]/1000.*self.yieldFromCache(setup, 'TTZ', channel, MC_2l, weight)
            logger.info("yield_MC_2l: %s"%yield_ttZ_2l)

            if self.useTop16009:
              sysError  = max((abs(x) for x in self.sysErrTop16009))    # not sure yet to handle assymetric errors
              statError = max((abs(x) for x in self.statErrTop16009))
              error     = sqrt(sysError*sysError+statError*statError)
	      return u_float(self.ratioTop16009, error)*yield_ttZ_2l

            else:
	      # pt leptons > 30, 20, 10 GeV
	      useTrigger            = False # setup.parameters['useTriggers'] # better not to use three lepton triggers, seems to be too inefficient
              lllSelection          = {}
	      lllSelection['MuMu']  = "&&".join([getLeptonString(3, 0), getPtThresholdString(30, 20, 10)]) + ("&&HLT_3mu"   if useTrigger else "")
	      lllSelection['MuMuE'] = "&&".join([getLeptonString(2, 1), getPtThresholdString(30, 20, 10)]) + ("&&HLT_2mu1e" if useTrigger else "") 
	      lllSelection['MuEE']  = "&&".join([getLeptonString(1, 2), getPtThresholdString(30, 20, 10)]) + ("&&HLT_2e1mu" if useTrigger else "")
	      lllSelection['EE']    = "&&".join([getLeptonString(0, 3), getPtThresholdString(30, 20, 10)]) + ("&&HLT_3e"    if useTrigger else "")
              lllSelection['EMu']   = "(("+lllSelection['MuMuE']+")||("+lllSelection['MuEE']+"))"

	      bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890))"
	      bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.605))"
	      zMassSelection  = "abs(mlmZ_mass-91.1876)<10"

	      # Start from base hadronic selection and add loose b-tag and Z-mass requirement
	      selection       = {}
	      for dataOrMC in ["Data", "MC"]:
		selection[dataOrMC]  = setup.selection(dataOrMC, hadronicSelection = True, **setup.defaultParameters(update={'nJets': self.nJets, 'nBTags':self.nMediumBTags, 'metMin': 0., 'metSigMin':0., 'dPhiJetMet':0. }))['cut']
		selection[dataOrMC] += "&&" + bJetSelectionL+">="+str(self.nLooseBTags[0])
		selection[dataOrMC] += "&&" + zMassSelection 
                logger.info("Selection " + dataOrMC + ": " + selection[dataOrMC])

	      # Calculate yields (take together channels together)
              channels      = ['MuMu','EMu','EE']
	      yield_ttZ_3l  = sum(self.yieldFromCache(setup, 'TTZ',  c, "&&".join([lllSelection[c], selection["MC"]]),   weight)*setup.dataLumi[channel]/1000 for c in ['MuMu','EMu','EE'])
	      yield_other   = sum(self.yieldFromCache(setup, s,      c, "&&".join([lllSelection[c], selection["MC"]]),   weight)*setup.dataLumi[channel]/1000 for c in ['MuMu','EMu','EE'] for s in ['TTJets', 'DY', 'other'])
	      yield_data_3l = sum(self.yieldFromCache(setup, 'Data', c, "&&".join([lllSelection[c], selection["Data"]]), "(1)")                               for c in ['MuMu','EMu','EE'])

              if not yield_ttZ_3l > 0:
                logger.warn("No yield for 3l selection")
                estimate = u_float(0, 0)

	      yield_ttZ_data = yield_data_3l - yield_other
	      if yield_ttZ_data < 0:
                logger.warn("Data-driven ratio is negative!")
                yield_ttZ_data = u_float(0, 0)

	      logger.info("Control region predictions: ")
	      logger.info("  data:        " + str(yield_data_3l))
	      logger.info("  MC other:    " + str(yield_other))
	      logger.info("  TTZ (MC):    " + str(yield_ttZ_3l))
	      logger.info("  TTZ (data):  " + str(yield_ttZ_data))
	      logger.info("  TTZ (ratio): " + str(yield_ttZ_data/yield_ttZ_3l))
	      estimate = (yield_ttZ_data/yield_ttZ_3l)*yield_ttZ_2l

        logger.info("  -->  " + str(estimate))
	return estimate

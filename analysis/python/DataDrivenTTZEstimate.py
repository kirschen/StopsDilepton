import os
from math import sqrt
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator
from StopsDilepton.analysis.u_float import u_float
from StopsDilepton.tools.objectSelection import muonSelectorString,eleSelectorString
from StopsDilepton.tools.user import analysis_results

# Logging
import logging
logger = logging.getLogger(__name__)

isoCut = 'VT'

def getLooseLeptonString(nMu, nE):
    return muonSelectorString(ptCut=10, iso=isoCut) + "==" + str(nMu) + "&&" + eleSelectorString(ptCut=10, iso=isoCut) + "==" + str(nE)

def getLeptonString(nMu, nE):
    return getLooseLeptonString(nMu, nE)

def getPtThresholdString(firstPt, secondPt):
    return "&&".join([muonSelectorString(ptCut=firstPt,  iso=isoCut) + "+" + eleSelectorString(ptCut=firstPt,  iso=isoCut) + ">=1",
                      muonSelectorString(ptCut=secondPt, iso=isoCut) + "+" + eleSelectorString(ptCut=secondPt, iso=isoCut) + ">=2"])

#    return "(Sum$(LepGood_pt>" + str(firstPt) + ")>=1&&Sum$(LepGood_pt>" + str(secondPt) + ")>=2&&Sum$(LepGood_pt>" + str(thirdPt) + ")>=3)"

class DataDrivenTTZEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None, useTop16009=False):
        super(DataDrivenTTZEstimate, self).__init__(name, cacheDir=cacheDir)
        self.nJets        = (3,-1) # jet selection (min, max)
        self.nLooseBTags  = (2,-1) # loose bjet selection (min, max)
        self.nMediumBTags = (0,-1) # bjet selection (min, max)

        self.useTop16009       = useTop16009
        self.ratioTop16009     = 0.89 #
        self.sysErrTop16009    = (-0.13, +0.15)
        self.statErrTop16009   = (-0.16, +0.18)

    #Concrete implementation of abstract method 'estimate' as defined in Systematic
    def _estimate(self, region, channel, setup):
        logger.info("Data-driven TTZ estimate for region " + str(region) + " in channel " + channel + " and setup " + str(setup.sys) + ":")

        #Sum of all channels for 'all'
        if channel=='all':
            estimate = sum([self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE', 'EMu']])

        elif channel=='SF':
            estimate = sum([self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE']])

        else:
            preSelection = setup.preselection('MC', channel=channel)

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
              lllSelection          = {}
              lllSelection['MuMu']  = "&&".join([getLeptonString(3, 0), getPtThresholdString(30, 20)])
              lllSelection['MuMuE'] = "&&".join([getLeptonString(2, 1), getPtThresholdString(30, 20)])
              lllSelection['MuEE']  = "&&".join([getLeptonString(1, 2), getPtThresholdString(30, 20)])
              lllSelection['EE']    = "&&".join([getLeptonString(0, 3), getPtThresholdString(30, 20)])
              lllSelection['EMu']   = "(("+lllSelection['MuMuE']+")||("+lllSelection['MuEE']+"))"

              bJetSelectionM  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.800))"
              bJetSelectionL  = "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.460))"
              zMassSelection  = "abs(mlmZ_mass-91.1876)<10"

              # Start from base hadronic selection and add loose b-tag and Z-mass requirement
              selection       = {}
              for dataOrMC in ["Data", "MC"]:
                selection[dataOrMC]  = setup.selection(dataOrMC, hadronicSelection = True, **setup.defaultParameters(update={'nJets': self.nJets, 'nBTags':self.nMediumBTags, 'metMin': 0., 'metSigMin':0., 'dPhi':False }))['cut']
                selection[dataOrMC] += "&&" + bJetSelectionL+">="+str(self.nLooseBTags[0])
                selection[dataOrMC] += "&&" + zMassSelection 

              # Calculate yields (take together channels together)
              channels      = ['MuMu','EE','EMu']
              yield_ttZ_3l  = sum(self.yieldFromCache(setup, 'TTZ',  c, "&&".join([lllSelection[c], selection["MC"]]),   weight)*setup.dataLumi[channel]/1000 for c in channels)
              yield_other   = sum(self.yieldFromCache(setup, s,      c, "&&".join([lllSelection[c], selection["MC"]]),   weight)*setup.dataLumi[channel]/1000 for c in channels for s in ['TTJets', 'DY', 'multiBoson', 'other'])
              yield_data_3l = sum(self.yieldFromCache(setup, 'Data', c, "&&".join([lllSelection[c], selection["Data"]]), "(1)")                               for c in channels)

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

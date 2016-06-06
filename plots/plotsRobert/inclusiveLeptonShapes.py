''' Analysis script for 1D 2l plots (RootTools)
'''
#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools
import os

#RootTools
from RootTools.core.standard import *

# StopsDilepton
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()  #smth smarter possible?
from StopsDilepton.tools.objectSelection import getLeptons, getOtherLeptons, getGoodLeptons, looseEleIDString, looseMuIDString, leptonVars, getGenPartsAll
from StopsDilepton.tools.helpers import deltaR

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='INFO',
      help="Log level for logging"
)

argParser.add_argument('--plot_directory',
    default='png25ns_3rdLep',
    action='store',
)

args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

import StopsDilepton.tools.user as user
from StopsDilepton.samples.helpers import fromHeppySample
maxN = 5 

TTJets              = fromHeppySample("TTJets", data_path = user.cmg_directory, maxN = maxN)
DYJetsToLL_M50      = fromHeppySample("DYJetsToLL_M50", data_path = user.cmg_directory, maxN = maxN)
QCD_Pt300to470_Mu5  = fromHeppySample("QCD_Pt300to470_Mu5", data_path = user.cmg_directory, maxN = maxN)

from StopsDilepton.samples.color import color
TTJets.color = color.TTJets
DYJetsToLL_M50.color = color.DY
QCD_Pt300to470_Mu5.color = color.QCD

samples = [TTJets, QCD_Pt300to470_Mu5]

from StopsDilepton.tools.user import plot_directory
plot_path = os.path.join(plot_directory, 'etc')

for iso in ["miniRelIso", "relIso03", "relIso04"]:
    histos={}
    for sample in samples:
        logger.info( "Working on %s" % sample.name )
        histos[sample.name+"_Good"] = sample.get1DHistoFromDraw("LepGood_"+iso, [40,0,1], selectionString = "LepGood_pt>20&&abs(LepGood_pdgId)==13")
        histos[sample.name+"_Good"].legendText = sample.name + " (Good)" 
        histos[sample.name+"_Good"].style = styles.lineStyle( sample.color )

        histos[sample.name+"_Other"] = sample.get1DHistoFromDraw("LepOther_"+iso, [40,0,1], selectionString = "LepOther_pt>20&&abs(LepGood_pdgId)==13")
        histos[sample.name+"_Other"].legendText = sample.name + " (Other)" 
        histos[sample.name+"_Other"].style = styles.lineStyle( sample.color + 1 )

        # histos[sample.name+"_Good"].Add( histos[sample.name+"_Other"] )
        

    plotting.draw(
        Plot.fromHisto(name = iso, histos = [ [histos[sample.name+"_Good"], histos[sample.name+"_Other"] ] for sample in samples ], texX = iso, texY = "Number of Events"),
        plot_directory = plot_path, #ratio = ratio, 
        logX = False, logY = True, sorting = False, 
        # yRange = (0.03, "auto"), 
        # scaling = {0:1},
        # drawObjects = drawObjects( dataMCScale )
    )

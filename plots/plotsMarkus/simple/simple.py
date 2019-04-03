#!/usr/bin/env python
''' simple analysis script 
'''
#
# Standard imports and batch mode
#
import ROOT
ROOT.gROOT.SetBatch(True)
from math import sqrt, cos, sin, pi, cosh
from RootTools.core.standard import *

# StopsDilepton
from StopsDilepton.tools.user import plot_directory
from StopsDilepton.tools.objectSelection import getGoodMuons, alwaysTrue

#
# Arguments
# 
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--plot_directory', action='store',      default='StopsDilepton')
argParser.add_argument('--small',       action='store_true',                                                                        help="Run the file on a small sample (for test purpose), bool flag set to True if used" )
args = argParser.parse_args()

#
# Logger
#
import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

#
# Samples 2016 
#
data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
#postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
#from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
postProcessing_directory = "stops_2016_nano_v0p3/dilep/"
from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
#mc             = [ Top_pow_16, TTXNoZ_16, TTZ_16, multiBoson_16, DY_LO_16]

#
# Samples 2017 
#
data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
#postProcessing_directory = "stops_2017_nano_v0p3/dilep/"
#from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
postProcessing_directory = "stops_2017_nano_v0p3/dilep/"
from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
#mc             = [ Top_pow_17, TTXNoZ_17, TTZ_17, multiBoson_17, DY_LO_17]

#
# Samples 2018 
#
data_directory = "/afs/hephy.at/data/dspitzbart01/nanoTuples/"
#postProcessing_directory = "stops_2018_nano_v0p3/dilep/"
#from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
postProcessing_directory = "stops_2018_nano_v0p3/dilep/"
from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
#mc             = [ Top_pow_18, TTXNoZ_18, TTZ_18, multiBoson_18, DY_LO_18]

# add all data
DoubleMuon  = Sample.combine( "DoubleMuon", [DoubleMuon_Run2016, DoubleMuon_Run2017, DoubleMuon_Run2018] )

data_sample = DoubleMuon

# make small
if args.small:
    data_sample.reduceFiles( to = 1 )

## 4 muon selection
preSelection = "Sum$(Muon_pt>10&&Muon_mediumPromptId)>=4"

#
# Read variables and sequences
#
read_variables = ["weight/F" , 
                  #"met_phi/F", 
                  "nMuon/I", "Muon[pt/F,eta/F,phi/F,mediumPromptId/O,pdgId/I,pfRelIso03_all/F]", 
]
muVars = ["pt", "eta", "phi", "mediumPromptId", 'pdgId', "pfRelIso03_all"]

def makeM4l(event, sample):

    # Get muons
    muons      = getGoodMuons(event, collVars = muVars, mu_selector = lambda m:m['pt']>10 and m['mediumPromptId'] and m["pfRelIso03_all"]<0.3 )

    event.m4l = float('nan')
    m4l2 = 0
    if len( muons ) ==4:

        # select 2 positiove and 2 negative charges
        pdgIds = [ p['pdgId'] for p in muons ]
        if pdgIds.count(+13) == 2 and pdgIds.count(-13)==2:
            for i in range(1,4):
                for j in range( i ):
                    #do something
                    m4l2 += 27.

    event.m4l = sqrt( m4l2 )
    #print event.m4l

sequence = [makeM4l]

#
# Text on the plots
#
def drawObjects( ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right
    lines = [
      (0.15, 0.95, 'CMS Preliminary'), 
    ]
    return [tex.DrawLatex(*l) for l in lines] 

data_sample.setSelectionString(preSelection)
data_sample.style = styles.errorStyle( ROOT.kBlack )

stack = Stack([data_sample])

# Use some defaults
Plot.setDefaults(stack = stack)

plots = []

plots.append(Plot(name = "m4l",
  texX = 'm(4l)', texY = 'Number of Events / 3 GeV',
  attribute = lambda event, sample: event.m4l,
  binning=[100,20,320],
))

plotting.fill(plots, read_variables = read_variables, sequence=sequence)

for plot in plots:
  plotting.draw(plot, 
      plot_directory = os.path.join(plot_directory, args.plot_directory),
      ratio = None, 
      logX = False, logY = False, sorting = True, 
      yRange = (0.003, "auto"),
      drawObjects = drawObjects( )
  )


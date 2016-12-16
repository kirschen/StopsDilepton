#Standard imports
import ROOT
import os

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
args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

#from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import dirs, color
#postProcessing_directory = "postProcessed_80X_v21/dilepTiny/"
#from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import Top as Top_relIso
postProcessing_directory = "postProcessed_80X_v12/dilepTiny"
data_directory = "/afs/hephy.at/data/rschoefbeck02/cmgTuples/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed_ICHEP import *

from RootTools.core.standard import *

from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain

samples = [TTJets_Dilep, TTLep_pow, TTJets]

maxN = -1
for sample in samples:
    if maxN>0:
        sample.reduceFiles(to=maxN)

from StopsDilepton.tools.objectSelection import multiIsoLepString
multiIsoWPVTVT = multiIsoLepString('VT','VT', ('l1_index','l2_index'))
multiIsoWPMT = multiIsoLepString('M','T', ('l1_index','l2_index'))
relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])

weight_string = 'weight*reweightDilepTriggerBackup*reweightLeptonSF'
lumiFac = 2.4

cuts=[
  ("opposite sign","isOS==1"),
  ("m(ll)>20", "dl_mass>20"),
  ("|m(ll) - mZ|>15 for SF","( (isMuMu==1||isEE==1)&&abs(dl_mass-91.2)>=15 || isEMu==1 )"),
  (">=2 jets", "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id))>=2"),
  (">=1 b-tags (CSVv2)", "Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id&&JetGood_btagCSV>0.890)>=1"),
  ("MET>80", "met_pt>80"),
  ("MET/sqrt(HT)>5", "met_pt/sqrt(Sum$(JetGood_pt*(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_id)))>5"),
  ("dPhiJetMET", "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
    ]

#relIso_cuts   =  [("==2 relIso03<0.12 leptons", "nGoodMuons+nGoodElectrons==2&&l1_relIso03<0.12&&l2_relIso03<0.12"),
#                  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_relIso03<0.4)==2"),
#                ]
multiIso_cuts =  [("==2 VT leptons (25/20)",    "nGoodMuons+nGoodElectrons==2&&l1_mIsoWP>=5&&l2_mIsoWP>=5&&l1_pt>25"),
                  ("looseLeptonVeto", "Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"),
                ]

#h_relIso   = Top_relIso.get1DHistoFromDraw( "dl_mt2ll", binning = [300/20,0,300], selectionString = "&&".join([c[1] for c in cuts + relIso_cuts]), addOverFlowBin = 'upper', weightString = weight_string )
#h_relIso.style = styles.errorStyle( ROOT.kRed )
#h_relIso.legendText = "relIso03<0.12"

h_TTJets_Dilep = TTJets_Dilep.get1DHistoFromDraw( "dl_mt2ll", binning = [300/20,0,300], selectionString = "&&".join([c[1] for c in cuts + multiIso_cuts]), addOverFlowBin = 'upper', weightString = weight_string )
h_TTJets_Dilep.style = styles.errorStyle( ROOT.kRed )
h_TTJets_Dilep.legendText = "madgraph"

h_TTLep_pow = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", binning = [300/20,0,300], selectionString = "&&".join([c[1] for c in cuts + multiIso_cuts]), addOverFlowBin = 'upper', weightString = weight_string )
h_TTLep_pow.style = styles.errorStyle( ROOT.kBlue )
h_TTLep_pow.legendText = "powheg"

h_TTJets = TTJets.get1DHistoFromDraw( "dl_mt2ll", binning = [300/20,0,300], selectionString = "&&".join([c[1] for c in cuts + multiIso_cuts]), addOverFlowBin = 'upper', weightString = weight_string )
h_TTJets.style = styles.errorStyle( ROOT.kGreen )
h_TTJets.legendText = "amc@nlo"

h_TTJets_Dilep.Scale(2.4)
h_TTLep_pow.Scale(2.4)
h_TTJets.Scale(2.4)

ratio = {'yRange':(0.1,1.9), 'texY':'pow/MG'}
plotting.draw(
    Plot.fromHisto("mt2ll_top_comparison",
        [[ h_TTJets_Dilep ], [ h_TTLep_pow ], [h_TTJets] ],
        texX = "MT_{2}^{ll} (GeV)"
    ), 
    plot_directory = "/afs/hephy.at/user/r/rschoefbeck/www/", ratio = ratio, 
    logX = False, logY = True, sorting = False, 
    yRange = (0.003, "auto"), 
    scaling = {1:0, 2:0},
    legend = "auto",
    #drawObjects = drawObjects( dataMCScale )
)

cuts += [("mt2ll100", "dl_mt2ll>100")]

h_TTJets_Dilep = TTJets_Dilep.get1DHistoFromDraw( "dl_mt2blbl", binning = [400/100,0,400], selectionString = "&&".join([c[1] for c in cuts + multiIso_cuts]), addOverFlowBin = 'upper', weightString = weight_string )
h_TTJets_Dilep.style = styles.errorStyle( ROOT.kRed )
h_TTJets_Dilep.legendText = "madgraph"

h_TTLep_pow = TTLep_pow.get1DHistoFromDraw( "dl_mt2blbl", binning = [400/100,0,400], selectionString = "&&".join([c[1] for c in cuts + multiIso_cuts]), addOverFlowBin = 'upper', weightString = weight_string )
h_TTLep_pow.style = styles.errorStyle( ROOT.kBlue )
h_TTLep_pow.legendText = "powheg"

h_TTJets = TTJets.get1DHistoFromDraw( "dl_mt2blbl", binning = [400/100,0,400], selectionString = "&&".join([c[1] for c in cuts + multiIso_cuts]), addOverFlowBin = 'upper', weightString = weight_string )
h_TTJets.style = styles.errorStyle( ROOT.kGreen )
h_TTJets.legendText = "amc@nlo"

h_TTJets_Dilep.Scale(2.4)
h_TTLep_pow.Scale(2.4)
h_TTJets.Scale(2.4)

ratio = {'yRange':(0.1,1.9)}
plotting.draw(
    Plot.fromHisto("mt2blbl_top_comparison",
        [[ h_TTJets_Dilep ], [ h_TTLep_pow ], [h_TTJets] ],
        texX = "MT_{2}^{blbl} (GeV)"
    ), 
    plot_directory = "/afs/hephy.at/user/r/rschoefbeck/www/", ratio = ratio, 
    logX = False, logY = True, sorting = False, 
    yRange = (0.003, "auto"), 
    scaling = {1:0, 2:0},
    legend = "auto",
    #drawObjects = drawObjects( dataMCScale )
)

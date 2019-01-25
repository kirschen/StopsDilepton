''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools,os
import copy

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
args = argParser.parse_args()


#RootTools
from RootTools.core.standard import *
from StopsDilepton.tools.user import data_directory as user_data_directory
data_directory = user_data_directory 

postProcessing_directory = "postProcessed_80X_v36/dilepTiny/"

from StopsDilepton.samples.color import color

import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)


dirs = {}
dirs['TTLep_pow'] = ["TTLep_pow"]
directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}

TTLep_pow = Sample.fromDirectory(name="TTLep_pow", treeName="Events", isData=False, color=color.TTJets, texName="t#bar{t} + Jets (lep,pow)", directory=directories['TTLep_pow'])
#TTLep_pow.reduceFiles( to = 10 )

#from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *


#for s in [dy_lo,dy]:
#    s.reduceFiles( to = 1 )

presel = "dl_mass>20&&l1_pt>25&&(l1_mIsoWP>=5&&l2_mIsoWP>=5) && Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0 && nGoodMuons+nGoodElectrons==2&&Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"
presel += '&&nJetGood>=2&&nBTag>=1'#&&dl_mass>75&&dl_mass<105&&met_pt>80'

#presel = '(1)'

#norm = TTLep_pow.getYieldFromDraw(selectionString=presel, weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF" )

h_tt_raw = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", selectionString=presel, binning = [15,0,300],  addOverFlowBin = 'upper', weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF" )
h_tt_isr = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", selectionString=presel, binning = [15,0,300],  addOverFlowBin = 'upper', weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF * reweight_nISR" )
h_tt_top = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", selectionString=presel, binning = [15,0,300],  addOverFlowBin = 'upper', weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF * reweightTopPt" )

#norm = TTLep_pow.getYieldFromDraw(selectionString=presel, weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF" )

h_tt_raw.style = styles.lineStyle( ROOT.kRed,  width=2 )
h_tt_isr.style = styles.lineStyle( ROOT.kBlue, width=2 )
h_tt_top.style = styles.lineStyle( ROOT.kGreen,width=2 )

h_tt_raw.legendText = "raw"
h_tt_isr.legendText = "ISR reweighted"
h_tt_top.legendText = "top pT reweighted"


plotting.draw(
    Plot.fromHisto("dl_mt2ll_njet2p_btag1p",
                [[ h_tt_raw ], [ h_tt_isr ], [ h_tt_top ]],
                texX = "M_{T}^{ll} (GeV)"
            ),
    plot_directory = "/afs/hephy.at/user/d/dspitzbart/www/stopsDilepton/TTJets_shapes/",
    logX = False, logY = True, #sorting = True, 
    yRange = (0.03, "auto"),
    #drawObjects = None,
    scaling = {0:1}
)

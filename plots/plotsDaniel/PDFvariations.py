''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools,os,pickle
import copy

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',           action='store',      default='INFO',          nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'], help="Log level for logging")
argParser.add_argument('--job',                action='store',      default=0,          help="Which variation")
argParser.add_argument('--combine',            action='store_true', help="Do combination")
args = argParser.parse_args()


#RootTools
from RootTools.core.standard import *
from StopsDilepton.tools.user import data_directory as user_data_directory
data_directory = user_data_directory 

postProcessing_directory = "postProcessed_80X_v36/dilep/"

from StopsDilepton.samples.color import color

import StopsDilepton.tools.logger as logger
import RootTools.core.logger as logger_rt
logger    = logger.get_logger(   args.logLevel, logFile = None)
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None)

resDir = '/afs/hephy.at/data/dspitzbart02/StopsDilepton/PDFvariations/'

dirs = {}
dirs['TTLep_pow'] = ["TTLep_pow"]
directories = { key : [ os.path.join( data_directory, postProcessing_directory, dir) for dir in dirs[key]] for key in dirs.keys()}

TTLep_pow = Sample.fromDirectory(name="TTLep_pow", treeName="Events", isData=False, color=color.TTJets, texName="t#bar{t} + Jets (lep,pow)", directory=directories['TTLep_pow'])
#TTLep_pow.reduceFiles( to = 5 )


presel = "dl_mass>20&&l1_pt>25&&(l1_mIsoWP>=5&&l2_mIsoWP>=5) && Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0 && nGoodMuons+nGoodElectrons==2&&Sum$(LepGood_pt>15&&LepGood_miniRelIso<0.4)==2"
presel += '&&nJetGood>=2&&nBTag>=1'#&&dl_mass>75&&dl_mass<105&&met_pt>80'

#presel = '(1)'

#norm = TTLep_pow.getYieldFromDraw(selectionString=presel, weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF" )
#varHists = []

#if args.job == 0:
#    h_tt_raw = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", selectionString=presel, binning = [15,0,300],  addOverFlowBin = 'upper', weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF * reweightTopPt" )
#    h_tt_raw.Scale(1/h_tt_raw.Integral(1,5))
#    pickle.dump(h_tt_raw, file(resDir + 'central.pkl', 'w'))   
#else:
#
##for i in range(9,111):
##for i in range(9,13):
#    print "Working on variation #",job
#    varHist = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", selectionString=presel, binning = [15,0,300],  addOverFlowBin = 'upper', weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF * reweightTopPt * LHEweight_wgt[%s]"%str(job) )
#    varHist.Scale(1/varHist.Integral(1,5))
#    pickle.dump(h_tt_raw, file(resDir + 'var_%s.pkl'%str(job), 'w'))

#combine = args.combine
combine = True

if combine:

    h_tt_raw = pickle.load(file(resDir + 'central.pkl'))
    
    varHists = []
    varFiles = os.listdir(resDir)
    for f in varFiles:
        if 'var_' in f:
            varHists.append(pickle.load(file(resDir + f)))
    
    lo_lo = h_tt_raw.GetXaxis().FindBin(100)
    lo_hi = h_tt_raw.GetXaxis().FindBin(139)
    mi_lo = h_tt_raw.GetXaxis().FindBin(140)
    mi_hi = h_tt_raw.GetXaxis().FindBin(239)
    hi_lo = h_tt_raw.GetXaxis().FindBin(240)
    hi_hi = h_tt_raw.GetXaxis().FindBin(1000)
    
    ref_lo = h_tt_raw.Integral(lo_lo, lo_hi)
    ref_mi = h_tt_raw.Integral(mi_lo, mi_hi)
    ref_hi = h_tt_raw.Integral(hi_lo, hi_hi)
    
    
    env_lo = ROOT.TH1F("mt2ll_low","",100,0.8*ref_lo,1.2*ref_lo)
    env_mi = ROOT.TH1F("mt2ll_mid","",100,0.8*ref_mi,1.2*ref_mi)
    env_hi = ROOT.TH1F("mt2ll_high","",100,0.8*ref_hi,min(1.2*ref_hi,ref_mi))
    
    for h in varHists:
        env_lo.Fill(h.Integral(lo_lo, lo_hi))
        env_mi.Fill(h.Integral(mi_lo, mi_hi))
        env_hi.Fill(h.Integral(hi_lo, hi_hi))

else:
    if args.job == '0':
        h_tt_raw = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", selectionString=presel, binning = [15,0,300],  addOverFlowBin = 'upper', weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF * reweightTopPt" )
        h_tt_raw.Scale(1/h_tt_raw.Integral(1,5))
        pickle.dump(h_tt_raw, file(resDir + 'central.pkl', 'w'))
    else:
        print "Working on variation #",args.job
        varHist = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", selectionString=presel, binning = [15,0,300],  addOverFlowBin = 'upper', weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF * reweightTopPt * LHEweight_wgt[%s]"%str(args.job) )
        varHist.Scale(1/varHist.Integral(1,5))
        pickle.dump(varHist, file(resDir + 'var_%s.pkl'%str(args.job), 'w'))



#h_tt_isr = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", selectionString=presel, binning = [15,0,300],  addOverFlowBin = 'upper', weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF * reweight_nISR" )
#h_tt_top = TTLep_pow.get1DHistoFromDraw( "dl_mt2ll", selectionString=presel, binning = [15,0,300],  addOverFlowBin = 'upper', weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF * reweightTopPt" )
#
##norm = TTLep_pow.getYieldFromDraw(selectionString=presel, weightString = "reweightDilepTriggerBackup * reweightLeptonSF * reweightBTag_SF * reweightPU36fb * reweightLeptonTrackingSF" )
#
#h_tt_raw.style = styles.lineStyle( ROOT.kRed,  width=2 )
#h_tt_isr.style = styles.lineStyle( ROOT.kBlue, width=2 )
#h_tt_top.style = styles.lineStyle( ROOT.kGreen,width=2 )
#
#h_tt_raw.legendText = "raw"
#h_tt_isr.legendText = "ISR reweighted"
#h_tt_top.legendText = "top pT reweighted"
#
#
#plotting.draw(
#    Plot.fromHisto("dl_mt2ll_njet2p_btag1p",
#                [[ h_tt_raw ], [ h_tt_isr ], [ h_tt_top ]],
#                texX = "M_{T}^{ll} (GeV)"
#            ),
#    plot_directory = "/afs/hephy.at/user/d/dspitzbart/www/stopsDilepton/TTJets_shapes/",
#    logX = False, logY = True, #sorting = True, 
#    yRange = (0.03, "auto"),
#    #drawObjects = None,
#    scaling = {0:1}
#)

# standard importd
import ROOT
import os
import pickle
from  math import sqrt
# RootTools
from RootTools.core.standard import *
from Analysis.Tools.metFilters            import getFilterCut

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
#argParser.add_argument('--signal',             action='store',      default=None,            nargs='?', choices=[None, "T2tt", "DM", "T8bbllnunu", "compilation"], help="Add signal to plot")
argParser.add_argument('--small',                                   action='store_true',     help='Run only on a small subset of the data?', )
argParser.add_argument('--overwrite',                               action='store_true',     help='Overwrite?', )
argParser.add_argument('--year',               action='store', type=int,      default=2016, choices = [2016, 2017, 2018])
#argParser.add_argument('--selection',          action='store',      default='lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1')
#argParser.add_argument('--plot_directory',     action='store',      default='v0p3')
argParser.add_argument('--dpm', action='store_true', help='Use dpm?', )
args = argParser.parse_args()

# Logging
import StopsDilepton.tools.logger as logger
from StopsDilepton.tools.user import plot_directory
logger = logger.get_logger(args.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger(args.logLevel, logFile = None )

# Load from DPM?
if args.dpm:
    data_directory = "/dpm/oeaw.ac.at/home/cms/store/user/rschoefbeck/Stops2l-postprocessed/"

#Samples
from StopsDilepton.samples.nanoTuples_Run2016_17Jul2018_postProcessed import *
from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
#samples             = [ multiBoson_16]
samples             = [ TTZ_16, TTXNoZ_16, multiBoson_16, DY_HT_LO_16, Top_pow_16]
from StopsDilepton.samples.nanoTuples_Run2017_31Mar2018_postProcessed import *
from StopsDilepton.samples.nanoTuples_Fall17_postProcessed import *
#samples             = [ multiBoson_17]
from StopsDilepton.samples.nanoTuples_Run2018_PromptReco_postProcessed import *
from StopsDilepton.samples.nanoTuples_Autumn18_postProcessed import *
#samples             = [ multiBoson_18]

#vv_16 = Sample.fromFiles('vv_16', files=[ file for file in multiBoson_16.files if 'VVTo2L2Nu' in file])
#vv_17 = Sample.fromFiles('vv_17', files=[ file for file in multiBoson_17.files if 'VVTo2L2Nu' in file])
#vv_18 = Sample.fromFiles('vv_18', files=[ file for file in multiBoson_18.files if 'VVTo2L2Nu' in file])
#
#mc  = [ vv_16, vv_17, vv_18]

data_sample16 = eval('Run2016')
lumi_scale16                 = data_sample16.lumi/1000
data_sample17 = eval('Run2017')
lumi_scale17                 = data_sample17.lumi/1000
data_sample18 = eval('Run2018')
lumi_scale18                 = data_sample18.lumi/1000
data_sample = [data_sample16, data_sample17, data_sample18]
#print lumi_scale16 , lumi_scale17, lumi_scale18
samples16 = [data_sample16] + samples

#samples16 = [vv_16, data_sample16] 
#samples17 = [vv_17, data_sample17]
#samples18 = [vv_18, data_sample18] 

#logger.info( "Loaded data for year %i", args.year )
#from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain


#relIso04sm12Cut =   "&&".join(["LepGood_relIso04["+ist+"]<0.12" for ist in ('l1_index','l2_index')])

weight_string   = 'weight'
weight_string_d18   = 'weight*reweightHEM'
weight_string16 = 'weight*reweightLeptonTrackingSF*reweightBTag_SF*reweightLeptonSF*reweightDilepTrigger*reweightPU*reweightL1Prefire*%f'%lumi_scale16
weight_string17 = 'weight*reweightLeptonTrackingSF*reweightBTag_SF*reweightLeptonSF*reweightDilepTrigger*reweightPU*reweightL1Prefire*%f'%lumi_scale17
weight_string18 = 'weight*reweightLeptonTrackingSF*reweightBTag_SF*reweightLeptonSF*reweightDilepTrigger*reweightPUVUp*reweightL1Prefire*reweightHEM*%f'%lumi_scale18 #FIXME! no PUVUP
#print weight_string_d18
#print weight_string16
#print weight_string17
#print weight_string18

cuts=[
  ("no cuts",                               "no cuts",                                  "(1)"),
  ("==2 SFleptons,l1pt>25,l2pt>20",         "$n_{\\textrm{lep.}==2}$",                  "nGoodMuons+nGoodElectrons==2&&l1_pt>25&&l2_pt>20&&abs(l1_pdgId)==abs(l2_pdgId)"),
  #("only  mumu",                            "only mumu",                                "isMuMu == 1"   ),  
  ("opposite sign",                         "opposite charge",                          "isOS==1"),
  ("MT2(blbl) > 140",                       "$M_{T2}(blbl)>140$ GeV",                   "dl_mt2blbl>140"),
  #("100<MT2(blbl) < 200",                   "$M_{T2}(blbl)<200$ GeV",               "dl_mt2blbl<200"),
  ("MT2(ll) >= 100",                        "$M_{T2}(ll)>=100$ GeV",                    "dl_mt2ll>=100"),
  #("looseLeptonVeto",                       "loose lepton veto",                        "(Sum$(Electron_pt>15&&abs(Electron_eta)<2.4&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>15&&abs(Muon_eta)<2.4&&Muon_pfRelIso03_all<0.4) )==2"),
  ("oldlooseLeptonVeto",                    "old loose lepton veto",                    "(Sum$(Electron_pt>15&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>15&&Muon_pfRelIso03_all<0.4) )==2"),
  ("m(ll)>20",                              "$M(ll)>20$ GeV",                           "dl_mass>20"),
  #("|m(ll) - mZ|>15 for SF",               "$|M(ll)-M_{Z}| > 15$ GeV (SF)",            "( (isMuMu==1||isEE==1)&&abs(dl_mass-91.1876)>=15 || isEMu==1 )"),
  ("|m(ll) - mZ|<15 for SF on Z",           "$|M(ll)-M_{Z}| < 15$ GeV (SF)",            "( (isMuMu==1||isEE==1)&&abs(dl_mass-91.1876)<=15 || isEMu==1 )"),
  (">=2 jets",                              "$n_{jet}>=2$",                             "nJetGood>=2"),
  ("==0 CSVV2 b-tags",                      "CSVV2$n_{b-tag}==0$",                      "(Sum$(JetGood_pt>30&&abs(JetGood_eta)<2.4&&JetGood_btagCSVV2>0.8484)==0)"),
  #("==0 b-tags",                            "$n_{b-tag}==0$",                           "nBTag==0"),
  #("relIso <=0.12",                         "relIso <= 0.12",                           "l1_relIso03 <= 0.12 && l2_relIso03 <= 0.12"),
  ("miniIso <=0.2",                         "miniIso <= 0.2",                           "l1_miniRelIso <= 0.2 && l2_miniRelIso <= 0.2"),
  #("MET_significance >= 12",               "$E_{T}^{miss}$ significance",              "MET_significance>=12"), 
  ("MET>80",                                "$\\ETmiss>80$ GeV",                        "met_pt>80"),
  ("MET/sqrt(HT)>5",                        "$\\ETmiss/\\sqrt{H_{T}}>5$",               "met_pt/sqrt(ht)>5."),
  #("only SF",                               "SameFlavor",                               "(isEE == 1 || isMuMu == 1)"   ),
  ("only  mumu",                            "only mumu",                                "isMuMu == 1"   ),  
  ("only  EE",                              "only EE",                                  "isEE == 1"   ),  

  #("dPhiJetMET",                            "$\\phi(\\ETmiss, jets)$ veto",             "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
    ]

cuts17=[
  ("no cuts",  "no cuts",       "(1)"),
  ("==2 SF leptons,l1 pt > 30, l2pt > 20",  "$n_{\\textrm{lep.}==2}$",       "nGoodMuons+nGoodElectrons==2&&l1_pt>30&&l2_pt>20&&abs(l1_pdgId)==abs(l2_pdgId)"),
  ("opposite sign",              "opposite charge",                    "isOS==1"),
  ("looseLeptonVeto",            "loose lepton veto",                  "(Sum$(Electron_pt>15&&abs(Electron_eta)<2.4&&Electron_pfRelIso03_all<0.4) + Sum$(Muon_pt>15&&abs(Muon_eta)<2.4&&Muon_pfRelIso03_all<0.4) )==2"),
  ("m(ll)>20",                   "$M(ll)>20$ GeV",                     "dl_mass>20"),
  #("|m(ll) - mZ|>15 for SF",     "$|M(ll)-M_{Z}| > 15$ GeV (SF)",      "( (isMuMu==1||isEE==1)&&abs(dl_mass-91.1876)>=15 || isEMu==1 )"),
  ("|m(ll) - mZ|<15 for SF on Z",     "$|M(ll)-M_{Z}| < 15$ GeV (SF)",      "( (isMuMu==1||isEE==1)&&abs(dl_mass-91.1876)<=15 || isEMu==1 )"),
  (">=2 jets",                   "$n_{jet}>=2$",       "nJetGood>=2"),
  ("==0 b-tags",         "$n_{b-tag}==0$",       "nBTag==0"),
  ("MET_significance >= 12",     "$E_{T}^{miss}$ significance",        "MET_significance>=12"), 
 # ("MET>80",                     "$\\ETmiss>80$ GeV",       "met_pt>80"),
 # ("MET/sqrt(HT)>5",             "$\\ETmiss/\\sqrt{H_{T}}>5$",       "met_pt/sqrt(ht)>5."),
  #("dPhiJetMET",                 "$\\phi(\\ETmiss, jets)$ veto",       "Sum$( ( cos(met_phi-JetGood_phi)>cos(0.25) )*(Iteration$<2) )+Sum$( ( cos(met_phi-JetGood_phi)>0.8 )*(Iteration$==0) )==0"),
  #2017:
  ("badEEJetVeto",               "badEEJetVeto",                       "Sum$((2.6<abs(Jet_eta)&&abs(Jet_eta)<3&&Jet_pt>30))==0"),
  ("MT2(ll) >= 140",              "$M_{T2}(ll)>=140$ GeV",               "dl_mt2ll>=140"),
    ]
#prefix = 'small_' if args.small else ''

if args.year == 2016:
    samples = samples16
    cuts = cuts
if args.year == 2017:
    samples = samples17
    cuts = cuts17
if args.year == 2018:
    samples = samples18
    cuts = cuts
for sample in samples:
    if "Run" in sample.name:
        sample.setSelectionString([getFilterCut(isData=True, year=args.year)])
    else:
        sample.setSelectionString([getFilterCut(year=args.year)])
#samples[0].setSelectionString([getFilterCut(isData=True, year=args.year)])
if args.small:
    for sample in samples:
        #sample.reduceFiles( to = 7)
        sample.reduceFiles( factor = 40 )
eff = {}
values = {}
for i_cut, cut in enumerate(cuts):
    name, texname, sel = cut
    values[i_cut]={}
    eff[i_cut]={}
    value_mc = 0
    for i_sample, sample in enumerate(samples):
        #print sample.name
        if i_cut < 10 : continue 
       # if sample.name == 'TTZ_16':
       #     values[i_cut][i_sample] = sample.getYieldFromDraw(selectionString = "&&".join([ '('+c[2]+')' for c in cuts[:i_cut+1]]), weightString = weight_string16)['val'] 
       # if sample.name == 'TTXNoZ_16':
       #     values[i_cut][i_sample] = sample.getYieldFromDraw(selectionString = "&&".join([ '('+c[2]+')' for c in cuts[:i_cut+1]]), weightString = weight_string16)['val'] 
        if sample.name == 'Run2016':
            values[i_cut][i_sample] = sample.getYieldFromDraw(selectionString = "&&".join([ '('+c[2]+')' for c in cuts[:i_cut+1]]), weightString = weight_string)['val']
            selection = "&&".join([ '('+c[2]+')' for c in cuts[:i_cut+1]])    
            print selection
            #print "reweight 16 data sample", weight_string
        else:
            values[i_cut][i_sample] = sample.getYieldFromDraw(selectionString = "&&".join([ '('+c[2]+')' for c in cuts[:i_cut+1]]), weightString = weight_string16)['val'] 
            #value_mc += values[i_cut][i_sample] 
            #print i_sample, sample.name, values[i_cut][i_sample]
            selection = "&&".join([ '('+c[2]+')' for c in cuts[:i_cut+1]])    
            print selection
    if i_cut >= 10:
        #logger.info( "%30s Data%i %6.2f  MC%i %6.2f ", cut[0],args.year, values[i_cut][0], args.year, value_mc ) 
   #    #logger.debug("I had a problem here: %s", "&&".join([ '('+c[2]+')' for c in cuts[:i_cut+1]]) )
   # else:
   #     logger.info( "%30s 2016 %6.2f 2017 %6.2f 2018 %6.2f ", cut[0], values[i_cut][0], values[i_cut][1], values[i_cut][2] )
    
        logger.info( "%20s Data%i %6.2f TTZ  %6.2f TTXNoZ %6.2f multiBoson %6.2f DY %6.2f Top_pow %6.2f", cut[0],args.year, values[i_cut][0], values[i_cut][1], values[i_cut][2], values[i_cut][3],values[i_cut][4], values[i_cut][5])
   # if i_cut>=5:
   #     logger.info("%30s Data efficiency %6.2f DY efficiency %6.2f multiBoson eff %6.2f", cut[0], eff[i_cut][0], eff[i_cut][4], eff[i_cut][3])


#values17 = {}
#for i_cut17, cut17 in enumerate(cuts17):
#    name, texname, sel = cut17
#    values17[i_cut17]={}
#    for i_sample, sample in enumerate(samples17):
#        #print sample.name
#        #if i_cut == 10 :
#        if sample.name == 'vv_17':
#            values17[i_cut17][i_sample] = sample.getYieldFromDraw(selectionString = "&&".join([ '('+c[2]+')' for c in cuts17[:i_cut17+1]]), weightString = weight_string17)['val'] 
#            print "reweight vv_17", weight_string17
#        elif sample.name == 'Run2017':
#            values17[i_cut17][i_sample] = sample.getYieldFromDraw(selectionString = "&&".join([ '('+c[2]+')' for c in cuts17[:i_cut17+1]]), weightString = weight_string)['val']
#            print "reweight 17 data sample", weight_string
   # if i_cut == 11:
   #     logger.info( "%30s 2016 %6.2f 2017 %6.2f 2018 %6.2f data16 %6.2f data17 %6.2f data18 %6.2f", cut[0], values[i_cut][0], values[i_cut][1], values[i_cut][2],values[i_cut][3],values[i_cut][4],values[i_cut][5] ) 
   #    #logger.debug("I had a problem here: %s", "&&".join([ '('+c[2]+')' for c in cuts[:i_cut+1]]) )
   # else:
   #     logger.info( "%30s 2016 %6.2f 2017 %6.2f 2018 %6.2f ", cut[0], values[i_cut][0], values[i_cut][1], values[i_cut][2] )
#    logger.info( "%30s 2017 %6.2f data17 ", cut17[0], values17[i_cut17][0], values17[i_cut17][1] )

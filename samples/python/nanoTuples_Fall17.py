import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT

# Logging
import logging
logger = logging.getLogger(__name__)

## these should go somewhere else
dbFile = '/afs/hephy.at/data/dspitzbart01/nanoAOD/DB_Fall17.sql'

# specify a local directory if you want to create (and afterwards automatically use) a local copy of the sample, otherwise use the grid.

## DY
#DYJetsToLL_M50_LO       = Sample.nanoAODfromDAS('DYJetsToLL_M50_LO', '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM', dbFile=dbFile, xSection=2008.*3)
DYJetsToLL_M50_LO_ext1  = Sample.nanoAODfromDAS('DYJetsToLL_M50_LO_ext1', '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM', dbFile=dbFile, xSection=2008.*3)
DYJetsToLL_M50          = Sample.nanoAODfromDAS('DYJetsToLL_M50', '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM', dbFile=dbFile, xSection=2008.*3)
DYJetsToLL_M50_ext1     = Sample.nanoAODfromDAS('DYJetsToLL_M50_ext1', '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM', dbFile=dbFile, xSection=2008.*3)

#DYJetsToLL_M10to50      = Sample.nanoAODfromDAS("DYJetsToLL_M10to50", "/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=18610)


#DYJetsToLL_M50_HT70to100      =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT70to100"    ,     "/DYJetsToLL_M-50_HT-70to100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",         dbFile=dbFile, xSection=170.4*1.23)
DYJetsToLL_M50_HT100to200     =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT100to200",        "/DYJetsToLL_M-50_HT-100to200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM",        dbFile=dbFile, xSection=147.4*1.23)
DYJetsToLL_M50_HT100to200_ext =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT100to200_ext",    "/DYJetsToLL_M-50_HT-100to200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM",   dbFile=dbFile, xSection=147.4*1.23)
DYJetsToLL_M50_HT200to400     =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT200to400",        "/DYJetsToLL_M-50_HT-200to400_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM",        dbFile=dbFile, xSection=40.99*1.23)
DYJetsToLL_M50_HT200to400_ext =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT200to400_ext",    "/DYJetsToLL_M-50_HT-200to400_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM",   dbFile=dbFile, xSection=40.99*1.23)
DYJetsToLL_M50_HT400to600     =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT400to600",        "/DYJetsToLL_M-50_HT-400to600_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM",        dbFile=dbFile, xSection=5.678*1.23)
DYJetsToLL_M50_HT400to600_ext =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT400to600_ext",    "/DYJetsToLL_M-50_HT-400to600_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM",   dbFile=dbFile, xSection=5.678*1.23)
DYJetsToLL_M50_HT600to800     =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT600to800"   ,     '/DYJetsToLL_M-50_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM',        dbFile=dbFile, xSection=1.367*1.23 )
DYJetsToLL_M50_HT800to1200    =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT800to1200"  ,     '/DYJetsToLL_M-50_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM',       dbFile=dbFile, xSection=0.6304*1.23 )
DYJetsToLL_M50_HT1200to2500   =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT1200to2500" ,     '/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM',      dbFile=dbFile, xSection=0.1514*1.23 )
DYJetsToLL_M50_HT2500toInf    =   Sample.nanoAODfromDAS("DYJetsToLL_M50_HT2500toInf"  ,     '/DYJetsToLL_M-50_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM',       dbFile=dbFile, xSection=0.003565*1.23 )

DYJetsM50HT = [
#DYJetsToLL_M50_HT70to100   , 
DYJetsToLL_M50_HT100to200,
DYJetsToLL_M50_HT100to200_ext,
DYJetsToLL_M50_HT200to400,
DYJetsToLL_M50_HT200to400_ext,
DYJetsToLL_M50_HT400to600,
DYJetsToLL_M50_HT400to600_ext,
DYJetsToLL_M50_HT600to800  ,
DYJetsToLL_M50_HT800to1200 ,
DYJetsToLL_M50_HT1200to2500,
DYJetsToLL_M50_HT2500toInf ,
]

DYJetsToLL_M4to50_HT70to100      = Sample.nanoAODfromDAS("DYJetsToLL_M4to50_HT70to100"     , "/DYJetsToLL_M-4to50_HT-70to100_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=303.4) #LO without 1.23 k-factor
DYJetsToLL_M4to50_HT100to200     = Sample.nanoAODfromDAS("DYJetsToLL_M4to50_HT100to200"    , "/DYJetsToLL_M-4to50_HT-100to200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=224.2) #LO without 1.23 k-factor
DYJetsToLL_M4to50_HT100to200_ext = Sample.nanoAODfromDAS("DYJetsToLL_M4to50_HT100to200_ext", "/DYJetsToLL_M-4to50_HT-100to200_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=224.2) #LO without 1.23 k-factor
DYJetsToLL_M4to50_HT200to400     = Sample.nanoAODfromDAS("DYJetsToLL_M4to50_HT200to400"    , "/DYJetsToLL_M-4to50_HT-200to400_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=37.2) #LO without 1.23 k-factor
DYJetsToLL_M4to50_HT400to600     = Sample.nanoAODfromDAS("DYJetsToLL_M4to50_HT400to600"    , "/DYJetsToLL_M-4to50_HT-400to600_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=3.581) #LO without 1.23 k-factor
DYJetsToLL_M4to50_HT600toInf     = Sample.nanoAODfromDAS("DYJetsToLL_M4to50_HT600toInf"    , "/DYJetsToLL_M-4to50_HT-600toInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=1.124) #LO without 1.23 k-factor

DYJetsM5to50HT = [
DYJetsToLL_M4to50_HT70to100,
DYJetsToLL_M4to50_HT100to200,
DYJetsToLL_M4to50_HT100to200_ext,
DYJetsToLL_M4to50_HT200to400,
DYJetsToLL_M4to50_HT200to400,
DYJetsToLL_M4to50_HT400to600,
DYJetsToLL_M4to50_HT600toInf,
]


DY = [
#    DYJetsToLL_M50_LO,
    DYJetsToLL_M50_LO_ext1,
#    DYJetsToLL_M10to50,
    DYJetsToLL_M50,
    DYJetsToLL_M50_ext1,
    ] + DYJetsM50HT + DYJetsM5to50HT

## ttbar
TTLep_pow       = Sample.nanoAODfromDAS("TTLep_pow", "/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=831.76*((3*0.108)**2) )

## single top
TToLeptons_sch_amcatnlo = Sample.nanoAODfromDAS("TToLeptons_sch_amcatnlo", "/ST_s-channel_4f_leptonDecays_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=(7.20+4.16)*0.108*3)

T_tch_powheg            = Sample.nanoAODfromDAS("T_tch_powheg", "/ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=136.02) # inclusive sample
TBar_tch_powheg         = Sample.nanoAODfromDAS("TBar_tch_powheg", "/ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=80.95) # inclusive sample

T_tWch_ext              = Sample.nanoAODfromDAS("T_tWch_ext", "/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=35.6)
TBar_tWch_ext           = Sample.nanoAODfromDAS("TBar_tWch_ext", "/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=35.6)

## ttH
#TTHbb                   = Sample.nanoAODfromDAS("TTHbb",                  "/ttHJetTobb_M125_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2_ext3-v1/NANOAODSIM", dbFile=dbFile, xSection=0.5085*(0.577))
TTHnobb_pow             = Sample.nanoAODfromDAS("TTHnobb_pow",            "/ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=0.5085*(1-0.577))
TTHnobb_mWCutfix_ext    = Sample.nanoAODfromDAS("TTHnobb_mWCutfix_ext",   "/ttHJetToNonbb_M125_TuneCP5_13TeV_amcatnloFXFX_madspin_pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=0.5085*(1-0.577))

#THQ = Sample.nanoAODfromDAS("THQ", "/THQ_Hincl_13TeV-madgraph-pythia8_TuneCUETP8M1/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",  dbFile=dbFile, xSection=0.07096)
#THW = Sample.nanoAODfromDAS("THW", "/THW_Hincl_13TeV-madgraph-pythia8_TuneCUETP8M1/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=0.1472)

## ttV
#TGJets              = Sample.nanoAODfromDAS("TGJets",     "/TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=2.967)
#TGJets_ext          = Sample.nanoAODfromDAS("TGJets_ext", "/TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=2.967)
tZq_ll_ext          = Sample.nanoAODfromDAS("tZq_ll_ext", "/tZq_ll_4f_ckm_NLO_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=0.09418 ) #0.0758 )
#tWll                = Sample.nanoAODfromDAS("tWll",       "/ST_tWll_5f_LO_13TeV-MadGraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=0.01123)
#tWnunu              = Sample.nanoAODfromDAS("tWnunu",     "/ST_tWnunu_5f_LO_13TeV-MadGraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=0.01123*1.9822 )

TTWToLNu            = Sample.nanoAODfromDAS("TTWToLNu", "/TTWJetsToLNu_TuneCP5_PSweights_13TeV-amcatnloFXFX-madspin-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=0.2043)
#TTWToQQ             = Sample.nanoAODfromDAS("TTWToQQ", "/TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=0.40620)
#TTW_LO              = Sample.nanoAODfromDAS("TTW_LO", "",  dbFile=dbFile, xSection=0.6105 )
#TTZToQQ             = Sample.nanoAODfromDAS("TTZToQQ","/TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=0.5297)
TTZToLLNuNu         = Sample.nanoAODfromDAS("TTZToLLNuNu", "/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=0.2728)
TTZToLLNuNu_m1to10  = Sample.nanoAODfromDAS("TTZToLLNuNu_m1to10", "/TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=0.0493)
#TTZ_LO              = Sample.nanoAODfromDAS("TTZ_LO", "/ttZJets_13TeV_madgraphMLM/RunIISummer16MiniAODv2-80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM", dbFile=dbFile, xSection=0.5297/0.692)
TTGJets             = Sample.nanoAODfromDAS("TTGJets",    "/TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=3.697)
TTGJets_ext         = Sample.nanoAODfromDAS("TTGJets_ext","/TTGJets_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=3.697)

TTV = [
#    TGJets,
#    TGJets_ext,
    tZq_ll_ext,
#    tWll,
#    tWnunu,
    TTWToLNu,
#    TTWToQQ,
#    TTW_LO,
#    TTZToQQ,
    TTZToLLNuNu,
    TTZToLLNuNu_m1to10,
#    TTZ_LO,
    TTGJets,
    TTGJets_ext
]

top = [
    TTLep_pow,
    TToLeptons_sch_amcatnlo,
    T_tch_powheg,
    TBar_tch_powheg,
    T_tWch_ext,
    TBar_tWch_ext,
#    TTHbb,
    TTHnobb_pow,
    TTHnobb_mWCutfix_ext,
#    THQ,
#    THW,
    ] + TTV

## di/multiboson
#WWTo2L2Nu       = Sample.nanoAODfromDAS("WWTo2L2Nu", "/WWTo2L2Nu_13TeV-powheg/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=10.481 )
WWToLNuQQ       = Sample.nanoAODfromDAS("WWToLNuQQ", "/WWToLNuQQ_NNPDF31_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=43.53 )
WWToLNuQQ_ext   = Sample.nanoAODfromDAS("WWToLNuQQ_ext", "/WWToLNuQQ_NNPDF31_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=43.53 )
#WWTo1L1Nu2Q     = Sample.nanoAODfromDAS("WWTo1L1Nu2Q", "/WWTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v2/NANOAODSIM", dbFile=dbFile, xSection=49.997 )

#ZZTo2L2Nu       = Sample.nanoAODfromDAS("ZZTo2L2Nu", "/ZZTo2L2Nu_13TeV_powheg_pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=0.564)
#ZZTo2L2Q        = Sample.nanoAODfromDAS("ZZTo2L2Q", "/ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",  dbFile=dbFile, xSection=3.28)
#ZZTo2Q2Nu       = Sample.nanoAODfromDAS("ZZTo2Q2Nu", "/ZZTo2Q2Nu_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",  dbFile=dbFile, xSection=4.04)
ZZTo4L          = Sample.nanoAODfromDAS("ZZTo4L", "/ZZTo4L_13TeV_powheg_pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=1.256*1.1)

#WZJToLLLNu      = Sample.nanoAODfromDAS("WZJToLLLNu"  , "/WZJToLLLNu_TuneCUETP8M1_13TeV-amcnlo-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM"  , "CMS", ".*root", 4.708 )
#WZTo1L3Nu       = Sample.nanoAODfromDAS("WZTo1L3Nu"  , "/WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM"  , "CMS", ".*root", (47.13)*(3*0.108)*(0.2) )
WZTo1L1Nu2Q     = Sample.nanoAODfromDAS("WZTo1L1Nu2Q", "/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/NANOAODSIM",  dbFile=dbFile, xSection=10.71)
#WZTo2L2Q        = Sample.nanoAODfromDAS("WZTo2L2Q"   , "/WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",  dbFile=dbFile, xSection=5.60)
#WZTo3LNu        = Sample.nanoAODfromDAS("WZTo3LNu"   , "/WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=4.42965)
#WZTo3LNu_mllmin01=Sample.nanoAODfromDAS("WZTo3LNu_mllmin01", "/WZTo3LNu_mllmin01_13TeV-powheg-pythia8_ext1/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=58.59)
WZTo3LNu_amcatnlo=Sample.nanoAODfromDAS("WZTo3LNu_amcatnlo", "/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=4.666)

#VVTo2L2Nu       = Sample.nanoAODfromDAS("VVTo2L2Nu","/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",  dbFile=dbFile, xSection=11.95)
#VVTo2L2Nu_ext   = Sample.nanoAODfromDAS("VVTo2L2Nu_ext" ,"/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2_ext1-v1/NANOAODSIM",  dbFile=dbFile, xSection=11.95)

#WGToLNuG                = Sample.nanoAODfromDAS("WGToLNuG", "/WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=585.8)
#WGToLNuG_amcatnlo_ext1  = Sample.nanoAODfromDAS("WGToLNuG_amcatnlo_ext1", "/WGToLNuG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=585.8) # cross section copied from MLM sample above, to be checked
#WGToLNuG_amcatnlo_ext3  = Sample.nanoAODfromDAS("WGToLNuG_amcatnlo_ext3", "/WGToLNuG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2_ext3-v1/NANOAODSIM", dbFile=dbFile, xSection=585.8) # cross section copied from MLM sample above, to be checked

#WGJets              = Sample.nanoAODfromDAS("WGJets", "/WGJets_MonoPhoton_PtG-130_TuneCUETP8M1_13TeV-madgraph/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=0.6637)
#ZNuNuGJets              = Sample.nanoAODfromDAS("ZNuNuGJets", "/ZNuNuGJets_MonoPhoton_PtG-130_TuneCUETP8M1_13TeV-madgraph/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM", "CMS", ".*root", 0.1903)
#ZNuNuGJets_40130    = Sample.nanoAODfromDAS("ZNuNuGJets_40130", "/ZNuNuGJets_MonoPhoton_PtG-40to130_TuneCUETP8M1_13TeV-madgraph/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=2.816)

#ZGTo2NuG            = Sample.nanoAODfromDAS("ZGTo2NuG","/ZGTo2NuG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=28.05)
#ZGTo2LG_ext         = Sample.nanoAODfromDAS("ZGTo2LG_ext", "/ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=131.3)

#WWDoubleTo2L    = Sample.nanoAODfromDAS("WWDoubleTo2L", "/WWTo2L2Nu_DoubleScattering_13TeV-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=0.1729)
#WpWpJJ          = Sample.nanoAODfromDAS("WpWpJJ", "/WpWpJJ_EWK-QCD_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=0.03711)


WW      = Sample.nanoAODfromDAS("WW", "/WW_TuneCP5_13TeV-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=63.21 * 1.82)
WZ      = Sample.nanoAODfromDAS("WZ", "/WZ_TuneCP5_13TeV-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=47.13)
ZZ      = Sample.nanoAODfromDAS("ZZ", "/ZZ_TuneCP5_13TeV-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=16.523)


boson = [
#    WWTo2L2Nu,
    WWToLNuQQ,
    WWToLNuQQ_ext,
#    WWTo1L1Nu2Q,
#    ZZTo2L2Nu,
#    ZZTo2L2Q,
#    ZZTo2Q2Nu,
    ZZTo4L,
    WZTo1L1Nu2Q,
#    WZTo2L2Q,
#    WZTo3LNu,
#    WZTo3LNu_mllmin01,
    WZTo3LNu_amcatnlo,
#    VVTo2L2Nu,
#    VVTo2L2Nu_ext,
#    WGToLNuG,
#    WGToLNuG_amcatnlo_ext1,
#    WGToLNuG_amcatnlo_ext3,
#    WGJets,
#    ZNuNuGJets_40130,
#    ZGTo2NuG,
#    ZGTo2LG_ext,
#    WWDoubleTo2L,
#    WpWpJJ,
    WW,
    WZ,
    ZZ,
    ]

## W+jets
#WJetsToLNu      = Sample.nanoAODfromDAS("WJetsToLNu", "/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM", dbFile=dbFile, xSection=3* 20508.9)
#WJetsToLNu_ext  = Sample.nanoAODfromDAS("WJetsToLNu_ext", "/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2_ext2-v1/NANOAODSIM", dbFile=dbFile, xSection=3* 20508.9)

wjets = [
#    WJetsToLNu,
#    WJetsToLNu_ext,
    ]

## rare
TTTT = Sample.nanoAODfromDAS("TTTT", "/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/RunIIFall17NanoAOD-PU2017_pilot_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=0.009103)
TTWW = Sample.nanoAODfromDAS("TTWW", "/TTWW_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM", dbFile=dbFile, xSection=0.007829)
#TTWZ = Sample.nanoAODfromDAS("TTWZ", "", "CMS", ".*root", 0.002919)
#TTZZ = Sample.nanoAODfromDAS("TTZZ", "", "CMS", ".*root", 0.001573)

rare = [
    TTTT,
    TTWW,
    ]


## Signals
#T2tt_mStop_1200_mLSP_100 = Sample.nanoAODfromDAS("T2tt_mStop_1200_mLSP_100", "/SMS-T2tt_mStop-1200_mLSP-100_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=1)
#T2tt_mStop_850_mLSP_100 = Sample.nanoAODfromDAS("T2tt_mStop_850_mLSP_100", "/SMS-T2tt_mStop-850_mLSP-100_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=1)
#T2tt_mStop_650_mLSP_350 = Sample.nanoAODfromDAS("T2tt_mStop_650_mLSP_350", "/SMS-T2tt_mStop-650_mLSP-350_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM", dbFile=dbFile, xSection=1)


other = [
    ]

allSamples = DY + top + boson + wjets + rare + other

allSamples = [ x for x in allSamples if x.normalization > 0 ]

for s in allSamples:
    s.isData = False


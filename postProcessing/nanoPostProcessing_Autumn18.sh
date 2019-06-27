#### DY
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --reduceSizeBy 2 --sample DYJetsToLL_M50_LO #SPLIT40
###python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50 #SPLIT40
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --reduceSizeBy 2 --sample DYJetsToLL_M10to50_LO #SPLIT40
#
# full stats
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50_LO #SPLIT40
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M10to50_LO #SPLIT40

# HT binned samples ##
# high mass #
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --LHEHTCut 70 --sample DYJetsToLL_M50_LO #SPLIT40
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50_HT70to100 #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50_HT100to200 #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50_HT200to400 #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50_HT400to600 DYJetsToLL_M50_HT400to600_ext #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50_HT600to800 #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50_HT800to1200 #SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50_HT1200to2500 #SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M50_HT2500toInf #SPLIT10
# low mass #
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --LHEHTCut 70 --sample DYJetsToLL_M10to50_LO #SPLIT40
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT70to100 #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT100to200 #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT200to400 #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT400to600 #SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT600toInf #SPLIT10
#
#
# top
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --reduceSizeBy 3 --sample TTLep_pow #SPLIT80
python nanoPostProcessing.py  --overwrite --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --flagTTBar --sample TTLep_pow #SPLIT80
python nanoPostProcessing.py  --overwrite --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --flagTTBar --sample TTSingleLep_pow #SPLIT80
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --flagTTGamma --sample TTGLep #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --reduceSizeBy 5 --sample TToLeptons_sch_amcatnlo #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample T_tWch #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TBar_tWch #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --reduceSizeBy 15 --sample T_tch_pow #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --reduceSizeBy 15 --sample TBar_tch_pow #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample tZq_ll #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample tWll #SPLIT11
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTWToLNu #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTWToQQ #SPLIT14
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTW_LO #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTZToLLNuNu #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTZToLLNuNu_m1to10 #SPLIT10
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTZ_LO #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTHbbLep #SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTHnobb_pow #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample THQ #SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample THW #SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTTT #SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample tWnunu #SPLIT5

#
#
## di/multi boson
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample VVTo2L2Nu #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample WZTo3LNu_amcatnlo #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample WZTo2L2Q #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample WZTo1L3Nu #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample WWTo1L1Nu2Q #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample WWToLNuQQ #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample ZZTo4L #SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample ZZTo2Q2Nu #SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --reduceSizeBy 5 --sample ZZTo2L2Q #SPLIT20
#
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample WW #SPLIT5
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample ZZ #SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample WWW_4F #SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample WWZ #SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample WZZ #SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample ZZZ #SPLIT5
#
## rare
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTWZ #SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTWW #SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p15  --skipGenLepMatching --sample TTZZ #SPLIT5

#python nanoPostProcessing.py  --forceProxy --skim dilep  --year 2018 --processingEra stops_2018_nano_v0p13 --overwrite  --skipGenLepMatching --susySignal --fastSim --sample SMS_T2tt_mStop_150to250 #SPLIT45
#python nanoPostProcessing.py  --forceProxy --skim dilep  --year 2018 --processingEra stops_2018_nano_v0p13 --overwrite  --skipGenLepMatching --susySignal --fastSim --sample SMS_T2tt_mStop_250to350 #SPLIT45
#python nanoPostProcessing.py  --forceProxy --skim dilep  --year 2018 --processingEra stops_2018_nano_v0p13 --overwrite  --skipGenLepMatching --susySignal --fastSim --sample SMS_T2tt_mStop_350to400 #SPLIT45
#python nanoPostProcessing.py  --forceProxy --skim dilep  --year 2018 --processingEra stops_2018_nano_v0p13 --overwrite  --skipGenLepMatching --susySignal --fastSim --sample SMS_T2tt_mStop_400to1200 #SPLIT45

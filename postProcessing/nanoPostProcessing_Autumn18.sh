### DY
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --reduceSizeBy 2 --sample DYJetsToLL_M50_LO # SPLIT40
###python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50 # SPLIT40
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --reduceSizeBy 2 --sample DYJetsToLL_M10to50_LO # SPLIT40
#
# full stats
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50_LO # SPLIT40
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M10to50_LO # SPLIT40

# HT binned samples ##
# high mass #
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --LHEHTCut 70 --sample DYJetsToLL_M50_LO # SPLIT40
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50_HT70to100 # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50_HT100to200 # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50_HT200to400 # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50_HT400to600 DYJetsToLL_M50_HT400to600_ext # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50_HT600to800 # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50_HT800to1200 # SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50_HT1200to2500 # SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M50_HT2500toInf # SPLIT10
# low mass #
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --LHEHTCut 70 --sample DYJetsToLL_M10to50_LO # SPLIT40
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT70to100 # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT100to200 # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT200to400 # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT400to600 # SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample DYJetsToLL_M4to50_HT600toInf # SPLIT10
#
#
# top
#python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --reduceSizeBy 3 --noTopPtReweighting --sample TTLep_pow # SPLIT80
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --noTopPtReweighting --flagTTBar --sample TTLep_pow # SPLIT80
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --noTopPtReweighting --flagTTBar --sample TTSingleLep_pow #SPLIT80
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --flagTTGamma --sample TTGLep # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --reduceSizeBy 5 --sample TToLeptons_sch_amcatnlo # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample T_tWch # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TBar_tWch # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --reduceSizeBy 15 --sample T_tch_pow # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --reduceSizeBy 15 --sample TBar_tch_pow # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample tZq_ll # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample tWll # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTWToLNu # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTWToQQ # SPLIT20
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTW_LO # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTZToLLNuNu # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTZToLLNuNu_m1to10 # SPLIT20
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTZ_LO # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTHbbLep # SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTHnobb_pow # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample THQ # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample THW # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTTT # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample tWnunu # SPLIT5

#
#
## di/multi boson
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11_fix  --skipGenLepMatching --sample VVTo2L2Nu # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample WZTo3LNu_amcatnlo # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample WZTo2L2Q # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample WZTo1L3Nu # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample WWTo1L1Nu2Q # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample WWToLNuQQ # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample ZZTo4L # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample ZZTo2Q2Nu # SPLIT10
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --reduceSizeBy 5 --sample ZZTo2L2Q # SPLIT20
#
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample WW # SPLIT5
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample ZZ # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample WWZ # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample WZZ # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample ZZZ # SPLIT5
#
## rare
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTWZ # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTWW # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p11  --skipGenLepMatching --sample TTZZ # SPLIT5


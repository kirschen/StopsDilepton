# DY
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --reduceSizeBy 2 --sample DYJetsToLL_M50_LO # SPLIT40
#python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample DYJetsToLL_M50 # SPLIT40
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --reduceSizeBy 2 --sample DYJetsToLL_M10to50_LO # SPLIT40

# top
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --reduceSizeBy 3 --noTopPtReweighting --sample TTLep_pow # SPLIT80
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --reduceSizeBy 5 --sample TToLeptons_sch_amcatnlo # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample T_tWch # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample TBar_tWch # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --reduceSizeBy 15 --sample T_tch_pow # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --reduceSizeBy 15 --sample TBar_tch_pow # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample tZq_ll # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample tWll # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample TTWToLNu # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample TTWToQQ # SPLIT20
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample TTW_LO # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample TTZToLLNuNu # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample TTZToLLNuNu_m1to10 # SPLIT20
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample TTZ_LO # SPLIT20
#
#
## di/multi boson
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample VVTo2L2Nu # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample WZTo3LNu_amcatnlo # SPLIT20
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample ZZTo4L # SPLIT20
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --reduceSizeBy 5 --sample ZZTo2L2Q # SPLIT20
#
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample WW # SPLIT5
##python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample ZZ # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample WWZ # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample WZZ # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample ZZZ # SPLIT5
#
## rare
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample TTWZ # SPLIT5
python nanoPostProcessing.py  --forceProxy --skim dilep --year 2018 --processingEra stops_2018_nano_v0p3  --skipGenLepMatching --sample TTZZ # SPLIT5

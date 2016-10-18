#!/bin/sh

# TTbarDM
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_10 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10 --overwrite $1 $2 --mode=doubleMu --zMode=offZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_10"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_20 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20 --overwrite $1 $2 --mode=doubleMu --zMode=offZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_20"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_50 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50 --overwrite $1 $2 --mode=doubleMu --zMode=offZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_50"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_10 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10 --overwrite $1 $2 --mode=doubleEle --zMode=offZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_10"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_20 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20 --overwrite $1 $2 --mode=doubleEle --zMode=offZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_20"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_50 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50 --overwrite $1 $2 --mode=doubleEle --zMode=offZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_50"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_10 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10 --overwrite $1 $2 --mode=muEle --zMode=allZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_10"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_20 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20 --overwrite $1 $2 --mode=muEle --zMode=allZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_20"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_50 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50 --overwrite $1 $2 --mode=muEle --zMode=allZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_50"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_10 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10 --overwrite $1 $2 --mode=sameFlavour --zMode=offZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_10"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_20 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20 --overwrite $1 $2 --mode=sameFlavour --zMode=offZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_20"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_50 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50 --overwrite $1 $2 --mode=sameFlavour --zMode=offZ  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_50"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_10 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_10 --overwrite $1 $2 --mode=dilepton  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_10"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_20 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_20 --overwrite $1 $2 --mode=dilepton  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_20"
./submit.sh "python simple1DPlots.py --signals TTbarDMJets_scalar_Mchi_1_Mphi_50 TTbarDMJets_pseudoscalar_Mchi_1_Mphi_50 --overwrite $1 $2 --mode=dilepton  --plot_directory=80X_v12_TTDM/Mchi_1_Mphi_50"

##mIsoWP
#python simple1DPlots.py  --noLoop --overwrite --mIsoWP 0 &
#python simple1DPlots.py  --noLoop --overwrite --mIsoWP 1 &
#python simple1DPlots.py  --noLoop --overwrite --mIsoWP 2 &
#python simple1DPlots.py  --noLoop --overwrite --mIsoWP 3 &
#python simple1DPlots.py  --noLoop --overwrite --mIsoWP 4 &
#python simple1DPlots.py  --noLoop --overwrite --mIsoWP 5 &
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --mIsoWP 0"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --mIsoWP 1"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --mIsoWP 2"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --mIsoWP 3"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --mIsoWP 4"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --mIsoWP 5"

#Isabell
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=def --mode=doubleMu --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=none --mode=doubleMu --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=lead --mode=doubleMu --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=inv --mode=doubleMu --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=def --mode=doubleEle --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=none --mode=doubleEle --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=lead --mode=doubleEle --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=inv --mode=doubleEle --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=def --mode=muEle --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=none --mode=muEle --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=lead --mode=muEle --zMode=onZ"
#./submit.sh "python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=inv --mode=muEle --zMode=onZ"

#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=def --mode=doubleMu --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=none --mode=doubleMu --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=lead --mode=doubleMu --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=inv --mode=doubleMu --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=def --mode=doubleEle --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=none --mode=doubleEle --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=lead --mode=doubleEle --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=inv --mode=doubleEle --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=def --mode=muEle --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=none --mode=muEle --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=lead --mode=muEle --zMode=onZ &
#python simple1DPlots.py  --noLoop --overwrite --nbtag=0 --dPhi=inv --mode=muEle --zMode=onZ &

#diboson CR
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ  --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 2p --nbtag 0 --dPhi=none"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ  --njet 2p --nbtag 0 --dPhi=none"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 2p --nbtag 0 --dPhi=none"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 2p --nbtag 0 --dPhi=inv"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ  --njet 2p --nbtag 0 --dPhi=inv"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 2p --nbtag 0 --dPhi=inv"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ  --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 1p --nbtag 0 --dPhi=none"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ  --njet 1p --nbtag 0 --dPhi=none"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 1p --nbtag 0 --dPhi=none"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 1p --nbtag 0 --dPhi=inv"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ  --njet 1p --nbtag 0 --dPhi=inv"
#./submit.sh "python simple1DPlots.py  --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 1p --nbtag 0 --dPhi=inv"

#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 01 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 01 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 01 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 2p --nbtag 0"
#
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 01 --nbtag 1p"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=dilepton --njet 01 --nbtag 1p"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 01 --nbtag 1p"
#
#./submit.sh "python simple1DPlots.py $1 --noLoop --mode=dilepton --njet 2p --nbtag 1p"
#./submit.sh "python simple1DPlots.py $1 --noLoop --mode=dilepton --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --mode=dilepton --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --mode=dilepton --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --mode=dilepton --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --mode=dilepton --njet 1 --nbtag 0"
#
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 01 --nbtag 0 --highMT2ll"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 01 --nbtag 0 --highMT2ll"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 2p --nbtag 0 --highMT2ll"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 2p --nbtag 0 --highMT2ll"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 01 --nbtag 1p --highMT2ll"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=dilepton --njet 01 --nbtag 1p --highMT2ll"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 01 --nbtag 1p --highMT2ll"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 01 --nbtag 0 --highMT2ll"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 2p --nbtag 0 --highMT2ll"
#
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=offZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=offZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=offZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=offZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=offZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=onZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=onZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=onZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=onZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=onZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=allZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=allZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=allZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=allZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleMu --zMode=allZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=offZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=offZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=offZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=offZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=offZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=onZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=onZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=onZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=onZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=onZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=allZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=allZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=allZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=allZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=doubleEle --zMode=allZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=offZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=offZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=offZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=offZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=offZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=onZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=onZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=onZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=onZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=onZ --njet 1 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 2p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 1p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 0p --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet 0 --nbtag 0"
#./submit.sh "python simple1DPlots.py $1 --noLoop --splitDiBoson --mode=muEle --zMode=allZ --njet  --nbtag 0"

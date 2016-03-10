#!/bin/sh
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M10to50" &
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M5to50_LO" &
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M5to50_LO --lheHTCut=100" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M50" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M50_LO" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M50_LO --lheHTCut=100" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M50_HT100to200" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M50_HT200to400" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M50_HT400to600" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M50_HT600toInf" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M5to50_HT100to200" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M5to50_HT200to400" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M5to50_HT400to600" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples DYJetsToLL_M5to50_HT600toInf" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples WJetsToLNu_HT100to200 WJetsToLNu_HT100to200_ext" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples WJetsToLNu_HT200to400 WJetsToLNu_HT200to400_ext" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples WJetsToLNu_HT400to600" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples WJetsToLNu_HT600toInf" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples WJetsToLNu_HT600to800" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples WJetsToLNu_HT800to1200" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples WJetsToLNu_HT1200to2500" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples WJetsToLNu_HT2500toInf" &

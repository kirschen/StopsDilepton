#!/bin/sh

python cmgPostProcessing.py --skim=$1 $2 --samples WW
python cmgPostProcessing.py --skim=$1 $2 --samples WZ
python cmgPostProcessing.py --skim=$1 $2 --samples ZZ
python cmgPostProcessing.py --skim=$1 $2 --samples WWTo2L2Nu
python cmgPostProcessing.py --skim=$1 $2 --samples WWToLNuQQ
python cmgPostProcessing.py --skim=$1 $2 --samples WWTo1L1Nu2Q
python cmgPostProcessing.py --skim=$1 $2 --samples ZZTo2L2Q
python cmgPostProcessing.py --skim=$1 $2 --samples ZZTo2Q2Nu
python cmgPostProcessing.py --skim=$1 $2 --samples ZZTo4L
python cmgPostProcessing.py --skim=$1 $2 --samples WZTo1L1Nu2Q
python cmgPostProcessing.py --skim=$1 $2 --samples WZTo2L2Q
python cmgPostProcessing.py --skim=$1 $2 --samples WZTo3LNu
python cmgPostProcessing.py --skim=$1 $2 --samples WZTo1L3Nu
python cmgPostProcessing.py --skim=$1 $2 --samples WZJets
python cmgPostProcessing.py --skim=$1 $2 --samples VVTo2L2Nu
python cmgPostProcessing.py --skim=$1 $2 --samples WGToLNuG
python cmgPostProcessing.py --skim=$1 $2 --samples ZGTo2LG

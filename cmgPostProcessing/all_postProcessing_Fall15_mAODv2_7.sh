#!/bin/sh

nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WW"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WZ"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples ZZ"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WWTo2L2Nu"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WWToLNuQQ"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WWTo1L1Nu2Q" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples ZZTo2L2Q"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples ZZTo2Q2Nu"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples ZZTo4L" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WZTo1L1Nu2Q"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WZTo2L2Q"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WZTo3LNu"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WZTo1L3Nu" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WZJets" &
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples=VVTo2L2Nu"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WGToLNuG"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples ZGTo2LG"  &

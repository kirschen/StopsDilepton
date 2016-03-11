#!/bin/sh 
nohup "python cmgPostProcessing.py --skim $1 $2 --keepPhotons --samples DoubleMuon_Run2015D_16Dec" &
nohup "python cmgPostProcessing.py --skim $1 $2 --keepPhotons --samples MuonEG_Run2015D_16Dec" &
nohup "python cmgPostProcessing.py --skim $1 $2 --keepPhotons --samples DoubleEG_Run2015D_16Dec" &

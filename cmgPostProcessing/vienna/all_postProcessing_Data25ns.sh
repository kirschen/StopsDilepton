#!/bin/sh 
python cmgPostProcessing.py --skim $1 $2 --keepPhotons --samples SingleElectron_Run2015D_16Dec
python cmgPostProcessing.py --skim $1 $2 --keepPhotons --samples SingleMuon_Run2015D_16Dec
python cmgPostProcessing.py --skim $1 $2 --keepPhotons --samples DoubleMuon_Run2015D_16Dec
python cmgPostProcessing.py --skim $1 $2 --keepPhotons --samples MuonEG_Run2015D_16Dec
python cmgPostProcessing.py --skim $1 $2 --keepPhotons --samples DoubleEG_Run2015D_16Dec

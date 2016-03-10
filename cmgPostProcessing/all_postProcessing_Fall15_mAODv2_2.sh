#!/bin/sh

nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTJets_SingleLeptonFromTbar TTJets_SingleLeptonFromTbar_ext" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTJets_SingleLeptonFromT TTJets_SingleLeptonFromT_ext" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTLep_pow" &

#!/bin/sh
python cmgPostProcessing.py --skim=$1 $2 $3 --eventsPerJob=1000000 --samples TTJets_SingleLeptonFromTbar TTJets_SingleLeptonFromTbar_ext
python cmgPostProcessing.py --skim=$1 $2 $3 --eventsPerJob=1000000 --samples TTJets_SingleLeptonFromT TTJets_SingleLeptonFromT_ext
python cmgPostProcessing.py --skim=$1 $2 $3 --eventsPerJob=1000000 --samples TTLep_pow TTLep_pow_ext

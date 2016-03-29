#!/bin/sh
python cmgPostProcessing.py --skim=$1 $2 --eventsPerJob=150000 --samples TTJets_SingleLeptonFromTbar TTJets_SingleLeptonFromTbar_ext
python cmgPostProcessing.py --skim=$1 $2 --eventsPerJob=150000 --samples TTJets_SingleLeptonFromT TTJets_SingleLeptonFromT_ext
python cmgPostProcessing.py --skim=$1 $2 --eventsPerJob=150000 --samples TTLep_pow,TTLep_pow_ext

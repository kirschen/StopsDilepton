#!/bin/sh
python cmgPostProcessing.py --skim=$1 $2 $3 --eventsPerJob=1000000 --samples TTJets TTJets_ext
python cmgPostProcessing.py --skim=$1 $2 $3 --eventsPerJob=1000000 --samples TTJets_DiLepton_ext
python cmgPostProcessing.py --skim=$1 $2 $3 --eventsPerJob=1000000 --samples TTJets_DiLepton TTJets_DiLepton_ext
python cmgPostProcessing.py --skim=$1 $2 $3 --eventsPerJob=1000000 --samples TTJets_LO

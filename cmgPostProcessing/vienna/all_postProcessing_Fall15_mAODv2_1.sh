#!/bin/sh
python cmgPostProcessing.py --skim=$1 $2  --samples TTJets_DiLepton_ext
python cmgPostProcessing.py --skim=$1 $2  --samples TTJets_DiLepton TTJets_DiLepton_ext
python cmgPostProcessing.py --skim=$1 $2  --samples TTJets TTJets_ext
python cmgPostProcessing.py --skim=$1 $2  --samples TTJets_LO

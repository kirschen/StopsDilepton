#!/bin/sh
python cmgPostProcessing.py --skim=$1 $2 --noTopPtReweighting --samples TTJets_LO_HT600to800 TTJets_LO_HT600to800_ext
python cmgPostProcessing.py --skim=$1 $2 --noTopPtReweighting --samples TTJets_LO_HT800to1200 TTJets_LO_HT800to1200
python cmgPostProcessing.py --skim=$1 $2 --noTopPtReweighting --samples TTJets_LO_HT1200to2500 TTJets_LO_HT1200to2500_ext
python cmgPostProcessing.py --skim=$1 $2 --noTopPtReweighting --samples TTJets_LO_HT2500toInf
#python cmgPostProcessing.py --skim=$1 $2 --noTopPtReweighting --samples TTHnobb_mWCutfix_ch0 TTHnobb_mWCutfix_ch1
python cmgPostProcessing.py --skim=$1 $2 --noTopPtReweighting --samples TTHnobb_mWCutfix_ch1
#python cmgPostProcessing.py --skim=$1 $2 --noTopPtReweighting --samples TTHbb TTHbb_ext1 TTHbb_ext2 TTHbb_ext3
python cmgPostProcessing.py --skim=$1 $2 --noTopPtReweighting --samples TTHbb_ext1 TTHbb_ext2 TTHbb_ext3
#python cmgPostProcessing.py --skim=$1 $2  --samples TTHnobb
#python cmgPostProcessing.py --skim=$1 $2  --samples TTHnobb_pow

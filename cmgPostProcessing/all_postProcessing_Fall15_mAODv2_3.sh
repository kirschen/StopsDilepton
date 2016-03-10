#!/bin/sh

nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTJets_LO_HT600to800 TTJets_LO_HT600to800_ext" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTJets_LO_HT800to1200" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTJets_LO_HT1200to2500 TTJets_LO_HT1200to2500_ext" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTJets_LO_HT2500toInf" &
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTHnobb" &
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTHnobb_pow" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTHnobb_mWCutfix_ch0 TTHnobb_mWCutfix_ch1" &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples TTHbb TTHbb_ext1 TTHbb_ext2 TTHbb_ext3" &

#!/bin/sh
# ./tails.sh 2018 mue lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
# echo python tails.py --year $1 --mode $2 --selection $3
yes q|python tailScanner.py --year $1 --mode $2 --selection $3 |sed "s/ *//g"|sed "s/^\*//g"| sed "s/[0-9]*\*\(.*\)/\1/g"|sed "s/\*$//g"|sed "s/\*/:/g" | grep "^[0-9]" > /afs/hephy.at/work/m/mdoppler/stopsdilepton/CMSSW_10_2_9/src/StopsDilepton/plots/plotsMarkus/tails/$1_$2_$3.txt

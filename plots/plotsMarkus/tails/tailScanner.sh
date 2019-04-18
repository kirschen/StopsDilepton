#!/bin/sh
# ./tails.sh 2018 mue lepSel-njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-dPhiJet0-dPhiJet1-POGMetSig12
# echo python tails.py --year $1 --mode $2 --selection $3
yes q|python tails.py --year $1 --mode $2 --selection $3 |sed "s/ *//g"|sed "s/^\*//g"| sed "s/[0-9]*\*\(.*\)/\1/g"|sed "s/\*$//g"|sed "s/\*/:/g" | grep "^[0-9]" > $1_$2_$3.txt

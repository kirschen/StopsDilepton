#!/bin/bash
mkdir -p log
for mode in doubleMu doubleEle muEle
do
  qsub -v zMode=$zMode,mode=$mode -q localgrid@cream02 -o log/$zMode-$mode.log -e log/$zMode-$mode.log runTTGPlotsOnCream02.sh 
done

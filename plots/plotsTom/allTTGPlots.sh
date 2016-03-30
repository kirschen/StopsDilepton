#!/bin/bash
mkdir -p log
for mode in doubleMu doubleEle muEle
do
  qsub -v mode=$mode -q localgrid@cream02 -o log/$mode.log -e log/$mode.log runTTGPlotsOnCream02.sh 
done

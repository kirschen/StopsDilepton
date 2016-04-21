#!/bin/bash
mkdir -p log
while read -r prefix; do
  for mode in 2mu1e 2e1mu 
  do
    qsub -v command="./ttZ.py --mode=$mode --selectPrefix=$prefix"                -q localgrid@cream02 -o log/$mode-$prefix.log              -e log/$mode-$prefix.log              runPlotsOnCream02.sh
    qsub -v command="./ttZ.py --mode=$mode --selectPrefix=$prefix --leptonsExact" -q localgrid@cream02 -o log/$mode-$prefix-leptonsExact.log -e log/$mode-$prefix-leptonsExact.log runPlotsOnCream02.sh
  done
done <$1

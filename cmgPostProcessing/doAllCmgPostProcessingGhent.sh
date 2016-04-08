#!/bin/bash 
mkdir -p log

# Make sure cmgdataset cache is available
if [ ! -d "/localgrid/$USER/.cmgdataset" ]; then
  cp -r ~/.cmgdataset /localgrid/$USER
fi

skim="singlelepReallyTiny"
# Run over samples given in input file
while read -r sample; do
    if [[ ${sample} = \#* || -z "${sample}" ]] ; then
      continue
    fi
    echo "${sample}"
    mkdir -p "/localgrid/$USER/cmgPostProcessing/$skim/${sample// /}"
    cp -r $CMSSW_BASE "/localgrid/$USER/cmgPostProcessing/$skim/${sample// /}"
    qsub -v sample="${sample}",cmssw=$CMSSW_VERSION,skim=$skim -q localgrid@cream02 -o "log/${sample// /}.txt" -e "log/${sample// /}.txt" runPostProcessingOnCream02.sh
  done <$1

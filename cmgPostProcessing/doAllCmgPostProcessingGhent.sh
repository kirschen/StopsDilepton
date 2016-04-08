#!/bin/bash 
mkdir -p log

# Make sure cmgdataset cache is available
if [ ! -d "/localgrid/$USER/.cmgdataset" ]; then
  cp -r ~/.cmgdataset /localgrid/$USER
fi

skim="dilepTiny"
# Run over samples given in input file
while read -r sample; do
    if [[ ${sample} = \#* || -z "${sample}" ]] ; then
      continue
    fi
    echo "${sample}"
    wallTime="02:00:00"
    if [[ ${sample} = TTJets* ]]; then
      wallTime="25:00:00"
    fi
    mkdir -p "/localgrid/$USER/cmgPostProcessing/$skim/${sample// /}"
    rsync -rq --exclude=.git --exclude=plots --exclude=crab_with_das --exclude=logs $CMSSW_BASE "/localgrid/$USER/cmgPostProcessing/$skim/${sample// /}"
    qsub -v sample="${sample}",cmssw=$CMSSW_VERSION,skim=$skim -q localgrid@cream02 -o "log/${sample// /}.txt" -e "log/${sample// /}.txt" -l walltime=$wallTime runPostProcessingOnCream02.sh
  done <$1

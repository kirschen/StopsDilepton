#!/bin/bash 
mkdir -p log

# Make sure cmgdataset cache is available
if [ ! -d "/user/$USER/.cmgdataset" ]; then
  cp -r ~/.cmgdataset /user/$USER
fi

skim="dilepTiny_new"
# Run over samples given in input file
while read -r sample; do
    if [[ ${sample} = \#* || -z "${sample}" ]] ; then
      continue
    fi
    echo "${sample}"
    wallTime="20:00:00"
    if [[ ${sample} = TTJets* || ${sample} = TTLep* ]]; then
      wallTime="168:00:00"
    fi
    mkdir -p "/user/$USER/cmgPostProcessing/$skim/${sample// /}"
    rsync -rq --exclude=.git --exclude=plots --exclude=crab_with_das --exclude=logs $CMSSW_BASE "/user/$USER/cmgPostProcessing/$skim/${sample// /}"
    qsub -v sample="${sample}",cmssw=$CMSSW_VERSION,skim=$skim -q localgrid@cream02 -o "log/${sample// /}.txt" -e "log/${sample// /}.txt" -l walltime=$wallTime runPostProcessingOnCream02.sh
  done <$1

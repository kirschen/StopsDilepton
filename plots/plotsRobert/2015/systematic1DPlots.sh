#!/bin/sh

./submit.sh "python systematic1DPlots.py $1 $2 --sysScaling --mode=muEle --zMode=allZ --njet 01 --nbtag 0  --met=low"
./submit.sh "python systematic1DPlots.py $1 $2 --sysScaling --mode=muEle --zMode=allZ --njet 2p --nbtag 0  --met=low"
./submit.sh "python systematic1DPlots.py $1 $2 --sysScaling --mode=muEle --zMode=allZ --njet 01 --nbtag 1p --met=low"
./submit.sh "python systematic1DPlots.py $1 $2 --sysScaling --mode=muEle --zMode=allZ --njet 2p --nbtag 1p --met=low"

./submit.sh "python systematic1DPlots.py $1 $2 --sysScaling --mode=muEle --zMode=allZ --njet 01 --nbtag 0  --met=def"
./submit.sh "python systematic1DPlots.py $1 $2 --sysScaling --mode=muEle --zMode=allZ --njet 2p --nbtag 0  --met=def"
./submit.sh "python systematic1DPlots.py $1 $2 --sysScaling --mode=muEle --zMode=allZ --njet 01 --nbtag 1p --met=def"
./submit.sh "python systematic1DPlots.py $1 $2 --sysScaling --mode=muEle --zMode=allZ --njet 2p --nbtag 1p --met=def"

## low njet, btag 0
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 01 --nbtag 0"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 01 --nbtag 0"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 01 --nbtag 0"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=muEle --zMode=allZ --njet 01 --nbtag 0"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=dilepton --njet 01 --nbtag 0"
#
## high njet, btag 0
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 2p --nbtag 0"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 2p --nbtag 0"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 2p --nbtag 0"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=muEle --zMode=allZ --njet 2p --nbtag 0"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=dilepton --njet 2p --nbtag 0"
#
## low njet, btag 1p
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 01 --nbtag 1p"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 01 --nbtag 1p"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 01 --nbtag 1p"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=muEle --zMode=allZ --njet 01 --nbtag 1p"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=dilepton --njet 01 --nbtag 1p"
#
## high njet, btag 1p
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=onZ --njet 2p --nbtag 1p"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=offZ --njet 2p --nbtag 1p"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=sameFlavour --zMode=allZ --njet 2p --nbtag 1p"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=muEle --zMode=allZ --njet 2p --nbtag 1p"
#./submit.sh "python systematic1DPlots.py $1 --sysScaling --splitDiBoson --mode=dilepton --njet 2p --nbtag 1p"



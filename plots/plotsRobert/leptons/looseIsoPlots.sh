#!/bin/sh

python looseIsoPlots.py --mode mumu --era Run2016
python looseIsoPlots.py --mode mumu --era Run2017
python looseIsoPlots.py --mode mumu --era Run2018 --reweightPU VUp

python looseIsoPlots.py --mode mue --era Run2016
python looseIsoPlots.py --mode mue --era Run2017
python looseIsoPlots.py --mode mue --era Run2018 --reweightPU VUp

python looseIsoPlots.py --mode ee --era Run2016
python looseIsoPlots.py --mode ee --era Run2017
python looseIsoPlots.py --mode ee --era Run2018 --reweightPU VUp

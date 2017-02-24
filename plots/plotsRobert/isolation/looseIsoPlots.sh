#!/bin/sh

python looseIsoPlots.py --removeLeptonsFromMET --mode=doubleMu  &
python looseIsoPlots.py --removeLeptonsFromMET --mode=doubleEle &
python looseIsoPlots.py --removeLeptonsFromMET --mode=muEle     &

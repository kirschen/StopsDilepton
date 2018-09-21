#!/bin/sh

#python looseIsoPlots.py --removeLeptonsFromMET --mode=doubleMu  &
#python looseIsoPlots.py --removeLeptonsFromMET --mode=doubleEle &
#python looseIsoPlots.py --removeLeptonsFromMET --mode=muEle     &
python looseIsoPlots.py --mode=doubleMu  & 
python looseIsoPlots.py --mode=doubleEle & 
python looseIsoPlots.py --mode=muEle     & 

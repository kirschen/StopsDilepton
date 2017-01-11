#!/bin/sh

submitBatch.py "python recoilPlots.py --mode=doubleMu --dPhi=None" 
submitBatch.py "python recoilPlots.py --mode=doubleEle --dPhi=None" 
submitBatch.py "python recoilPlots.py --mode=sameFlavour --dPhi=None" 
submitBatch.py "python recoilPlots.py --mode=doubleMu --dPhi=inv" 
submitBatch.py "python recoilPlots.py --mode=doubleEle --dPhi=inv" 
submitBatch.py "python recoilPlots.py --mode=sameFlavour --dPhi=inv" 
submitBatch.py "python recoilPlots.py --mode=doubleMu --dPhi=def" 
submitBatch.py "python recoilPlots.py --mode=doubleEle --dPhi=def" 
submitBatch.py "python recoilPlots.py --mode=sameFlavour --dPhi=def" 
#python recoilplots.py --mode=doubleMu --dPhi=None &
#python recoilplots.py --mode=doubleEle --dPhi=None &
#python recoilplots.py --mode=sameFlavour --dPhi=None &
#python recoilplots.py --mode=doubleMu --dPhi=inv &
#python recoilplots.py --mode=doubleEle --dPhi=inv &
#python recoilplots.py --mode=sameFlavour --dPhi=inv &
#python recoilplots.py --mode=doubleMu --dPhi=def &
#python recoilplots.py --mode=doubleEle --dPhi=def &
#python recoilplots.py --mode=sameFlavour --dPhi=def &

#!/bin/sh

#submitBatch.py "python recoilPlots.py --mode=doubleMu --dPhi=none" 
#submitBatch.py "python recoilPlots.py --mode=doubleEle --dPhi=none" 
#submitBatch.py "python recoilPlots.py --mode=sameFlavour --dPhi=none" 
#submitBatch.py "python recoilPlots.py --mode=doubleMu --dPhi=inv" 
#submitBatch.py "python recoilPlots.py --mode=doubleEle --dPhi=inv" 
#submitBatch.py "python recoilPlots.py --mode=sameFlavour --dPhi=inv" 
#submitBatch.py "python recoilPlots.py --mode=doubleMu --dPhi=def" 
#submitBatch.py "python recoilPlots.py --mode=doubleEle --dPhi=def" 
#submitBatch.py "python recoilPlots.py --mode=sameFlavour --dPhi=def" 
python recoilPlots.py --mode=doubleMu --dPhi=none &
python recoilPlots.py --mode=doubleEle --dPhi=none &
python recoilPlots.py --mode=sameFlavour --dPhi=none &
python recoilPlots.py --mode=doubleMu --dPhi=inv &
python recoilPlots.py --mode=doubleEle --dPhi=inv &
python recoilPlots.py --mode=sameFlavour --dPhi=inv &
python recoilPlots.py --mode=doubleMu --dPhi=def &
python recoilPlots.py --mode=doubleEle --dPhi=def &
python recoilPlots.py --mode=sameFlavour --dPhi=def &

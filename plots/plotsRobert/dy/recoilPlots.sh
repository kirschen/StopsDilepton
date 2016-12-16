#!/bin/sh

./submit.sh "python recoilPlots.py --mode=doubleMu --dPhi=none" &
./submit.sh "python recoilPlots.py --mode=doubleEle --dPhi=none" &
./submit.sh "python recoilPlots.py --mode=sameFlavour --dPhi=none" &
./submit.sh "python recoilPlots.py --mode=doubleMu --dPhi=inv" &
./submit.sh "python recoilPlots.py --mode=doubleEle --dPhi=inv" &
./submit.sh "python recoilPlots.py --mode=sameFlavour --dPhi=inv" &
./submit.sh "python recoilPlots.py --mode=doubleMu --dPhi=def" &
./submit.sh "python recoilPlots.py --mode=doubleEle --dPhi=def" &
./submit.sh "python recoilPlots.py --mode=sameFlavour --dPhi=def" &
#python recoilPlots.py --mode=doubleMu --dPhi=none &
#python recoilPlots.py --mode=doubleEle --dPhi=none &
#python recoilPlots.py --mode=sameFlavour --dPhi=none &
#python recoilPlots.py --mode=doubleMu --dPhi=inv &
#python recoilPlots.py --mode=doubleEle --dPhi=inv &
#python recoilPlots.py --mode=sameFlavour --dPhi=inv &
#python recoilPlots.py --mode=doubleMu --dPhi=def &
#python recoilPlots.py --mode=doubleEle --dPhi=def &
#python recoilPlots.py --mode=sameFlavour --dPhi=def &

#!/bin/sh
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WWDouble"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WpWpJJ"  &
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WWZ"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WZZ"  &
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples ZZZ"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples TTWToLNu"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples TTWToQQ"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples TTZToQQ"  &
nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples TTZToLLNuNu"  &
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples=TTGJets"  &

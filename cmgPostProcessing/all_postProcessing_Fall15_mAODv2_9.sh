#!/bin/sh
python cmgPostProcessing.py --skim=$1 $2 --samples WWDouble
python cmgPostProcessing.py --skim=$1 $2 --samples WpWpJJ
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples WWZ"  
python cmgPostProcessing.py --skim=$1 $2 --samples WZZ
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples ZZZ"  
python cmgPostProcessing.py --skim=$1 $2 --samples TTWToLNu
python cmgPostProcessing.py --skim=$1 $2 --samples TTWToQQ
python cmgPostProcessing.py --skim=$1 $2 --samples TTZToQQ
python cmgPostProcessing.py --skim=$1 $2 --samples TTZToLLNuNu
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2 --samples=TTGJets"  

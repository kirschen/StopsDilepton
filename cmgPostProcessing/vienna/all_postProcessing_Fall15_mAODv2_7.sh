#!/bin/sh
#nohup krenew -t -K 10 -- bash -c "python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt15to20_Mu5" 
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt20to30_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt30to50_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt50to80_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt80to120_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt120to170_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt170to300_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt300to470_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt470to600_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt600to800_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt800to1000_Mu5
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt1000toInf_Mu5

#python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt15to20_EMEnriched
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt20to30_EMEnriched
#python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt30to50_EMEnriched
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt50to80_EMEnriched
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt80to120_EMEnriched
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt120to170_EMEnriched
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt170to300_EMEnriched
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt300toInf_EMEnriched

#python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt_15to20_bcToE 
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt_20to30_bcToE
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt_30to80_bcToE
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt_80to170_bcToE
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt_170to250_bcToE
python cmgPostProcessing.py --skim=$1 $2  --samples=QCD_Pt_250toInf_bcToE

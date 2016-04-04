#!/bin/sh
python cmgPostProcessing.py --skim=$1 $2 $3 --samples WJetsToLNu
python cmgPostProcessing.py --skim=$1 $2 $3 --samples WJetsToLNu_LO
python cmgPostProcessing.py --skim=$1 $2 $3 --samples tZq_ll
python cmgPostProcessing.py --skim=$1 $2 $3 --samples tZq_nunu
python cmgPostProcessing.py --skim=$1 $2 $3 --samples TToLeptons_tch_amcatnlo TToLeptons_tch_amcatnlo_ext
python cmgPostProcessing.py --skim=$1 $2 $3 --samples TBarToLeptons_tch_powheg
python cmgPostProcessing.py --skim=$1 $2 $3 --samples TToLeptons_tch_powheg
python cmgPostProcessing.py --skim=$1 $2 $3 --samples TToLeptons_sch_amcatnlo
#python cmgPostProcessing.py --skim=$1 $2 $3 --samples TBar_tWch
#python cmgPostProcessing.py --skim=$1 $2 $3 --samples TBar_tWch_DS
#python cmgPostProcessing.py --skim=$1 $2 $3 --samples T_tWch
#python cmgPostProcessing.py --skim=$1 $2 $3 --samples T_tWch_DS


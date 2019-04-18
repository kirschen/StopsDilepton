#!/bin/sh

#python recoil_v5.py --fine --mode mumu --year 2016                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --fine --mode mumu --year 2017                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --fine --mode mumu --year 2018                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --fine --mode mumu --year 2018 --preHEM       --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --fine --mode mumu --year 2018 --postHEM      --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#
#python recoil_v5.py --fine --mode ee --year 2016                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --fine --mode ee --year 2017                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --fine --mode ee --year 2018                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --fine --mode ee --year 2018 --preHEM       --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --fine --mode ee --year 2018 --postHEM      --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#
#python recoil_v5.py --fine --mode SF --year 2016                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --fine --mode SF --year 2017                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --fine --mode SF --year 2018                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --fine --mode SF --year 2018 --preHEM       --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --fine --mode SF --year 2018 --postHEM      --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ


#python recoil_v5.py --mode mumu --year 2016                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --mode mumu --year 2017                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --mode mumu --year 2018                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --mode mumu --year 2018 --preHEM       --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --mode mumu --year 2018 --postHEM      --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#
#python recoil_v5.py --mode ee --year 2016                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --mode ee --year 2017                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --mode ee --year 2018                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --mode ee --year 2018 --preHEM       --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --mode ee --year 2018 --postHEM      --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#
#python recoil_v5.py --mode SF --year 2016                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --mode SF --year 2017                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ 
#python recoil_v5.py --mode SF --year 2018                --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --mode SF --year 2018 --preHEM       --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --mode SF --year 2018 --postHEM      --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ
#python recoil_v5.py --mode ee --year 2016 &
#python recoil_v5.py --mode ee --year 2017 &
#python recoil_v5.py --mode ee --year 2018 --preHEM &
#python recoil_v5.py --mode ee --year 2018 --postHEM &

python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2016
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2016BCD
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2016EF
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2016GH

python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2017
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2017B
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2017CDE
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2017F

python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2018
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2018A
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2018B
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2018C
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode SF --era Run2018D

python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2016
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2016BCD
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2016EF
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2016GH

python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2017
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2017B
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2017CDE
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2017F

python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2018
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2018A
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2018B
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2018C
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode mumu --era Run2018D

python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2016
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2016BCD
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2016EF
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2016GH

python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2017
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2017B
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2017CDE
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2017F

python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2018
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2018A
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2018B
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2018C
python recoil_v5.py --fine --selection lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ --mode ee --era Run2018D

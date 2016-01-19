import copy, os, sys
from StopsDilepton.tools.localInfo import dataDir
import ROOT
dir = dataDir 

DY={\
"name" : "DY",
"bins" : [
"DYJetsToLL_M10to50",
"DYJetsToLL_M50",
],
'dir' : dir,
'isData':False,
'color': 8,
'texName':"DY + Jets",
}

DY_LO={\
"name" : "DY_LO",
"bins" : [
"DYJetsToLL_M5to50_LO",
"DYJetsToLL_M50_LO",
],
'dir' : dir,
'isData':False,
'color': 8,
'texName':"DY + Jets (LO)",
}

DY_HT_LO={\
"name" : "DY_HT_LO",
"bins" : [
"DYJetsToLL_M50_LO_lheHT100",
"DYJetsToLL_M50_HT100to200",
"DYJetsToLL_M50_HT200to400",
"DYJetsToLL_M50_HT400to600",
"DYJetsToLL_M50_HT600toInf",
"DYJetsToLL_M5to50_LO_lheHT100",
"DYJetsToLL_M5to50_HT100to200",
"DYJetsToLL_M5to50_HT200to400",
"DYJetsToLL_M5to50_HT400to600",
"DYJetsToLL_M5to50_HT600toInf",
],
'dir' : dir,
'isData':False,
'color': 8,
'texName':"DY + Jets (LO,HT)",
}


TTJets={
"name":"TTJets",
"bins":[
"TTJets",
],
'dir' : dir,
'isData':False,
'color': 7,
'texName':"t#bar{t} + Jets",
}
TTJets_LO={
"name":"TTJets_LO",
"bins":[
"TTJets_LO",
],
'dir' : dir,
'isData':False,
'color': 7,
'texName':"t#bar{t} + Jets (LO)",
}
TTLep_pow={
"name":"TTLep_pow",
"bins":[
"TTLep_pow",
],
'dir' : dir,
'isData':False,
'color': 7,
'texName':"t#bar{t} (lep,pow)",
}


TTJets_Lep={
"name":"TTJets_Lep",
"bins":[
"TTJets_DiLepton_comb",
"TTJets_SingleLeptonFromTbar_comb",
"TTJets_SingleLeptonFromT_comb",
],
'dir' : dir,
'isData':False,
'color': 7,
'texName':"t#bar{t} + Jets (lep)",
}

TTJets_HT_LO={
"name":"TTJets_HT_LO",
"bins":[
"TTJets_LO_HT600to800",
"TTJets_LO_HT800to1200",
"TTJets_LO_HT1200to2500",
"TTJets_LO_HT2500toInf",
],
'dir' : dir,
'isData':False,
'color': 7,
'texName':"t#bar{t} + Jets (HT,LO)",
}

singleTop={
"name":"singleT",
"bins":[
"TBar_tWch",
#"TBar_tWch_DS",
"TToLeptons_sch",
"TToLeptons_tch_amcatnlo_comb",
"T_tWch",
#"T_tWch_DS",
],
'dir' : dir,
'isData':False,
'color': 40,
'texName':"single top",
}

TTX={\
"name" : "TTX",
"bins" : [
"TTHbb_comb",
"TTHnobb",
"TTWToLNu",
"TTWToQQ",
"TTZToLLNuNu",
"TTZToQQ",
"tZq_ll",
"tZq_nunu",
],
'dir' : dir,
'isData':False,
'color': ROOT.kPink,
'texName':"t#bar{t}X",
}
TTXNoZ={\
"name" : "TTXNoZ",
"bins" : [
"TTHbb_comb",
"TTHnobb",
"TTWToLNu",
"TTWToQQ",
"tZq_ll",
"tZq_nunu",
],
'dir' : dir,
'isData':False,
'color': ROOT.kPink,
'texName':"t#bar{t}H/W, tZq",
}

TTH={\
"name" : "TTH",
"bins" : [
"TTHbb_comb",
"TTHnobb",
],
'dir' : dir,
'isData':False,
'color': ROOT.kPink-4,
'texName':"t#bar{t}H",
}

TTW={\
"name" : "TTW",
"bins" : [
"TTWToLNu",
"TTWToQQ",
],
'dir' : dir,
'isData':False,
'color': ROOT.kPink-8,
'texName':"t#bar{t}W",
}

TTZ={\
"name" : "TTZ",
"bins" : [
"TTZToLLNuNu",
"TTZToQQ",
],
'dir' : dir,
'isData':False,
'color': ROOT.kPink+9,
'texName':"t#bar{t}Z",
}

TZQ={\
"name" : "TZQ",
"bins" : [
"tZq_ll",
"tZq_nunu",
],
'dir' : dir,
'isDta':False,
'color': ROOT.kPink-7,
'texName':"tZq",
}

WJetsToLNu={
"name":"WJetsToLNu",
"bins":[
"WJetsToLNu",
],
'dir':dir,
'isData':False,
'color': ROOT.kRed-10,
'texName':"W(l,#nu) + Jets",
}

WJetsToLNu_LO={
"name":"WJetsToLNu_LO",
"bins":[
"WJetsToLNu_LO",
],
'dir':dir,
'isData':False,
'color': ROOT.kRed-10,
'texName':"W(l,#nu) + Jets (LO)",
}

WJetsToLNu_HT={
"name":"WJetsToLNu_HT",
"bins":[
"WJetsToLNu_HT100to200",
"WJetsToLNu_HT200to400",
"WJetsToLNu_HT400to600",
"WJetsToLNu_HT600to800",
#"WJetsToLNu_HT600toInf",
"WJetsToLNu_HT800to1200",
"WJetsToLNu_HT1200to2500",
"WJetsToLNu_HT2500toInf",
],
'dir':dir,
'isData':False,
'color': ROOT.kRed-10,
'texName':"W(l,#nu) + Jets (HT)",
}

diBoson={
"name":"diBoson",
"bins":[
#"VVTo2L2Nu",
"WWTo2L2Nu",
"WWToLNuQQ",
"WZTo1L1Nu2Q",
"WZTo2L2Q",
"WZTo3LNu",
"ZZTo2L2Q",
"ZZTo2Q2Nu",
],
'dir':dir,
'isData':False,
'color': ROOT.kOrange,
'texName':"WW/ZZ/WZ",
}

ZZ={
"name":"ZZ",
"bins":[
"ZZTo2L2Q",
"ZZTo2Q2Nu",
],
'dir':dir,
'isData':False,
'color': ROOT.kOrange+1,
'texName':"ZZ",
}

WZ={
"name":"WZ",
"bins":[
"WZTo1L1Nu2Q",
"WZTo2L2Q",
"WZTo3LNu"
],
'dir':dir,
'isData':False,
'color': ROOT.kOrange+2,
'texName':"WZ",
}


triBoson={
"name":"triBoson",
"bins":[
"WWZ",
"WZZ",
"ZZZ",
],
'dir':dir,
'isData':False,
'color': ROOT.kYellow,
'texName':"WWZ/WZZ/ZZZ",
}

QCD_HT={\
"name" : "QCD_HT",
"bins" : [
"QCD_HT100to200",
"QCD_HT200to300",
"QCD_HT300to500",
"QCD_HT500to700",
"QCD_HT700to1000",
"QCD_HT1000to1500",
"QCD_HT1500to2000",
"QCD_HT2000toInf",
],
'dir' : dir,
'isData':False,
'color': 46,
'texName':"QCD (HT)",
}

QCD_Mu5={\
"name" : "QCD_Mu5",
"bins" : [
#"QCD_Pt15to20_Mu5",#omit
"QCD_Pt20to30_Mu5",
"QCD_Pt50to80_Mu5",
"QCD_Pt80to120_Mu5",
"QCD_Pt120to170_Mu5",
"QCD_Pt170to300_Mu5",
"QCD_Pt300to470_Mu5",
"QCD_Pt470to600_Mu5",
"QCD_Pt600to800_Mu5",
"QCD_Pt800to1000_Mu5",
"QCD_Pt1000toInf_Mu5",
],
'dir' : dir,
'isData':False,
'color': 46,
'texName':"QCD (Mu5)",
}

QCD_EMbcToE={\
"name" : "QCD_EM+bcToE",
"bins" : [
"QCD_Pt_15to20_bcToE",
"QCD_Pt_20to30_bcToE",
"QCD_Pt_30to80_bcToE",
"QCD_Pt_80to170_bcToE",
"QCD_Pt_170to250_bcToE",
"QCD_Pt_250toInf_bcToE",
"QCD_Pt15to20_EMEnriched",
"QCD_Pt20to30_EMEnriched",
"QCD_Pt30to50_EMEnriched",
"QCD_Pt50to80_EMEnriched",
"QCD_Pt80to120_EMEnriched",
"QCD_Pt120to170_EMEnriched",
"QCD_Pt170to300_EMEnriched",
"QCD_Pt300toInf_EMEnriched",
],
'dir' : dir,
'isData':False,
'color': 46,
'texName':"QCD (EM+bcToE)",
}

QCD_Mu5EMbcToE={\
"name" : "QCD_Mu5+EM+bcToE",
"bins" : [

"QCD_Pt20to30_Mu5",
"QCD_Pt50to80_Mu5",
"QCD_Pt80to120_Mu5",
"QCD_Pt120to170_Mu5",
"QCD_Pt170to300_Mu5",
"QCD_Pt300to470_Mu5",
"QCD_Pt470to600_Mu5",
"QCD_Pt600to800_Mu5",
"QCD_Pt800to1000_Mu5",
"QCD_Pt1000toInf_Mu5",

"QCD_Pt_15to20_bcToE",
"QCD_Pt_20to30_bcToE",
"QCD_Pt_30to80_bcToE",
"QCD_Pt_80to170_bcToE",
"QCD_Pt_170to250_bcToE",
"QCD_Pt_250toInf_bcToE",
"QCD_Pt15to20_EMEnriched",
"QCD_Pt20to30_EMEnriched",
"QCD_Pt30to50_EMEnriched",
"QCD_Pt50to80_EMEnriched",
"QCD_Pt80to120_EMEnriched",
"QCD_Pt120to170_EMEnriched",
"QCD_Pt170to300_EMEnriched",
"QCD_Pt300toInf_EMEnriched",
],
'dir' : dir,
'isData':False,
'color': 46,
'texName':"QCD (Mu5+EM+bcToE)",
}



QCD_Pt={\
"name" : "QCD",
"bins" : [
"QCD_Pt10to15",
"QCD_Pt15to30",
"QCD_Pt30to50",
"QCD_Pt50to80",
"QCD_Pt80to120",
"QCD_Pt120to170",
"QCD_Pt170to300",
"QCD_Pt300to470",
"QCD_Pt470to600",
"QCD_Pt600to800",
"QCD_Pt800to1000",
"QCD_Pt1000to1400",
"QCD_Pt1400to1800",
"QCD_Pt1800to2400",
"QCD_Pt2400to3200",
"QCD_Pt3200",
],
'dir' : dir,
'isData':False,
'color': 46,
'texName':"QCD",
}

import copy, os, sys
#from StopsDilepton.tools.user import dataDir
#dir = dataDir
#if anybody else wants to use this: please add a 0l data-directory to user and remove the hard coded location
dir = "/afs/hephy.at/data/rschoefbeck01/cmgTuples/postProcessed_mAODv2/inclusive"

GJets={\
"name" : "Gamma + Jets",
"bins" : [
"GJets_HT40to100",
"GJets_HT100to200",
"GJets_HT200to400",
"GJets_HT600toInf",
"GJets_HT400to600",
],
'dir' : dir,
'isData':False,
}

DY={\
"name" : "DY + Jets",
"bins" : [
"DYJetsToLL_M10to50",
"DYJetsToLL_M50",
],
'dir' : dir,
'isData':False,
}


TTJets={
"name":"TTJets",
"bins":[
"TTJets",
],
'dir' : dir,
'isData':False,
}
singleTop={
"name":"single T",
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
}

QCD_Mu5={\
"name" : "QCD (Mu5)",
"bins" : [
#"QCD_Pt15to20_Mu5",#omit
#"QCD_Pt20to30_Mu5",
#"QCD_Pt50to80_Mu5",
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
}

QCD_EMbcToE={\
"name" : "QCD (EM+bcToE)",
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
}

QCD_Mu5EMbcToE={\
"name" : "QCD (Mu5+EM+bcToE)",
"bins" : [

#"QCD_Pt20to30_Mu5",
#"QCD_Pt50to80_Mu5",
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
}




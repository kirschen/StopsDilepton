import copy, os, sys
from StopsDilepton.tools.user import dataDir
dir = dataDir

DY_15={\
"name": "DY_15",
"bins": ["DYJetsToLL_M50/treeProducerSusyStopDilepton/"],
'dir': "/afs/cern.ch/work/w/wvandrie/public/STOPS/CMSSW_7_4_7/src/CMGTools/TTHAnalysis/cfg/spring15/",
'totalweight': [4.52712069256e+11],
}

DY_HT_15={\
"name": "DY_HT_15",
"bins": ["DYJetsToLL_M50_HT100to200/treeProducerSusyStopDilepton/"],
'dir': "/afs/cern.ch/work/w/wvandrie/public/STOPS/CMSSW_7_4_7/src/CMGTools/TTHAnalysis/cfg/spring15/",
'totalweight': [2625679.0, ],
}

TTJets_15={\
"name" : "tt+Jets_15",
"bins" : ["TTJets_0/treeProducerSusyStopDilepton/","TTJets_1/treeProducerSusyStopDilepton/","TTJets_2/treeProducerSusyStopDilepton/","TTJets_3/treeProducerSusyStopDilepton/"],
'dir': "/afs/cern.ch/work/w/wvandrie/public/STOPS/CMSSW_7_4_7/src/CMGTools/TTHAnalysis/cfg/spring15/",
'totalweight': [21443041971.5, 21475153027.7,21405785485.6,26139089236.5],
}

WJetsHTToLNu_15={\
"name" : "W+Jets_15",
"bins" : ["WJetsToLNu_HT100to200/treeProducerSusyStopDilepton/", "WJetsToLNu_HT200to400/treeProducerSusyStopDilepton/", "WJetsToLNu_HT400to600/treeProducerSusyStopDilepton/", "WJetsToLNu_HT600toInf/treeProducerSusyStopDilepton/"],
'dir' : "/afs/cern.ch/work/w/wvandrie/public/STOPS/CMSSW_7_4_7/src/CMGTools/TTHAnalysis/cfg/spring15/",
'totalweight': [10142187.0,5231856.0,1901705.0,1036108.0],
}

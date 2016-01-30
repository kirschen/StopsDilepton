import copy, os, sys
from StopsDilepton.tools.localInfo import dataDir
dir = dataDir

DoubleEG_Run2015D = { "name" :"DoubleEG_Run2015D",
"bins":[
"DoubleEG_Run2015D_05Oct",
"DoubleEG_Run2015D_v4"
],
"lumi":1000*(0.553+1.612),
"texName":"DoubleEG (Run2015D)"
}
DoubleMuon_Run2015D = { "name" : "DoubleMuon_Run2015D",
"bins":[
"DoubleMuon_Run2015D_05Oct",
"DoubleMuon_Run2015D_v4"
],
"lumi":1000*(0.551+1.613),
"texName":"DoubleMuon (Run2015D)"
}

MuonEG_Run2015D = { "name" :"MuonEG_Run2015D",
"bins":[
"MuonEG_Run2015D_05Oct",
"MuonEG_Run2015D_v4"
],
"lumi":1000*(0.528+1.598),
"texName":"MuonEG (Run2015D)"
}

allSamples_Data25ns = [DoubleEG_Run2015D, MuonEG_Run2015D, DoubleMuon_Run2015D]
import ROOT
for s in allSamples_Data25ns:
    s.update({
        'dir' : dir,
        'color':ROOT.kBlack,
        'isData':True
    })


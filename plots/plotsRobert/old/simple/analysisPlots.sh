#!/bin/sh

submitBatch.py "python analysisPlots.py $@ --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1" 
submitBatch.py "python analysisPlots.py $@ --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1" 
submitBatch.py "python analysisPlots.py $@ --signal=T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1" 
submitBatch.py "python analysisPlots.py $@ --signal=T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1" 
submitBatch.py "python analysisPlots.py $@ --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1" 
submitBatch.py "python analysisPlots.py $@ --signal=T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metTo80-metSig5-dPhiJet0-dPhiJet1" 
submitBatch.py "python analysisPlots.py $@ --signal=T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metTo80-metSig5-dPhiJet0-dPhiJet1" 
submitBatch.py "python analysisPlots.py $@ --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metTo80-metSig5-dPhiJet0-dPhiJet1" 
submitBatch.py "python analysisPlots.py $@ --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metTo80-metSig5-dPhiJet0-dPhiJet1" 

submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection relIso0.12-looseLeptonVeto-mll20"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metInv"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-relIso0.12-looseLeptonVeto-mll20"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-relIso0.12-looseLeptonVeto-mll20-onZ"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv-mt2ll100"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ" #DY tail control
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metInv"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-mt2ll100"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-mt2ll100"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv" #DY control
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiInv-mt2ll100"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1" #VV control
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metInv"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll140"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1"
submitBatch.py "python analysisPlots.py $@  --signal=T2tt --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100"

#submitBatch.py "python analysisPlots.py $@ --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1" 
#submitBatch.py "python analysisPlots.py $@ --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1" 
#submitBatch.py "python analysisPlots.py $@ --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-dPhiJet0-dPhiJet1" 
#submitBatch.py "python analysisPlots.py $@ --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-onZ-met80-dPhiJet0-dPhiJet1" 
#submitBatch.py "python analysisPlots.py $@ --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-met80-metSig5-dPhiJet0-dPhiJet1" 
#submitBatch.py "python analysisPlots.py $@ --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-metTo80-dPhiJet0-dPhiJet1" 
#submitBatch.py "python analysisPlots.py $@ --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-onZ-metTo80-dPhiJet0-dPhiJet1" 
#submitBatch.py "python analysisPlots.py $@ --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ-metTo80-metSig5-dPhiJet0-dPhiJet1" 
#submitBatch.py "python analysisPlots.py $@ --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-onZ-metTo80-metSig5-dPhiJet0-dPhiJet1" 

#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll0To25
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll25To50
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll50To75
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll75To100
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100To140

#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80To200-metSig5-dPhiJet0-dPhiJet1-mt2ll0To25
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80To200-metSig5-dPhiJet0-dPhiJet1-mt2ll25To50
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80To200-metSig5-dPhiJet0-dPhiJet1-mt2ll50To75
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80To200-metSig5-dPhiJet0-dPhiJet1-mt2ll75To100
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80To200-metSig5-dPhiJet0-dPhiJet1-mt2ll100To140
#
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met200-metSig5-dPhiJet0-dPhiJet1-mt2ll0To25
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met200-metSig5-dPhiJet0-dPhiJet1-mt2ll25To50
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met200-metSig5-dPhiJet0-dPhiJet1-mt2ll50To75
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met200-metSig5-dPhiJet0-dPhiJet1-mt2ll75To100
#python analysisPlots.py --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met200-metSig5-dPhiJet0-dPhiJet1-mt2ll100To140

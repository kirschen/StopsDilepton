#!/bin/sh
python systematicsPlots_v2.py $@ --normalizationSelection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2llTo100 --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1 #default
python systematicsPlots_v2.py $@ --normalizationSelection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2llTo100 --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2ll100 #high mt2ll

python systematicsPlots_v2.py $@ --normalizationSelection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-mt2llTo100 --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1 #a
python systematicsPlots_v2.py $@ --normalizationSelection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1-mt2llTo100 --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-met80-dPhiJet0-dPhiJet1 #b
python systematicsPlots_v2.py $@ --normalizationSelection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1-mt2llTo100 --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-met80-metSig5-dPhiJet0-dPhiJet1 #c
python systematicsPlots_v2.py $@ --normalizationSelection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metTo80-dPhiJet0-dPhiJet1-mt2llTo100 --selection njet01-btag0-relIso0.12-looseLeptonVeto-mll20-metTo80-dPhiJet0-dPhiJet1 #d
python systematicsPlots_v2.py $@ --normalizationSelection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metTo80-dPhiJet0-dPhiJet1-mt2llTo100 --selection njet01-btag1p-relIso0.12-looseLeptonVeto-mll20-metTo80-dPhiJet0-dPhiJet1 #e
python systematicsPlots_v2.py $@ --normalizationSelection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metTo80-dPhiJet0-dPhiJet1-mt2llTo100 --selection njet2p-btag0-relIso0.12-looseLeptonVeto-mll20-metTo80-dPhiJet0-dPhiJet1 #f
python systematicsPlots_v2.py $@ --normalizationSelection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metTo80-dPhiJet0-dPhiJet1-mt2llTo100 --selection njet2p-btag1p-relIso0.12-looseLeptonVeto-mll20-metTo80-dPhiJet0-dPhiJet1 #g

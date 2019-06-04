#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1
#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --offZForllg
#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --offZForllg
#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-photondR-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --offZForllg
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-photonEta-photondR-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --offZForllg
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-photonEta-photondR-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --offZForllg
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-photonEta-photondR-njet2p-relIso0.12-HEMJetVetoWide-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --offZForllg
#
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-njet2p-relIso0.12-HEMJetVetoWide-looseLeptonVeto-mll40-photondR-photonEta-dPhiJet0-dPhiJet1
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-njet2p-relIso0.12-HEMJetVetoWide-looseLeptonVeto-mll40-photondR-photonEta-dPhiJet0-dPhiJet1 --offZForllg
#python ttgamma.py --era Run2018 --reweightBosonPt --selection lepSel-POGMetSig12-photon30-njet2p-relIso0.12-HEMJetVetoWide-looseLeptonVeto-mll40-photondR-photonEta-dPhiJet0-dPhiJet1 --offZForllg
#
python gen.py --era Run2018 --plot_directory gen --selection lepSel-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1
python gen.py --era Run2018 --plot_directory gen --reweightBosonPt --selection lepSel-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1

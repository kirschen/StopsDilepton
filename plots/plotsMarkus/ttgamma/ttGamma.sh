python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1
#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-photondR-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-photonEta-photondR-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-photonEta-photondR-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-photonEta-photondR-njet2p-relIso0.12-HEMJetVetoWide-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#
python gen.py --era Run2018 --plot_directory gen --beta njet0p
python gen.py --era Run2018 --plot_directory gen --beta njet0p --reweightBosonPt
python gen.py --era Run2018 --plot_directory gen --beta njet2p --selection njet2p
python gen.py --era Run2018 --plot_directory gen --beta njet2p --selection njet2p --reweightBosonPt

#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1
#python ttgamma.py --era Run2016 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1

#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-photon30-photonEta-photondR-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-photonEta-photondR-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-photonEta-photondR-njet2p-relIso0.12-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#python ttgamma.py --era Run2018 --selection lepSel-POGMetSig12-photon30-photonEta-photondR-njet2p-relIso0.12-HEMJetVetoWide-looseLeptonVeto-mll40-dPhiJet0-dPhiJet1 --reweightBosonPt --llgNoZ
#
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30
#python gen.py --era Run2018 --plot_directory gen --selection njet2p --reweightBosonPt --minBosonPt 30
#python gen.py --era Run2018 --plot_directory gen --selection njet0p
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt
#python gen.py --era Run2018 --plot_directory gen --selection njet2p
#python gen.py --era Run2018 --plot_directory gen --selection njet2p --reweightBosonPt
#python gen.py --era Run2016 --plot_directory gen --selection njet0p
#python gen.py --era Run2016 --plot_directory gen --selection njet2p --reweightBosonPt

#python gen.py --era Run2016 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 0 --inBins 60
#python gen.py --era Run2016 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 0 --inBins 25
python gen.py --era Run2016 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 25
#python gen.py --era Run2016 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 57

#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 0 --inBins 60
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 0 --inBins 25
python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 25
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 57
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 57 --metCut 0 240
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 57 --metCut 240 340
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 57 --metCut 0 300

#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 57 --mt2llCut 0 30
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 57 --mt2llCut 30 300
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 57 --mt2llCut 270 300
#python gen.py --era Run2018 --plot_directory gen --selection njet0p --reweightBosonPt --minBosonPt 30 --inBins 57 --mt2llCut 0 270

#python gen.py --era Run2016 --plot_directory gen --selection njet0p 
#python gen.py --era Run2018 --plot_directory gen --selection njet0p 

python gen.py --era Run2016 --plot_directory gen --selection njet0p --minBosonPt 30 --inBins 25
python gen.py --era Run2018 --plot_directory gen --selection njet0p --minBosonPt 30 --inBins 25

python tom.py --plot_directory tom --era Run2016 --selection ptGamma30 
python tom.py --plot_directory tom --era Run2018 --selection ptGamma30 

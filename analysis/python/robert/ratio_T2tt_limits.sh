#!/bin/sh


#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met100-metSig3-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met100-metSig4-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met100-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met100-metSig6-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met120-metSig3-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met120-metSig4-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met120-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met140-metSig3-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met60-metSig3-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met60-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met60-metSig6-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met60-metSig7-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met60-metSig8-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met80-metSig3-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met80-metSig4-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met80-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met80-metSig6-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met80-metSig8-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root

#,MET>100,MetSig>5:/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met100-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root
#,MET>60,MetSig>5:/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met60-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root

python ratio_T2tt_limits.py --outfile=etc/MetMetSigText.png --files="/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met120-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root,/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met80-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root"
python ratio_T2tt_limits.py --outfile=etc/MetMetSigText.pdf --files="/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met120-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root,/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test3/isOS-nJets2p-nbtag1p-met80-metSig5-dPhiJet0-dPhiJet-mll20/limits/flavSplit_almostAllReg/T2tt_limitResults.root"

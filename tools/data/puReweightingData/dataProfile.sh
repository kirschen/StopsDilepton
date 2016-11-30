#!/bin/sh

PILEUP_LATEST=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt
JSON=Cert_271036-280385_13TeV_PromptReco_Collisions16_JSON.txt
LUMI=27000

if [ ! -f "$PILEUP_LATEST" ]; then
   echo "File $PILEUP_LATEST does not exist on this site, copying from lxplus"
   scp $USER@lxplus.cern.ch:$PILEUP_LATEST pileup_latest.txt
   PILEUP_LATEST=pileup_latest.txt
fi


pileupCalc.py -i $JSON --inputLumiJSON $PILEUP_LATEST --calcMode true --minBiasXsec 56700 --maxPileupBin 50 --numPileupBins 50 PU_2016_${LUMI}_XSecVDown.root
pileupCalc.py -i $JSON --inputLumiJSON $PILEUP_LATEST --calcMode true --minBiasXsec 59850 --maxPileupBin 50 --numPileupBins 50 PU_2016_${LUMI}_XSecDown.root
pileupCalc.py -i $JSON --inputLumiJSON $PILEUP_LATEST --calcMode true --minBiasXsec 63000 --maxPileupBin 50 --numPileupBins 50 PU_2016_${LUMI}_XSecCentral.root
pileupCalc.py -i $JSON --inputLumiJSON $PILEUP_LATEST --calcMode true --minBiasXsec 66150 --maxPileupBin 50 --numPileupBins 50 PU_2016_${LUMI}_XSecUp.root
pileupCalc.py -i $JSON --inputLumiJSON $PILEUP_LATEST --calcMode true --minBiasXsec 69300 --maxPileupBin 50 --numPileupBins 50 PU_2016_${LUMI}_XSecVUp.root

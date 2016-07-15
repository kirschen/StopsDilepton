#!/bin/sh
#python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger=HLT_mumuIso --sample=JetHT --minLeadingLeptonPt 0 &
#python triggerEff.py --mode=doubleEle   --baseTrigger="" --dileptonTrigger=HLT_ee_DZ --sample=JetHT --minLeadingLeptonPt 0 &
#python triggerEff.py --mode=muEle       --baseTrigger="" --dileptonTrigger=HLT_mue --sample=JetHT --minLeadingLeptonPt 0 &

python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger="HLT_mumuIso||HLT_mumuNoiso||HLT_SingleMu_noniso" --sample=MET --minLeadingLeptonPt 0 &
python triggerEff.py --mode=doubleEle   --baseTrigger="" --dileptonTrigger="HLT_ee_DZ||HLT_SingleEle_noniso" --sample=MET --minLeadingLeptonPt 0 &
python triggerEff.py --mode=muEle       --baseTrigger="" --dileptonTrigger="HLT_mue||HLT_SingleEle_noniso||HLT_SingleMu_noniso" --sample=MET --minLeadingLeptonPt 0 &

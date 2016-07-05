#!/bin/sh
python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger=HLT_mumuIso --sample=JetHT --minLeadingLeptonPt 0 &
python triggerEff.py --mode=doubleEle   --baseTrigger="" --dileptonTrigger=HLT_ee_DZ --sample=JetHT --minLeadingLeptonPt 0 &
python triggerEff.py --mode=muEle       --baseTrigger="" --dileptonTrigger=HLT_mue --sample=JetHT --minLeadingLeptonPt 0 &
python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger=HLT_mumuIso --sample=MET --minLeadingLeptonPt 0 &
python triggerEff.py --mode=doubleEle   --baseTrigger="" --dileptonTrigger=HLT_ee_DZ --sample=MET --minLeadingLeptonPt 0 &
python triggerEff.py --mode=muEle       --baseTrigger="" --dileptonTrigger=HLT_mue --sample=MET --minLeadingLeptonPt 0 &

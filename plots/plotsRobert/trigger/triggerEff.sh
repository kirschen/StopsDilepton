#!/bin/sh

#MuMu
# for measurement in MET/JetPD: (HLT_mumuIso||HLT_mumuNoiso||HLT_SingleMu_noniso)
#DoubleMuon (main):         HLT_mumuIso||HLT_mumuNoiso
#SingleMuon backup:         HLT_SingleMu_noniso&&(!(HLT_mumuIso||HLT_mumuNoiso))

#EE
# for measurement in MET/JetPD: (HLT_ee_DZ||HLT_ee_33||HLT_ee_33_MW||HLT_SingleEle_noniso)
# DoubleEG (main):          HLT_ee_DZ||HLT_ee_33||HLT_ee_33_MW
#SingleElectron backup:     HLT_SingleEle_noniso&&(!(HLT_ee_DZ||HLT_ee_33||HLT_ee_33_MW))

#EMu
# for measurement in MET/JetPD: (HLT_mue||HLT_mu30e30||HLT_SingleEle_noniso||HLT_SingleMu_noniso)
# MuonEG (main):            HLT_mue||HLT_mu30e30
# SingleElectron backup:    HLT_SingleEle_noniso && (!(HLT_mue||HLT_mu30e30))
# SingleMuon backup:        HLT_SingleMu_noniso && (!(HLT_mue||HLT_mu30e30)) && (!HLT_SingleEle_noniso)

#python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger="HLT_mumuIso" --sample=JetHT --minLeadingLeptonPt 0 &
#python triggerEff.py --mode=doubleEle   --baseTrigger="" --dileptonTrigger="HLT_ee_DZ" --sample=JetHT --minLeadingLeptonPt 0 &
#python triggerEff.py --mode=muEle       --baseTrigger="" --dileptonTrigger="HLT_mue" --sample=JetHT --minLeadingLeptonPt 0 &

#python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger="HLT_mumuIso||HLT_mumuNoiso||HLT_SingleMu_noniso" --sample=MET --minLeadingLeptonPt 0 &
#python triggerEff.py --mode=doubleEle   --baseTrigger="" --dileptonTrigger="HLT_ee_DZ||HLT_SingleEle_noniso" --sample=MET --minLeadingLeptonPt 0 &
#python triggerEff.py --mode=muEle       --baseTrigger="" --dileptonTrigger="HLT_mue||HLT_SingleEle_noniso||HLT_SingleMu_noniso" --sample=MET --minLeadingLeptonPt 0 &

#python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger="HLT_mumuIso" --sample=MET --minLeadingLeptonPt 0 
#python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger="HLT_mumuIso||HLT_mumuNoiso" --sample=MET --minLeadingLeptonPt 0 
#python triggerEff.py --mode=doubleEle   --baseTrigger="" --dileptonTrigger="HLT_ee_DZ" --sample=MET --minLeadingLeptonPt 0 
#python triggerEff.py --mode=muEle       --baseTrigger="" --dileptonTrigger="HLT_mue" --sample=MET --minLeadingLeptonPt 0 

python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger="HLT_mumuIso||HLT_mumuNoiso||HLT_SingleMu_noniso" --sample=MET --minLeadingLeptonPt 0 
python triggerEff.py --mode=doubleEle   --baseTrigger="" --dileptonTrigger="HLT_ee_DZ||HLT_ee_33||HLT_ee_33_MW||HLT_SingleEle_noniso" --sample=MET --minLeadingLeptonPt 0 
python triggerEff.py --mode=muEle       --baseTrigger="" --dileptonTrigger="HLT_mue||HLT_mu30e30||HLT_SingleEle_noniso||HLT_SingleMu_noniso" --sample=MET --minLeadingLeptonPt 0 

python triggerEff.py --mode=doubleMu    --baseTrigger="" --dileptonTrigger="HLT_mumuIso||HLT_mumuNoiso||HLT_SingleMu_noniso" --sample=JetHT --minLeadingLeptonPt 0 
python triggerEff.py --mode=doubleEle   --baseTrigger="" --dileptonTrigger="HLT_ee_DZ||HLT_ee_33||HLT_ee_33_MW||HLT_SingleEle_noniso" --sample=JetHT --minLeadingLeptonPt 0 
python triggerEff.py --mode=muEle       --baseTrigger="" --dileptonTrigger="HLT_mue||HLT_mu30e30||HLT_SingleEle_noniso||HLT_SingleMu_noniso" --sample=JetHT --minLeadingLeptonPt 0 

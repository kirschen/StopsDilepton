#!/bin/bash
cd "/user/tomc/StopsDilepton/CMSSW_7_6_3/src/StopsDilepton/plots/plotsTom"
source $VO_CMS_SW_DIR/cmsset_default.sh
eval `scram runtime -sh`
eval $command

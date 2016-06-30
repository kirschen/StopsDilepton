#!/bin/bash
cd "/user/tomc/StopsDilepton/CMSSW_8_0_10_patch2/src/StopsDilepton/plots/plotsTom"
source $VO_CMS_SW_DIR/cmsset_default.sh
eval `scram runtime -sh`
eval $command

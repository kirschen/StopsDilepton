#!/bin/bash
cd "/user/tomc/StopsDilepton/CMSSW_8_0_20/src/StopsDilepton/plots/plotsTom"
source $VO_CMS_SW_DIR/cmsset_default.sh
eval `scram runtime -sh`
eval $command

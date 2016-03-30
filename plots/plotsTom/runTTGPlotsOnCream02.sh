#!/bin/bash
source $VO_CMS_SW_DIR/cmsset_default.sh
cd /user/tomc/StopsDilepton/CMSSW_7_6_3/src/StopsDilepton/plots/plotsTom
eval `scram runtime -sh`
./ttG.py --zMode=$zMode --mode=$mode --logLevel=DEBUG

#!/bin/bash
echo "cmfPostProcessing of sample ${sample} in $cmssw"
pwd=$PWD
source $VO_CMS_SW_DIR/cmsset_default.sh
cd "/localgrid/$USER/cmgPostProcessing/${sample// /}/$cmssw/src/StopsDilepton/cmgPostProcessing/"
eval `scram runtime -sh`
python cmgPostProcessing.py --dataDir=/pnfs/iihe/cms/store/user/tomc/cmgTuples/763_4 --sample ${sample} --log=TRACE
cd /localgrid/$USER
rm -rf "/localgrid/$USER/cmgPostProcessing/${sample// /}"

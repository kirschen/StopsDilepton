#PBS -l nodes=1:ppn=1
#!/bin/bash
cd "/user/tomc/StopsDilepton/CMSSW_8_0_25/src/StopsDilepton/analysis/python/run"
source $VO_CMS_SW_DIR/cmsset_default.sh
eval `scram runtime -sh`
eval $command

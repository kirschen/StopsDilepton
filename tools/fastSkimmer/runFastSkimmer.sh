#PBS -l nodes=1:ppn=8
#!/bin/zsh
echo "Running fastSkimer"
echo "Id: $PBS_JOBID" >&2

cd /user/tomc/StopsDilepton/CMSSW_7_6_3/src/StopsDilepton/tools/fastSkimmer
source $VO_CMS_SW_DIR/cmsset_default.sh
eval `scram runtime -sh`
./fastSkimmer.py

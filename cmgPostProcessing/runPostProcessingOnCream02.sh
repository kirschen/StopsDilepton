#PBS -l nodes=1:ppn=8
#!/bin/bash
echo "cmgPostProcessing of sample ${sample} in $cmssw"
echo $TMPDIR
source $VO_CMS_SW_DIR/cmsset_default.sh
cd "/localgrid/$USER/cmgPostProcessing/$skim/${sample// /}/$cmssw/src/StopsDilepton/cmgPostProcessing/"
eval `scram runtime -sh`
python cmgPostProcessing.py --dataDir=/pnfs/iihe/cms/store/user/tomc/cmgTuples/763_4 --sample ${sample} --log=TRACE --skim=$skim --keepPhotons --minNJobs=8 --overwrite --targetDir=/user/tomc/StopsDilepton/data
cd /localgrid/$USER
rm -rf "/localgrid/$USER/cmgPostProcessing/$skim/${sample// /}"

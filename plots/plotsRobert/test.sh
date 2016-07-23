#! /bin/sh
#SBATCH -J PlotsRobert
#SBATCH -D /afs/hephy.at/work/r/rschoefbeck/CMS/tmp/CMSSW_8_0_10_patch2/src/StopsDilepton/plots/plotsRobert 
#SBATCH -o /afs/hephy.at/work/r/rschoefbeck/slurm/slurm-test.%j.out
eval `scram runtime -sh`
echo  CMSSW_BASE: $CMSSW_BASE



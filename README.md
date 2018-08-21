# Stops-dilepton. No CMG needed anymore.
```
cmsrel CMSSW_10_1_5
cd CMSSW_10_1_5/src
cmsenv
git cms-init
git clone https://github.com/HephySusySW/StopsDilepton
./StopsDilepton/setup101X.sh
```
# for OptiMass M2 variables
```
./StopsDilepton/setupOptiMass.sh
```

# Combine for limit setting
Make a 8_1_0 WS following the recipe at [HiggsCombination gitbook](https://cms-hcomb.gitbooks.io/combine/content/part1/)
```
export SCRAM_ARCH=slc6_amd64_gcc530
cmsrel CMSSW_8_1_0
cd CMSSW_8_1_0/src 
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit

cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v7.0.10
scramv1 b clean; scramv1 b # always make a clean build
```

# for impact studies
Inside the combine release location do
```
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester
scram b -j 6
```

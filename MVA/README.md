# Stops-dilepton + CMG in 80X
```
cmsrel CMSSW_8_0_26_patch1
cd CMSSW_8_0_26_patch1/src
cmsenv
git cms-init
git clone https://github.com/GhentAnalysis/StopsDilepton
./StopsDilepton/setupOptiMass.sh
./StopsDilepton/setup80X.sh
```
# for OptiMass M2 variables
```
./StopsDilepton/setupOptiMass.sh
```

# for limit setting
Make a 7_4_7 WS following the recipe at [SWGuideHiggsAnalysisCombinedLimit](https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideHiggsAnalysisCombinedLimit)
```
export SCRAM_ARCH=slc6_amd64_gcc491
cmsrel CMSSW_7_4_7
cd CMSSW_7_4_7/src 
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit

cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v6.3.1
scramv1 b clean; scramv1 b
```
# for impact studies
Inside the combine release location do
```
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester
scram b -j 6
```

# for MVA
```
cmsenv
./setPyMva.sh
```

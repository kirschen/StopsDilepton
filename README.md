# Stops-dilepton + CMG in 80X
```
cmsrel CMSSW_8_0_11
cd CMSSW_8_0_11/src
cmsenv
git cms-init
git clone https://github.com/GhentAnalysis/StopsDilepton
./StopsDilepton/setup80X.sh
```

# for limit setting
Make a 7_1_5 WS following the recipe at [SWGuideHiggsAnalysisCombinedLimit](https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideHiggsAnalysisCombinedLimit)
```
export SCRAM_ARCH=slc6_amd64_gcc481
cmsrel CMSSW_7_1_5 ### must be a 7_1_X release  >= 7_1_5;  (7.0.X and 7.2.X are NOT supported either) 
cd CMSSW_7_1_5/src 
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit

cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v5.0.1
scramv1 b clean; scramv1 b # always make a clean build, as scram doesn't always see updates to src/LinkDef.h
```

# Stops-dilepton 
```
cmsrel CMSSW_7_4_12_patch4
cd CMSSW_7_4_12_patch4/src
cmsenv
git cms-init
git clone -b 74X https://github.com/GhentAnalysis/StopsDilepton
git clone git@github.com:GhentAnalysis/PlotsSMS StopsDilepton/PlotsSMS #X-PAG code for limit
scram b -j9
```

# for CMG
see here:
https://twiki.cern.ch/twiki/bin/viewauth/CMS/CMGToolsReleasesExperimental#Git_MiniAOD_release_for_Summer_2

Minimal fetch of central and ghent fork (add new branches with the -t option):
```
git remote add cmg-central https://github.com/CERN-PH-CMG/cmg-cmssw.git  -f -t CMGTools-from-CMSSW_7_4_12 -t heppy_74X
git fetch cmg-central
git remote add cmg-ghent https://github.com/GhentAnalysis/cmg-cmssw.git -f -t CMGTools-from-CMSSW_7_4_12_LocalDevelopmentsPass2
git fetch cmg-ghent
```
sparse checkout (extra echos can be omitted)
```
cp /afs/cern.ch/user/c/cmgtools/public/sparse-checkout_7412_heppy .git/info/sparse-checkout
echo "/CMGTools/ObjectStudies/" >> .git/info/sparse-checkout
echo "/JetMETCorrections/Type1MET/" >> .git/info/sparse-checkout
echo "/PhysicsTools/PatAlgos/" >> .git/info/sparse-checkout
echo "/PhysicsTools/PatUtils/" >> .git/info/sparse-checkout
git read-tree -mu HEAD
```
configure local branch
```
git checkout -b CMGTools-from-CMSSW_7_4_12_LocalDevelopmentsPass2 cmg-ghent/CMGTools-from-CMSSW_7_4_12_LocalDevelopmentsPass2
git push -u cmg-ghent CMGTools-from-CMSSW_7_4_12_LocalDevelopmentsPass2
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

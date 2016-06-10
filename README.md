# Stops-dilepton + CMG in 80X
```
cmsrel CMSSW_8_0_10_patch2
cd CMSSW_8_0_10_patch2/src
cmsenv
git cms-init
git clone https://github.com/GhentAnalysis/StopsDilepton
./StopsDilepton/setup80X.sh
```

# Stops-dilepton in 76X 
```
cmsrel CMSSW_7_6_4
cd CMSSW_7_6_4/src
cmsenv
git cms-init
git clone https://github.com/GhentAnalysis/StopsDilepton
git clone git@github.com:GhentAnalysis/PlotsSMS StopsDilepton/PlotsSMS #X-PAG code for limit
scram b -j9
```

# for CMG in 76X
see here:
https://twiki.cern.ch/twiki/bin/viewauth/CMS/CMGToolsReleasesExperimental#Git_MiniAOD_release_for_Summer_2

[Untested in 76X] Minimal fetch of central and ghent fork (add new branches with the -t option):
```
git remote add cmg-central https://github.com/CERN-PH-CMG/cmg-cmssw.git  -f  -t heppy_76X

cp /afs/cern.ch/user/c/cmgtools/public/sparse-checkout_76X_heppy .git/info/sparse-checkout
echo /CommonTools/PileupAlgos/ >> .git/info/sparse-checkout
echo /CommonTools/Utils/ >> .git/info/sparse-checkout
echo /JetMETCorrections/Configuration/ >> .git/info/sparse-checkout
echo /JetMETCorrections/Modules/ >> .git/info/sparse-checkout
echo /JetMETCorrections/Type1MET/ >> .git/info/sparse-checkout
echo /PhysicsTools/PatAlgos/ >> .git/info/sparse-checkout
echo /PhysicsTools/PatUtils/ >> .git/info/sparse-checkout
echo /RecoMET/METAlgorithms/ >> .git/info/sparse-checkout
echo /RecoMET/METProducers/ >> .git/info/sparse-checkout
git checkout -b heppy_76X cmg-central/heppy_76X

git remote add origin git@github.com:GhentAnalysis/cmg-cmssw.git
git push -u origin heppy_76X_StopsDilepton #This has merged: https://github.com/mariadalfonso/cmg-cmssw.git:heppy_76X_metTool
git clone -o cmg-central https://github.com/CERN-PH-CMG/cmgtools-lite.git -b 76X  CMGTools
cd CMGTools 

git remote add origin  git@github.com:GhentAnalysis/cmgtools-lite.git 
git push -u origin 76X

git fetch origin
git checkout -b 76X_StopsDilepton origin/76X_StopsDilepton

#compile
cd $CMSSW_BASE/src && scram b -j 8
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

# 
# Recipe to continue the setup of our 80X analysis after the checkout of StopsDilepton package
#
eval `scram runtime -sh`
cd $CMSSW_BASE/src

# 
# X-PAG code for limit
#
git clone git@github.com:GhentAnalysis/PlotsSMS StopsDilepton/PlotsSMS
scram b -j9

#
# Setting up CMG
#
git remote add cmg-central https://github.com/CERN-PH-CMG/cmg-cmssw.git -f -t heppy_80X
cp StopsDilepton/.sparse-checkout .git/info/sparse-checkout
git checkout -b heppy_80X cmg-central/heppy_80X

# add your mirror, and push the 80X branch to it
git remote add origin git@github.com:GhentAnalysis/cmg-cmssw.git
git push -u origin heppy_80X

# now get the CMGTools subsystem from the cmgtools-lite repository
git clone -o cmg-central https://github.com/CERN-PH-CMG/cmgtools-lite.git -b 80X CMGTools
cd CMGTools 

# add your fork, and push the 80X branch to it
git remote add origin git@github.com:GhentAnalysis/cmgtools-lite.git 
git push -u origin 80X_StopsDilepton

git fetch origin
git checkout -b 80X_StopsDilepton origin/80X_StopsDilepton

#compile
cd $CMSSW_BASE/src && scram b -j 8 

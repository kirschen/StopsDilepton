# 
# Recipe to continue the setup of our 80X analysis after the checkout of StopsDilepton package
#
eval `scram runtime -sh`
cd $CMSSW_BASE/src

# 
# X-PAG code for limit
#
git clone https://github.com/GhentAnalysis/PlotsSMS StopsDilepton/PlotsSMS.git
git clone https://github.com/schoef/RootTools.git
scram b -j9

cd $CMSSW_BASE/src
git fetch origin
git checkout -b 80X_StopsDilepton origin/101X

#compile
cd $CMSSW_BASE/src && scram b -j 8 

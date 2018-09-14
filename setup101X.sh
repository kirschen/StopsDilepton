# 
# Recipe to continue the setup of our 80X analysis after the checkout of StopsDilepton package
#
eval `scram runtime -sh`
cd $CMSSW_BASE/src

# nanoAOD tools
git clone https://github.com/danbarto/nanoAOD-tools.git PhysicsTools/NanoAODTools
cd $CMSSW_BASE/src

# 
# X-PAG code for limit
#
git clone https://github.com/GhentAnalysis/PlotsSMS StopsDilepton/PlotsSMS.git
cd $CMSSW_BASE/src

# RootTools
git clone https://github.com/danbarto/RootTools.git
cd $CMSSW_BASE/src

scram b -j9

cd $CMSSW_BASE/src
git fetch origin
git checkout -b 80X_StopsDilepton origin/101X

#compile
cd $CMSSW_BASE/src && scram b -j 8 

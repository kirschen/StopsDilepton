# Stops-dilepton. No CMG needed anymore.

```
cmsrel CMSSW_10_2_9
cd CMSSW_10_2_9/src
cmsenv
git cms-init
git clone https://github.com/HephyAnalysisSW/StopsDilepton
./StopsDilepton/setup102X.sh
```

VERY IMPORTANT: if you use the MVA, run `MVA/setPyMva.sh` or best, add it to your bash profile.

# for CTPPS reconstruction
```
git remote add hephy https://github.com/HephyAnalysisSW/cmssw.git
git fetch hephy
git cms-addpkg \
CondFormats/CTPPSOpticsObjects \
DataFormats/ProtonReco \
IOMC/EventVertexGenerators \
IOMC/ParticleGuns \
RecoCTPPS/ProtonReconstruction \
RecoCTPPS/TotemRPLocal \
SimCTPPS/OpticsParameterisation \
Validation/CTPPS
git checkout -b ctpps_initial_proton_reconstruction_CMSSW_10_2_0 hephy/ctpps_initial_proton_reconstruction_CMSSW_10_2_0
```

# for impact studies
Inside the combine release location do
```
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester
scram b -j 6
```

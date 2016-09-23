#!/bin/sh

#Tom, if you see this you probably cry. Feel free to make it a nice install script

OPTIMASS=OptiMass-v1.0.3
EXROOT=ExRootAnalysis_V1.1.2

# Set up ExRootAnalysis -> only used because it is necessary to compile the Optimass main program (which is not ued)
cd $CMSSW_BASE/tmp
wget http://madgraph.physics.illinois.edu/Downloads/ExRootAnalysis/${EXROOT}.tar.gz
tar -xzvf ${EXROOT}.tar.gz
cd ExRootAnalysis
make

# Download Optimass
cd $CMSSW_BASE/src
wget http://hep-pulgrim.ibs.re.kr/optimass/download/${OPTIMASS}.tar.gz
tar -xvzf ${OPTIMASS}.tar.gz
cd ${OPTIMASS}
sed -i "s/#EXROOT :=/EXROOT=\${CMSSW_BASE}\/tmp\/ExRootAnalysis#/" Makefile
cd alm_base 
sed -i "s/ROOTDIR2=.*/ROOTDIR2=\$ROOTDIR1/g" configure
export LD_LIBRARY_PATH=$CMSSW_BASE/src/ExRootAnalysis/:$CMSSW_BASE/src/OptiMass-v1.0.3/lib/:$LD_LIBRARY_PATH


./configure   # Configuring the build environment
make 
make install

cd $CMSSW_BASE/src/${OPTIMASS}
make

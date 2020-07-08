#!/bin/bash

#
# Example of usage:
# submitCondor.py --execFile submit_on_lxplus.sh --queue nextweek nanoPostProcessing_Summer16_private.sh
# submitCondor.py --execFile THISFILE (setup for condor environment) --queue NAMEofCONDORQUEUE fileWithCommands.sh
#

export USER=$(whoami)
initial="$(echo $USER | head -c 1)"
export SCRAM_ARCH=slc6_amd64_gcc630

echo "---------------------"
echo "Grid certificate 1"
voms-proxy-info --all
echo "---------------------"
echo "Current dir: `pwd`"
ls -l
echo "---------------------"
export HOME=`pwd`
echo "Current home dir: ${HOME}"
echo "---------------------"

scram project CMSSW CMSSW_10_2_9
cd CMSSW_10_2_9/src/
eval `scramv1 runtime -sh`
# github repos
git cms-init
git clone -b '101X' --single-branch --depth 1 https://github.com/kirschen/StopsDilepton.git
./StopsDilepton/setupCondor.sh

scram b
eval `scramv1 runtime -sh`

echo "---------------------"
echo "Current dir: `pwd`"
ls -l
echo "---------------------"

#echo "---------------------"
#echo "Using hephy token: /afs/cern.ch/user/${initial}/${USER}/private/kerberos/krb5_token_hephy.at"
#export KRB5CCNAME=/afs/cern.ch/user/${initial}/${USER}/private/kerberos/krb5_token_hephy.at
#aklog -d hephy.at
#echo "---------------------"

echo "---------------------"
echo "Changing to script dir: ../$1/"
cd ../$1/
ls -l
echo "---------------------"

echo "Executing:"
echo ${@:2} --runOnLxPlus 
#echo ${@:2} --runOnLxPlus --writeToDPM
echo "---------------------"

${@:2} --runOnLxPlus 
#${@:2} --runOnLxPlus --writeToDPM

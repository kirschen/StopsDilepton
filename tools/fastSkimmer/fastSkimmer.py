#! /usr/bin/env python

#
# Small fast script which does additional skims on already postprocessed samples
# Takes into account systematics when skimming on jet variables
#

from ROOT import TFile, TTree
from collections import defaultdict
import os

import StopsDilepton.tools.logger as logger
log = logger.get_logger("DEBUG")

def skimmer(input, output):
  inputFile  = TFile(input)
  outputFile = TFile(output,"RECREATE")

  inputTree = inputFile.Get("Events")
  if not inputTree:
    log.warn("No Events tree found, aborting")
    return False

  outputFile.cd()
  outputTree = inputTree.CloneTree(0)

  # Vars needed to skim on
  #varsToSkim = ["met_pt","nJetGood"]
  varsToSkim = ["nJetGood"]

  # Take variants/systematics into account (i.e. _photonEstimated, _JECUp, _JECDown,... etc)
  allVariants = defaultdict(list)
  for branch in inputTree.GetListOfBranches():
    for var in varsToSkim:
      if branch.GetName().startswith(var):
        allVariants[var].append(branch.GetName())


  log.info("Variants checked for skimming:")
  for var in allVariants:
    log.info(var + " --> " + str(allVariants[var]))
    
  for i in range(inputTree.GetEntries()):
    inputTree.GetEntry(i)
    maxVar = {}
    for var in allVariants:
      maxVar[var] = max((getattr(inputTree, x)) for x in allVariants[var])
#    if maxVar['met_pt'] > 80 and maxVar['nJetGood'] >= 2: 						# Fill when any of the MET variables surpasses 80 and at least two jets
    if maxVar['nJetGood'] > 2:			 							# Fill when at least three jets
      outputTree.Fill() 
  outputTree.AutoSave()
  outputFile.Close()
  inputFile.Close()
  return True

base = "/user/tomc/StopsDilepton/data/postProcessed_Fall15_mAODv2/"
basicSkim = "dilepTiny"
dirs = os.walk(base + basicSkim)

def wrapper(i):
  for j in i[2]:
    if j.endswith('.root'):
      input  = os.path.join(i[0], j)
      output = os.path.join(i[0].replace(basicSkim, basicSkim+"_3jet"), j)
      if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))
      if not os.path.exists(output):
        log.info("Skimming " + input)
        skimmer(input, output)
      else:
        log.info("Skipping " + input + " because " + output + " does already exists")

from multiprocessing import Pool
pool = Pool( 8 )
results = pool.map(wrapper, dirs)
pool.close()

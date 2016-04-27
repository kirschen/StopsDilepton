#! /usr/bin/env python

#
# To split up cmgPostProcessed samples according to their TTGJetsEventType such that you can show the sample split up
#


from ROOT import TFile, TTree
import os

import StopsDilepton.tools.logger as logger
log = logger.get_logger("DEBUG")

def filter(input, output, eventType):
  inputFile  = TFile(input)
  outputFile = TFile(output,"RECREATE")

  inputTree = inputFile.Get("Events")
  if not inputTree:
    log.warn("No Events tree found, aborting")
    return False

  outputFile.cd()
  outputTree = inputTree.CloneTree(0)

  for i in range(inputTree.GetEntries()):
    inputTree.GetEntry(i)
    if inputTree.TTGJetsEventType == eventType:								# Fill for given eventType
      outputTree.Fill() 
  outputTree.AutoSave()
  outputFile.Close()
  inputFile.Close()
  return True

base = "/user/tomc/StopsDilepton/data/postProcessed_Fall15_mAODv2/dilepTiny_new/"
for sampleDir in ["TTGJets", "TTJets_comb"]:
  for eventType in range(5):
    for j in os.listdir(os.path.join(base, sampleDir)):
      print j
      if j.endswith('.root'):
	input  = os.path.join(base, sampleDir, j)
	output = os.path.join(base, sampleDir + "_TTGJetsEventType" + str(eventType), j)
	if not os.path.exists(os.path.dirname(output)):
	  os.makedirs(os.path.dirname(output))
	if not os.path.exists(output):
	  log.info("Filtering TTGJetsEventType " + str(eventType) + " from " + input)
	  filter(input, output, eventType)
	else:
	  log.info("Skipping " + input + " because " + output + " does already exists")

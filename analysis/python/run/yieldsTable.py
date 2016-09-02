#!/usr/bin/env python
import os
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--metSigMin",      action='store', default=5,                   type=int,                                                                                                         help="metSigMin?")
argParser.add_argument("--metMin",         action='store', default=80,                  type=int,                                                                                                         help="metMin?")
argParser.add_argument("--regions",        action='store', default='regions80X',        nargs='?', choices=["superRegion","superRegion140"],                                                              help="which regions setup?")
argParser.add_argument("--signal",         action='store', default='T2tt',              nargs='?', choices=["T2tt","DM"],                                                                                 help="which signal?")
argParser.add_argument("--estimates",      action='store', default='mc',                nargs='?', choices=["mc","dd"],                                                                                   help="mc estimators or data-driven estimators?")
argParser.add_argument("--onlyStat",       action='store_true', default=False,          help="show only stat errors?")
args = argParser.parse_args()

from StopsDilepton.analysis.SetupHelpers    import allChannels, channels
from StopsDilepton.analysis.estimators      import setup, constructEstimatorList, MCBasedEstimate
from StopsDilepton.analysis.DataObservation import DataObservation
from StopsDilepton.analysis.SumEstimate     import SumEstimate
from StopsDilepton.analysis.regions         import regions80X, superRegion, superRegion140
from StopsDilepton.analysis.Cache           import Cache

# Logging
import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )

setup.verbose = False
setup.parameters['metMin']    = args.metMin
setup.parameters['metSigMin'] = args.metSigMin

if   args.regions == "regions80X":        regions = regions80X
elif args.regions == "superRegion":       regions = superRegion
elif args.regions == "superRegion140":    regions = superRegion140
else: raise Exception("Unknown regions setup")

if   args.estimates == "mc": estimators = constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'TTXNoZ'])
elif args.estimates == "dd": estimators = constructEstimatorList(["TTJets-DD","TTZ-DD-Top16009","DY-DD", 'multiBoson-DD', 'TTXNoZ'])
summedEstimate = SumEstimate(name="sum" if args.estimates == "mc" else "sum_dd")

DYestimators = constructEstimatorList(["DY", "DY-DD"])
observation = DataObservation(name='Data', sample=setup.sample['Data'])

from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed    import *
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
signalEstimator = [MCBasedEstimate(name=s.name,  sample={channel:s for channel in allChannels}, cacheDir=setup.defaultCacheDir() ) for s in ([T2tt_450_1] if args.signal == "T2tt" else [TTbarDMJets_scalar_Mchi1_Mphi100])][0]
signalEstimator.isSignal=True


setup.verbose = False
setup.parameters['metMin']    = args.metMin
setup.parameters['metSigMin'] = args.metSigMin

signalSetup = setup.sysClone(isSignal=(args.signal=="T2tt")) # little hack for the old trees

for e in estimators + [summedEstimate, observation] + DYestimators + [signalEstimator]:
    e.initCache(setup.defaultCacheDir())

from StopsDilepton.analysis.u_float                                           import u_float
from math                                                                     import sqrt


texdir  = os.path.join(setup.analysis_results, setup.prefix(), 'tables' + ("_dd" if args.estimates == "dd" else ""), args.regions, args.signal)

try:    os.makedirs(texdir)
except: pass


for channel in allChannels:
  try:    os.makedirs(os.path.join(texdir, channel))
  except: pass

  yieldTexfile = os.path.join(texdir, channel, "yields_onlyStat.tex" if args.onlyStat else "yields.tex")
  print "Writing to " + yieldTexfile
  with open(yieldTexfile, "w") as yieldTable:
    yieldTable.write("\\begin{tabular}{c||" + "c|"*len(estimators) + "|c||c||c} \n")
    yieldTable.write("  signal region & " + "& ".join([e.getTexName(channel, rootTex=False) for e in estimators]) + "& signal & total & observed \\\\ \n")
    yieldTable.write("  \\hline \n")

    ttJetsErr = None
    ttzErr    = None
    dyErr     = None
                 
    for i, r in enumerate(regions[1:]):
      yieldTable.write(" $" + str(i) + "$ ")
      
      for e in estimators + [signalEstimator, summedEstimate]:

	expected = int(100*e.cachedEstimate(r, channel, signalSetup if e.name.count('T2tt') else setup).val+0.5)/100.
        stat     = int(100*e.cachedEstimate(r, channel, signalSetup if e.name.count('T2tt') else setup).sigma+0.99)/100.

        if args.onlyStat: 
          yieldTable.write(" & $ %.2f \pm %.2f $" % (expected, stat))
        elif e == signalEstimator:
          yieldTable.write(" & $ %.2f $" % (expected))
        else:
	  if e.name.count("TTJets"): ttJetsErr = expected*(0.3 if i < 6 else 0.2 if i < 12 else 1)	# these should be absolute errors, because we will propagate it also to the sum
	  if e.name.count("TTZ"):    ttzErr    = expected*0.2
	  if e.name.count("DY"):     
	#    mc    = int(100*DYestimators[0].cachedEstimate(r, channel, setup).val+0.5)/100.
	#    dd    = int(100*DYestimators[1].cachedEstimate(r, channel, setup).val+0.5)/100.
	#    dyErr = abs(mc-dd)
	     dyErr = expected*0.5 #just assign 50% error
	  if e.name.count("multiBoson"): multiBosonErr = expected*0.25
	  if e.name.count("TTXNoZ"):     ttxErr        = expected*0.25

	  errors   = [stat/expected if expected > 0 else 0]
	  errors.append(e.PUSystematic(         r, channel, setup).val)
	  errors.append(e.JECSystematic(        r, channel, setup).val)
	  errors.append(e.topPtSystematic(      r, channel, setup).val)
	  errors.append(e.btaggingSFbSystematic(r, channel, setup).val)
	  errors.append(e.btaggingSFlSystematic(r, channel, setup).val)
	  if e.name.count("sum") or e.name.count("TTJets"):     errors.append(ttJetsErr/expected     if expected > 0 else 0) # Now to relative errors in order to combine with other errors
	  if e.name.count("sum") or e.name.count("TTZ"):        errors.append(ttzErr/expected        if expected > 0 else 0)
	  if e.name.count("sum") or e.name.count("DY"):         errors.append(dyErr/expected         if expected > 0 else 0)
	  if e.name.count("sum") or e.name.count("TTXNoZ"):     errors.append(ttxErr/expected        if expected > 0 else 0)
	  if e.name.count("sum") or e.name.count("multiBoson"): errors.append(multiBosonErr/expected if expected > 0 else 0)

          totalError = sqrt(sum([err*err for err in errors]))
	  yieldTable.write(" & $ %.2f \pm %.2f $" % (expected, totalError*expected))              # And back to absolute error
 
      observed = observation.cachedObservation(r, channel, setup).val
      yieldTable.write(" & %d \\\\ \n" % observed)

    yieldTable.write("\\end{tabular} \n")
    yieldTable.write("\\caption{Yields and uncertainties for each background and their sum in channel " + channel + (" (stat only)" if args.onlyStat else "") + "} \n")

#!/usr/bin/env python
from StopsDilepton.analysis.Region import Region
from StopsDilepton.analysis.estimators import setup, DataDrivenDYEstimate
from StopsDilepton.analysis.regions import regions80X
import os

import StopsDilepton.tools.logger as logger
logger = logger.get_logger("DEBUG", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("DEBUG", logFile = None )


modifiers = [ {},
#             {'reweight':['reweightPUUp']},
#             {'reweight':['reweightPUDown']},
#             {'reweight':['reweightTopPt']},
#             {'selectionModifier':'JERUp'},
#             {'selectionModifier':'JERDown'},
#             {'selectionModifier':'JECVUp'},
#             {'selectionModifier':'JECVDown'},
#             {'reweight':['reweightLeptonFastSimSFUp']},
#             {'reweight':['reweightLeptonFastSimSFDown']},
#             {'reweight':['reweightBTag_SF']},
#             {'reweight':['reweightBTag_SF_b_Down']},
            ]

selections = [ "met50", "met80",
               "met50\\_metSig5", "met80\\_metSig5",
               "met50\\_dPhiInv", "met80\\_dPhiInv",
               "met50\\_metSig5\\_dPhi", "met80\\_metSig5\\_dPhi",
               "met50\\_metSig5\\_dPhiInv", "met80\\_metSig5\\_dPhiInv"]

texdir = os.path.join(setup.analysis_results, setup.prefix(), 'tables')
try:
  os.makedirs(texdir)
except:
  pass 

columns = ["DY","TTJets","multiBoson","TTX","observed","scale factor", "DY purity"]
texfile = os.path.join(texdir, "DY_scalefactors.tex")
with open(texfile, "w") as table:
  table.write("\\begin{tabular}{l|c" + "c"*len(columns) + "} \n")
  table.write("  selection & " + "&".join(columns) + " \\\\ \n")
  table.write("  \\hline \n")
  for selection in selections:
    logger.info("Getting scalefactor for " + selection)
    metMin     = 80 if selection.count("met80") else 50 if selection.count("met50") else 0
    metSigMin  = 5 if selection.count("metSig") else 0
    dPhi       = selection.count("dPhi") and not selection.count("dPhiInv")
    dPhiInv    = selection.count("dPhiInv")
    estimateDY = DataDrivenDYEstimate(name='DY-DD', cacheDir=None, controlRegion=Region('dl_mt2ll', (100,-1)), dPhi=dPhi, dPhiInv=dPhiInv, metMin=metMin, metSigMin=metSigMin)
    estimateDY.initCache(setup.defaultCacheDir())

    for channel in ['MuMu']:  # is the same for EE
      for r in [Region('dl_mt2ll', (100,-1))]:  # also the same in each applied region because we use a controlRegion
        for modifier in modifiers:
  	  (yields, data, scaleFactor) = estimateDY._estimate(r, channel, setup.sysClone(modifier), returnScaleFactor=True)
          table.write(selection + " & "+ " & ".join([("%.2f" % yields[s].val) for s in ['DY','TTJets','multiBoson','TTX']]) + " & " + "%d" % data.val)
          table.write("& $%.2f\pm%.2f$" % (scaleFactor.val, scaleFactor.sigma))
          table.write(" & $%.0f\\%%$" % (100*yields['DY'].val/sum(yields[s].val for s in ['DY','TTJets','multiBoson','TTX'])))
          table.write("\\\\ \n")
  table.write("\\end{tabular} \n")

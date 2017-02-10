#!/usr/bin/env python
from StopsDilepton.analysis.Region import Region
from StopsDilepton.analysis.estimators import setup, DataDrivenDYEstimate, DataDrivenMultiBosonEstimate
import os

import StopsDilepton.tools.logger as logger
logger = logger.get_logger("INFO", logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger("INFO", logFile = None )


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

selections = [ 
#               ("met50",                 "$\\met > 50$ GeV"),
#               ("met80",                 "$\\met > 80$ GeV"),
#               ("met50_metSig5",         "$\\met > 50$ GeV, $\\metSig > 5$"),
#               ("met80_metSig5",         "$\\met > 80$ GeV, $\\metSig > 5$"),
#               ("met50_dPhiInv",         "$\\met > 50$ GeV, inv. $\\Delta\\phi$"),
#               ("met80_dPhiInv",         "$\\met > 80$ GeV, inv. $\\Delta\\phi$"),
#               ("met50_metSig5_dPhi",    "$\\met > 50$ GeV, $\\metSig > 5, \\Delta\\phi$"),
               ("met80_metSig5_dPhi",    "$\\met > 80$ GeV, $\\metSig > 5, \\Delta\\phi$"),
#               ("met50_metSig5_dPhiInv", "$\\met > 50$ GeV, $\\metSig > 5$, inv. $\\Delta\\phi$"),
               ("met80_metSig5_dPhiInv", "$\\met > 80$ GeV, $\\metSig > 5$, inv. $\\Delta\\phi$")
             ]

texdir = os.path.join(setup.analysis_results, setup.prefix(), 'tables')
try:
  os.makedirs(texdir)
except:
  pass 

columns = ["DY","TTJets","multiBoson","TTZ","TTXNoZ","observed","scale factor", "DY purity"]
texfile = os.path.join(texdir, "scalefactorsDY.tex")
with open(texfile, "w") as table:
  table.write("\\begin{tabular}{l|c" + "c"*len(columns) + "} \n")
  table.write("  selection & " + "&".join(columns) + " \\\\ \n")
  table.write("  \\hline \n")
  for selection, tex in selections:
    logger.info("Getting scalefactor for " + selection)
    metMin     = 80 if selection.count("met80") else 50 if selection.count("met50") else 0
    metSigMin  = 5 if selection.count("metSig") else 0
    dPhi       = selection.count("dPhi") and not selection.count("dPhiInv")
    dPhiInv    = selection.count("dPhiInv")
    estimateDY = DataDrivenDYEstimate(name='DY-DD', cacheDir=None, controlRegion=Region('dl_mt2ll', (100,-1)), dPhi=dPhi, dPhiInv=dPhiInv, metMin=metMin, metSigMin=metSigMin)
    estimateDY.initCache(setup.defaultCacheDir())

    for channel in ['MuMu']:  # is the same for EE
      for r in [Region('dl_mt2ll', (100,-1))]:  # also the same in each applied region because we use a control
        for modifier in modifiers:
  	  (yields, data, scaleFactor) = estimateDY._estimate(r, channel, setup.sysClone(modifier), returnScaleFactor=True)
          table.write("  " + tex + " & "+ " & ".join([("%.2f" % yields[s].val) for s in ['DY','TTJets','multiBoson','TTZ','TTXNoZ']]) + " & " + "%d" % data.val)
          table.write("& $%.2f\pm%.2f$" % (scaleFactor.val, scaleFactor.sigma))
          table.write(" & $%.0f\\%%$" % (100*yields['DY'].val/sum(yields[s].val for s in ['DY','TTJets','multiBoson','TTZ','TTXNoZ'])))
          table.write("\\\\ \n")
  table.write("\\end{tabular} \n")




columns = ["multiBoson","TTJets","DY (DD)","TTZ","TTXNoZ","observed","scale factor", "multiBoson purity"]
texfile = os.path.join(texdir, "scalefactorsMultiBoson.tex")
with open(texfile, "w") as table:
  table.write("\\begin{tabular}{l|c" + "c"*len(columns) + "} \n")
  table.write("  selection & " + "&".join(columns) + " \\\\ \n")
  table.write("  \\hline \n")
  for selection, tex in selections:
    logger.info("Getting scalefactor for " + selection)
    metMin     = 80 if selection.count("met80") else 50 if selection.count("met50") else 0
    metSigMin  = 5 if selection.count("metSig") else 0
    dPhi       = selection.count("dPhi") and not selection.count("dPhiInv")
    dPhiInv    = selection.count("dPhiInv")
    estimateDY = DataDrivenDYEstimate(name='DY-DD', cacheDir=None, controlRegion=Region('dl_mt2ll', (100,-1)))
    estimateMB = DataDrivenMultiBosonEstimate(name='multiBoson-DD', cacheDir=None, controlRegion=Region('dl_mt2ll', (100,-1)), dPhi=dPhi, dPhiInv=dPhiInv, metMin=metMin, metSigMin=metSigMin)
    estimateMB.initCache(setup.defaultCacheDir())

    for channel in ['MuMu']:  # is the same for EE
      for r in [Region('dl_mt2ll', (100,-1))]:  # also the same in each applied region because we use a controlRegion
        for modifier in modifiers:
  	  (yields, data, scaleFactor) = estimateMB._estimate(r, channel, setup.sysClone(modifier), returnScaleFactor=True, estimateDY=estimateDY)
          table.write("  " + tex + " & "+ " & ".join([("%.2f" % yields[s].val) for s in ['multiBoson','TTJets','DY-DD','TTZ','TTXNoZ']]) + " & " + "%d" % data.val)
          table.write("& $%.2f\pm%.2f$" % (scaleFactor.val, scaleFactor.sigma))
          table.write(" & $%.0f\\%%$" % (100*yields['multiBoson'].val/sum(yields[s].val for s in ['multiBoson','TTJets','DY-DD','TTZ','TTXNoZ'])))
          table.write("\\\\ \n")
  table.write("\\end{tabular} \n")

#!/usr/bin/env python

from math import sqrt, cos, sin, pi
import os

from optparse import OptionParser
parser = OptionParser()
#parser.add_option("--year",       dest="year",                  default=2016, type="int",    action="store",      help="Which year?")
parser.add_option('--logLevel',   dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])

(options, args) = parser.parse_args()

from StopsDilepton.analysis.SetupHelpers import channels, allChannels, trilepChannels
from StopsDilepton.analysis.estimators   import *
from StopsDilepton.analysis.regions      import regionsLegacy, noRegions, regions2016

# Logging
import Analysis.Tools.logger as logger
logger  = logger.get_logger(options.logLevel, logFile = None)

import StopsDilepton.tools.logger as logger
logger = logger.get_logger(options.logLevel, logFile = None )
import Analysis.Tools.logger as logger_an
logger_an = logger_an.get_logger(options.logLevel, logFile = None )
import RootTools.core.logger as logger_rt
logger_rt = logger_rt.get_logger('INFO', logFile = None )

from StopsDilepton.analysis.Setup import Setup

#analysis_results        = '/afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v5/'

all_regions = regionsLegacy

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.analysis.DataObservation import DataObservation

# Syntax: ('sys', correlated?)
systematic_uncertainties_list = [\
('PU',  True ),
('JER', False ),
('JEC', True ),
('topPt', True ),
('unclustered', False ),
#('leptonFS',True ),
#('L1Prefire',True ),
('btaggingSFb', False ),
('btaggingSFl', False ),
#('btaggingSFFS',True ),
('leptonSF', True ),
('trigger', True ),
#('fastSimMET',True ),
#('fastSimPU',True ),
]

channels =  ['SF','EMu', 'all']
years    =  [2016, 2017, 2018]
lumis    =  [35.9, 41.5, 60.0]

yield_data          = {}
for year in years:
    setup           = Setup(year=year)
    setup           .verbose = True
    estimators      = estimatorList(setup)
    bkg_estimators  = estimators.constructEstimatorList(["TTJets", "TTZ", "DY", 'multiBoson', 'other'])
    all_estimators  = bkg_estimators

    for estimator in all_estimators:
        estimator.initCache(setup.defaultCacheDir())

    yield_data[year] = {}
    for (i_region, region) in enumerate(all_regions):
        for channel in channels:
            logger.info( " At Region %s | %s ", channel, region )
            yield_data[year][(region, channel)] = {}
            yield_data[year][(region, channel)]['ref'] = sum(e.cachedEstimate(region, channel, setup) for e in bkg_estimators)

            up   = {sys:0. for sys, _ in systematic_uncertainties_list}
            down = {sys:0. for sys, _ in systematic_uncertainties_list}
     
            for e in bkg_estimators:
                if year == 2018:
                    up   ['PU']+= e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightPUVVUp']}))
                    down ['PU']+= e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightPUUp']}))
                else: 
                    up   ['PU']+= e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightPUUp']}))
                    down ['PU']+= e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightPUDown']}))
                    #sys = e.PUSystematic(r, channel, setup).val

                up  ['JER']    += e.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'jerUp'}))
                down['JER']    += e.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'jerDown'}))
                #syst_tuple = e.JERSystematicAsym(region, channel, setup)
                #sys = max(abs(syst_tuple[0]-1), abs(syst_tuple[1]-1)) if syst_tuple[0] != 0. or syst_tuple[1] != 0. else 0.
                up  ['JEC']    += e.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'jesTotalUp'}))
                down['JEC']    += e.cachedEstimate(region, channel, setup.sysClone({'selectionModifier':'jesTotalDown'}))
                #syst_tuple = e.JECSystematicAsym(region, channel, setup)
                #sys = max(abs(syst_tuple[0]-1), abs(syst_tuple[1]-1)) if syst_tuple[0] != 0. or syst_tuple[1] != 0. else 0.
                up  ['topPt']  += e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightTopPt']}))
                down['topPt']  += e.cachedEstimate(region, channel, setup)
                #sys = e.topPtSystematic(region, channel, setup).val
                up  ['unclustered'] += e.cachedEstimate(region, 'all', setup.sysClone({'selectionModifier':'unclustEnUp'}))
                down['unclustered'] += e.cachedEstimate(region, 'all', setup.sysClone({'selectionModifier':'unclustEnDown'}))
                #sys = max(abs(syst_tuple[0]-1), abs(syst_tuple[1]-1)) if syst_tuple[0] != 0. or syst_tuple[1] != 0. else 0.
                up  ['btaggingSFb'] += e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Up']}))
                down['btaggingSFb'] += e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Down']}))
                #sys = e.btaggingSFbSystematic(region, channel, setup).val
                up  ['btaggingSFl'] += e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Up']}))
                down['btaggingSFl'] += e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Down']}))
                #sys = e.btaggingSFlSystematic(region, channel, setup).val
                up  ['leptonSF']    += e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonSFUp']}))
                down['leptonSF']    += e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightLeptonSFDown']}))
                #sys = e.leptonSFSystematic(region, channel, setup).val
                up  ['trigger']     += e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightDilepTriggerUp']}))
                down['trigger']     += e.cachedEstimate(region, channel, setup.sysClone({'reweight':['reweightDilepTriggerDown']}))
                #sys = e.triggerSystematic(region, channel, setup).val

            yield_data[year][(region, channel)]['up']   = up 
            yield_data[year][(region, channel)]['down'] = down

# adding up across years
yield_data["RunII"] = {}
for (i_region, region) in enumerate(all_regions):
    for channel in channels:
        yield_data["RunII"][(region, channel)] = {}
        yield_data["RunII"][(region, channel)]['ref']  = 0.  
        yield_data["RunII"][(region, channel)]['up']   = {sys:0. for sys, _ in systematic_uncertainties_list} 
        yield_data["RunII"][(region, channel)]['down'] = {sys:0. for sys, _ in systematic_uncertainties_list}
        for year in years:
            yield_data["RunII"][(region, channel)]['ref'] += yield_data[year][(region, channel)]['ref']  
            for sys, _ in systematic_uncertainties_list:
                yield_data["RunII"][(region, channel)]['up'][sys]   += yield_data[year][(region, channel)]['up'][sys] 
                yield_data["RunII"][(region, channel)]['down'][sys] += yield_data[year][(region, channel)]['down'][sys] 

# computing systematics and the correlated RunII ones
sys_data  = {}
for year in years + ["RunII"]:
    postfix = "_correlated" if year == "RunII" else ""
    key = str(year)+postfix
    sys_data[key] = {}
    for (i_region, region) in enumerate(all_regions):
        for channel in channels:
            ref  = yield_data[year][ (region, channel) ]['ref'].val
            up   = yield_data[year][ (region, channel) ]['up']
            down = yield_data[year][ (region, channel) ]['down']
    
            sys_data[key][(region, channel)] = {}
            sys_data[key][(region, channel)]['ref']  = ref
            sys_data[key][(region, channel)]['PU']   = abs( 0.5*(up['PU'].val-down['PU'].val)) / ref
            sys_data[key][(region, channel)]['JEC']  = abs( 0.5*(up['JEC'].val-down['JEC'].val)) / ref
            sys_data[key][(region, channel)]['JER']  = abs( 0.5*(up['JER'].val+down['JER'].val) / ref - 1. )
            sys_data[key][(region, channel)]['topPt']= abs( (up['topPt'].val-ref)/ref )
            sys_data[key][(region, channel)]['unclustered']  = abs( 0.5*(up['unclustered'].val-down['unclustered'].val)) / ref
            sys_data[key][(region, channel)]['btaggingSFb']  = abs( 0.5*(up['btaggingSFb'].val-down['btaggingSFb'].val)) / ref
            sys_data[key][(region, channel)]['btaggingSFl']  = abs( 0.5*(up['btaggingSFl'].val-down['btaggingSFl'].val)) / ref
            sys_data[key][(region, channel)]['leptonSF']  = abs( 0.5*(up['leptonSF'].val-down['leptonSF'].val)) / ref
            sys_data[key][(region, channel)]['trigger']   = abs( 0.5*(up['trigger'].val-down['trigger'].val)) / ref

sys_data["RunII_uncorrelated"] = {}
for (i_region, region) in enumerate(all_regions):
    for channel in channels:
        sys_data["RunII_uncorrelated"][(region, channel)] = {}
        for sys, _ in systematic_uncertainties_list:
            sys_data["RunII_uncorrelated"][(region, channel)][sys]  = 1./sys_data["RunII_correlated"][(region, channel)]['ref']* sqrt(sum( (sys_data[str(year)][(region, channel)]['ref']*sys_data[str(year)][(region, channel)][sys])**2 for year in years ) )


eras = map(str, years) + ["RunII_correlated", "RunII_uncorrelated"]
table_strings = []
for systematic, correlated in systematic_uncertainties_list:
    print
    print "systematic: ", systematic
    print "".join( ["%18s           "%str(era) for era in eras ] )
    for region in all_regions:
        strings = []
        for era in eras: 
            strings.append( " ".join( [ "%s %5.1f"%( channel, 100*sys_data[era][(region, channel)][systematic] ) for channel in channels ]) )
        print "|".join(strings)
  
     
    max_SF  = max([ sys_data["RunII_correlated" if correlated else "RunII_uncorrelated"][(region, 'SF')][systematic] for region in all_regions ])
    max_EMu = max([ sys_data["RunII_correlated" if correlated else "RunII_uncorrelated"][(region, 'EMu')][systematic] for region in all_regions ])
 
    table_strings.append( "%s & %s &\\leq %5.1f"%( systematic, "yes" if correlated else "no", 100*max([ max_SF, max_EMu])) )

table_string = \
"""
\\begin{{table}}
   \caption{{Overview of systematic uncertainties.}} \label{{tab:experimental-uncertainties}}
   \center
      \\begin{{tabular}}{{r|c|c}}
            systematic    & correlated? &\% \\\\\\hline
{systematics}
      \end{{tabular}}
\end{{table}}
""".format(systematics = "\n".join(table_strings))

print table_string



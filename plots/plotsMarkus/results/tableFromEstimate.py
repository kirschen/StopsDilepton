#!/usr/bin/env python
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--year",                  dest="year",                  default=2016, type="int",    action="store",      help="Which year?")
parser.add_option('--logLevel',              dest="logLevel",              default='INFO',              action='store',      help="log level?", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'])

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

setup = Setup(year=options.year)

allRegions = regionsLegacy

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.analysis.DataObservation import DataObservation

# signals, so far only T2tt
signals_T2tt = []
if options.year == 2016:
    data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
    postProcessing_directory    = 'stops_2016_nano_v0p16/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2tt
    #from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2bW
    #from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 
    #from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5  
    #from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 
elif options.year == 2017:
    data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
    postProcessing_directory    = 'stops_2017_nano_v0p16/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt
    #from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2bW
    #from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 
    #from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5  
    #from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 
elif options.year == 2018:
    data_directory              = '/afs/hephy.at/data/cms05/nanoTuples/'
    postProcessing_directory    = 'stops_2018_nano_v0p16/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T2tt
    #from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T2bW
    #from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05
    #from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5 
    #from StopsDilepton.samples.nanoTuples_FastSim_Autumn18_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95

#signalEstimators = [s.name for s in signals_T2tt]
#signalEstimators = [s.name for s in signals_T2bW]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p05]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p5]
#signalEstimators = [s.name for s in signals_T8bbllnunu_XCha0p5_XSlep0p95]



estimators = estimatorList(setup)
allEstimators = estimators.constructEstimatorList(["TTJets","TTZ","DY", 'multiBoson', 'other'])
#allEstimators += [ MCBasedEstimate(name=s.name, sample={channel:s for channel in channels + trilepChannels}) for s in signals_T2tt ]

for samp in signals_T2tt:
    if samp.name == "T2tt_600_0":
        s = samp
        allEstimators += [ MCBasedEstimate(name=s.name, sample=s, cacheDir=setup.defaultCacheDir()) ]


setup.verbose=True

systematic_uncertainties_list = [\
'PU',
'JER',
'JEC',
'topPt',
'unclustered',
#'leptonFS',
#'L1Prefire',
'btaggingSFb',
'btaggingSFl',
#'btaggingSFFS',
'leptonSF',
'trigger',
#'fastSimMET',
#'fastSimPU',
]

#for reg in allRegions:
#    print [reg]

#allRegions = [
##    Region('MET_significance', (12, 50))+Region('dl_mt2blbl', (0, 100))+Region('dl_mt2ll', (140, 240)),
#    Region('MET_significance', (12, 50))+Region('dl_mt2blbl', (100, 200))+Region('dl_mt2ll', (140, 240)),
##    Region('MET_significance', (12, 50))+Region('dl_mt2blbl', (200, -1))+Region('dl_mt2ll', (140, 240)),
#]
allRegions = [Region('MET_significance', (12, 50))+Region('dl_mt2blbl', (100, 200))+Region('dl_mt2ll', (140, 240))]
#allRegions

channels = ['all']#['SF','all']

sys_errors = {}
up_variation = {}
down_variation = {}
reference = {}

e_yield = {}
for estimate in allEstimators:
    # Select estimate
    if estimate.name is not 'Data':
        e = estimate
        e.isSignal = False
        e.isData = False
    elif "T2tt" in estimate.name:
        setup = setup.sysClone(sys={'reweight':['reweight_nISR', 'reweightLeptonFastSimSF'], 'remove':[]}) 
        e = estimate
        assert False, "Signal"
        #e.cachedEstimate(r, channel, signalSetup)
        e.isData   = False
    else:
        assert False, "Cannot look at data!! We're blinded!!"
        estimate = DataObservation(name='Data', sample=setup.samples['Data'], cacheDir=setup.defaultCacheDir())
        e.isSignal = False
        e.isData   = True
    print e.name
    sys_errors[e.name] = {}
    up_variation[e.name] = {}
    down_variation[e.name] = {}
    reference[e.name] = {}
    e.initCache(setup.defaultCacheDir())

#    if e.name.count('T2tt') or e.name.count('TTbarDM') or e.name.count('T8bbllnunu'): e.isSignal = True
#
#    isFastSim = e.name.count('T2tt')
#    isFastSim = e.name.count('T8bbllnunu')
#    if isFastSim:
#      setup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF'], 'remove':['reweightPU36fb']})

    for channel in channels:
        up_variation[e.name][channel] = []
        down_variation[e.name][channel] = []
        reference[e.name][channel] = []
        for (i, r) in enumerate(allRegions):
            up_variation[e.name][channel].append({})
            down_variation[e.name][channel].append({})
            reference[e.name][channel].append({})
            #print " ", i, r
            e_yield[e.name] = e.cachedEstimate(r, channel, setup).val
            for syst in systematic_uncertainties_list:
                sys_contribution = eval("e."+syst+"Systematic")(r, channel, setup)
                #print sys_contribution.sigma
                #print "    "+syst+":", "{:.2f} %".format(sys_contribution.sigma/total_val*100) if total_val != 0 else float('nan')
                if syst == "PU":
                    ref  = e.cachedEstimate(r, channel, setup)
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightPUUp']}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightPUDown']}))
                    #print "\t\t\tref: {} up: {} down: {}".format(ref.val,up.val,down.val)
                elif syst == "JER":
                    ref  = e.cachedEstimate(r, channel, setup)
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'jerUp'}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'jerDown'}))
                    #print "\t\t\tref: {} up: {} down: {}".format(ref.val,up.val,down.val)
                elif syst == "JEC":
                    ref  = e.cachedEstimate(r, channel, setup)
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'jesTotalUp'}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'jesTotalDown'}))
                    #print "\t\t\tref: {} up: {} down: {}".format(ref.val,up.val,down.val)
                elif syst == "topPt":
                    ref  = e.cachedEstimate(r, channel, setup)
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'remove':['reweightTopPt']}))
                    down = ref
                    #print "\t\t\tref: {} up: {}".format(ref.val,up.val)
                elif syst == "unclustered":
                    ref  = e.cachedEstimate(r, channel, setup)
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'unclustEnUp'}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'unclustEnDown'}))
                    #print "\t\t\tref: {} up: {} down: {}".format(ref.val,up.val,down.val)
                elif syst == "btaggingSFb":
                    ref  = e.cachedEstimate(r, channel, setup)
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Up']}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Down']}))
                    #print "\t\t\tref: {} up: {} down: {}".format(ref.val,up.val,down.val)
                elif syst == "btaggingSFl":
                    ref  = e.cachedEstimate(r, channel, setup)
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Up']}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Down']}))
                    #print "\t\t\tref: {} up: {} down: {}".format(ref.val,up.val,down.val)
                elif syst == "leptonSF":
                    ref  = e.cachedEstimate(r, channel, setup)
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightLeptonSFUp']}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightLeptonSFDown']}))
                    #print "\t\t\tref: {} up: {} down: {}".format(ref.val,up.val,down.val)
                elif syst == "trigger":
                    ref  = e.cachedEstimate(r, channel, setup)
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightDilepTriggerUp']}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightDilepTriggerDown']}))
                    #print "\t\t\tref: {} up: {} down: {}".format(ref.val,up.val,down.val)
                
                up_variation[e.name][channel][i][syst] = up
                down_variation[e.name][channel][i][syst] = down
                reference[e.name][channel][i][syst] = ref 

                #print "\t"+syst+":", "{:.3f} ({:.3f})".format(sys_contribution.val, e_yield[e.name])
                sys_errors[e.name][syst] = sys_contribution.val


# OUTPUT

header_string = "\t"
est_yield = 0
for e in allEstimators:
    if not "T2tt" in e.name: est_yield += e_yield[e.name]
    header_string += "\t&" + e.name
print est_yield
print header_string + " \\\\ \\hline\\hline"
#print "&", "&".join(systematic_uncertainties_list), "& yield\\\\ \\hline"

for syst in systematic_uncertainties_list:
    est_string = syst+"\t"
    for e in allEstimators:
        #est_string += "\t& {:.1f}\\%".format(sys_errors[e.name][syst]/est_yield*100 if est_yield != 0 else float('nan')) 
        est_string += "\t& {:.1f}\\%".format(sys_errors[e.name][syst]*100 if est_yield != 0 else float('nan')) 
    print est_string + "\\\\"

est_string = "\\hline\n"+"yield = ${:.1f}$\t".format(est_yield)
for e in allEstimators:
    est_string += "\t& {:.1f}".format(e_yield[e.name]) 
print est_string + "\\\\"



# OUTPUT 2

header_string = "        "


for syst in systematic_uncertainties_list:
    slide_start = """
    \\begin{frame}
        \\frametitle{"""+syst+"""}
        \\begin{table}[h!]
            \\renewcommand{\\arraystretch}{1.5}
            \\centering
            \\footnotesize
            \\begin{tabular}{r||c|c|c|c|c||c}
    """
    slide_end = """
            \\end{tabular}
        \\end{table}
    \\end{frame}
    """
    print syst
    table_data=""
    for (i, r) in enumerate(allRegions):
        print "  Region",i
        for channel in channels:
            print "    "+channel+" channel"
            up_est = 0
            down_est = 0
            ref_est = 0
            for estimate in allEstimators:
                up_est += up_variation[estimate.name][channel][i][syst]
                down_est += down_variation[estimate.name][channel][i][syst]
                ref_est += reference[estimate.name][channel][i][syst]
            print "      up:   ", up_est.val
            print "      ref:  ", ref_est.val
            print "      down: ", down_est.val
            print "      up-ref:  ", (up_est.val-ref_est.val)/ref_est.val if ref_est.val != 0 else 0 
            print "      ref-down:", (up_est.val-ref_est.val)/ref_est.val if ref_est.val != 0 else 0 
            table_data += ""

    #print slide_start+table_data+slide_end+"\n\n\n"

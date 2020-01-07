#!/usr/bin/env python
from math import sqrt, cos, sin, pi

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--year",                  dest="year",                  default=2016, type="int",    action="store",      help="Which year?")
parser.add_option("--details",                                                                          action="store_true", help="Print details?")
parser.add_option("--minmax",                                                                           action="store_true", help="Print min/max?")
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

#analysis_results        = '/afs/hephy.at/data/cms05/StopsDileptonLegacy/results/v5/'

setup = Setup(year=options.year)

allRegions = regionsLegacy

from StopsDilepton.analysis.MCBasedEstimate import MCBasedEstimate
from StopsDilepton.analysis.DataObservation import DataObservation

# signals, so far only T2tt
signals_T2tt = []
if options.year == 2016:
    data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
    postProcessing_directory    = 'stops_2016_nano_v0p19/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2tt
    #from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T2bW
    #from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 
    #from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5  
    #from StopsDilepton.samples.nanoTuples_FastSim_Summer16_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 
elif options.year == 2017:
    data_directory              = '/afs/hephy.at/data/cms01/nanoTuples/'
    postProcessing_directory    = 'stops_2017_nano_v0p19/dilep/'
    from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2tt
    #from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T2bW
    #from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p05 
    #from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p5  
    #from StopsDilepton.samples.nanoTuples_FastSim_Fall17_postProcessed import signals_T8bbllnunu_XCha0p5_XSlep0p95 
elif options.year == 2018:
    data_directory              = '/afs/hephy.at/data/cms02/nanoTuples/'
    postProcessing_directory    = 'stops_2018_nano_v0p19/dilep/'
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

mcEstimators = allEstimators
for samp in signals_T2tt:
    if samp.name == "T2tt_600_0":
        s = samp
        signal_estimate = MCBasedEstimate(name=s.name, sample=s, cacheDir=setup.defaultCacheDir())
        #allEstimators += [ signal_estimate ]

setup.verbose=True

systematic_uncertainties_list = [\
'PU',
'JER',
'JEC',
#'topPt',
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
#    if options.details: print [reg]

#allRegions = [
##    Region('MET_significance', (12, 50))+Region('dl_mt2blbl', (0, 100))+Region('dl_mt2ll', (140, 240)),
#    Region('MET_significance', (12, 50))+Region('dl_mt2blbl', (100, 200))+Region('dl_mt2ll', (140, 240)),
##    Region('MET_significance', (12, 50))+Region('dl_mt2blbl', (200, -1))+Region('dl_mt2ll', (140, 240)),
#]
#allRegions = [Region('MET_significance', (12, 50))+Region('dl_mt2blbl', (100, 200))+Region('dl_mt2ll', (140, 240))]
#allRegions = allRegions[1:]
allRegions #= [allRegions[2]] 
#allRegions = [allRegions[2]] 

#channels = ['SF','EMu']
channels = ['all']

sys_errors = {}
up_cachedEstimate = {}
down_cachedEstimate = {}
ref_cachedEstimate = {}
sys_cachedEstimate = {}

e_yield = {}
for estimate in allEstimators:
    # Select estimate
    if "T2tt" in estimate.name:
        setup = setup.sysClone(sys={'reweight':['reweight_nISR', 'reweightLeptonFastSimSF'], 'remove':[]}) 
        e = estimate
        #assert False, "Signal"
        #e.cachedEstimate(r, channel, signalSetup)
        e.isSignal = True
        e.isData   = False
    elif estimate.name is not 'Data':
        e = estimate
        e.isSignal = False
        e.isData = False
    else:
        assert False, "Cannot look at data!! We're blinded!!"
        estimate = DataObservation(name='Data', sample=setup.samples['Data'], cacheDir=setup.defaultCacheDir())
        e.isSignal = False
        e.isData   = True
    if options.details: print e.name
    e.initCache(setup.defaultCacheDir())
    sys_errors[e.name] = {}
    up_cachedEstimate[e.name] = {}
    down_cachedEstimate[e.name] = {}
    ref_cachedEstimate[e.name] = {}
    sys_cachedEstimate[e.name] = {}

#    if e.name.count('T2tt') or e.name.count('TTbarDM') or e.name.count('T8bbllnunu'): e.isSignal = True
#
#    isFastSim = e.name.count('T2tt')
#    isFastSim = e.name.count('T8bbllnunu')
#    if isFastSim:
#      setup = setup.sysClone(sys={'reweight':['reweightLeptonFastSimSF'], 'remove':['reweightPU36fb']})

    for channel in channels:
        up_cachedEstimate[e.name][channel] = []
        down_cachedEstimate[e.name][channel] = []
        ref_cachedEstimate[e.name][channel] = []
        sys_cachedEstimate[e.name][channel] = []
        for (i, r) in enumerate(allRegions):
            up_cachedEstimate[e.name][channel].append({})
            down_cachedEstimate[e.name][channel].append({})
            ref_cachedEstimate[e.name][channel].append({})
            sys_cachedEstimate[e.name][channel].append({})
            if options.details: print " Region", i, "|", channel
            e_yield[e.name] = e.cachedEstimate(r, channel, setup).val
            for syst in systematic_uncertainties_list:
                #print "\t"+syst
                sys_contribution = eval("e."+syst+"Systematic")(r, channel, setup)
                ref  = e.cachedEstimate(r, channel, setup)

                #! getting systematics with functions from SystematicEstimator.py
                if syst == "PU":
                    if options.year == 2018:
                        up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightPUVVUp']}))
                        down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightPUUp']}))
                    else: 
                        up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightPUUp']}))
                        down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightPUDown']}))
                    sys = e.PUSystematic(r, channel, setup).val
                elif syst == "JER":
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'jerUp'}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'jerDown'}))
                    syst_tuple = e.JERSystematicAsym(r, channel, setup)
                    #print "\t\t", abs(syst_tuple[0]-1), "|", abs(syst_tuple[1]-1)
                    sys = max(abs(syst_tuple[0]-1), abs(syst_tuple[1]-1)) if syst_tuple[0] != 0. or syst_tuple[1] != 0. else 0.
                elif syst == "JEC":
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'jesTotalUp'}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'jesTotalDown'}))
                    syst_tuple = e.JECSystematicAsym(r, channel, setup)
                    #print "\t\t", abs(syst_tuple[0]-1), "|", abs(syst_tuple[1]-1)
                    sys = max(abs(syst_tuple[0]-1), abs(syst_tuple[1]-1)) if syst_tuple[0] != 0. or syst_tuple[1] != 0. else 0.
                elif syst == "topPt":
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'remove':['reweightTopPt']}))
                    down = ref
                    sys = e.topPtSystematic(r, channel, setup).val
                elif syst == "unclustered":
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'unclustEnUp'}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'selectionModifier':'unclustEnDown'}))
                    syst_tuple = e.unclusteredSystematicAsym(r, channel, setup)
                    #print "Unclustered", r, channel, syst_tuple
                    # calculate statistics
                    #n_up = (up.val/up.sigma)**2 if up.sigma != 0 else 0.
                    #n_down = (down.val/down.sigma)**2 if down.sigma != 0 else 0.
                    #if options.details: print "n_down-n_up/sigma(n_down)=", (n_down-n_up)/sqrt(n_down) if n_down != 0. else 0.
                    #if n_down != 0. and (n_down)/sqrt(n_down) < 3: print "!! (n_down)/sqrt(n_down)", (n_down)/sqrt(n_down), "excluding region", i
                    #if n_up != 0. and (n_up)/sqrt(n_up) < 3: print "!! (n_up)/sqrt(n_up)", (n_up)/sqrt(n_up), "excluding region", i
                    #if options.details: print "up:", up, "down:", down
                    # ----------------------------
                    if options.details: print "\t\tdown/ref-1=", syst_tuple[0]-1, "| up/ref-1=", syst_tuple[1]-1
                    sys = max(abs(syst_tuple[0]-1), abs(syst_tuple[1]-1)) if syst_tuple[0] != 0. or syst_tuple[1] != 0. else 0.
                elif syst == "btaggingSFb":
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Up']}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightBTag_SF_b_Down']}))
                    sys = e.btaggingSFbSystematic(r, channel, setup).val
                elif syst == "btaggingSFl":
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Up']}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightBTag_SF_l_Down']}))
                    sys = e.btaggingSFlSystematic(r, channel, setup).val
                elif syst == "leptonSF":
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightLeptonSFUp']}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightLeptonSFDown']}))
                    sys = e.leptonSFSystematic(r, channel, setup).val
                elif syst == "trigger":
                    up   = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightDilepTriggerUp']}))
                    down = e.cachedEstimate(r, channel, setup.sysClone({'reweight':['reweightDilepTriggerDown']}))
                    sys = e.triggerSystematic(r, channel, setup).val
                
                #print "\t\tref {} | up {} | down {}".format(ref.val,up.val,down.val)
                #print "\t\t", sys, "(systematicEstimator)"
                #print "\t\t", (up.val-down.val)/(2*ref.val) if ref.val>0 else 0, "(self-made)"

                up_cachedEstimate[e.name][channel][i][syst] = up
                down_cachedEstimate[e.name][channel][i][syst] = down
                ref_cachedEstimate[e.name][channel][i][syst] = ref 
                sys_cachedEstimate[e.name][channel][i][syst] = sys
                sys_errors[e.name][syst] = sys_contribution.val




# OUTPUT

#header_string = "\t"
#est_yield = 0
#for e in allEstimators:
#    if not "T2tt" in e.name: est_yield += e_yield[e.name]
#    header_string += "\t&" + e.name
##print est_yield
##print header_string + " \\\\ \\hline\\hline"
##print "&", "&".join(systematic_uncertainties_list), "& yield\\\\ \\hline"
#
#for syst in systematic_uncertainties_list:
#    est_string = syst+"\t"
#    for e in allEstimators:
#        #est_string += "\t& {:.1f}\\%".format(sys_errors[e.name][syst]/est_yield*100 if est_yield != 0 else float('nan')) 
#        est_string += "\t& {:.1f}\\%".format(sys_errors[e.name][syst]*100 if est_yield != 0 else float('nan')) 
#    #print est_string + "\\\\"
#
#est_string = "\\hline\n"+"yield = ${:.1f}$\t".format(est_yield)
#for e in allEstimators:
#    est_string += "\t& {:.1f}".format(e_yield[e.name]) 
##print est_string + "\\\\"



# OUTPUT 2

header_string = "                "

export_string = ""
unc_string = ""
for syst in systematic_uncertainties_list:
    if options.details: print syst
    slide_start = """
    \\begin{frame}
        \\frametitle{"""+syst+" | "+str(options.year)+"""}
        \\begin{table}[h!]
            \\renewcommand{\\arraystretch}{1.5}
            \\centering
            \\footnotesize
            \\begin{tabular}{r||"""+"||".join(["c" for channel in channels])+"}\n"
    table_header = header_string
    for channel in channels:
        table_header += "& \\textbf{MC "+channel+" channel}"
        #table_header += "& \\textbf{T2tt 600 0 "+channel+" channel}"
    table_header += "\\\\ \\hline\\hline\n"
    slide_end = """
            \\end{tabular}
        \\end{table}
    \\end{frame}
    """

    table_data=""
    min_unc_mc = 999.0
    max_unc_mc = 0.0
    min_unc_sig = 999.0
    max_unc_sig = 0.0
    for (i, r) in enumerate(allRegions):
        if options.details: print "  Region",i

        table_row = header_string+"Region "+str(i)

        for (i_c, channel) in enumerate(channels):
            if options.details: print "    "+channel+" channel"
            up_est = 0
            down_est = 0
            ref_est = 0
            for estimate in mcEstimators:
                up_est   += up_cachedEstimate[estimate.name][channel][i][syst]
                down_est += down_cachedEstimate[estimate.name][channel][i][syst]
                ref_est  += ref_cachedEstimate[estimate.name][channel][i][syst]
            
            #! adding absolute uncertainties in quadrature
            sys_est = 0
            up = 0.
            down = 0.
            ref = 0.
            for estimate in mcEstimators:
                if options.details: print "        ",estimate.name+":"," & {:.1f}% (yield: {}) ".format( 100.0*sys_cachedEstimate[estimate.name][channel][i][syst], ref_cachedEstimate[estimate.name][channel][i][syst] )
                # add samples uncorrelated
                #sys_est  += (sys_cachedEstimate[estimate.name][channel][i][syst]*ref_cachedEstimate[estimate.name][channel][i][syst].val)**2
                # add samples correlated
                sys_est  += (1.0 + sys_cachedEstimate[estimate.name][channel][i][syst])*ref_cachedEstimate[estimate.name][channel][i][syst].val
                up += up_cachedEstimate[estimate.name][channel][i][syst]
                down += down_cachedEstimate[estimate.name][channel][i][syst]
                ref += ref_cachedEstimate[estimate.name][channel][i][syst]
            
            # calculate statitics
            #if options.details: print "up", up, "down", down, "ref", ref
            #n_up = (up.val/up.sigma)**2 if up.sigma != 0 else 0.
            #n_down = (down.val/down.sigma)**2 if down.sigma != 0 else 0.
            #n_ref = (ref.val/ref.sigma)**2 if ref.sigma != 0 else 0.
            #if options.details: print "n_up", n_up, "n_down", n_down, "n_ref", n_ref
            #discr_up = n_up/sqrt(n_up) if n_up!=0 else 0.
            #discr_down = n_down/sqrt(n_down) if n_up!=0 else 0.
            #if options.details: print "n/sigma(n): up:", discr_up, "down:", discr_down
            #if discr_up < 3:
            #    print "n_up/sqrt(n_up) < 3", "Region", i, "Channel", channel, "syst", syst, "unc", sqrt(sys_est)/ref_est.val if ref_est.val != 0 else 0.
            #if discr_down < 3:
            #    print "n_down/sqrt(n_down) < 3", "Region", i, "Channel", channel, "syst", syst, "unc", sqrt(sys_est)/ref_est.val if ref_est.val != 0 else 0.
            # ---------------------

            if ref_est.val == 0.: print "Region", i, "| Channel", channel, ": ref yield is zero"
            #mc_uncertainty = sqrt(sys_est)/ref_est.val if ref_est.val != 0 else 0.
            # correlated
            mc_uncertainty = sys_est/ref_est.val-1.0 if ref_est.val != 0 else 0.
            #signal_uncertainty = sys_cachedEstimate[signal_estimate.name][channel][i][syst]
            #print "mc    ", mc_uncertainty
            #print "signal", signal_uncertainty

            table_row += " & {:.1f}\\% ".format(abs(mc_uncertainty)*100)
            #table_row += " & {:.1f}\\% & {:.1f}\\%".format(abs(mc_uncertainty)*100, abs(signal_uncertainty)*100)
            #print "\t\t\t{:.1f}\\%".format(abs(mc_uncertainty)*100)
            #print "\t\t\t{:.1f}\\%".format(abs(signal_uncertainty)*100)

            # max/minimasation of uncertainties
            if mc_uncertainty < min_unc_mc: min_unc_mc = mc_uncertainty
            if mc_uncertainty > max_unc_mc: max_unc_mc = mc_uncertainty
            #if signal_uncertainty < min_unc_sig: min_unc_sig = signal_uncertainty
            #if signal_uncertainty > max_unc_sig: max_unc_sig = signal_uncertainty
         
        table_data += table_row + "\\\\ \n"

    if options.details: print "\tmin: {:.1f} | max: {:.1f}\\%".format(abs(min_unc_mc*100), abs(max_unc_mc*100))
    #print " & {:.1f}-{:.1f}\\%".format(abs(min_unc_sig*100), abs(max_unc_sig*100))
    #unc_string += "{} & {:.1f}-{:.1f}\\% & {:.1f}-{:.1f}\\% \\ \n".format(syst, min_unc_mc*100, max_unc_mc*100, min_unc_sig*100, max_unc_sig*100)    
    unc_string += "{} & {:.1f}-{:.1f}\\% & \n".format(syst, min_unc_mc*100, max_unc_mc*100)    

    export_string += slide_start+table_header+table_data+slide_end+"\n\n\n"

#print export_string
if options.minmax: print unc_string

export_path = "/afs/hephy.at/user/m/mdoppler/www/uncertaintiesTable/"
with file( export_path + "table_v5_"+str(options.year)+".tex", 'w' ) as f:
    f.write( export_string )
    #f.write( "\n\n"+unc_string )





# OUTPUT 3

print "-----------------------------------------------------------------------------------------------------------"
print " Compare to http://www.hephy.at/user/dspitzbart/stopsDileptonLegacy/controlRegions/v6/signalOnly_2017.png"
print "-----------------------------------------------------------------------------------------------------------"

for (i, r) in enumerate(allRegions):
    for (i_c, channel) in enumerate(channels):
        yield_sum = 0
        for estimate in mcEstimators:
            yield_sum += ref_cachedEstimate[estimate.name][channel][i][syst].val

        #! adding absolute uncertainties in quadrature
        unc_sum = 0
        for estimate in mcEstimators:
            for syst in systematic_uncertainties_list:
                unc_sum += (sys_cachedEstimate[estimate.name][channel][i][syst]*ref_cachedEstimate[estimate.name][channel][i][syst].val)**2
            "TTJets","TTZ","DY", 'multiBoson', 'other'
            if estimate.name == "TTJets":       unc_sum += (ref_cachedEstimate[estimate.name][channel][i][syst].val * 0.10)**2
            elif estimate.name == "TTZ":        unc_sum += (ref_cachedEstimate[estimate.name][channel][i][syst].val * 0.20)**2
            elif estimate.name == "DY":         unc_sum += (ref_cachedEstimate[estimate.name][channel][i][syst].val * 0.25)**2
            elif estimate.name == "multiBoson": unc_sum += (ref_cachedEstimate[estimate.name][channel][i][syst].val * 0.25)**2
            elif estimate.name == "other":      unc_sum += (ref_cachedEstimate[estimate.name][channel][i][syst].val * 0.25)**2


        if options.details: print "Region", i, "|\t", channel, "\t{:3.1f}% ({:.1f})".format(100*sqrt(unc_sum)/yield_sum if yield_sum != 0 else 0., yield_sum)

print "-----------------------------------------------------------------------------------------------------------"

for (i, r) in enumerate(allRegions):
    if options.details: print "Region", i, "-", r


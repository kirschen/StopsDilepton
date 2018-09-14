''' All samples for MVA training'''

# Standard imports
from RootTools.core.standard import *

#
# Stopsdilepton samples 
#

postProcessing_directory = "stops_2016_nano_v2/dilep/"
# from daniels analysis plot script
postProcessing_directory = "stops_2016_nano_v2/dilep/"
from StopsDilepton.samples.nanoTuples_Summer16_postProcessed import *
postProcessing_directory = "stops_2016_nano_v2/dilep/"
from StopsDilepton.samples.nanoTuples_Run2016_05Feb2018_postProcessed import *

# T2tt Sample 
from StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed import *
# Combine in Region of interest to increase statistics
T2tt_mStop600to1200 = Sample.combine('T2tt_mStop600to1200', [ x for x in signals_T2tt if (600<x.mStop<1200 and x.mNeu<400.)])
T2tt_all = Sample.combine('T2tt_all', signals_T2tt)

T2tt_dM350 = Sample.combine('T2tt_dM350', [ x for x in signals_T2tt if (x.mStop-x.mNeu)>350 ])
T2tt_dM350_smaller = Sample.combine('T2tt_dM350_smaller', [ x for x in signals_T2tt if (x.mStop-x.mNeu)<350 ])

T8bbllnunu_XCha0p5_XSlep0p05_dM350 = Sample.combine('T8bbllnunu_XCha0p5_XSlep0p5_dM350', [ x for x in signals_T8bbllnunu_XCha0p5_XSlep0p05 if (x.mStop-x.mNeu)>350 ])
T8bbllnunu_XCha0p5_XSlep0p05_dM350_smaller = Sample.combine('T8bbllnunu_XCha0p5_XSlep0p5_dM350', [ x for x in signals_T8bbllnunu_XCha0p5_XSlep0p05 if (x.mStop-x.mNeu)<350 ])

T8bbllnunu_XCha0p5_XSlep0p5_dM350 = Sample.combine('T8bbllnunu_XCha0p5_XSlep0p5_dM350', [ x for x in signals_T8bbllnunu_XCha0p5_XSlep0p5 if (x.mStop-x.mNeu)>350 ])
T8bbllnunu_XCha0p5_XSlep0p5_dM350_smaller = Sample.combine('T8bbllnunu_XCha0p5_XSlep0p5_dM350', [ x for x in signals_T8bbllnunu_XCha0p5_XSlep0p5 if (x.mStop-x.mNeu)<350 ])

T8bbllnunu_XCha0p5_XSlep0p95_dM350 = Sample.combine('T8bbllnunu_XCha0p5_XSlep0p5_dM350', [ x for x in signals_T8bbllnunu_XCha0p5_XSlep0p95 if (x.mStop-x.mNeu)>350 ])
T8bbllnunu_XCha0p5_XSlep0p95_dM350_smaller = Sample.combine('T8bbllnunu_XCha0p5_XSlep0p5_dM350', [ x for x in signals_T8bbllnunu_XCha0p5_XSlep0p95 if (x.mStop-x.mNeu)<350 ])

TTLep_pow = Sample.fromDirectory(name="TTLep_pow", treeName="Events", isData=False, color=color.TTJets, texName="t#bar{t} + Jets (lep,pow)", directory=directories['TTLep_pow'])

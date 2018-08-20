''' All samples for MVA training'''

# Standard imports
from RootTools.core.standard import *

#
# Stopsdilepton samples 
#
postProcessing_directory = "postProcessed_80X_v35/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Summer16_mAODv2_postProcessed import *
postProcessing_directory = "postProcessed_80X_v35/dilepTiny"
from StopsDilepton.samples.cmgTuples_FastSimT8bbllnunu_mAODv2_25ns_postProcessed import *

SMS_T8bbllnunu_XCha0p5_XSlep0p09 = Sample.fromDirectory( "SMS_T8bbllnunu_XCha0p5_XSlep0p09", directory = ["/afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v37/dilepTiny/SMS_T8bbllnunu_XCha0p5_XSlep0p09"] )
SMS_T2tt_mStop_400to1200         = Sample.fromDirectory( "SMS_T2tt_mStop_400to1200", directory = ['/afs/hephy.at/data/dspitzbart02/cmgTuples/postProcessed_80X_v40/dilepTiny/SMS_T2tt_mStop_400to1200'] )

data_directory_fromdaniel = '/afs/hephy.at/data/dspitzbart02/cmgTuples/'
postProcessing_directory_fromdaniel = "postProcessed_80X_v40/dilepTiny"
from StopsDilepton.samples.cmgTuples_FastSimT2tt_mAODv2_25ns_postProcessed import *
T2tt_mStop600to1200 = Sample.combine('T2tt_mStop600to1200', [ x for x in signals_T2tt if (600<x.mStop<1200 and x.mNeu<400.)])

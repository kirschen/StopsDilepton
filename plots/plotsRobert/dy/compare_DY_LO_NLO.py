''' Analysis script for 1D 2l plots (RootTools)
'''

#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools
import copy

#RootTools
from RootTools.core.standard import *

postProcessing_directory = "postProcessed_80X_v21/dilepTiny/"
from StopsDilepton.samples.cmgTuples_Spring16_mAODv2_postProcessed import *

dy_lo   = DY_HT_LO
dy      = DY

#for s in [dy_lo,dy]:
#    s.reduceFiles( to = 1 )

h_dy_lo = dy_lo.get1DHistoFromDraw( "dl_pt", binning = [500/20,0,500],  addOverFlowBin = 'upper', weightString = "weight" )
h_dy = dy.get1DHistoFromDraw( "dl_pt", binning = [500/20,0,500],  addOverFlowBin = 'upper', weightString = "weight" )

h_dy_lo.style = styles.lineStyle( ROOT.kRed)
h_dy.style = styles.lineStyle( ROOT.kBlue)
h_dy_lo.legendText = "LO"
h_dy.legendText = "NLO"

plotting.draw(
    Plot.fromHisto("ptll",
                [[ h_dy_lo], [ h_dy]],
                texX = "p_{T}(ll)"
            ),
    plot_directory = "/afs/hephy.at/user/r/rschoefbeck/www/etc/ptz.png", 
    logX = False, logY = True, #sorting = True, 
    yRange = (0.03, "auto"), 
    #drawObjects = None,
    scaling = {0:1}
)

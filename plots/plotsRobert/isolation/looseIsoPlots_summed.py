#Standard imports
import ROOT
from math import sqrt, cos, sin, pi, acos
import itertools
import pickle
import os

#user
from StopsDilepton.tools.user import plot_directory

#RootTools
from RootTools.core.standard import *

# Logging
import StopsDilepton.tools.logger as logger

logger = logger.get_logger('INFO', logFile = None )
histos = {}
for m in ['doubleMu', 'doubleEle', 'muEle']:
    plot_path = "80X_looseIso/%s_offZ_standard_isOS-njet2-nbtag1-met80-metSig5-dPhiJetMET/" % m
    for fh in ["leadingLepIso"]:
        for swap in ["L1", "L2"]:
            for fs in ["mm","me","em","ee"]:
                ofile = os.path.join(plot_directory, plot_path,  "dl_mt2ll_%s_swap%s_%s.pkl"%(fh, swap, fs))
                if os.path.isfile(ofile):
                    logger.info( "Loading %s", ofile )
                    histos["%s_mt2ll_%s_swap%s_%s"%(m, fh, swap, fs)] = pickle.load( file( ofile) )
                else:
                    logger.warning( "File not found: %s", ofile)

def drawObjects( ):
    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetTextSize(0.04)
    tex.SetTextAlign(11) # align right

    lines = [ (0.15, 0.95, 'CMS Preliminary') ]
    lines.append( (0.45, 0.95, 'L=%3.1f fb{}^{-1} (13 TeV)'% ( 36.4 ) ) )
    return [tex.DrawLatex(*l) for l in lines] 

def transpose(l):
    return list(map(list, zip(*l)))

def add_histos( l ):
    res = l[0].Clone()
    for h in l[1:]: res.Add(h)
    return res

for name, fss in [
    ['doubleMu', ['mm']], 
    ['muEle', ['me', 'em']], 
    ['doubleEle', ['ee']],
    ['all',['mm','ee','em','me']]
    ]:
    to_be_added = []
    for key in histos.keys():
        if not any( key.endswith('_'+fs) for fs in fss): continue
        logger.info( "Adding to %s key %s", name, key )
        to_be_added.append( key )

    mc_histos = map( add_histos, transpose( [ histos[key][0] for key in to_be_added ] ) )
    mc_histos = [add_histos(mc_histos[1:4]+[mc_histos[8]]), add_histos(mc_histos[4:6]), add_histos(mc_histos[6:8])]
    mc_histos[0].legendText = "t#bar{t}/single-t"
    mc_histos[1].legendText = "TT+V"
    # mc_histos[1].style = styles.fillStyle(ROOT.kOrange )
    mc_histos[2].legendText = "multi boson"
    mc_histos[2].SetFillColor( ROOT.kOrange )
    for h in mc_histos:
        h.style = styles.fillStyle(h.GetFillColor(), lineColor = h.GetFillColor(), errors = True)
    #for m in mc_histos:
    #    m.legendText = ' '.join(m.GetName().split('_')[4:-5])

    data_histo = add_histos( [ histos[key][1][0] for key in to_be_added ] )
    data_histo.style = styles.errorStyle( ROOT.kBlack )

    dl_mt2ll  = Plot(
        name = "%s_dl_mt2ll"%name,
        texX = 'M_{T2}(ll) (GeV)', texY = 'Number of Events / 15 GeV',
        stack = None, 
        attribute = TreeVariable.fromString( "dl_mt2ll/F" ),
        binning=[300/15,0,300],
        #selectionString = selectionString,
        #weight = weight,
        )
    dl_mt2ll.histos = [mc_histos, [data_histo]]

    data_histo.legendText = "Data ( 3 lep. )"

    ratio = {'yRange':(0.1,1.9)}
    plotting.draw(
        dl_mt2ll,
        plot_directory = plot_directory+'/etc/', ratio = ratio, 
        logX = False, logY = True, #sorting = True,
         yRange = (0.003, "auto") ,
         scaling = {0:1},
         legend = [0.50,0.88-0.05*4,0.92,0.88],
        drawObjects = drawObjects( )
    )
 

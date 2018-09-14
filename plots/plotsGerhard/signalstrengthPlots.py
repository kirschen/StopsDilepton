'''
Plot Skript to display signalstrength vs MVAcuts
'''

from StopsDilepton.tools.user import analysis_results, plot_directory
import os
import pickle
import ROOT
from array import array
from tdrstyle import setTDRStyle

#
# Plotpath
#
plotdir_sig = os.path.join( plot_directory, 'Signalstrenght' )
if not os.path.exists( plotdir_sig ):
    os.makedirs( plotdir_sig ) 

#
# Define Masspoints
#
resultsdict = { 
                (850,0):[],
                (900,50):[],
                (850,100):[],
                (900,150):[],
                (600,300):[],
                (750,350):[],
               }                 
cutlist = []

#
# Define MVAs
#
MVAList = { 'MVA_T2tt_lep_pt':'T2tt vs TTLep_pow',
            }


for MVAName in MVAList.keys():
    
    #
    # read data
    #
    
    subdirs = next(os.walk(analysis_results))[1]
    for subdir in subdirs:
        if MVAName in subdir:
            # MVA cuts
            cutlist.append( float(subdir.split('_')[-1]) )
            # signal stength
            res = pickle.load( file( os.path.join(analysis_results, subdir,'cardFiles','T2tt','calculatedLimits.pkl'),'r') )
            for masspoint in resultsdict.keys():
               resultsdict[masspoint].append( res[masspoint]['0.500'] )
    
    # sorting
    
    for masspoint in resultsdict.keys():
        resultsdict[masspoint] =  [x for _, x in sorted(zip(cutlist, resultsdict[masspoint]), key=lambda pair: pair[0])]
    cutlist.sort()
    
    #
    # plot
    #
    
    colorList = []
    lineWidthList = []
    
    colorList.append(ROOT.kGreen )
    colorList.append(ROOT.kMagenta )
    colorList.append(ROOT.kCyan )
    colorList.append(ROOT.kBlue )
    colorList.append(ROOT.kRed )
    colorList.append(ROOT.kOrange )
    
    lineWidthList.append(1)
    lineWidthList.append(1)
    lineWidthList.append(1)
    lineWidthList.append(1)
    lineWidthList.append(1)
    lineWidthList.append(1)
    
    
    c = ROOT.TCanvas()
    c.SetGrid()
    c.SetRightMargin( 0.1 )
    c.SetLeftMargin(  0.15 )
    c.SetTopMargin(   0.1 )
    c.SetBottomMargin(0.15 )
    
    mg = ROOT.TMultiGraph()
    g=[]
    #ROOT.gROOT.ForceStyle()
    #setTDRStyle()
    
    for i,masspoint in enumerate(resultsdict.keys()):
        g.append( ROOT.TGraph( len( cutlist ), array('d', cutlist ), array('d', resultsdict[masspoint] )) )
        g[-1].SetName( str(masspoint) )
        g[-1].SetTitle( str(masspoint) )
        g[-1].SetLineColor( colorList[i] )
        g[-1].SetLineWidth( lineWidthList[i] )
        g[-1].SetMarkerColor( colorList[i] )
        g[-1].SetMarkerStyle( 20 )
        g[-1].SetFillStyle(0)
        g[-1].SetFillColor(0)
        g[-1].SetMarkerSize(1)
        g[-1].Draw("ALP")
        mg.Add(g[-1])
    
    #Draw Options: L Polyline between pointsc, C smooth curve between points, P Marker at points, * Star at points
    mg.Draw("ALP")
    mg.SetTitle( MVAList[MVAName] )
    mg.GetXaxis().SetTitle('MVA cut')
    mg.GetXaxis().SetRangeUser(0, max( cutlist ) )
    mg.GetXaxis().SetTitleColor(1)
    mg.GetXaxis().SetTitleFont(43)
    mg.GetXaxis().SetTitleSize(30)
    mg.GetXaxis().SetLabelColor(1)
    mg.GetXaxis().SetLabelFont(43)
    mg.GetXaxis().SetLabelOffset(0.007)
    mg.GetXaxis().SetLabelSize(28)

    mg.GetYaxis().SetTitle('signal strength')
    mg.GetYaxis().SetRangeUser(0.0, 2)
    mg.GetYaxis().SetTitleColor(1)
    mg.GetYaxis().SetTitleFont(43)
    mg.GetYaxis().SetTitleSize(30)
    mg.GetYaxis().SetLabelColor(1)
    mg.GetYaxis().SetLabelFont(43)
    mg.GetYaxis().SetLabelOffset(0.007)
    mg.GetYaxis().SetLabelSize(28)
    
    #c.BuildLegend(0.7,0.16,0.89,0.55, '   Masspoints' )
    c.BuildLegend(0.8,0.16,0.98,0.6, '   Masspoints' )
    c.Print( os.path.join( plotdir_sig, MVAName + '.png' ))
    
    #print cutlist
    #print resultsdict[(800,0)]

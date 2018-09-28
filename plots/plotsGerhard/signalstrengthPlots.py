'''
Plot Skript to display signalstrength vs MVAcuts

python signalstrengthPlots.py --signal T2tt
'''

from StopsDilepton.tools.user import analysis_results, plot_directory
import os
import pickle
import ROOT
from array import array

import os
import argparse

argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument("--signal", action='store', default='T2tt', nargs='?', choices=["T2tt","T8bbllnunu_XCha0p5_XSlep0p05", "T8bbllnunu_XCha0p5_XSlep0p5", "T8bbllnunu_XCha0p5_XSlep0p95"], help="which signal?")

args = argParser.parse_args()

#
# Plotpath
#
plotdir_sig = os.path.join( plot_directory, 'Signalstrenght' )
plotdir_sig = os.path.join( plotdir_sig, args.signal )

if not os.path.exists( plotdir_sig ):
    os.makedirs( plotdir_sig ) 

#
# MVAs for signals
#

if   args.signal == "T2tt":
   MVAList = ['MVA_T2tt_dM350_smaller_TTLep_pow', 'MVA_T2tt_dM350_TTLep_pow', 'MVA_T2tt_dM350_TTZtoLLNuNu']

elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05":
   MVAList = ['MVA_T8bbllnunu_XCha0p5_XSlep0p05_dM350_TTLep_pow']

elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":
   MVAList = ['MVA_T8bbllnunu_XCha0p5_XSlep0p5_dM350_smaller_TTLep_pow','MVA_T8bbllnunu_XCha0p5_XSlep0p5_dM350_TTLep_pow']

elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95":
   MVAList = ['MVA_T8bbllnunu_XCha0p5_XSlep0p95_dM350_smaller_TTLep_pow', 'MVA_T8bbllnunu_XCha0p5_XSlep0p95_dM350_TTLep_pow']

#
# 1 plot per MVA
#

for MVAName in MVAList:
    #
    # Define Masspoints for Signal
    # 
    if   args.signal == "T2tt":
        resultsdict = { 
                        (850,0):  [[],[]],
                        (900,50): [[],[]],
                        (850,100):[[],[]],
                        (900,150):[[],[]],
                        (600,300):[[],[]],
                        (750,350):[[],[]],
                       }                 
    
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05":
        resultsdict = { 
                        (1100,0): [[],[]],
                        (1000,25):[[],[]],
                        (900,50): [[],[]],
                        (800,50): [[],[]],
                       }                 
    
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":
        resultsdict = { 
                        (1200,0):  [[],[]],
                        (1252,200):[[],[]],
                        (1252,400):[[],[]],
                        (1152,600):[[],[]],
                        (1000,650):[[],[]],
                        (800,550): [[],[]],
                       }                 
    
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95":
        resultsdict = { 
                        (1300,0):[[],[]],
                        (1300,200):[[],[]],
                        (1300,400):[[],[]],
                        (1200,800):[[],[]],
                        (1000,800):[[],[]],
                       }                 

    #
    # read data
    #
    subdirs = next(os.walk(analysis_results))[1]
    for subdir in subdirs:
        if MVAName in subdir:
            filename = os.path.join(analysis_results, subdir,'cardFiles', args.signal ,'calculatedLimits.pkl')
            for masspoint in resultsdict.keys():
                # MVA cuts
                resultsdict[masspoint][0].append( float(subdir.split('_')[-1]) )
                # open pickle
                try:
                    res = pickle.load( file( filename, 'r') )
                except ValueError as e:
                    print "Error in pkl file %s" % filename
                    raise e

                # signal stength
                try: 
                    resultsdict[masspoint][1].append( res[masspoint]['0.500'] )
                except KeyError:
                    resultsdict[masspoint][0].pop()
                        
    # sorting
    
    for masspoint in resultsdict.keys():
        resultsdict[masspoint][1] =  [x for _, x in sorted(zip( resultsdict[masspoint][0], resultsdict[masspoint][1]), key=lambda pair: pair[0])]
        print '************'
        print masspoint
        print resultsdict[masspoint][1]
        resultsdict[masspoint][0].sort()
        print resultsdict[masspoint][0]
        print '************'
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
        g.append( ROOT.TGraph( len( resultsdict[masspoint][0] ), array('d', resultsdict[masspoint][0] ), array('d', resultsdict[masspoint][1] )) )
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
#    mg.SetTitle( MVAName )
    mg.GetXaxis().SetTitle('MVA cut')
    mg.GetXaxis().SetRangeUser(0, 1 )
    mg.GetXaxis().SetTitleColor(1)
    mg.GetXaxis().SetTitleFont(43)
    mg.GetXaxis().SetTitleSize(30)
    mg.GetXaxis().SetLabelColor(1)
    mg.GetXaxis().SetLabelFont(43)
    mg.GetXaxis().SetLabelOffset(0.007)
    mg.GetXaxis().SetLabelSize(28)

    mg.GetYaxis().SetTitle('95% CL upper limit on r')
    if   args.signal == "T2tt":
        mg.GetYaxis().SetRangeUser(0.0, 1.5)
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p05":
        mg.GetYaxis().SetRangeUser(0.0, 1.5)
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p5":
        mg.GetYaxis().SetRangeUser(0.0, 1.5)
    elif args.signal == "T8bbllnunu_XCha0p5_XSlep0p95":
        mg.GetYaxis().SetRangeUser(0.0, 1.2)
    mg.GetYaxis().SetTitleColor(1)
    mg.GetYaxis().SetTitleFont(43)
    mg.GetYaxis().SetTitleSize(30)
    mg.GetYaxis().SetLabelColor(1)
    mg.GetYaxis().SetLabelFont(43)
    mg.GetYaxis().SetLabelOffset(0.007)
    mg.GetYaxis().SetLabelSize(28)
    
    c.BuildLegend(0.16,0.16,0.31,0.5, '   Masspoints' )
    #c.BuildLegend(0.8,0.16,0.98,0.6, '   Masspoints' )
    c.Print( os.path.join( plotdir_sig, MVAName + '.png' ))
    c.Print( os.path.join( plotdir_sig, MVAName + '.pdf' ))
    c.Print( os.path.join( plotdir_sig, MVAName + '.root' ))

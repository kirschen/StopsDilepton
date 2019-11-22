'''
Extracting post-fit information.
Happily stolen from:
https://github.com/HephySusySW/Workspace/blob/94X-master/DegenerateStopAnalysis/python/tools/sysTools.py
and
https://github.com/HephySusySW/Workspace/blob/94X-master/DegenerateStopAnalysis/python/tools/degTools.py
'''

# Standard imports
import ROOT, pickle, itertools, os
from operator import mul

# Logging
import logging
logger = logging.getLogger(__name__)

from StopsDilepton.tools.u_float import u_float
import math

from StopsDilepton.tools.helpers import getObjFromFile, natural_sort

def getValFrom1BinnedHistOrGraph( hist ):
    """
        if input is AsymTGraph, the average of errors is given 
    """
    if type(hist) in [ ROOT.TH1F , ROOT.TH1D ]:
        e = ROOT.Double()
        v = hist.IntegralAndError(0,500,e) # 500 is an arbitrary choice
        #e = hist.GetBinError(1)
    if type(hist) in [ ROOT.TH2F , ROOT.TH2D ]:
        v = hist.GetBinContent(1,1)
        e = hist.GetBinError(1,1)
    if type(hist) in [ROOT.TGraphAsymmErrors]:
        v = hist.GetY()[0]
        el = hist.GetEYlow()[0]
        eh = hist.GetEYhigh()[0]
        if el and eh:
            e  = sum( [abs(el), abs(eh)] )/2.
        else:
            e  = max(abs(el),abs(eh))
        #print hist , (v,el,eh)
        #return (v, el, eh )
    return u_float(v,e)

def dict_function ( d,  func ):
    """
    creates a new dictionary with the same structure and depth as the input dictionary
    but the final values are determined by func(val)
    """
    new_dict = {}
    for k in d.keys():
        v = d.get(k)
        if type(v)==dict:
            ret = dict_function( v , func)         
        else:
            ret = func(v)        
        new_dict[k] = ret
    return new_dict


def getPrePostFitFromMLF( mlfit ):
    if type(mlfit)==type(""):
        mlfit = ROOT.TFile(mlfit, "READ")
    shape_dirs = ['shapes_prefit', 'shapes_fit_b', 'shapes_fit_s']
    shape_hists = {}
    overalls = ['total_overall', 'total_signal', 'total_data','total_background', 'overall_total_covar'] 
    overall_outs = {}
    shape_dirs_ = {}
    for shape_dir_name in shape_dirs:
        shape_dir = mlfit.Get(shape_dir_name)
        shape_dirs_[shape_dir_name]=shape_dir
        list_of_channels = [x.GetName() for x in shape_dir.GetListOfKeys() if x.IsFolder()]
        shape_hists[shape_dir_name] = {}
        overall_outs[shape_dir_name] = {}
        for channel_name in list_of_channels:
            channel  = shape_dir.Get(channel_name)
            bin_name = channel_name.replace("ch1_","")
            list_of_hists = [x.GetName() for x in channel.GetListOfKeys() ]
            shape_hists[shape_dir_name][bin_name] = {}
            for hist in list_of_hists:
                if hist =='signal' and shape_dir_name == 'shapes_fit_b' and False: ## ignore for now
                    shape_hists[shape_dir_name][bin_name][hist] = shape_dirs_['shapes_prefit'].Get(channel_name).Get(hist)
                else:
                    shape_hists[shape_dir_name][bin_name][hist] = channel.Get(hist)
                
    shape_results = dict_function( shape_hists, func = getValFrom1BinnedHistOrGraph )
    
    ret = {'hists':shape_hists, 'results':shape_results, 'mlfit':mlfit }
    return ret

def getCovarianceFromMLF( mlfit, postFit=False ):
    if type(mlfit)==type(""):
        mlfit = ROOT.TFile(mlfit, "READ")

    tt = mlfit.Get("shapes_fit_s") if postFit else mlfit.Get("shapes_prefit")

    h2 = tt.Get("overall_total_covar")

    binNames = []
    matrix = {}
    nbins = h2.GetNbinsX()
    
    for i in range(1, nbins+1):
        binNames.append(h2.GetXaxis().GetBinLabel(i))
        matrix[h2.GetXaxis().GetBinLabel(i)] = {}
        for j in range(1, nbins+1):
            matrix[h2.GetXaxis().GetBinLabel(i)][h2.GetXaxis().GetBinLabel(j)] = h2.GetBinContent(i,j)

    sorted_cov = ROOT.TH2D('cov','',nbins,0,nbins,nbins,0,nbins)
    binNames = natural_sort(binNames)
    
    #SRnames = []
    #for i in range(nbins/2):
    #    SRnames.append("SF "+str(i))
    #    SRnames.append("DF "+str(i))
    #
    #for i,k in enumerate(binNames):
    #    if i < nSR:
    #        sorted_cov.GetXaxis().SetBinLabel(i+1,SRnames[i])
    #        sorted_cov.GetYaxis().SetBinLabel(i+1,SRnames[i])
    #    for j,l in enumerate(binNames):
    #        sorted_cov.SetBinContent(i+1,j+1,matrix[k][l])
    #
    #sorted_cov.GetXaxis().LabelsOption("v")

    return matrix


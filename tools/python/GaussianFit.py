# Standard importts
import os
import ROOT
ROOT.gROOT.SetBatch(True)

# RooFit
ROOT.gSystem.Load("libRooFit.so")
ROOT.gSystem.Load("libRooFitCore.so")
ROOT.gROOT.SetStyle("Plain") # Not sure this is needed
ROOT.gSystem.SetIncludePath( "-I$ROOFITSYS/include/" )

# Logging
import logging
logger = logging.getLogger(__name__)

def GaussianFit( shape, isData, var_name, fit_plot_directory=None, fit_filename = None):
    ''' Gaussian fit from Zeynep
    '''

    logger.info( "Performing a gaussian fit to get the mean" )
    # declare the observable mean, and import the histogram to a RooDataHist
    variable   = ROOT.RooRealVar(var_name, var_name,-10,10) ;
    data_histo         = ROOT.RooDataHist("datahistshape","datahistshape",ROOT.RooArgList(variable),ROOT.RooFit.Import(shape)) ;
    
    # plot the data hist with error from sum of weighted events
    frame       = variable.frame(ROOT.RooFit.Title(var_name))
    if isData:
        logger.debug( "Settings for data with Poisson error bars" )
        data_histo.plotOn(frame,ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson))
    else:
        logger.debug( "Settings for mc with SumW2 error bars" )
        data_histo.plotOn(frame,ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2)) ;

    # create a simple gaussian pdf
    gauss_mean  = ROOT.RooRealVar("mean","mean",0,-1.2,1.2)
    gauss_sigma = ROOT.RooRealVar("sigma","sigma",0.1,0,2)
    gauss       = ROOT.RooGaussian("gauss","gauss",variable,gauss_mean,gauss_sigma) 
    
    # now do the fit and extract the parameters with the correct error
    if isData: 
        gauss.fitTo(data_histo,ROOT.RooFit.Save(),ROOT.RooFit.Range(data_histo.mean(variable)-2*data_histo.sigma(variable),data_histo.mean(variable)+2*data_histo.sigma(variable)))
    else:
        gauss.fitTo(data_histo,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(True),ROOT.RooFit.Range(data_histo.mean(variable)-2*data_histo.sigma(variable),data_histo.mean(variable)+2*data_histo.sigma(variable)))

    gauss.plotOn(frame)

    argset_fit = ROOT.RooArgSet(gauss_mean,gauss_sigma)
    gauss.paramOn(frame,ROOT.RooFit.Format("NELU",ROOT.RooFit.AutoPrecision(1)),ROOT.RooFit.Layout(0.55)) 
    frame.SetMaximum(frame.GetMaximum()*1.2)

    # add chi2 info
    chi2_text = ROOT.TPaveText(0.3,0.8,0.4,0.9,"BRNDC")
    chi2_text.AddText("#chi^{2} fit = %s" %round(frame.chiSquare(6),2))
    chi2_text.SetTextSize(0.04)
    chi2_text.SetTextColor(2)
    chi2_text.SetShadowColor(0)
    chi2_text.SetFillColor(0)
    chi2_text.SetLineColor(0)
    frame.addObject(chi2_text)

    if (fit_plot_directory is not None) and (fit_filename is not None):
        c = ROOT.TCanvas()
        frame.Draw()
        if not os.path.exists(fit_plot_directory): os.makedirs(fit_plot_directory)
        # c.SaveAs(os.path.join( fit_plot_directory, fit_filename+".pdf"))
        c.SaveAs(os.path.join( fit_plot_directory, fit_filename+".png"))
        del c

    mean_variable        = gauss_mean.getVal()
    mean_variable_error  = gauss_mean.getError()

    return mean_variable, mean_variable_error

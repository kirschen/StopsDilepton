''' recoil corrector for Stops-2l
'''
# Standard imports
import os
import ROOT

# Analysis
from Analysis.Tools.RecoilCorrector import RecoilCorrector as _RecoilCorrector

# Logging
import logging
logger = logging.getLogger(__name__)

# all the recoil correction data
recoilFitResultDir = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/recoilCorrections/"
postfix = "recoil_v3"

class RecoilCorrector:

    def __init__( self, year, era = None):

        if year == 2016:
            self.corrector = _RecoilCorrector( os.path.join( recoilFitResultDir, "2016_recoil_fitResults_SF.pkl" ) )
        if year == 2017:
            self.corrector = _RecoilCorrector( os.path.join( recoilFitResultDir, "2017_recoil_fitResults_SF.pkl" ) )
        if year == 2018:
            if era=="preHEM":
                self.corrector  = _RecoilCorrector( os.path.join( recoilFitResultDir, "2018_preHEM_recoil_fitResults_SF.pkl" ) )
            elif era=="postHEM":
                self.corrector = _RecoilCorrector( os.path.join( recoilFitResultDir, "2018_postHEM_recoil_fitResults_SF.pkl" ) )
            else:
                self.corrector = _RecoilCorrector( os.path.join( recoilFitResultDir, "2018_recoil_fitResults_SF.pkl" ) )

    def predict_para(self, njet, qt, u_para ):
        if njet<1: return u_para # in case of jesTotalUp/Down within systematics variation
        return self.corrector.predict_para( njet, qt, u_para )

    def predict_perp(self, njet, qt, u_perp ):
        if njet<1: return u_perp # in case of jesTotalUp/Down witin systematics variation
        return self.corrector.predict_perp( njet, qt, u_perp )

if __name__=="__main__":

    from RootTools.core.standard import *
    from StopsDilepton.tools.user import plot_directory

    eras = [ ( 2016, None), (2017, None), (2018, "preHEM"), (2018, "postHEM")]

    color = { ( 2016, None): ROOT.kBlue,
              ( 2017, None): ROOT.kRed,
              ( 2018, "preHEM"): ROOT.kGreen,
              ( 2018, "postHEM"):ROOT.kMagenta,
            }
    sigma_para_ratio_histo  = {}
    sigma_perp_ratio_histo  = {}
    median_para_shift_histo = {}
    median_perp_shift_histo = {}
    
    for year, era in eras: 
        corrector = RecoilCorrector(year, era)
        sigma_para_ratio_histo  [(year,era)] = {}
        sigma_perp_ratio_histo  [(year,era)] = {}
        median_para_shift_histo [(year,era)] = {}
        median_perp_shift_histo [(year,era)] = {}

        for njet_bin in corrector.corrector.njet_bins:

            sigma_para_ratio_histo  [(year,era)][njet_bin] = ROOT.TH1F("sigma_para_ratio_%s_%s_nj_%i_%i"%(year, era, njet_bin[0], njet_bin[1]), "sigma_para_ratio_%s_%s"%(year, era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) ) 
            sigma_perp_ratio_histo  [(year,era)][njet_bin] = ROOT.TH1F("sigma_perp_ratio_%s_%s_nj_%i_%i"%(year, era, njet_bin[0], njet_bin[1]), "sigma_perp_ratio_%s_%s"%(year, era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) )
            median_para_shift_histo [(year,era)][njet_bin] = ROOT.TH1F("median_para_shift_%s_%s_nj_%i_%i"%(year, era, njet_bin[0], njet_bin[1]), "median_para_shift_%s_%s"%(year, era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) ) 
            median_perp_shift_histo [(year,era)][njet_bin] = ROOT.TH1F("median_perp_shift_%s_%s_nj_%i_%i"%(year, era, njet_bin[0], njet_bin[1]), "median_perp_shift_%s_%s"%(year, era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) )

            for i_qt_bin, qt_bin in enumerate(corrector.corrector.qt_bins):

                sigma_para_ratio_histo  [(year,era)][njet_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin)  
                sigma_perp_ratio_histo  [(year,era)][njet_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin) 
                median_para_shift_histo [(year,era)][njet_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin)  
                median_perp_shift_histo [(year,era)][njet_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin) 

                qm1,qm,qp1 =  corrector.corrector.para_matcher[njet_bin][qt_bin].get_h1_quantiles()
                para_mc_sigma  = 0.5*(qp1-qm1) 
                para_mc_median = qm
                qm1,qm,qp1 =  corrector.corrector.para_matcher[njet_bin][qt_bin].get_h2_quantiles()
                para_data_sigma  = 0.5*(qp1-qm1) 
                para_data_median = qm
                qm1,qm,qp1 =  corrector.corrector.perp_matcher[njet_bin][qt_bin].get_h1_quantiles()
                perp_mc_sigma  = 0.5*(qp1-qm1) 
                perp_mc_median = qm
                qm1,qm,qp1 =  corrector.corrector.perp_matcher[njet_bin][qt_bin].get_h2_quantiles()
                perp_data_sigma  = 0.5*(qp1-qm1) 
                perp_data_median = qm

                #print "Nj",njet_bin, "qt",qt_bin,"para mean shift", para_data_median-para_mc_median, "para sigmaD/sigmaMC", para_data_sigma/para_mc_sigma, "perp mean shift", perp_data_median-perp_mc_median, "perp sigmaD/sigmaMC", perp_data_sigma/perp_mc_sigma

                sigma_para_ratio_histo  [(year,era)][njet_bin].SetBinContent( i_qt_bin+1, para_data_sigma/para_mc_sigma )
                #print year, era, njet_bin, qt_bin, para_data_median, perp_data_median, para_data_sigma, perp_mc_sigma,  para_data_sigma/perp_mc_sigma 
                sigma_perp_ratio_histo  [(year,era)][njet_bin].SetBinContent( i_qt_bin+1, perp_data_sigma/perp_mc_sigma )
                median_para_shift_histo [(year,era)][njet_bin].SetBinContent( i_qt_bin+1, para_data_median - para_mc_median) 
                median_perp_shift_histo [(year,era)][njet_bin].SetBinContent( i_qt_bin+1, perp_data_median - perp_mc_median)

            for h in [ sigma_para_ratio_histo[(year,era)][njet_bin], sigma_perp_ratio_histo  [(year,era)][njet_bin], median_para_shift_histo [(year,era)][njet_bin], median_perp_shift_histo [(year,era)][njet_bin] ]:
                h.legendText = "%i"%year
                if era is not None:
                    h.legendText+= " (%s)"%era
                h.GetXaxis().LabelsOption("v")
                h.style = styles.lineStyle( color[(year, era)] ) 

    def modify_canvas(c):
        c.SetBottomMargin( 0.25 )

    for prefix, histos, texY, yRange in [
        [ "sigma_ratio_para", sigma_para_ratio_histo, "#sigma(Data)/sigma(MC)", (0.8,1.5)],
        [ "sigma_ratio_perp", sigma_perp_ratio_histo, "#sigma(Data)/sigma(MC)", (0.8,1.5)],
        [ "median_shift_para", median_para_shift_histo, "Median(Data) - Median(MC)",(-20,20)],
        [ "median_shift_perp", median_perp_shift_histo, "Median(Data) - Median(MC)",(-20,20)],
            ]:    
        for njet_bin in corrector.corrector.njet_bins:
            name = "%s_nj_%i_%i"%(prefix, njet_bin[0], njet_bin[1])
            plot = Plot.fromHisto(
                    name = name, 
                    histos = [ [ histos[(year, era)][njet_bin]] for year, era in eras ], 
                    #texX = "%s Jet #phi"%refname , texY = "response ratio plan1/plan0"
                    texY = texY 
                )
            plotting.draw(plot, 
                plot_directory = os.path.join(plot_directory,"StopsDilepton",postfix), ratio = None, logY = False, logX = False, 
                yRange=yRange,copyIndexPHP=True,
                canvasModifications = [modify_canvas])

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
recoilFitResultDir = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/recoil_v4.1/"
postfix = "recoil_v4.1"

class RecoilCorrector:

    def __init__( self, era):

        self.corrector = _RecoilCorrector( os.path.join( recoilFitResultDir, era+"_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl" ) )

    def predict_para(self, dl_phi, qt, u_para ):
        return self.corrector.predict_para( dl_phi, qt, u_para )

    def predict_perp(self, dl_phi, qt, u_perp ):
        return self.corrector.predict_perp( dl_phi, qt, u_perp )

if __name__=="__main__":

    from RootTools.core.standard import *
    from StopsDilepton.tools.user import plot_directory

    years = [( 2016, ( "Run2016BCD", "Run2016EF", "Run2016GH", )), 
             ( 2017, ( "Run2017B", "Run2017CDE", "Run2017F", )),
             ( 2018, ( "Run2018A", "Run2018B", "Run2018C", "Run2018D")) ]
    color = [  ROOT.kBlue,
               ROOT.kRed,
               ROOT.kGreen,
               ROOT.kMagenta,
            ]

    def modify_canvas(c):
        c.SetBottomMargin( 0.25 )

    for year, eras in years: 
        sigma_para_ratio_histo   = {}
        sigma_perp_ratio_histo   = {}
        median_para_shift_histo  = {}
        median_perp_shift_histo  = {}

        for i_era, era in enumerate(eras):
            corrector = RecoilCorrector(era)
            sigma_para_ratio_histo  [era] = {}
            sigma_perp_ratio_histo  [era] = {}
            median_para_shift_histo [era] = {}
            median_perp_shift_histo [era] = {}
            for dl_phi_bin in corrector.corrector.var_bins:

                sigma_para_ratio_histo  [era][dl_phi_bin] = ROOT.TH1F("sigma_para_ratio_%s_dlphi_%3.2f_%3.2f"%(era, dl_phi_bin[0], dl_phi_bin[1]), "sigma_para_ratio_%s"%(era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) ) 
                sigma_perp_ratio_histo  [era][dl_phi_bin] = ROOT.TH1F("sigma_perp_ratio_%s_dlphi_%3.2f_%3.2f"%(era, dl_phi_bin[0], dl_phi_bin[1]), "sigma_perp_ratio_%s"%(era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) )
                median_para_shift_histo [era][dl_phi_bin] = ROOT.TH1F("median_para_shift_%s_dlphi_%3.2f_%3.2f"%(era, dl_phi_bin[0], dl_phi_bin[1]), "median_para_shift_%s"%(era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) ) 
                median_perp_shift_histo [era][dl_phi_bin] = ROOT.TH1F("median_perp_shift_%s_dlphi_%3.2f_%3.2f"%(era, dl_phi_bin[0], dl_phi_bin[1]), "median_perp_shift_%s"%(era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) )

                for i_qt_bin, qt_bin in enumerate(corrector.corrector.qt_bins):

                    sigma_para_ratio_histo  [era][dl_phi_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin)  
                    sigma_perp_ratio_histo  [era][dl_phi_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin) 
                    median_para_shift_histo [era][dl_phi_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin)  
                    median_perp_shift_histo [era][dl_phi_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin) 

                    qm1,qm,qp1 =  corrector.corrector.para_matcher[dl_phi_bin][qt_bin].get_h1_quantiles()
                    para_mc_sigma  = 0.5*(qp1-qm1) 
                    para_mc_median = qm
                    qm1,qm,qp1 =  corrector.corrector.para_matcher[dl_phi_bin][qt_bin].get_h2_quantiles()
                    para_data_sigma  = 0.5*(qp1-qm1) 
                    para_data_median = qm
                    qm1,qm,qp1 =  corrector.corrector.perp_matcher[dl_phi_bin][qt_bin].get_h1_quantiles()
                    perp_mc_sigma  = 0.5*(qp1-qm1) 
                    perp_mc_median = qm
                    qm1,qm,qp1 =  corrector.corrector.perp_matcher[dl_phi_bin][qt_bin].get_h2_quantiles()
                    perp_data_sigma  = 0.5*(qp1-qm1) 
                    perp_data_median = qm

                    #print "Nj",dl_phi_bin, "qt",qt_bin,"para mean shift", para_data_median-para_mc_median, "para sigmaD/sigmaMC", para_data_sigma/para_mc_sigma, "perp mean shift", perp_data_median-perp_mc_median, "perp sigmaD/sigmaMC", perp_data_sigma/perp_mc_sigma

                    sigma_para_ratio_histo  [era][dl_phi_bin].SetBinContent( i_qt_bin+1, para_data_sigma/para_mc_sigma )
                    #print era, dl_phi_bin, qt_bin, para_data_median, perp_data_median, para_data_sigma, perp_mc_sigma,  para_data_sigma/perp_mc_sigma 
                    sigma_perp_ratio_histo  [era][dl_phi_bin].SetBinContent( i_qt_bin+1, perp_data_sigma/perp_mc_sigma )
                    median_para_shift_histo [era][dl_phi_bin].SetBinContent( i_qt_bin+1, para_data_median - para_mc_median) 
                    median_perp_shift_histo [era][dl_phi_bin].SetBinContent( i_qt_bin+1, perp_data_median - perp_mc_median)

                for h in [ sigma_para_ratio_histo[era][dl_phi_bin], sigma_perp_ratio_histo  [era][dl_phi_bin], median_para_shift_histo [era][dl_phi_bin], median_perp_shift_histo [era][dl_phi_bin] ]:
                    h.legendText = era
                    h.GetXaxis().LabelsOption("v")
                    h.style = styles.lineStyle( color[i_era] ) 

        for prefix, histos, texY, yRange in [
            [ "sigma_ratio_para", sigma_para_ratio_histo, "#sigma(Data)/sigma(MC)", (0.8,1.5)],
            [ "sigma_ratio_perp", sigma_perp_ratio_histo, "#sigma(Data)/sigma(MC)", (0.8,1.5)],
            [ "median_shift_para", median_para_shift_histo, "Median(Data) - Median(MC)",(-20,20)],
            [ "median_shift_perp", median_perp_shift_histo, "Median(Data) - Median(MC)",(-20,20)],
                ]:    
            for dl_phi_bin in corrector.corrector.var_bins:
                name = "%s_%i_dlphi_%3.2f_%3.2f"%(prefix, year, dl_phi_bin[0], dl_phi_bin[1])
                plot = Plot.fromHisto(
                        name = name, 
                        histos = [ [ histos[era][dl_phi_bin]] for era in eras ], 
                        #texX = "%s Jet #phi"%refname , texY = "response ratio plan1/plan0"
                        texY = texY 
                    )
                plotting.draw(plot, 
                    plot_directory = os.path.join(plot_directory,"StopsDilepton",postfix), ratio = None, logY = False, logX = False, 
                    yRange=yRange,copyIndexPHP=True,
                    canvasModifications = [modify_canvas])

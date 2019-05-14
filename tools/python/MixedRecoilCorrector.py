''' Mixed recoil corrector for Stops-2l
'''
# Standard imports
import os
import ROOT
import random

# Analysis
from Analysis.Tools.RecoilCorrector import RecoilCorrector as _RecoilCorrector

# Logging
import logging
logger = logging.getLogger(__name__)

# Recoil data directories
recoil_subdir = "recoil_v0p10_fine"
recoil_dir    = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/"

# eras
eras_ = {
    'Run2016BCD':{ 'lumi':5.883+2.646+4.353,    'file': "Run2016BCD_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
    'Run2016EF' :{ 'lumi':4.050+3.124,          'file': "Run2016EF_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
    'Run2016GH' :{ 'lumi':7.554+8.494+0.217,    'file': "Run2016GH_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
    'Run2017B'  :{ 'lumi':4.823,                'file': "Run2017B_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
    'Run2017CDE':{ 'lumi':9.664+4.252+9.278,    'file': "Run2017CDE_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
    'Run2017F'  :{ 'lumi':13.540,               'file': "Run2017F_lepSel-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
    'Run2018A'  :{ 'lumi':14.00,                'file': "Run2018A_lepSel-HEMJetVetoWide-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
    'Run2018B'  :{ 'lumi':7.10,                 'file': "Run2018B_lepSel-HEMJetVetoWide-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
    'Run2018C'  :{ 'lumi':6.94,                 'file': "Run2018C_lepSel-HEMJetVetoWide-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
    'Run2018D'  :{ 'lumi':31.93,                'file': "Run2018D_lepSel-HEMJetVetoWide-njet1p-btag0-relIso0.12-looseLeptonVeto-mll20-onZ_recoil_fitResults_SF.pkl"},
}

eras = { k: [ (v['lumi'], v['file']) ] for k, v in eras_.iteritems() }

for era_sum, era_const in [
        [ "Run2016", ["Run2016BCD", "Run2016EF", "Run2016GH"] ],
        [ "Run2017", ["Run2017B", "Run2017CDE", "Run2017F"] ],
        [ "Run2018", ["Run2018A", "Run2018B", "Run2018C", "Run2018D"] ],
    ]:
    eras[era_sum] = sum( [eras[k] for k in era_const], [] )

class MixedRecoilCorrector:

    def __init__( self, era):

        self.eras = eras[era]
        lumis = [ e[0] for e in self.eras ]
        tot_lumi = sum( lumis )
        self.random_thresholds = [sum(lumis[:i+1])/tot_lumi for i in range(len(lumis)-1) ] + [1.]
        self.correctors = [ _RecoilCorrector( os.path.join( recoil_dir, recoil_subdir, e[1])) for e in self.eras ]
        

    def predict_para(self, *args, **kwargs):
        x = random.random()
        for i_th, th in enumerate( self.random_thresholds ):
            if x<th:
                #print "Random number",x,"corr",i_th
                return self.correctors[i_th].predict_para( *args, **kwargs )

    def predict_perp(self, *args, **kwargs):
        x = random.random()
        for i_th, th in enumerate( self.random_thresholds ):
            if x<th:
                #print "Random number",x,"corr",i_th
                return self.correctors[i_th].predict_perp( *args, **kwargs )


m = MixedRecoilCorrector("Run2016")

#class RecoilCorrector:
#
#    def __init__( self, year, era = None):
#
#        if year == 2016:
#            self.corrector = _RecoilCorrector( os.path.join( recoilFitResultDir, "2016_recoil_fitResults_SF.pkl" ) )
#        if year == 2017:
#            self.corrector = _RecoilCorrector( os.path.join( recoilFitResultDir, "2017_recoil_fitResults_SF.pkl" ) )
#        if year == 2018:
#            if era=="preHEM":
#                self.corrector  = _RecoilCorrector( os.path.join( recoilFitResultDir, "2018_preHEM_recoil_fitResults_SF.pkl" ) )
#            elif era=="postHEM":
#                self.corrector = _RecoilCorrector( os.path.join( recoilFitResultDir, "2018_postHEM_recoil_fitResults_SF.pkl" ) )
#            else:
#                self.corrector = _RecoilCorrector( os.path.join( recoilFitResultDir, "2018_recoil_fitResults_SF.pkl" ) )
#
#    def predict_para(self, njet, qt, u_para ):
#        if njet<1: return u_para # in case of jesTotalUp/Down within systematics variation
#        return self.corrector.predict_para( njet, qt, u_para )
#
#    def predict_perp(self, njet, qt, u_perp ):
#        if njet<1: return u_perp # in case of jesTotalUp/Down witin systematics variation
#        return self.corrector.predict_perp( njet, qt, u_perp )

#if __name__=="__main__":

#    from RootTools.core.standard import *
#    from StopsDilepton.tools.user import plot_directory
#
#    eras = [ ( 2016, None), (2017, None), (2018, "preHEM"), (2018, "postHEM")]
#
#    color = { ( 2016, None): ROOT.kBlue,
#              ( 2017, None): ROOT.kRed,
#              ( 2018, "preHEM"): ROOT.kGreen,
#              ( 2018, "postHEM"):ROOT.kMagenta,
#            }
#    sigma_para_ratio_histo  = {}
#    sigma_perp_ratio_histo  = {}
#    median_para_shift_histo = {}
#    median_perp_shift_histo = {}
#    
#    for year, era in eras: 
#        corrector = RecoilCorrector(year, era)
#        sigma_para_ratio_histo  [(year,era)] = {}
#        sigma_perp_ratio_histo  [(year,era)] = {}
#        median_para_shift_histo [(year,era)] = {}
#        median_perp_shift_histo [(year,era)] = {}
#
#        for njet_bin in corrector.corrector.njet_bins:
#
#            sigma_para_ratio_histo  [(year,era)][njet_bin] = ROOT.TH1F("sigma_para_ratio_%s_%s_nj_%i_%i"%(year, era, njet_bin[0], njet_bin[1]), "sigma_para_ratio_%s_%s"%(year, era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) ) 
#            sigma_perp_ratio_histo  [(year,era)][njet_bin] = ROOT.TH1F("sigma_perp_ratio_%s_%s_nj_%i_%i"%(year, era, njet_bin[0], njet_bin[1]), "sigma_perp_ratio_%s_%s"%(year, era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) )
#            median_para_shift_histo [(year,era)][njet_bin] = ROOT.TH1F("median_para_shift_%s_%s_nj_%i_%i"%(year, era, njet_bin[0], njet_bin[1]), "median_para_shift_%s_%s"%(year, era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) ) 
#            median_perp_shift_histo [(year,era)][njet_bin] = ROOT.TH1F("median_perp_shift_%s_%s_nj_%i_%i"%(year, era, njet_bin[0], njet_bin[1]), "median_perp_shift_%s_%s"%(year, era), len(corrector.corrector.qt_bins),0,len(corrector.corrector.qt_bins) )
#
#            for i_qt_bin, qt_bin in enumerate(corrector.corrector.qt_bins):
#
#                sigma_para_ratio_histo  [(year,era)][njet_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin)  
#                sigma_perp_ratio_histo  [(year,era)][njet_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin) 
#                median_para_shift_histo [(year,era)][njet_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin)  
#                median_perp_shift_histo [(year,era)][njet_bin].GetXaxis().SetBinLabel(i_qt_bin+1, "%i<q_{T}<%i"%qt_bin) 
#
#                qm1,qm,qp1 =  corrector.corrector.para_matcher[njet_bin][qt_bin].get_h1_quantiles()
#                para_mc_sigma  = 0.5*(qp1-qm1) 
#                para_mc_median = qm
#                qm1,qm,qp1 =  corrector.corrector.para_matcher[njet_bin][qt_bin].get_h2_quantiles()
#                para_data_sigma  = 0.5*(qp1-qm1) 
#                para_data_median = qm
#                qm1,qm,qp1 =  corrector.corrector.perp_matcher[njet_bin][qt_bin].get_h1_quantiles()
#                perp_mc_sigma  = 0.5*(qp1-qm1) 
#                perp_mc_median = qm
#                qm1,qm,qp1 =  corrector.corrector.perp_matcher[njet_bin][qt_bin].get_h2_quantiles()
#                perp_data_sigma  = 0.5*(qp1-qm1) 
#                perp_data_median = qm
#
#                #print "Nj",njet_bin, "qt",qt_bin,"para mean shift", para_data_median-para_mc_median, "para sigmaD/sigmaMC", para_data_sigma/para_mc_sigma, "perp mean shift", perp_data_median-perp_mc_median, "perp sigmaD/sigmaMC", perp_data_sigma/perp_mc_sigma
#
#                sigma_para_ratio_histo  [(year,era)][njet_bin].SetBinContent( i_qt_bin+1, para_data_sigma/para_mc_sigma )
#                #print year, era, njet_bin, qt_bin, para_data_median, perp_data_median, para_data_sigma, perp_mc_sigma,  para_data_sigma/perp_mc_sigma 
#                sigma_perp_ratio_histo  [(year,era)][njet_bin].SetBinContent( i_qt_bin+1, perp_data_sigma/perp_mc_sigma )
#                median_para_shift_histo [(year,era)][njet_bin].SetBinContent( i_qt_bin+1, para_data_median - para_mc_median) 
#                median_perp_shift_histo [(year,era)][njet_bin].SetBinContent( i_qt_bin+1, perp_data_median - perp_mc_median)
#
#            for h in [ sigma_para_ratio_histo[(year,era)][njet_bin], sigma_perp_ratio_histo  [(year,era)][njet_bin], median_para_shift_histo [(year,era)][njet_bin], median_perp_shift_histo [(year,era)][njet_bin] ]:
#                h.legendText = "%i"%year
#                if era is not None:
#                    h.legendText+= " (%s)"%era
#                h.GetXaxis().LabelsOption("v")
#                h.style = styles.lineStyle( color[(year, era)] ) 
#
#    def modify_canvas(c):
#        c.SetBottomMargin( 0.25 )
#
#    for prefix, histos, texY, yRange in [
#        [ "sigma_ratio_para", sigma_para_ratio_histo, "#sigma(Data)/sigma(MC)", (0.8,1.5)],
#        [ "sigma_ratio_perp", sigma_perp_ratio_histo, "#sigma(Data)/sigma(MC)", (0.8,1.5)],
#        [ "median_shift_para", median_para_shift_histo, "Median(Data) - Median(MC)",(-20,20)],
#        [ "median_shift_perp", median_perp_shift_histo, "Median(Data) - Median(MC)",(-20,20)],
#            ]:    
#        for njet_bin in corrector.corrector.njet_bins:
#            name = "%s_nj_%i_%i"%(prefix, njet_bin[0], njet_bin[1])
#            plot = Plot.fromHisto(
#                    name = name, 
#                    histos = [ [ histos[(year, era)][njet_bin]] for year, era in eras ], 
#                    #texX = "%s Jet #phi"%refname , texY = "response ratio plan1/plan0"
#                    texY = texY 
#                )
#            plotting.draw(plot, 
#                plot_directory = os.path.join(plot_directory,"StopsDilepton",postfix), ratio = None, logY = False, logX = False, 
#                yRange=yRange,copyIndexPHP=True,
#                canvasModifications = [modify_canvas])

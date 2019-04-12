''' recoil corrector for Stops-2l
'''

from Analysis.Tools.RecoilCorrector import RecoilCorrector as _RecoilCorrector
import os

recoilFitResultDir = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/recoilCorrections/"

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
        return self.corrector.predict_para( njet, qt, u_para )

    def predict_perp(self, njet, qt, u_perp ):
        return self.corrector.predict_perp( njet, qt, u_perp )

            

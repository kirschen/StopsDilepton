from StopsDilepton.analysis.MCBasedEstimate              import MCBasedEstimate
from StopsDilepton.analysis.DataDrivenDYEstimate         import DataDrivenDYEstimate
from StopsDilepton.analysis.DataDrivenMultiBosonEstimate import DataDrivenMultiBosonEstimate
#from StopsDilepton.analysis.DataDrivenTTZEstimate        import DataDrivenTTZEstimate
from StopsDilepton.analysis.DataDrivenTTJetsEstimate     import DataDrivenTTJetsEstimate
from StopsDilepton.analysis.Region                       import *

class estimatorList:
    def __init__(self, setup, samples=['DY','TTJets','TTZ','multiBoson','other','TTXNoZ','Top_gaussian','Top_nongaussian','Top_fakes', 'TTJets-DD']):
        for s in samples:
            if not s.count('DD'):
                setattr(self, s, MCBasedEstimate(name=s, sample=setup.samples[s]))
            else:
                setattr(self, s, DataDrivenTTJetsEstimate(name='TTJets-DD', controlRegion=Region('dl_mt2ll', (0,100))))
                
        
    def constructEstimatorList(self, samples):
        self.estimatorList = [ getattr(self, s) for s in samples ]
        return self.estimatorList



class xSecSusy:
    def __init__(self):
        from StopsDilepton.tools.xSecSusyData.stops_13TeV import xsec as stop13TeV
        self.xSec = {
            'stop13TeV':stop13TeV
        }

    def getXSec(self, mass, sigma=0, channel='stop13TeV'):
        return self.xSec[channel][mass][0]+sigma*self.xSec[channel][mass][1]*self.xSec[channel][mass][0]

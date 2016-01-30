from StopsDilepton.tools.helpers import getYieldFromChain
from math import sqrt
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator
from StopsDilepton.analysis.u_float import u_float
from StopsDilepton.tools.helpers import printHeader

class DataDrivenDYEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(DataDrivenDYEstimate, self).__init__(name, cacheDir=cacheDir)
#Concrete implementation of abstract method 'estimate' as defined in Systematic
    def _estimate(self, region, channel, setup):

        printHeader("DD DY prediction for %s channel %s" %(self.name, channel))

        #Sum of all channels for 'all'
        if channel=='all':
            return sum( [ self.cachedEstimate(region, c, setup) for c in ['MuMu', 'EE', 'EMu'] ], u_float(0.,0.) )

        #MC based for 'EMu'
        elif channel=='EMu':
            preSelection = setup.preselection('MC', zWindow='allZ', channel=channel)
            cut = "&&".join([region.cutString(setup.sys['selectionModifier']), preSelection['cut'] ])
            weight = preSelection['weightStr']

            if setup.verbose:
                print "Using cut %s and weight %s"%(cut, weight)
            return setup.lumi[channel]/1000. * u_float( getYieldFromChain(setup.sample['DY'][channel]['chain'], cutString = cut, weight=weight, returnError = True) )

        #Data driven for EE and MuMu
        else:
            preSelection = setup.preselection('MC', zWindow='offZ', channel=channel)
            weight = preSelection['weightStr']

            assert abs(1.-setup.lumi[channel]/setup.sample['Data'][channel]['lumi'])<0.01, "Lumi specified in setup %f does not match lumi in data sample %f in channel %s"%(setup.lumi[channel], setup.sample['Data'][channel]['lumi'], channel)
            cut_offZ_1b = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('MC', channel=channel, zWindow = 'offZ', **setup.defaultParameters(update={'nBTags':(1,-1)}))['cut'] ])
            cut_onZ_1b  = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('MC', channel=channel, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(1,-1)}))['cut'] ])
            cut_onZ_0b  = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('MC', channel=channel, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(0,0)}))['cut'] ])
            cut_data_onZ_0b    = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('Data', channel=channel, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(0,0)}) )['cut'] ])
    #    R1 = DY-MC (offZ, 1b) / DY-MC (onZ, 1b)
    #    R2 = DY-MC (onZ, 1b) / DY-MC (onZ, 0b)
    #    DY-est = R1*R2*(Data(2l, onZ, 0b) - EWK(onZ, 0b)) = DY-MC (offZ, 1b) / DY-MC (onZ, 0b) *( Data(2l, onZ, 0b) - EWK(onZ, 0b))

            yield_offZ_1b = u_float( getYieldFromChain(setup.sample['DY'][channel]['chain'], cutString = cut_offZ_1b, weight=weight, returnError = True))
            if setup.verbose: print "yield_offZ_1b: %s"%yield_offZ_1b
            yield_onZ_0b  = u_float( getYieldFromChain(setup.sample['DY'][channel]['chain'], cutString = cut_onZ_0b,  weight=weight, returnError = True))
            if setup.verbose: print "yield_onZ_0b: %s"%yield_onZ_0b
            yield_data    = u_float( getYieldFromChain(setup.sample['Data'][channel]['chain'], cutString = cut_data_onZ_0b,  weight=weight, returnError = True))
            if setup.verbose: print "yield_data: %s (for cut: %s \n with weight: %s)"%(yield_data, cut_data_onZ_0b, weight)

            #electroweak subtraction
            print "\n Substracting electroweak backgrounds from data: \n"
            yield_other = u_float(0., 0.)
            for s in ['TTJets' , 'TTZ' , 'other']:
                yield_other+=u_float(getYieldFromChain(setup.sample[s][channel]['chain'], cutString = cut_onZ_0b,  weight=weight, returnError=True))
                if setup.verbose: print "yield_other_onZ_0b %s added, now: %s"%(s, yield_other)

            normRegYield = yield_data - yield_other
            if normRegYield.val<0: print "\n !!!Warning!!! \n Negative normalization region yield data: (%s), MC: (%s) \n"%(yield_data, yield_other)

            mcRatio = yield_offZ_1b / yield_onZ_0b
            res = mcRatio * normRegYield

            return res

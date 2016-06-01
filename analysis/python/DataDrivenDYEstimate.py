from math import sqrt
from StopsDilepton.analysis.SystematicEstimator import SystematicEstimator
from StopsDilepton.analysis.u_float import u_float

class DataDrivenDYEstimate(SystematicEstimator):
    def __init__(self, name, cacheDir=None):
        super(DataDrivenDYEstimate, self).__init__(name, cacheDir=cacheDir)

    #Concrete implementation of abstract method 'estimate' as defined in Systematic
    def _estimate(self, region, channel, setup):

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
            return setup.lumi[channel]/1000. * u_float(**setup.sample['DY'][channel].getYieldFromDraw(selectionString = cut, weightString=weight))

        #Data driven for EE and MuMu
        else:
            preSelection = setup.preselection('MC', zWindow='offZ', channel=channel)
            weight = preSelection['weightStr']

            cut_offZ_1b     = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=channel, zWindow = 'offZ', **setup.defaultParameters(update={'nBTags':(1,-1)}))['cut']])
            cut_onZ_1b      = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=channel, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(1,-1)}))['cut']])
            cut_onZ_0b      = "&&".join([region.cutString(setup.sys['selectionModifier']), setup.selection('MC',   channel=channel, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(0,0 )}))['cut']])
            cut_data_onZ_0b = "&&".join([region.cutString(),                               setup.selection('Data', channel=channel, zWindow = 'onZ',  **setup.defaultParameters(update={'nBTags':(0,0 )}))['cut']])
    #    R1 = DY-MC (offZ, 1b) / DY-MC (onZ, 1b)
    #    R2 = DY-MC (onZ, 1b) / DY-MC (onZ, 0b)
    #    DY-est = R1*R2*(Data(2l, onZ, 0b) - EWK(onZ, 0b)) = DY-MC (offZ, 1b) / DY-MC (onZ, 0b) *( Data(2l, onZ, 0b) - EWK(onZ, 0b))

            yield_offZ_1b = u_float(**setup.sample['DY'][channel].getYieldFromDraw(  selectionString = cut_offZ_1b,     weightString=weight))
            yield_onZ_0b  = u_float(**setup.sample['DY'][channel].getYieldFromDraw(  selectionString = cut_onZ_0b,      weightString=weight))
            yield_data    = u_float(**setup.sample['Data'][channel].getYieldFromDraw(selectionString = cut_data_onZ_0b, weightString="(1)"))
            if setup.verbose: 
              print "yield_offZ_1b: %s"%yield_offZ_1b
              print "yield_onZ_0b: %s"%yield_onZ_0b
              print "yield_data: %s (for cut: %s \n with weight: %s)"%(yield_data, cut_data_onZ_0b, weight)

            #electroweak subtraction
            print "\n Substracting electroweak backgrounds from data: \n"
            yield_other = u_float(0., 0.)
            for s in ['TTJets' , 'TTZ' , 'other']:
                yield_other+=u_float(**setup.sample[s][channel].getYieldFromDraw(selectionString = cut_onZ_0b, weightString=weight))
                if setup.verbose: print "yield_other_onZ_0b %s added, now: %s"%(s, yield_other)

            normRegYield = yield_data - yield_other
            if normRegYield.val<0: print "\n !!!Warning!!! \n Negative normalization region yield data: (%s), MC: (%s) \n"%(yield_data, yield_other)

            mcRatio = yield_offZ_1b / yield_onZ_0b if yield_onZ_0b > 0 else 0
            res = mcRatio * normRegYield

            return res

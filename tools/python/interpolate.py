import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/interpolate.h")

def interpolate(h, firstInterpolationDirection="NE"):
    '''interpolate() implements a two step smearing. Its arguments are the histogram that should be interpolated
and the direction in which to interpolate first (normally the direction in which the histogram changes
most slowly).
Allowed types are SW (equivalently NE), SE (equivalently NW), NS, EW
The second interpolation uses a "Swiss Cross" average (non-zero N, S, E, W neighbors)'''
    return ROOT.interpolate(h, firstInterpolationDirection)

def rebin(h, firstInterpolationDirection="NE"):
    '''increases binning by factor of two and rebins in specified direction'''
    return ROOT.rebin(h, firstInterpolationDirection)

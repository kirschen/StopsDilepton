allowedVars = ["dl_mt2ll", "dl_mt2blbl", "dl_mt2bb", "MET_pt"]
texString  = { "dl_mt2ll":"M_{T2}(ll)", "dl_mt2blbl":"M_{T2}(blbl)", "dl_mt2bb":"M_{T2}(bb)", "MET_pt":"E_{T}^{miss}" }

from StopsDilepton.analysis.SystematicEstimator import jmeVariations, metVariations
from StopsDilepton.analysis.fastSimGenMetReplacements import fastSimGenMetReplacements

class Region:

    def __init__(self, var, val):
        assert type(val)==type(()) and len(val)==2, "Don't know how to make region with this val argument: %r."%val
#    assert type(var)==type(""), "Argument 'var' must be string"
        assert var in allowedVars, "Use only these variables: %r"%allowedVars
        assert val[0]>=0, "Need nonzero lower threshold."
        self.vals = {var:val}

    def variables(self):
        return self.vals.keys()

    def __iadd__(self, otherRegion):
        if not type(self)==type(otherRegion): raise TypeError("Can't add this type to a region %r"%type(otherRegion))
        for v in otherRegion.vals.keys():
            assert v not in self.vals.keys(), "Can't add regions, variable %s in both summands!"%v
        self.vals.update(otherRegion.vals)
        return self

    def __add__(self, otherRegion):
        if not type(self)==type(otherRegion): raise TypeError("Can't add this type to a region %r"%type(otherRegion))
        for v in otherRegion.vals.keys():
            assert v not in self.variables(), "Can't add regions, variable %s in both summands!"%v
        import copy
        res=copy.deepcopy(self)
        res.vals.update(otherRegion.vals)
        return res

    def cutString(self, selectionModifier=None):
        if selectionModifier: assert selectionModifier in jmeVariations+metVariations+['genMet'] or 'nVert' in selectionModifier or 'MVA' in selectionModifier, "Don't know about systematic variation %r, take one of %s"%(selectionModifier, ",".join(jmeVariations+['genMet']))

        sysStr = ""
        metStr = ""
        if selectionModifier in jmeVariations:
            sysStr = "_" + selectionModifier
        if selectionModifier in metVariations:
            metStr = "_" + selectionModifier

        res=[]
        for var in self.variables():
            if var.count('met'): svar = var + sysStr + metStr
            else:                svar = var if (not selectionModifier or selectionModifier == 'genMet' or 'nVert' in selectionModifier or 'MVA' in selectionModifier) else var+"_"+selectionModifier
            s1=svar+">="+str(self.vals[var][0])
            if self.vals[var][1]>0: s1+="&&"+svar+"<"+str(self.vals[var][1])
            res.append(s1)
        if selectionModifier=='genMet':
            res = [fastSimGenMetReplacements(r) for r in res]
        return "&&".join(res)

    def texStringForVar(self, var = None, useRootLatex = True):
        if var not in self.variables(): return None
	s1=str(self.vals[var][0]) + (" #leq " if useRootLatex else " \\leq ") + texString[var]
	if self.vals[var][1]>0: s1+=" < "+str(self.vals[var][1])
	return s1


    def texString(self, useRootLatex = True):
        res=[]
        for var in allowedVars: #Always keep the sequence in allowedVars
            if var in self.variables():
                res.append(self.texStringForVar(var, useRootLatex))
        return ", ".join(res)

    def __str__(self):
        return self.cutString()

    def __repr__(self):
        ''' Sorry.'''
#    return self.cutString()
        return "+".join([ "Region('%s', %r)"%(v, self.vals[v]) for v in self.variables()])

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

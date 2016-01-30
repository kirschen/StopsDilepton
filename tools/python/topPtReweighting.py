from math import exp, sqrt

#def getUnscaledTopPtReweightungFunction(a,b):
#  def f(pt1):
#    return exp(a+b*pt1)
#  return f

#https://indico.cern.ch/event/463433/contribution/5/attachments/1193635/1733505/MSavitskyi_ToppTRew13TeV_TopModGen.pdf
aDef = 0.148
bDef = -0.00129

def getUnscaledTopPairPtReweightungFunction(a=aDef, b=bDef):
    def f(topPts):
        assert len(topPts)<=2, "Found too many top pts: %i"%len(topPts)
        res=1.
        for pt in topPts:
            res*=exp(a+b*pt)
        return sqrt(res)
    return f

#https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting
def getTopPtDrawString(a=aDef, b=bDef):
#  assert b < 0, "b is not a negative number"
    return "sqrt(exp(Sum$(("+str(a)+"+("+str(b)+")*genPartAll_pt)*(abs(genPartAll_pdgId)==6&&genPartAll_nDaughters==2&&genPartAll_status==62&&genPartAll_pt<=400))))"

def getTopPtsForReweighting(r):
    res=[]
    for i in range(r.ngenPartAll):
        if abs(r.genPartAll_pdgId[i])==6 and r.genPartAll_nDaughters[i]==2 and r.genPartAll_status[i]==62 and r.genPartAll_pt[i]<400:
            res.append(r.genPartAll_pt[i])
    return res

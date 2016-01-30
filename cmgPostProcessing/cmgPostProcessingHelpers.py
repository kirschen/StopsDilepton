import ROOT
def getTreeFromChunk(c, skimCond, iSplit=0, nSplit=1, treeName='tree'):
    if not c.has_key('file'):return
    rf = ROOT.TFile.Open(c['file'])
    assert not rf.IsZombie()
    rf.cd()
    tc = rf.Get(treeName)
    nTot = tc.GetEntries()
    fromFrac = iSplit/float(nSplit)
    toFrac   = (iSplit+1)/float(nSplit)
    start = int(fromFrac*nTot)
    stop  = int(toFrac*nTot)
    ROOT.gDirectory.cd('PyROOT:/')
    print "Copy tree from source: total number of events found:",nTot,"Split counter: ",iSplit,"<",nSplit,"first Event:",start,"nEvents:",stop-start
    t = tc.CopyTree(skimCond,"",stop-start,start)
    tc.Delete()
    del tc
    rf.Close()
    del rf
    return t


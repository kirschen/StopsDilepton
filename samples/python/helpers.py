def getSubDir(dataset):
    import re
    m=re.match("\/(.*)\/(.*)\/(.*)",dataset)
    if not m :
        print "NO GOOD DATASET"
        return
    sample=m.group(1)+"_"+m.group(2)
    return sample

def combineSamples(sList):
    import copy
    if not sList: return
    assert all([s.has_key("bins") for s in sList]), "Key 'bins' not found in one or more samples."
    assert len(list(set(s['dir'] for s in sList)))==1, "Directories not unique!"
    res = copy.deepcopy(sList[0])
    for s in sList[1:]:
        res['bins'].extend(s['bins'])
    return res

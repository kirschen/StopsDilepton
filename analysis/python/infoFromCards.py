def getPull(nuisanceFile, name):
    with open(nuisanceFile) as f:
      for line in f:
        if name != line.split()[0]: continue
        return float(line.split(',')[0].split()[-1])
    return 0 # Sometimes a bin is not found in the nuisance file because its yield is 0

def getUncFromCard(cardFile, estimateName, uncName, bin):
    with open(cardFile) as f:
      binList = False
      estimateList = False
      for line in f:
        if len(line.split())==0: continue
        if line.split()[0] == "bin":
          if not binList: binList = True
          else:           binList = line.split()[1:]
        if line.split()[0] == "process":
          if not estimateList: estimateList = line.split()[1:]
        if line.split()[0] != uncName: continue
        for i in range(len(binList)):
          if binList[i] == ('Bin' + str(bin)) and estimateList[i]==estimateName:
	    try:    return float(line.split()[2:][i])-1.
	    except: return 0 # muted bin has -, cannot be converted to float

def applyNuisance(cardsFile, estimate, res, bin):
    nuisanceFile = cardsFile.replace('.txt','_nuisances_full.txt')
    if not estimate.name in ['DY','multiBoson']: return res
    scaledRes  = res*(1+getUncFromCard(cardsFile, estimate.name, estimate.name, bin)*getPull(nuisanceFile, estimate.name))
    scaledRes2 = scaledRes*(1+res.sigma/res.val*getPull(nuisanceFile, 'Stat_Bin' + str(bin) + '_' + estimate.name)) if scaledRes.val > 0 else scaledRes
    return scaledRes2

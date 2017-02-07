def getPull(nuisanceFile, name):
    with open(nuisanceFile) as f:
      for line in f:
        if name != line.split()[0]: continue
        return float(line.split(',')[0].split()[-1])
    return 0 # Sometimes a bin is not found in the nuisance file because its yield is 0

    # Returns something of the form "Bin0" if bin name (as written in the comment lines of the cards) are given
def getBinNumber(cardFile, binName):
    with open(cardFile) as f:
      for line in f:
        if binName in line: return line.split(':')[0].split()[-1]

def getFittedUncertainty(nuisanceFile, name):
    with open(nuisanceFile) as f:
      for line in f:
        if name != line.split()[0]: continue
        return float(line.split(',')[1].split()[0].replace('!','').replace('*',''))
    return 0 # Sometimes a bin is not found in the nuisance file because its yield is 0


def getPostFitUncFromCard(cardFile, estimateName, uncName, binName):
    nuisanceFile = cardFile.replace('.txt','_nuisances_full.txt')
    return getFittedUncertainty(nuisanceFile, estimateName)*getPreFitUncFromCard(cardFile, estimateName, uncName, binName)

def getPreFitUncFromCard(cardFile, estimateName, uncName, binName):
    binNumber = getBinNumber(cardFile, binName)
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
          if binList[i] == binNumber and estimateList[i]==estimateName:
            try:    return float(line.split()[2:][i])-1
            except: 
              return 0. # muted bin has -, cannot be converted to float
      raise Warning('No uncertainty for ' + estimateName + ' ' + binName)

def applyNuisance(cardFile, estimate, res, binName):
    if not estimate.name in ['DY','multiBoson','TTZ']: return res
    nuisanceFile = cardFile.replace('.txt','_nuisances_full.txt')
    binNumber    = getBinNumber(cardFile, binName)
    scaledRes    = res*(1+getPreFitUncFromCard(cardFile, estimate.name, estimate.name, binName)*getPull(nuisanceFile, estimate.name))
    scaledRes2   = scaledRes*(1+res.sigma/res.val*getPull(nuisanceFile, 'Stat_' + binNumber + '_' + estimate.name)) if scaledRes.val > 0 else scaledRes
    return scaledRes2

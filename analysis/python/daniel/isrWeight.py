
class ISRweight:

  def __init__(self):
    #Parameters for 2016 data
    self.weights = [1, 0.920, 0.821, 0.715, 0.662, 0.561, 0.511]

  def getWeightString(self):

    self.weightStr = '( '
    njet_max = len(self.weights)-1

    for njet, weight in enumerate(self.weights):
      op = '=='
      if njet == njet_max: op = '>='
      self.weightStr += '{}*(nIsr{}{}) + '.format(weight,op,njet)

    self.weightStr += ' 0 )'

    return self.weightStr

from StopsDilepton.tools.helpers import getChain

channels = ['EE', 'MuMu', 'EMu']
allChannels = ['all', 'EE', 'MuMu', 'EMu']

#def loadChain(s, verbose=False):
#    '''Use this function to add the chain to the sample dictionary.
#Will not load again if has already loaded'''
#    if not s.has_key('chain'):
#        if verbose:print "Loading chain for sample %s. (Only the first time)."%s['name']
#        s['chain']=getChain(s)

from StopsDilepton.tools.helpers import mZ
def getZCut(mode, zMassRange=15):
    zstr = "abs(dl_mass - "+str(mZ)+")"
    if mode.lower()=="onz": return zstr+"<="+str(zMassRange)
    if mode.lower()=="offz": return zstr+">"+str(zMassRange)
    return "(1)"


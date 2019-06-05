''' Implement veto list functionality
'''
# Standard imports
import pickle
import os

# Logging
import logging
logger = logging.getLogger(__name__)

class vetoList:
    def __init__(self, filenames):
        self.events = {}
        import os, sys

        self.filenames=filenames if type(filenames)==type([]) else [filenames]
        count = 0
        for filename in self.filenames:
            if not os.path.exists(filename):    
                raise ValueError( "File %s not found." % filename )
            if filename.endswith('.tar.gz'):
                import tarfile
                tar = tarfile.open(filename, 'r:gz')
                logger.debug( "Loaded vetoList %s", filename )
                for member in tar.getmembers():
                    logger.debug( "Found file %s", member.name )
                    f=tar.extractfile(member)
                    count += self.read(f)
                    logger.debug( "Loaded %i events from %s in %s", count,  member.name, filename)
            elif filename.endswith('.txt.gz'):
                import gzip
                with gzip.open(filename, 'rb') as f:
                  logger.debug( "Found file %s" % filename )
                  count += self.read(f)
            elif filename.endswith('.pkl'):
                events = pickle.load(file(filename))
                count += len(events)
                for event in events:
                    self.add_event( *event) 
            else:
                raise ValueError( "Can't load file %s", filename )
            logger.debug( "So far loaded %i events from %s", count, filename )
            print "So far loaded %i events from %s" %( count, filename )
        logger.info( "Loaded in total %i events from %i files.", len(self.events), len(filenames) )

    @classmethod
    def fromDirectory( cls, directory ):
        filenames = []
        for filename in os.listdir(directory):
            if filename.endswith( '.pkl' ):
                filenames.append(os.path.join(directory,filename))
        return cls( filenames ) 

    def read(self, f):
        count=0
        for x in f.read().split('\n'):
            try:
               (run, lumi, event) = tuple([int(i) for i in x.split(":")])
               self.add_event( run, lumi, event )
               count+=1
            except:
               logger.debug( "Skipping line %s", x)
        return count

    def add_event( self, run, lumi, event):
       if run not in self.events:         self.events[run] = {lumi : [event]}
       elif lumi not in self.events[run]: self.events[run][lumi] = [event]
       else:                              self.events[run][lumi].append(event)

    def passesVeto(self, run, lumi, event):
        if run not in self.events or lumi not in self.events[run]: return True
        return (event not in self.events[run][lumi])

    def write_pkl(self, filename):
        events=[]
        for run in self.events.keys():
            for lumi in self.events[run].keys():
                for event in self.events[run][lumi]:  
                    events.append( (run, lumi, event) )
        pickle.dump( events, file(filename, 'w') ) 

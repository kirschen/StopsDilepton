''' Implement veto list functionality
'''

# Logging
import logging
logger = logging.getLogger(__name__)

class vetoList:
    def __init__(self, filenames):
        self.events=set([])
        import os, sys

        self.filenames=filenames if type(filenames)==type([]) else [filenames]
        for filename in self.filenames:
            if not os.path.exists(filename):    
                raise ValueError( "File %s not found." % filename )

            if filename.endswith('.tar.gz'):
                import tarfile
                tar = tarfile.open(filename, 'r:gz')
                logger.debug( "Loaded vetoList %s", filename )
                count = 0
                for member in tar.getmembers():
                    logger.debug( "Found file %s", member.name )
                    f=tar.extractfile(member)
                    count += self.read(f)
                    logger.debug( "Loaded %i events from %s in %s", count,  member.name, filename)
            elif filename.endswith('.txt.gz'):
                import gzip
                f = gzip.open(filename, 'rb')
                logger.debug( "Found file %s" % filename )
                count = self.read(f)
            else:
                raise ValueError( "Can't load file %s", filename )
            logger.debug( "Loaded %i events from %s", count, filename )
        logger.info( "Loaded in total %i events from %i files.", len(self.events), len(filenames) )


    def read(self, f):
        count=0
        for x in f.read().split('\n'):
            try:
                self.events.add( tuple([int(i) for i in x.split(":")]) )
                count+=1
            except:
               logger.debug( "Skipping line %s", x)
        return count

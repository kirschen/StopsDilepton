class vetoList:
    def __init__(self, filenames, verbose=False):
        self.events=set([])
        import os, sys
        self.verbose=verbose

        self.filenames=filenames if type(filenames)==type([]) else [filenames]
        for filename in self.filenames:
            assert os.path.exists(filename), "[vetoList] File %s not found."%(filename)
            if filename.endswith('.tar.gz'):
                import tarfile
                tar = tarfile.open(filename, 'r:gz')
                if self.verbose: print "[vetoList] Loaded %s"%filename
                count = 0
                for member in tar.getmembers():
                    if self.verbose: print "[vetoList] Found file %s"%member.name
                    f=tar.extractfile(member)
                    count += self.read(f)
                    if self.verbose: print "[vetoList] Loaded %i events from %s in %s"%(count, member.name, filename)
            elif filename.endswith('.txt.gz'):
                import gzip
                f = gzip.open(filename, 'rb')
                if self.verbose: print "[vetoList] Found file %s"%filename
                count = self.read(f)
            print "[vetoList] Loaded %i events from %s"%(count, filename)
        print "[vetoList] Loaded in total %i events from %i files."%(len(self.events), len(filenames))


    def read(self, f):
        count=0
        for x in f.read().split('\n'):
            try:
                self.events.add( tuple([int(i) for i in x.split(":")]) )
                count+=1
            except:
                if self.verbose: print "Skipping line %s in %s in %s"%(x, member.name, filename)
        return count

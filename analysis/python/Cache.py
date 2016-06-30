import pickle, os, time
class Cache:
    def __init__(self, filename=None, verbosity=0, overwrite=False):
        self.verbosity=verbosity
        self.cacheFileLoaded = False
        self.initCache(filename)

    def initCache(self, filename):
        self.filename=filename
        try:
            with open(filename, 'r') as f:
	      self._cache = pickle.load(f)
            if self.verbosity>=1: print "Loaded cache file %s"%filename
            self.cacheFileLoaded = True
        except:# (IOError, ValueError, EOFError):
            if self.verbosity>=2: print "File %s not found or corrupted. Starting new cache."%filename
            self._cache = {}

    # Try to reload to cache file in order to get updates from other jobs/threads
    def reload(self, attempt = 0):
        try:
            with open(self.filename, 'r') as f:
              temp = self._cache
	      self._cache = pickle.load(f)
              self._cache.update(temp)
        except:# (IOError, ValueError, EOFError):
            if self.verbosity>=2: print "Cache file %s could not be reloaded"%self.filename
            if attempt < 10:
	      time.sleep(20)
	      self.reload(attempt + 1)

    def contains (self, key):
        return key in self._cache

    def get(self, key):
        return self._cache[key]

    def add(self, key, val, save):
        self._cache[key] = val
        if save==True:
            if self.verbosity>=2: print "Storing new result %r to key %r"%(val, key)
            self.save()
        return self._cache[key]

    def save(self):
        self.reload()
        with open(self.filename, 'w') as f:
          pickle.dump(self._cache, f)
        if self.verbosity>=2: print "Written cache file %s"%self.filename

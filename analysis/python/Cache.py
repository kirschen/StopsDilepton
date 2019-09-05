import pickle, os, time
import errno

# Logging
import logging
logger = logging.getLogger(__name__)

from Analysis.Tools.MergingDirDB import MergingDirDB

class Cache:
    def __init__(self, filepath=None, verbosity=0, overwrite=False):
        self.verbosity=verbosity
        self.initCache(filepath)

    def initCache(self, filepath):
        self.filepath = filepath
        self.DB = MergingDirDB(filepath)

    def contains (self, key):
        return self.DB.contains(key)

    def get(self, key):
        return self.DB.get(key)

    def add(self, key, val, overwrite=True):
        return self.DB.add(key, val, overwrite)

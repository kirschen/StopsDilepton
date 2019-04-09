import time
import random

from StopsDilepton.tools.resultsDB import *
from Analysis.Tools.DirDB import DirDB

import StopsDilepton.tools.logger as logger
logger = logger.get_logger( "DEBUG", logFile = None)

#db = resultsDB("test_batch.sql", "mytable", ["names"])
db = DirDB("./test")

import time
start = time.time()
for i in range(1000):
    print i
    overwrite = False

#    if not db.contains({"names":i}):
#        db.add({"names":i}, float(i), overwrite=overwrite)
    if not db.contains(i):
        db.add(float(i)+0.1, float(i), overwrite=overwrite)

end = time.time()
print("time:", end - start)

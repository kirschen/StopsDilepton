import random

from StopsDilepton.tools.resultsDB import *

import StopsDilepton.tools.logger as logger
logger = logger.get_logger( "DEBUG", logFile = None)

res = resultsDB("test_batch.sql", "mytable", ["names"])

import time

for i in range(15000):
    print i
    overwrite = False
    #overwrite = random.randint(0,1)
    #print i, "Overwrite", overwrite
    if not res.contains({"names":i}):
        res.add({"names":i}, float(i), overwrite=overwrite)
    #if i%100==0:
    #    time.sleep(10.*random.random())


#!/usr/bin/env python

import subprocess
import os
import time
import sys

# Logging
import StopsDilepton.tools.logger as logger
logger  = logger.get_logger('INFO', logFile = None)

processes = set()
max_processes = 14

#command = "echo"
command = ""

input_file = sys.argv[1]

if os.path.exists(input_file):
    with open(input_file) as f:
        # Remove everything after #
        # jobs_ = [l.split('#')[0].rstrip() for l in f.readlines() ]
        jobs_ = [ l.rstrip() for l in f.readlines() ]
        # remove empty lines
        jobs_ = filter(lambda l:len(l)>0, jobs_) 
else:
    raise ValueError( "Could not find file %s", input_file )

jobs = []
for job in jobs_:
    # Implement '<job>#SPLITn'
    if job.count('#'):
        job, comment = job.split('#')[:2]
    else:
        comment = None
    #cmds = job.split() 
    #split = filter(lambda s:s.startswith("SPLIT"), cmds)
    args  = job.split() #filter(lambda s:not s.startswith("SPLIT"), cmds)
    if comment is not None and "SPLIT" in comment:
        try:
            n = int(comment.replace("SPLIT", ""))
        except ValueError:
            n = -1
    else:
        n = -1

    if n>0:
        logger.info( "Splitting into %i jobs: %r", n, " ".join( args ) )
        for i in range(n):
            jobs.append(args+["--nJobs",str(n),"--job",str(i)])
    else:
        jobs.append(args)

if len(sys.argv)>=2:
    extra_args = sys.argv[2:]
else:
    extra_args = []
for cmds in jobs:
    if command!="": cmds_ = [command] + cmds + extra_args
    else:           cmds_ = cmds + extra_args
    logger.info( "Processing: %s", " ".join(cmds_) )
    processes.add(subprocess.Popen( cmds_ ))
    if len(processes) >= max_processes:
        os.wait()
        processes.difference_update(
            [p for p in processes if p.poll() is not None])

#Check if all the child processes were closed
for p in processes:
    if p.poll() is None:
        p.wait()

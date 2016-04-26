#!/usr/bin/env python

import subprocess
import os
import time
import sys

processes = set()
max_processes = 10

#command = "echo"
command = ""

input_file = sys.argv[1]

if os.path.exists(input_file):
    with open(input_file) as f:
        # Remove everything after #
        jobs_ = [l.split('#')[0].rstrip() for l in f.readlines() ]
        # remove empty lines
        jobs_ = filter(lambda l:len(l)>0, jobs_) 
else:
    raise ValueError( "Could not find file %s", input_file )

jobs = []
for job in jobs_:
    cmds = job.split() 
    split = filter(lambda s:s.startswith("SPLIT"), cmds)
    args  = filter(lambda s:not s.startswith("SPLIT"), cmds)
    if len(split)>0:
        try:
            n = int(split[0].replace("SPLIT", ""))
        except ValueError:
            n = -1
    else:
        n = -1

    if n>0:
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
    print "Processing:", " ".join(cmds_)
    processes.add(subprocess.Popen( cmds_ ))
    if len(processes) >= max_processes:
        os.wait()
        processes.difference_update(
            [p for p in processes if p.poll() is not None])

#Check if all the child processes were closed
for p in processes:
    if p.poll() is None:
        p.wait()

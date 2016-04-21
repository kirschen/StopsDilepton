#!/usr/bin/env python

import subprocess
import os
import time
import sys

processes = set()
max_processes = 5

#command = "echo"
command = ""

input_file = sys.argv[1]

if os.path.exists(input_file):
    with open(input_file) as f:
        # Remove everything after #
        jobs = [l.split('#')[0].rstrip() for l in f.readlines() ]
        # remove empty lines
        jobs = filter(lambda l:len(l)>0, jobs) 
else:
    raise ValueError( "Could not find file %s", input_file )

if len(sys.argv):
    extra_args = sys.argv[2:]
else:
    extra_args = []

for job in jobs:
    cmds = job.split() + extra_args
    if command!="": cmds = [command] + cmds
    print "Processing:", " ".join(cmds)
    processes.add(subprocess.Popen( cmds ))
    if len(processes) >= max_processes:
        os.wait()
        processes.difference_update(
            [p for p in processes if p.poll() is not None])

#Check if all the child processes were closed
for p in processes:
    if p.poll() is None:
        p.wait()

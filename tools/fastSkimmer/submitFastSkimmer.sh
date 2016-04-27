#!/bin/bash 
qsub -q localgrid@cream02 -o log.txt -e log.txt runFastSkimmer.sh

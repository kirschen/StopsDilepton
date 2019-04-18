#!/bin/sh
echo ${@:2}
yes q|python test.py |sed "s/ *//g"|sed "s/^\*//g"| sed "s/[0-9]*\*\(.*\)/\1/g"|sed "s/\*$//g"|sed "s/\*/:/g" | grep "^[0-9]">& output_$1.txt

#!/usr/bin/env python
import os
import pickle

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")

argParser.add_argument('--input',   action='store', default=[],  nargs='*',  type = str, help="Input directories" )
argParser.add_argument('--output',  action='store', default=".", type = str, help="Output directory" )

args = argParser.parse_args()

filenames = sum( [ [ os.path.join( path, filename ) for filename in os.listdir( path )] for path in args.input], [])

output = {}
for filename in filenames:
    category = os.path.splitext(os.path.basename(filename))[0].split('_')[-1]
    if not output.has_key( category ): output[category] = []
    output[category].append( filename )

print "Loading %i files."%len( filenames )
results = {filename: pickle.load(file(filename)) for filename in filenames}
print "Loaded %i files."%len( filenames )

for category in output.keys():
    print "Total results for %s: %i" % (category, sum( [ len(results[f]) for f in output[category] ], 0 ))
    outfile = os.path.join( args.output, category+".pkl" )
    outdict =  dict(sum([ results[d].items() for d in output[category] ], []))
    pickle.dump( outdict, file( outfile, "w") )
    print "Written %i results to %s" % ( len(outdict.items()), outfile)

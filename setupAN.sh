svn co -N svn+ssh://svn.cern.ch/reps/tdr2 analysisNote
cd analysisNote
svn update utils
svn update -N notes
svn update notes/AN-15-266
eval `notes/tdr runtime -sh`
cd notes/AN-15-266/trunk
tdr --style=pas b AN-15-266

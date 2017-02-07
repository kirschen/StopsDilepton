svn co -N svn+ssh://svn.cern.ch/reps/tdr2 paper
cd paper
svn update utils
svn update -N papers
svn update papers/SUS-17-001
eval `papers/tdr runtime -sh`
cd papers/SUS-17-001/trunk
tdr --style=paper b SUS-17-001

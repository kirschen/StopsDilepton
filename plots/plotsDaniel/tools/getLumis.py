import os
import subprocess

datadir = '/afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v31/dilepTiny/'
data = os.listdir(datadir)

lumis = []

for d in data[:5]:
    print "Getting lumi for dataset %s"%d
    res = []
    cmd = 'brilcalc lumi -b "STABLE BEAMS" --normtag /afs/cern.ch/user/l/lumipro/public/Normtags/normtag_DATACERT.json -i %s/%s/%s.json'%(datadir,d,d)
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    while True:
        l = proc.stdout.readline()
        if l !=  '':
            res.append( l.rstrip() )
        else:
            break
    print "Lumi is %f"%float(res[-4].split('|')[-2])
    lumis.append({'dataset':d,'lumi':float(res[-4].split('|')[-2])})

subsets = ['DoubleEG','DoubleMuon','MuonEG']

print
print "Summary"
print "{:60}{:20}".format("Dataset","Lumi (1/fb)")
for subset in subsets:
  print
  tmp = 0
  for l in lumis:
      if subset in l['dataset']:
        print "{:60}{:20f}".format(l['dataset'],round(l['lumi']*1e-9,3))
        tmp += l['lumi']
  print "{:60}{:20f}".format(subset,round(tmp*1e-9,3))



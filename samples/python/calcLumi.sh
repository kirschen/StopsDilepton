export PATH=$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.0.3/bin:$PATH
for x in `ls /afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v2/dilepTiny/*/*.json`; do echo $x; brilcalc lumi -b "STABLE BEAMS" --normtag /afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json -i $x; done

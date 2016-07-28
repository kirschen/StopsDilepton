#for x in `ls /afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v2/dilep/*/*.json`; do echo $x; brilcalc lumi -b "STABLE BEAMS" -i $x -u /fb; done
#for x in `ls /afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v2/dilep/*/*.json`; do echo $x; brilcalc lumi -i $x -u /fb; done
for x in `ls /afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v12/dilepTiny/*/*.json`; do echo $x; brilcalc lumi -b "STABLE BEAMS" --normtag=/afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json -i $x -u /fb; done


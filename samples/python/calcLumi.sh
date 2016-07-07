#for x in `ls /afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v2/dilepTiny/*/*.json`; do echo $x; brilcalc lumi -b "STABLE BEAMS" -i $x -u /fb; done
#for x in `ls /afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v2/dilepTiny/*/*.json`; do echo $x; brilcalc lumi -i $x -u /fb; done
for x in `ls /afs/hephy.at/data/rschoefbeck02/cmgTuples/postProcessed_80X_v7/dilepTiny/*/*.json`; do echo $x; brilcalc lumi -i $x -u /fb; done

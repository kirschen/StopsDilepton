systematicPlotsDir=/afs/hephy.at/user/r/rschoefbeck/public/forTom/
for f in */*/*.pdf; do
   echo "Updating $f"
   cp $systematicPlotsDir/$f $f
done

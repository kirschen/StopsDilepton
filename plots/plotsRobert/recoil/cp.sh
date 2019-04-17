
targetdir=/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/$2/
mkdir -p ${targetdir}
for x in `ls $1/*/*/recoil_fitResults_SF.pkl`; do
    newfile=${x/\/lepSel/_lepSel};
    newfile=${newfile/\/recoil_fitResults/_recoil_fitResults}
    cp ${x} ${targetdir}/$(basename /${newfile})
done

#cp /afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/$1/2018/lepSel-btag0-relIso0.12-looseLeptonVeto-mll20-onZ/recoil_fitResults_SF.pkl /afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/$2/2018_recoil_fitResults_SF.pkl
#cp /afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/$1/2018_preHEM/lepSel-btag0-relIso0.12-looseLeptonVeto-mll20-onZ/recoil_fitResults_SF.pkl /afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/$2/2018_preHEM_recoil_fitResults_SF.pkl
#cp /afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/$1/2018_postHEM/lepSel-btag0-relIso0.12-looseLeptonVeto-mll20-onZ/recoil_fitResults_SF.pkl /afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/$2/2018_postHEM_recoil_fitResults_SF.pkl
#cp /afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/$1/2017/lepSel-btag0-relIso0.12-looseLeptonVeto-mll20-onZ/recoil_fitResults_SF.pkl /afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/$2/2017_recoil_fitResults_SF.pkl
#cp /afs/hephy.at/user/r/rschoefbeck/www/StopsDilepton/$1/2016/lepSel-btag0-relIso0.12-looseLeptonVeto-mll20-onZ/recoil_fitResults_SF.pkl /afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/$2/2016_recoil_fitResults_SF.pkl

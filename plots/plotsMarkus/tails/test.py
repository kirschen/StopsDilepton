import ROOT
c = ROOT.TChain("Events")
c.Add("/afs/hephy.at/data/rschoefbeck01/TTXPheno/skims/gen/RunII_v01/fwlite_tt_full_LO_order2_15weights/fwlite_tt_full_LO_order2_15weights_18.root")
c.SetScanField(1000)
c.Scan("run:lumi:evt")

#yes q|python test.py|sed "s/ *//g"|sed "s/^\*//g"| sed "s/[0-9]*\*\(.*\)/\1/g"|sed "s/\*$//g"|sed "s/\*/:/g" | grep "^[0-9]">& output.txt

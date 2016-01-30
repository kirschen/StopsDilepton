#Interfaces are much too specialized to work generally
def latexmaker_1(channel,plots,mt2cut):

    for cut in mt2cut:

        mt2ll = plots[channel]['mt2llwithcut'+cut]

        output = open("./tables/table_"+channel+"_mt2cutat"+cut+".tex","w")

        output.write("\\documentclass[8pt]{article}" + '\n')
        output.write("\\usepackage[margin=0.5in]{geometry}" + '\n')
        output.write("\\usepackage{verbatim}" + '\n')
        output.write("\\usepackage{hyperref}" + '\n')
        output.write("\\usepackage{epsfig}" + '\n')
        output.write("\\usepackage{graphicx}" + '\n')
        output.write("\\usepackage{epsfig}" + '\n')
        output.write("\\usepackage{subfigure,              rotating,              rotate}" + '\n')
        output.write("\\usepackage{relsize}" + '\n')
        output.write("\\usepackage{fancyheadings}" + '\n')
        output.write("\usepackage{multirow}" + '\n')
        output.write("\\usepackage[latin1]{inputenc}" + '\n')
        output.write("\\usepackage{footnpag}" + '\n')
        output.write("\\usepackage{enumerate}" + '\n')
        output.write("\\usepackage{color}" + '\n')
        output.write("\\newcommand{\\doglobally}[1]{{\\globaldefs=1#1}}" + '\n')
        output.write("\\begin{document}" + '\n')


        output.write("\\begin{tabular}{|c|c|c|c|c|c|}" + '\n')
        output.write("\\hline" + '\n')
        output.write("$M_{T2}$ cut at " + str(cut)  + " (GeV) & Count \\\\"+ '\n')
        output.write("\\hline" + '\n')
        output.write("\\hline" + '\n')

        sortedhist = sorted(mt2ll['histo'].items(),key=lambda l:l[1].Integral()) #set histogram with highest value first
        for item in sortedhist:
            samplename = item[0].replace("_","\_")
            output.write(samplename + " & " + str(round(item[1].Integral(),2)) + "\\\\" + '\n')
        output.write("\\hline" + '\n')
        output.write("\\hline" + '\n')

        output.write("\\end{tabular}" + '\n')

        output.write("\\end{document}")

        output.close()

def latexmaker_2(piechart,mt2llcut,channel):

    mt2ll = piechart[str(mt2llcut)][channel]["(>=2,>=1)"]

    output = open("./tables/table_"+channel+"_mt2ll"+str(mt2llcut)+".tex","w")

    output.write("\\documentclass[8pt]{article}" + '\n')
    output.write("\\usepackage[margin=0.5in]{geometry}" + '\n')
    output.write("\\usepackage{verbatim}" + '\n')
    output.write("\\usepackage{hyperref}" + '\n')
    output.write("\\usepackage{epsfig}" + '\n')
    output.write("\\usepackage{graphicx}" + '\n')
    output.write("\\usepackage{epsfig}" + '\n')
    output.write("\\usepackage{subfigure,              rotating,              rotate}" + '\n')
    output.write("\\usepackage{relsize}" + '\n')
    output.write("\\usepackage{fancyheadings}" + '\n')
    output.write("\usepackage{multirow}" + '\n')
    output.write("\\usepackage[latin1]{inputenc}" + '\n')
    output.write("\\usepackage{footnpag}" + '\n')
    output.write("\\usepackage{enumerate}" + '\n')
    output.write("\\usepackage{color}" + '\n')
    output.write("\\newcommand{\\doglobally}[1]{{\\globaldefs=1#1}}" + '\n')
    output.write("\\begin{document}" + '\n')


    output.write("\\begin{tabular}{|c|c|c|c|c|c|}" + '\n')
    output.write("\\hline" + '\n')
    output.write("$M_{T2}$ cut at " + str(mt2llcut)  + " (GeV) \\textcolor{red}{\\textbf{" +channel+ "}} & Count \\\\"+ '\n')
    output.write("\\hline" + '\n')
    output.write("\\hline" + '\n')

    #sortedhist = sorted(mt2ll.items(),key=lambda l:l[1])
    sortedhist = mt2ll.items()
    for item in sortedhist:
        samplename = item[0].replace("_","\_")
        output.write(samplename + " & " + str(round(item[1],2)) + "\\\\" + '\n')
    output.write("\\hline" + '\n')
    output.write("\\hline" + '\n')

    output.write("\\end{tabular}" + '\n')

    output.write("\\end{document}")

    output.close()
def piemaker(mt2cut,piechart):

    ROOT.gStyle.SetOptStat(0)
    canvas = ROOT.TCanvas('canvas','canvas',700,572)
    canvas.SetLeftMargin(0.2)
    ROOT.gStyle.SetPadLeftMargin(0.2)
    canvas.SetRightMargin(0.3)
    canvas.SetBottomMargin(0.3)
    height=1-ROOT.gStyle.GetPadBottomMargin()-ROOT.gStyle.GetPadTopMargin()
    width =1-ROOT.gStyle.GetPadLeftMargin()-ROOT.gStyle.GetPadRightMargin()
    canvas.cd()
    pies = []
    pads = []
    canvas.Divide(5,1)
    for ipiece, piece in enumerate(piechart["SF"].keys()):
        x0 = ROOT.gStyle.GetPadLeftMargin() + (0.01+ipiece)*width/float(len(piechart["SF"]))
        x1 = ROOT.gStyle.GetPadLeftMargin() + (0.99+ipiece)*width/float(len(piechart["SF"]))
        y0 = ROOT.gStyle.GetPadBottomMargin() + (0.01+1.)*height/float(2)
        y1 = ROOT.gStyle.GetPadBottomMargin() + (0.99+1.)*height/float(2)

        cols = array('i', [1])

        pielist = [piechart["SF"][piece][i] for i in piechart["SF"][piece]]
        pielist = array('f',pielist)
        temp = ROOT.TPie('pie_'+piece,'',len(pielist),pielist,cols)
        pies.append(temp)

    for ipiece, piece in enumerate(piechart["SF"].keys()):
        canvas.cd(ipiece+1)
        pies[ipiece].Draw("nol")

    canvas.SaveAs("Pie_SF_forMT2llcutat.png")
    #canvas.Close()



# Calculate correlation matrix


import pickle
from StopsDilepton.samples.cmgTuples_FullSimTTbarDM_mAODv2_25ns_postProcessed import *
from StopsDilepton.tools.user import combineReleaseLocation, analysis_results, plot_directory

categories = []
mChi_list = []
mPhi_list = []

for s in DMsamples:
    if not s[0] in mChi_list: mChi_list.append(s[0])
    if not s[1] in mPhi_list: mPhi_list.append(s[1])
    if not s[2] in categories: categories.append(s[2])

res = pickle.load(file(os.path.join(analysis_results,"fitAll","cardFiles","TTbarDM","calculatedLimits.pkl")))


texdir = os.path.join(plot_directory,'DMLimits')
if not os.path.exists(texdir): os.makedirs(texdir)
ofile = texdir+'/limits_update.tex'

with open(ofile, "w") as f:
    f.write("\\documentclass[a4paper,10pt,oneside]{article} \n \\usepackage{caption} \n \\usepackage{rotating} \n \\begin{document} \n")
    
    for cat in categories:
        if cat=='S': catname = "scalar"
        elif cat=='PS': catname = "pseudoscalar"
        else: catname = "unknown"

        f.write("\n \\begin{table} \n\\resizebox{\\textwidth}{!}{ \\begin{tabular}{c||" + "c"*len(mPhi_list) + "} \n")
        f.write(" & \\multicolumn{"+str(len(mPhi_list))+"}{c}{$m_{\\Phi}$ (GeV)} \\\\ \n \n")

        fbase = "{:30}"+"{:10}"*len(mPhi_list)
        line = ["$m_{\\chi}$ (GeV) "]
        line += ["& "+str(x) for x in sorted(mPhi_list)]
        f.write(fbase.format(*line) + "\\\\ \\hline \\hline \n\n")

        for i,mChi in enumerate(sorted(mChi_list)):
          line = [str(mChi)] #+ "& "
          for mPhi in sorted(mPhi_list):
              obs = None
              try:
                  l = res[(mChi,mPhi,cat)]
              except KeyError:
                  l = None
              if l:
                  try:
                      obs = l['-1.000']
                  except KeyError:
                      obs = None
              if obs:
                  if obs<1000: line.append("& " + str(round(obs,1)))
                  else: line.append("& $\\gg 1$ ")
              else: line.append("& ")
          f.write(fbase.format(*line)+"\\\\ \n") # \n \\hline

        f.write(" \n \\end{tabular}}")
        f.write(" \\caption{Observed limits for %s mediator} \n "%catname)
        f.write(" \\end{table} \n")

    f.write(" \\end{document}")

os.system("cd "+texdir+";pdflatex "+ofile)




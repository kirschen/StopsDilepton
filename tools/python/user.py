import os
if os.environ['USER'] in ['schoef', 'rschoefbeck', 'schoefbeck']:
    # Where you store the data
    data_directory      = "/afs/hephy.at/data/rschoefbeck01/cmgTuples/postProcessed_mAODv2/dilepTiny"
    # Where postprocessed data goes 
    data_output_directory      = "/afs/hephy.at/data/rschoefbeck01/cmgTuples/"
    # Where the plots go
    plot_directory      = "/afs/hephy.at/user/r/rschoefbeck/www/"
    # Analysis result files
    analysis_results    = '/afs/hephy.at/data/rschoefbeck01/StopsDilepton/results/test' #Path to analysis results
    # directory with veto lists
    veto_lists = "/afs/hephy.at/data/rschoefbeck01/StopsDilepton/vetoLists/"
    # 715 release for limit calculation 
    releaseLocation71XC = '/afs/hephy.at/work/r/rschoefbeck/CMS/tmp/CMSSW_7_1_5/src'

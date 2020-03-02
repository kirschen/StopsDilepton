#python controlRegionPlot.py --year 2016     --region controlDYVV 
#python controlRegionPlot.py --year 2017     --region controlDYVV 
#python controlRegionPlot.py --year 2018     --region controlDYVV 
#python controlRegionPlot.py --year 2016     --region controlDYVV --combine
#python controlRegionPlot.py --year 2016     --region controlDYVV --postFit
#python controlRegionPlot.py --year 2017     --region controlDYVV --postFit
#python controlRegionPlot.py --year 2018     --region controlDYVV --postFit
#python controlRegionPlot.py --year 2016     --region controlDYVV --postFit --combine
#
#python controlRegionPlot.py --year 2016     --region controlTTZ 
#python controlRegionPlot.py --year 2017     --region controlTTZ 
#python controlRegionPlot.py --year 2018     --region controlTTZ 
#python controlRegionPlot.py --year 2016     --region controlTTZ --combine
#python controlRegionPlot.py --year 2016     --region controlTTZ --postFit
#python controlRegionPlot.py --year 2017     --region controlTTZ --postFit
#python controlRegionPlot.py --year 2018     --region controlTTZ --postFit
#python controlRegionPlot.py --year 2016     --region controlTTZ --postFit --combine
#
#python controlRegionPlot.py --year 2016     --region controlTT 
#python controlRegionPlot.py --year 2017     --region controlTT 
#python controlRegionPlot.py --year 2018     --region controlTT 
#python controlRegionPlot.py --year 2016     --region controlTT --combine
#python controlRegionPlot.py --year 2016     --region controlTT --postFit
#python controlRegionPlot.py --year 2017     --region controlTT --postFit
#python controlRegionPlot.py --year 2018     --region controlTT --postFit
#python controlRegionPlot.py --year 2016     --region controlTT --postFit --combine

#python controlRegionPlot.py --year 2016     --region controlAll 
#python controlRegionPlot.py --year 2017     --region controlAll 
#python controlRegionPlot.py --year 2018     --region controlAll 
#python controlRegionPlot.py --year 2016     --region controlAll --combine
#python controlRegionPlot.py --year 2016     --region controlAll --postFit
#python controlRegionPlot.py --year 2017     --region controlAll --postFit
#python controlRegionPlot.py --year 2018     --region controlAll --postFit
#python controlRegionPlot.py --year 2016     --region controlAll --postFit --combine


python signalRegionPlot_combine_split.py --combine --region fitAll --year 2016
python signalRegionPlot_combine_split.py --combine --region fitAll --year 2017
python signalRegionPlot_combine_split.py --combine --region fitAll --year 2018
python signalRegionPlot_combine_split.py --combine --region fitAll --postFit --year 2016
python signalRegionPlot_combine_split.py --combine --region fitAll --postFit --year 2017
python signalRegionPlot_combine_split.py --combine --region fitAll --postFit --year 2018


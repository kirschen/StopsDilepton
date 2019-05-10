# Get estimates

Example command:
```
python run_estimates.py --selectEstimator TTJets --year 2018 --logLevel DEBUG
```
This will get you all the estimates for TTJets (which can take some time).
You need to run over `TTJets, DY, TTZ, other, multiBoson, Data` to be prepared.
Options that might be needed are to only run over the DYVV control region, in order to do so add the `--control DYVV` option.
Only one region can be selected by using `--selectRegion 1`.
For a quick check of the central values (omitting systematic uncertainties), use `--noSystematics`.
If you want to submit jobs to the batch system you should also set `--nThreads 1` to not kill the batch system.

# Run limits
Example command:
```
python run_limit.py --year 2018 --only T2tt_800_0 --expected
```
To only run over the DYVV CR use the `--controlDYVV`.
If you decide to just run in the CR you can also remove the `--expected` option.
Using `--fitAll` will run the fit in signal and control regions.
Be very careful to use `--expected` in this case.

# Plot limits
Run `run_limit.py` without the only option to get the limits on all points.
You should get a root file with the 2D histogram in the result directory.
The `plot_SMS_limit.py` script in the plot directory should make a nice plot out of it (not tested with new setup yet).

----------------------
Old MVA explaination below (outdated!)
----------------------

For MVA studies we only use MC, no Data (at least for now).

Samples for SM backgrounds are defined in
`StopsDilepton.samples.nanoTuples_Summer16_postProcessed`
Signal samples (so far only T2tt) are in
`StopsDilepton.samples.nanoTuples_FastSim_Spring16_postProcessed`

# Getting estimates
First, get estimates using the following command:
```
python run_estimate.py --selectEstimator TTJets --MVAselection MVA_T2tt_default --MVAcut 0.5
```
This fills caches with several jobs in parallel, so don't run more than one of those jobs on one machine at a time. We use `TTJets`, `DY`, `TTZ`, `multiBoson` and `other`. Four MVA classifiers are implemented so far, the interesting ones as a start are: `MVA_T2tt_default`, `MVA_T2tt_lep_pt`.
The MVAcut flag defines the lower cut on this classifier.

If you run over a lot of points you can also write a script that submits to the batch system.
In that case, use no multithreading (`--noMultiThreading`) and submit one job per signal region (0-13) with `--selectRegion`.
```
python run_estimate.py --selectEstimator DY --MVAselection MVA_T2tt_default --MVAcut 0.5 --selectRegion 0 --noMultiThreading
```
Right now, we use regions 0-25.

# Running limits
To run limits (and at the same time get estimates for the signal point) for e.g. the T2tt mStop=800, mNeutralino=0 point use:
```
python run_limit.py --signal T2tt --only T2tt_800_0 --expected --MVAselection MVA_T2tt_default --MVAcut 0.5
```
You need to have set-up the right release for running the combine tool (see recipe README) and also correctly set the path in
`StopsDilepton.tools.user`.
Calculated limits are stored in a pickle file in your results directory.

Happy running!

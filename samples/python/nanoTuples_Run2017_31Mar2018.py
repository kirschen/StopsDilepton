import copy, os, sys
from RootTools.core.Sample import Sample
import ROOT


## these should go somewhere else
dbFile = '/afs/hephy.at/data/dspitzbart01/nanoAOD/DB_Run2017.sql'

# specify a local directory if you want to create (and afterwards automatically use) a local copy of the sample, otherwise use the grid.

## DoubleMuon
DoubleMuon_Run2017B_31Mar2018  = Sample.nanoAODfromDAS('DoubleMuon_Run2017B_31Mar2018',   '/DoubleMuon/Run2017B-31Mar2018-v1/NANOAOD', dbFile=dbFile)
DoubleMuon_Run2017C_31Mar2018  = Sample.nanoAODfromDAS('DoubleMuon_Run2017C_31Mar2018',   '/DoubleMuon/Run2017C-31Mar2018-v1/NANOAOD', dbFile=dbFile)
DoubleMuon_Run2017D_31Mar2018  = Sample.nanoAODfromDAS('DoubleMuon_Run2017D_31Mar2018',   '/DoubleMuon/Run2017D-31Mar2018-v1/NANOAOD', dbFile=dbFile)
DoubleMuon_Run2017E_31Mar2018  = Sample.nanoAODfromDAS('DoubleMuon_Run2017E_31Mar2018',   '/DoubleMuon/Run2017E-31Mar2018-v1/NANOAOD', dbFile=dbFile)
DoubleMuon_Run2017F_31Mar2018  = Sample.nanoAODfromDAS('DoubleMuon_Run2017F_31Mar2018',   '/DoubleMuon/Run2017F-31Mar2018-v1/NANOAOD', dbFile=dbFile)

DoubleMuon_Run2017 = [\
    DoubleMuon_Run2017B_31Mar2018,
    DoubleMuon_Run2017C_31Mar2018,
    DoubleMuon_Run2017D_31Mar2018,
    DoubleMuon_Run2017E_31Mar2018,
    DoubleMuon_Run2017F_31Mar2018,
    ]

## MuonEG
MuonEG_Run2017B_31Mar2018  = Sample.nanoAODfromDAS('MuonEG_Run2017B_31Mar2018',   '/MuonEG/Run2017B-31Mar2018-v1/NANOAOD', dbFile=dbFile)
MuonEG_Run2017C_31Mar2018  = Sample.nanoAODfromDAS('MuonEG_Run2017C_31Mar2018',   '/MuonEG/Run2017C-31Mar2018-v1/NANOAOD', dbFile=dbFile)
MuonEG_Run2017D_31Mar2018  = Sample.nanoAODfromDAS('MuonEG_Run2017D_31Mar2018',   '/MuonEG/Run2017D-31Mar2018-v1/NANOAOD', dbFile=dbFile)
MuonEG_Run2017E_31Mar2018  = Sample.nanoAODfromDAS('MuonEG_Run2017E_31Mar2018',   '/MuonEG/Run2017E-31Mar2018-v1/NANOAOD', dbFile=dbFile)
MuonEG_Run2017F_31Mar2018  = Sample.nanoAODfromDAS('MuonEG_Run2017F_31Mar2018',   '/MuonEG/Run2017F-31Mar2018-v1/NANOAOD', dbFile=dbFile)

MuonEG_Run2017 = [\
    MuonEG_Run2017B_31Mar2018,
    MuonEG_Run2017C_31Mar2018,
    MuonEG_Run2017D_31Mar2018,
    MuonEG_Run2017E_31Mar2018,
    MuonEG_Run2017F_31Mar2018,
    ]

## DoubleEG
DoubleEG_Run2017B_31Mar2018  = Sample.nanoAODfromDAS('DoubleEG_Run2017B_31Mar2018',   '/DoubleEG/Run2017B-31Mar2018-v1/NANOAOD', dbFile=dbFile)
DoubleEG_Run2017C_31Mar2018  = Sample.nanoAODfromDAS('DoubleEG_Run2017C_31Mar2018',   '/DoubleEG/Run2017C-31Mar2018-v1/NANOAOD', dbFile=dbFile)
DoubleEG_Run2017D_31Mar2018  = Sample.nanoAODfromDAS('DoubleEG_Run2017D_31Mar2018',   '/DoubleEG/Run2017D-31Mar2018-v1/NANOAOD', dbFile=dbFile)
DoubleEG_Run2017E_31Mar2018  = Sample.nanoAODfromDAS('DoubleEG_Run2017E_31Mar2018',   '/DoubleEG/Run2017E-31Mar2018-v1/NANOAOD', dbFile=dbFile)
DoubleEG_Run2017F_31Mar2018  = Sample.nanoAODfromDAS('DoubleEG_Run2017F_31Mar2018',   '/DoubleEG/Run2017F-31Mar2018-v1/NANOAOD', dbFile=dbFile)

DoubleEG_Run2017 = [\
    DoubleEG_Run2017B_31Mar2018,
    DoubleEG_Run2017C_31Mar2018,
    DoubleEG_Run2017D_31Mar2018,
    DoubleEG_Run2017E_31Mar2018,
    DoubleEG_Run2017F_31Mar2018,
    ]
    
allSamples = DoubleMuon_Run2017 + MuonEG_Run2017 + DoubleEG_Run2017

for s in allSamples:
    s.isData = True


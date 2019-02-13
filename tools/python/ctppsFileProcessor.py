'''ctppsFileProcessor: process miniAOD data and write ctpps proton track flat ntuple
'''

# Standard imports
import os
import subprocess
import uuid
import ROOT
from math import sqrt, sin, cos

# RootTools 
from RootTools.core.standard import *

# Logging
import logging
logger = logging.getLogger(__name__)

class ctppsFileProcessor:

    def __init__( self, infiles, outfile, year, isMC = False, overwrite = False, maxEvents = -1):
        
        if type(infiles)==type(""): infiles = [infiles ]

        logger.info( "Running on files: %s" % ( ",".join( infiles ) ) )

        if not year == 2017:
            raise NotImplementedError

        if not ( os.path.exists( outfile ) and helpers.checkRootFile( outfile) ) or overwrite:

            # Write EDM file
            #tmpfile = "/tmp/b3068f86-3202-4aa7-9f3b-fc72c7d8112c.root"
            tmpfile = "/tmp/"+str(uuid.uuid4())+'.root'
            extra_args = ["maxEvents="+str(maxEvents)] if maxEvents>0 else []
            cfg = "data_ctpps_reco.py" if not isMC else "mc_ctpps_reco.py"

            args = ["cmsRun", os.path.expandvars( "$CMSSW_BASE/src/RecoCTPPS/ProtonReconstruction/test/%i/%s"%( year, cfg ) ), "inputFiles="+",".join( infiles ), "outfile=file:"+tmpfile ] + extra_args

            logger.info( "Calling: %s", " ".join(args) )
            subprocess.check_output(args)
            logger.info( "Done with CTPPS reco. Written edm file %s", tmpfile ) 

            logger.info( "Write flat ntuple now to %s", outfile ) 

            ctpps_edm  = FWLiteSample.fromFiles("ctpps", files = [ tmpfile ] ) 
            reader = ctpps_edm.fwliteReader( 
                products = { 'ptracks':{'type':'vector<reco::ProtonTrack>', 'label': ( "ctppsProtonReconstructionOFDB" ) } }
            )

            proton_variables = [ "evt/l", "run/I", "lumi/I", "proton[xi/F,thx/F,thy/F,t/F,ismultirp/I,rpId/I]" ]

            # Maker
            tmp_dir     = ROOT.gDirectory
            output_file = ROOT.TFile( outfile, 'recreate')
            output_file.cd()
            maker =    TreeMaker( sequence = [], variables = map( TreeVariable.fromString, proton_variables ), treeName = "Events")
            tmp_dir.cd()

            reader.start()
            maker.start()

            counter_read = -1
            while reader.run():
                counter_read += 1
                if counter_read%100==0: logger.info("Reading event %i.", counter_read)

                maker.event.run, maker.event.lumi, maker.event.evt = reader.evt

                reco_protons = []
                for proton in reader.products['ptracks']:

                    if not proton.valid(): continue

                    th_y = (proton.direction().y()) / (proton.direction().mag())
                    th_x = (proton.direction().x()) / (proton.direction().mag())
                    xi = proton.xi()

                    # t
                    m = 0.938 # GeV # proton mass
                    p = 6500. # GeV # beam energy

                    t0 = 2.*m*m + 2.*p*p*(1.-xi) - 2.*sqrt( (m*m + p*p) * (m*m + p*p*(1.-xi)*(1.-xi)) )
                    th = sqrt(th_x * th_x + th_y * th_y)
                    S = sin(th/2.)
                    t = t0 - 4. * p*p * (1.-xi) * S*S

                    if proton.method == ROOT.reco.ProtonTrack.rmSingleRP:
                        rpId = ROOT.CTPPSDetId( int(proton.contributingRPIds.begin()) )
                        decRPId = rpId.arm()*100 + rpId.station()*10 + rpId.rp()
                        ismultirp = 0
                    elif proton.method == ROOT.reco.ProtonTrack.rmMultiRP:
                        rpId = ROOT.CTPPSDetId( int(proton.contributingRPIds.begin()) )
                        armId = rpId.arm()
                        ismultirp = 1
                    else:
                        ismultirp = -1

                    reco_protons.append( {
                        'xi' :proton.xi(),
                        'thx':th_x,
                        'thy':th_y,
                        't':t,
                        'ismultirp':ismultirp,
                        'rpId': armId if ismultirp==1 else decRPId 
                        })

                maker.event.nproton = len( reco_protons )
                #print maker.event.nproton, maker.event.proton_xi, maker.event.proton_xi[3]
                for i_proton, proton in enumerate( reco_protons ):
                    maker.event.proton_xi[i_proton]        = proton['xi']
                    maker.event.proton_thx[i_proton]       = proton['thx']
                    maker.event.proton_thy[i_proton]       = proton['thy']
                    maker.event.proton_t[i_proton]         = proton['t']
                    maker.event.proton_ismultirp[i_proton] = int(proton['ismultirp'])
                    maker.event.proton_rpId[i_proton]      = int(proton['rpId'])

                maker.run()

            output_file.cd()
            maker.tree.Write()
            output_file.Close()

            logger.info( "Written file %s", outfile)
            #os.remove( tmpfile )
            logger.info( "Deleted %s", tmpfile)
        else: 
            logger.info( "Found %s. Skip.", outfile ) 
            
if __name__ == "__main__":
    import StopsDilepton.tools.logger as logger
    import RootTools.core.logger as logger_rt
    logger    = logger.get_logger(   'INFO', logFile = None)
    logger_rt = logger_rt.get_logger('INFO', logFile = None)

    ctppsFileProcessor( 
        'root://cms-xrd-global.cern.ch//store/data/Run2017H/FSQJet1/MINIAOD/17Nov2017-v1/70000/E0A4F930-6E4D-E811-8EB8-90E2BACBAA90.root', 
        outfile = 'ctpps.root',
        year = 2017,
        isMC = False,
        overwrite = True,
        maxEvents = 10
     )
 

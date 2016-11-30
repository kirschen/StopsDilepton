# Standard imports
import subprocess
import os, re
import shutil
import commands

# Logging
import logging
logger = logging.getLogger(__name__)

def is_nonemptydir( line ):
    '''Checks whether a line of output from dpns-ls corresponds to an non-empty directory
    '''
    try:
        lsplit = line.split()
        return lsplit[4]=='0' and int(lsplit[1])>0
    except:
        pass
    return False

def is_nonemptyfile( line ):
    '''Checks whether a line of output from dpns-ls corresponds to an non-empty file
    '''
    try:
        lsplit = line.split()
        return int(lsplit[4])>0 and int(lsplit[1])==1
    except:
        pass
    return False


def is_cmgdirectory( res ):
    ''' Returns true if the directory looks like a cmg directory
    '''
    treeFiles = len(filter(lambda f:f['is_treefile'], res))
    logFiles = len(filter(lambda f:f['is_logfile'], res))
    isCMG = treeFiles>0 and logFiles>0
    if isCMG:
        logger.debug("Found %i tree files and %i log files -> This is a cmg directory.", treeFiles, logFiles)

    return isCMG

def get_job_number(f):
    s=f['path'].split('/')[-1]
    ints = map(int, re.findall(r'\d+', s))
    assert len(ints)>0, 'Couldn\'nt find number in %s'%f['path']
    assert len(ints)<=1, 'Found more than one number in  %s'%f['path']
    return ints[0]

def read_normalization( filename, skimReport_file = 'SkimReport.txt'):
    string = commands.getoutput('/usr/bin/rfcat %s | tar xzOf - Output/%s' % (filename, skimReport_file) )

    sumW = None
    allEvents = None

    for line in string.split('\n'):
      if "Sum Weights" in line: sumW = float(line.split()[2])
      if 'All Events'  in line: allEvents = float(line.split()[2])

    if sumW is not None: 
        logger.debug( "Read 'Sum Weights' normalization %3.2f from file %s.", sumW, filename )  
        return sumW
    else:                
        logger.debug( "Read 'All Events' normalization %3.2f from file %s.", allEvents, filename )  
        return allEvents

class walk_dpm:

    def __init__( self, path ):
        self.cp_cmd = "/usr/bin/rfcp"
        # self.pretend = False
        self.path = path
        self.tree_filename_prefix = "tree_"
        self.log_filename_prefix  = "output.log_"

    def abs_path( self, rel_path ):
        return os.path.join( self.path, rel_path ).replace('/./', '/')


    def is_treefilename( self, filename ):
        return filename.endswith('.root') and filename.split('/')[-1].startswith( self.tree_filename_prefix )

    def is_logfilename( self, filename ):
        return filename.endswith('.tgz') and filename.split('/')[-1].startswith( self.log_filename_prefix )

    def ls( self, rel_path ):
        ''' Perform ls of the relative dp path
        '''
        abs_path = self.abs_path( rel_path )
        p = subprocess.Popen(["dpns-ls -l %s" % abs_path], shell = True , stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        res=[]
        for line in p.stdout.readlines():
                line = line[:-1]
                filename = line.split()[-1] # The filename is the last string of the output of dpns-ls
                if is_nonemptydir( line ):
                    res.append( { 'is_dir':True, 'is_file':False, 'path':rel_path+'/'+filename, 'is_logfile':False, 'is_treefile':False } )
                elif is_nonemptyfile( line ):
                    res.append( { 'is_dir':False, 'is_file':True, 'path':rel_path+'/'+filename,\
                        'is_logfile':self.is_logfilename( filename ), 
                        'is_treefile':self.is_treefilename( filename ) } 
                    )
                else:
                    logger.debug( "Skipping line:\n%s", line )
        return res

    def cmg_directory_content( self, rel_path, maxN = -1):
        everything = self.ls( rel_path )

        tree_files = {get_job_number(f): f for f in everything if f['is_treefile']}
        log_files  = {get_job_number(f): f for f in everything if f['is_logfile']}

        result = []

        pairs = [n for n in tree_files.keys() if n in log_files.keys()]
        logger.info( "Now loading %i from %i files from directory %s", min( [ maxN, len(pairs)]) if maxN>0 else len(pairs), len(pairs), self.abs_path( rel_path ) ) 
        for jobID in pairs:
            normalization = read_normalization( self.abs_path( log_files[jobID]['path'] ) )
            if normalization is not None:
                result.append( (jobID, self.abs_path(tree_files[jobID]['path']), normalization ) )

            if maxN > 0 and len(result)>=maxN:
                break
         
        return result 

    def walk_dpm_cmgdirectories( self, rel_path = '.', result = {}, maxN = -1, path_substrings = []):
        ''' Recursively looks for directories that look like cmg directories
        '''
        res = self.ls( rel_path )
        if is_cmgdirectory( res ):
            logger.debug( "Found CMG dir: %s", rel_path )
            abs_path = self.abs_path(rel_path)
            # If we're not interested, return
            for substr in path_substrings:
                if not substr in abs_path:
                    logger.debug( "Couldn't find %s in %s. Skip.", substr, abs_path )
                    return result
            # Otherwise update
            result[ self.abs_path(rel_path) ] = self.cmg_directory_content( rel_path, maxN = maxN)
            return result
        else:
            dirs = filter( lambda f:f['is_dir'], res )
            if len(dirs)>0:
                for f in dirs:
                    logger.debug( "Stepping into %s", f['path'] )
                    result.update( self.walk_dpm_cmgdirectories( f['path'], result = result, maxN = maxN, path_substrings = path_substrings) )

            else:
                logger.debug( "Nothing found in %s", rel_path )
        return result


    @staticmethod
    def combine_cmg_directories( cmg_directories ):
        import operator
        total = sum(cmg_directories.values(),[])
        all_jobIDs = set( map(operator.itemgetter(0), total ) )
        all_jobIDs_withNorm = set( map(operator.itemgetter(0,2), total ) )
        for jobID in all_jobIDs:
            if len(filter( lambda w:w[0]==jobID, all_jobIDs_withNorm ))>1:
                raise RuntimeError( "Found multiple instances of job %i with different normalizations!" % jobID )
        files = [] 
        normalization = 0.
        for jobID in all_jobIDs:
            jobID_, file_, normalization_ = next(tup for tup in total if tup[0]==jobID)
            normalization += normalization_
            files.append( file_ )

        return normalization, files

if __name__ == "__main__":
    import StopsDilepton.tools.logger as logger
    logger = logger.get_logger('DEBUG')

    walker = walk_dpm('/dpm/oeaw.ac.at/home/cms/store/user/schoef/cmgTuples/80X_2/JetHT')
    cmg_directories = walker.walk_dpm_cmgdirectories('.', maxN = 1,  path_substrings = [ 'Run2016B' ] )

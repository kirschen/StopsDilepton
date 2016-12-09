#!/usr/bin/env python
"""
Usage:
submitBatch.py path/to/file_with_commands
or
submitBatch.py "command"

Will submit a batch job for each command line in the file_with_commands.
--dpm: Will create proxy certificate.
"""

from optparse import OptionParser
import hashlib, time
import os

parser = OptionParser()

slurm_job_file="slurm_job"
#slurm_job_title="BATCHSUBMIT"
#slurm_output_dir="/afs/hephy.at/work/%s/%s/slurm_output/"%(hephy_user_initial, hephy_user)

hephy_user = os.getenv("USER")
hephy_user_initial = os.getenv("USER")[0]

parser.add_option("--title", dest="title",
                  help="Job Title viewied in squeue", default = "BATCHSUBMIT" )
parser.add_option("--output", dest="output", 
                  default="/afs/hephy.at/work/%s/%s/slurm_output/"%(hephy_user_initial, hephy_user),
                  help="path for slurm output ")

parser.add_option('--dpm', dest="dpm", default=False, action='store_true', help="Use dpm?")

(options,args) = parser.parse_args()

slurm_job_title  = options.title
slurm_output_dir = options.output

if not os.path.isdir(slurm_output_dir):
    os.mkdir(slurm_output_dir)


def make_slurm_job( slurm_job_file, slurm_job_title, slurm_output_dir , command ):

    # If X509_USER_PROXY is set, use existing proxy.
    if options.dpm:
        from StopsDilepton.tools.helpers import renew_proxy
        proxy = renew_proxy()

        print "Using proxy certificate %s" % proxy
        proxy_cmd = "export X509_USER_PROXY=%s"%proxy
    else:
        proxy_cmd = ""            

    template =\
"""\
#!/bin/sh
#SBATCH -J {slurm_job_title}
#SBATCH -D {pwd}
#SBATCH -o {slurm_output_dir}slurm-test.%j.out

{proxy_cmd}
voms-proxy-info -all
eval \`"scram runtime -sh"\` 
echo CMSSW_BASE: {cmssw_base} 
echo Executing user command  
echo "{command}"
{command} 

voms-proxy-info -all

""".format(\
                command          = command,
                cmssw_base       = os.getenv("CMSSW_BASE"),
                slurm_output_dir = slurm_output_dir,
                slurm_job_title  = slurm_job_title,
                pwd              = os.getenv("PWD"),
                proxy_cmd = proxy_cmd
              )

    slurm_job = file(slurm_job_file, "w")
    slurm_job.write(template)
    slurm_job.close()
    return


if __name__ == '__main__':
    if not len(args) == 1:
        raise Exception("Only one argument accepted! Instead this was given: %s"%args)
    if os.path.isfile(args[0]):
        print "Reading commands from file: %s"%args[0]
        commands = []
        with open(args[0]) as f:
            for line in f.xreadlines():
                line = line.rstrip("\n")
                if line:
                    if line.startswith("#"):    
                        print "Skipping line, seems to be a comment %s"%line
                        continue
                    commands.append(line)
    elif type(args[0]) == type(""):
        commands = [args[0]]
    if commands:
        #hash_string = hashlib.md5("%s"%time.time()).hexdigest()
        #tmp_job_dir = "tmp_%s"%hash_string
        #os.mkdir(tmp_job_dir)
        for command in commands:
            #job_file = tmp_job_dir +"/" + slurm_job_file
            hash_string = hashlib.md5("%s"%time.time()).hexdigest()
            job_file = slurm_job_file.rstrip(".sh")+"_%s.sh"%hash_string
            make_slurm_job( job_file , slurm_job_title, slurm_output_dir , command  )
            os.system("sbatch %s"%job_file)
            os.remove(job_file)

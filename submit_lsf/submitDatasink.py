"""
	This script is used to submit single job to LSF based cluster Minerva for one GO term given the path to the data.
	Requested cpu number is 50, time is 30 hours and memeory usage no more than 10240 mb
	
	Author: Linhua Wang
	Created at: 06/21/2018
"""
from os.path import abspath
from os import remove, system
import argparse

parser = argparse.ArgumentParser(description='Feed some bsub parameters')
parser.add_argument('--path', '-P', type=str, required=True, help='data path')
parser.add_argument('--queue', '-Q', type=str, default='premium', help='LSF queue to submit the job')
parser.add_argument('--node', '-N', type=str, default='50', help='number of node requested')
parser.add_argument('--time', '-T', type=str, default='30', help='number of hours requested')
parser.add_argument('--memory', '-M', type=str,default='10240', help='memory requsted in MB')
args = parser.parse_args()
data = abspath(args.path).split('/')[-1]

script = open(data + '.lsf','w')
script.write('#!/bin/bash\n#BSUB -P acc_pandeg01a\n#BSUB -q %s\n#BSUB -J %s\n#BSUB -W %s:00\n#BSUB -R rusage[mem=%s]\n#BSUB -n %s\n' %(args.queue,data,args.time,args.memory,args.node))
script.write('#BSUB -o std/%s.out\n#BSUB -eo std/%s.err\n#BSUB -L /bin/bash\n' %(data,data))
script.write('module load python\nmodule load py_packages\nmodule load java\nmodule load groovy\nmodule load selfsched\nmodule load weka\n')
script.write('export _JAVA_OPTIONS=\"-XX:ParallelGCThreads=10\"\nexport JAVA_OPTS=\"-Xmx10g\"\nexport CLASSPATH=/hpc/users/wangl35/.sdkman/candidates/java/weka.jar\n')
script.write('python generate_jobs.py %s %s\n' %(abspath(args.path),data))
script.write('mpirun selfsched < %s.jobs\n' %data)
script.write('python combine.py %s\n' %abspath(args.path))
script.write('rm %s.jobs' %data)
script.close()
system('bsub < %s.lsf' %data)
remove('%s.lsf' %data)


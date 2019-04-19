
"""
	This script is used to submit single job to LSF based cluster hpc for one GO term given the path to the data.
	Requested cpu number is 50, time is 30 hours and memeory usage no more than 10240 mb
	
	Author: Linhua Wang
	Created at: 06/21/2018
"""
from os.path import abspath
from os import remove, system
import argparse
from common import load_properties

from itertools import product
from os import environ, system
from os.path import abspath, dirname, exists
from sys import argv
from common import load_arff_headers, load_properties

def make_jobs(all_parameters):
    job_file = open("%s.jobs" %data,"w")
    for parameters in all_parameters:
        working_dir, project_path, classifier, fold, bag, pipeline,seed = parameters
        job_file.write('groovy -cp %s %s/%s %s %s %s %s %s\n' % (classpath, working_dir, pipeline, project_path, fold, bag, seed,classifier))
    job_file.close()

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

#### Parse arguments
parser = argparse.ArgumentParser(description='Feed some bsub parameters')
parser.add_argument('--path', '-P', type=str, required=True, help='data path')
parser.add_argument('--queue', '-Q', type=str, default='premium', help='LSF queue to submit the job')
parser.add_argument('--node', '-N', type=str, default='20', help='number of node requested')
parser.add_argument('--time', '-T', type=str, default='10:00', help='number of hours requested')
parser.add_argument('--memory', '-M', type=str,default='10240', help='memory requsted in MB')
parser.add_argument('--classpath', '-CP', type=str,default='./weka.jar', help='path to weka.jar')
parser.add_argument('--hpc', '-MIN', type=str2bool,default='true', help='use hpc cluster or not')
parser.add_argument('--seed', '-S', type=str,default='1', help='the seed use to generate cross-validataion data')

### Get attributes
args = parser.parse_args()
path = abspath(args.path)
data = path.split('/')[-1]
p = load_properties(path)
nested_fold_values = range(int(p['nestedFoldCount']))
bag_count = int(p['bagCount'])
bag_values = range(bag_count) if bag_count > 1 else [0]
# ensure java's classpath is set
classpath = args.classpath
assert exists(classpath)
# ensure data path exists
assert exists(path)
# decide which pipeline to use
if 'idAttribute' in p.keys():
	pipeline = 'base_id.groovy'
else:
	pipeline = 'base.groovy'

###### Write the jobs
classifiers_fn = '%s/%s' % (path, p['classifiersFilename'])
input_fn = '%s/%s' % (path, p['inputFilename'])
assert exists(input_fn)
# Get cross validation values
assert ('foldAttribute' in p) or ('foldCount' in p)
if 'foldAttribute' in p:
    headers = load_arff_headers(input_fn)
    fold_values = headers[p['foldAttribute']]
else:
    fold_values = range(int(p['foldCount']))
# load classifiers from file, skip commented lines
classifiers = filter(lambda x: not x.startswith('#'), open(classifiers_fn).readlines())
classifiers = [_.strip() for _ in classifiers]
working_dir = dirname(abspath(argv[0]))
all_parameters = list(product([working_dir], [path], classifiers, fold_values, bag_values,[pipeline],[args.seed]))
make_jobs(all_parameters)

if args.hpc:
    print 'submitting largeGOPred job to hpc...'
    ####### Write the lsf file 
    script = open(data + '.lsf','w')
    script.write('#!/bin/bash\n#BSUB -P acc_pandeg01a\n#BSUB -q %s\n#BSUB -J %s\n#BSUB -W %s\n#BSUB -R rusage[mem=%s]\n#BSUB -n %s\n#BSUB -sp 100\n' %(args.queue,data,args.time,args.memory,args.node))
    script.write('#BSUB -o %s.%%J.stdout\n#BSUB -eo %s.%%J.stderr\n#BSUB -L /bin/bash\n' %(data,data))
    script.write('module load python\nmodule load py_packages\nmodule load java\nmodule load groovy\nmodule load selfsched\nmodule load weka\n')
    script.write('export _JAVA_OPTIONS=\"-XX:ParallelGCThreads=10\"\nexport JAVA_OPTS=\"-Xmx10g\"\n')
    script.write('mpirun selfsched < %s.jobs\n' %data)
    script.write('python combine.py %s\n' %abspath(args.path))
    script.write('rm %s.jobs' %data)
    script.close()
    ####### Submit the lsf job and remove lsf script
    system('bsub < %s.lsf' %data)
    remove('%s.lsf' %data)

else:
    print 'running largeGOPred locally...'
    system('sh %s.jobs' %data)
    system('python combine.py %s\n' %abspath(args.path))
    system('rm %s.jobs' %data)










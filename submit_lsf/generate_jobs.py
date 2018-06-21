#!/usr/bin/env python

"""
    This specific program is used to make job file for parallizing the processes
    in generating each classfier in each inner CV train round with 
    prediction on inner CV test data.  
"""
from itertools import product
from os import environ, system
from os.path import abspath, dirname, exists
from sys import argv
from common import load_arff_headers, load_properties

def make_jobs(all_parameters):
    job_file = open("%s.jobs" %data,"w")
    for parameters in all_parameters:
        working_dir, project_path, classifier, fold, bag = parameters
        expected_filenames = ['%s/%s/predictions-%s-%02i.csv.gz' % (project_path, classifier.split()[0], fold, bag)] + ['%s/%s/validation-%s-%02i-%02i.csv.gz' % (project_path, classifier.split()[0], fold, nested_fold, bag) for nested_fold in nested_fold_values]
#        if sum(map(exists, expected_filenames)) == len(expected_filenames):
#            return
        job_file.write('groovy -cp %s %s/Pipeline.groovy %s %s %s %s\n' % (classpath, working_dir, project_path, fold, bag, classifier))
    job_file.close()           

# ensure project directory exists
project_path = abspath(argv[1])
print project_path
assert exists(project_path)
data = argv[2]
# load and parse project properties
p = load_properties(project_path)
classifiers_fn = '%s/%s' % (project_path, p['classifiersFilename'])
input_fn = '%s/%s' % (project_path, p['inputFilename'])
print input_fn
assert exists(input_fn)

# generate cross validation values for leave-one-value-out or k-fold
assert ('foldAttribute' in p) or ('foldCount' in p)
if 'foldAttribute' in p:
    headers = load_arff_headers(input_fn)
    fold_values = headers[p['foldAttribute']]
else:
    fold_values = range(int(p['foldCount']))
nested_fold_values = range(int(p['nestedFoldCount']))
bag_count = int(p['bagCount'])
bag_values = range(bag_count) if bag_count > 1 else [0]

# ensure java's classpath is set
classpath = environ['CLASSPATH']

# load classifiers from file, skip commented lines
classifiers = filter(lambda x: not x.startswith('#'), open(classifiers_fn).readlines())
classifiers = [_.strip() for _ in classifiers]
working_dir = dirname(abspath(argv[0]))
n_jobs = -1
all_parameters = list(product([working_dir], [project_path], classifiers, fold_values, bag_values))
make_jobs(all_parameters)


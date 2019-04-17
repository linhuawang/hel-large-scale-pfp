#!/usr/bin/env python

'''
@author: Linhua Wang
@usage: combine predictions for later ensemble
@date: 07/17/2018
'''

from glob import glob
import gzip
from os.path import abspath, exists, isdir
from sys import argv
from common import load_properties
from pandas import concat, read_csv

path = abspath(argv[1]) ## path to the data
assert exists(path)
p = load_properties(path)
fold_count = int(p['foldCount'])
nested_fold_count = int(p['nestedFoldCount'])
bag_count = max(1, int(p['bagCount']))
dirnames = sorted(filter(isdir, glob('%s/weka.classifiers.*' % path)))

### Combine validation files from nested inner test predictions for each base classifier
for fold in range(fold_count):
    dirname_dfs = []
    for dirname in dirnames:
        classifier = dirname.split('.')[-1]
        nested_fold_dfs = []
        for nested_fold in range(nested_fold_count):
            bag_dfs = []
            for bag in range(bag_count):
                filename = '%s/validation-%s-%02i-%02i.csv.gz' % (dirname, fold, nested_fold, bag)
		try:
    	            df = read_csv(filename, comment="#", index_col = [0, 1], compression = 'gzip')
                    df = df[['prediction']]
                    df.rename(columns = {'prediction': '%s.%s' % (classifier, bag)}, inplace = True)
                    bag_dfs.append(df)
		except:
		    print '###### file %s not found or crashed .............' %filename
            nested_fold_dfs.append(concat(bag_dfs, axis = 1))
        dirname_dfs.append(concat(nested_fold_dfs, axis = 0))
    fn = '%s/validation-%s.csv.gz' % (path, fold)
    concat(dirname_dfs, axis = 1).sort_index().to_csv(fn,compression='gzip')

### Combine prediction files from outer test predictions for each base classifier
for fold in range(fold_count):
    dirname_dfs = []
    for dirname in dirnames:
        classifier = dirname.split('.')[-1]
        bag_dfs = []
        for bag in range(bag_count):
            filename = '%s/predictions-%s-%02i.csv.gz' % (dirname, fold, bag)
	    df = read_csv(filename, comment="#", index_col = [0, 1], compression = 'gzip')
            df = df[['prediction']]
            df.rename(columns = {'prediction': '%s.%s' % (classifier, bag)}, inplace = True)
            bag_dfs.append(df)
        dirname_dfs.append(concat(bag_dfs, axis = 1))
    fn = '%s/predictions-%s.csv.gz' % (path, fold)
    concat(dirname_dfs, axis = 1).sort_index().to_csv(fn,compression='gzip')
 

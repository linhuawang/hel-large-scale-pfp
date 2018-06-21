#!/usr/bin/env python

"""
    datasink: A Pipeline for Large-Scale Heterogeneous Ensemble Learning
    Copyright (C) 2013 Sean Whalen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see [http://www.gnu.org/licenses/].
"""
'''
	last edited by Linhua Wang@09/07/2017
'''
from glob import glob
import gzip
from os.path import abspath, exists, isdir
from sys import argv
from common import load_properties,load_arff_headers
from pandas import concat, read_csv
path = abspath(argv[1])
assert exists(path)
p = load_properties(path)
#fold_count = int(p['foldCount'])
nested_fold_count = int(p['nestedFoldCount'])
bag_count = max(1, int(p['bagCount']))
dirnames = sorted(filter(isdir, glob('%s/weka.classifiers.*' % path)))

input_fn = '%s/%s' % (path, p['inputFilename'])
if 'foldAttribute' in p:
    headers = load_arff_headers(input_fn)
    fold_values = headers[p['foldAttribute']]
else:
    fold_values = range(int(p['foldCount']))


for fold in fold_values:
    dirname_dfs = []
    for dirname in dirnames:
        classifier = dirname.split('.')[-1]
        nested_fold_dfs = []
        for nested_fold in range(nested_fold_count):
            bag_dfs = []
            for bag in range(bag_count):
                filename = '%s/validation-%s-%02i-%02i.csv.gz' % (dirname, fold, nested_fold, bag)
		print filename
                df = read_csv(filename, skiprows = 1, index_col = [0, 1], compression = 'gzip')
                df = df[['prediction']]
                df.rename(columns = {'prediction': '%s.%s' % (classifier, bag)}, inplace = True)
                bag_dfs.append(df)
            nested_fold_dfs.append(concat(bag_dfs, axis = 1))
        dirname_dfs.append(concat(nested_fold_dfs, axis = 0))
    with gzip.open('%s/validation-%s.csv.gz' % (path, fold), 'wb') as f:
    	#@edited by Linhua Wang@09/07/2017: ndarray sort --> sort_index
        concat(dirname_dfs, axis = 1).sort_index().to_csv(f)

for fold in fold_values:
    dirname_dfs = []
    for dirname in dirnames:
        classifier = dirname.split('.')[-1]
        bag_dfs = []
        for bag in range(bag_count):
            filename = '%s/predictions-%s-%02i.csv.gz' % (dirname, fold, bag)
	    print filename
            df = read_csv(filename, skiprows = 1, index_col = [0, 1], compression = 'gzip')
            df = df[['prediction']]
            df.rename(columns = {'prediction': '%s.%s' % (classifier, bag)}, inplace = True)
            bag_dfs.append(df)
        dirname_dfs.append(concat(bag_dfs, axis = 1))
    with gzip.open('%s/predictions-%s.csv.gz' % (path, fold), 'wb') as f:
    	#@edited by Linhua Wang@09/07/2017: ndarray sort --> sort_index
        concat(dirname_dfs, axis = 1).sort_index().to_csv(f)

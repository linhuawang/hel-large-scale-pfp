#!/usr/bin/env python

"""
	This scirpt is used for stacking using logistic regression in leave-one-species-out validation
	This script is based on Sean Whalen's script for package: datasink (https://github.com/shwhalen/datasink)
    datasink: A Pipeline for Large-Scale Heterogeneous Ensemble Learning
    Copyright (C) 2013 Sean Whalen
"""
from os import mkdir
from os.path import abspath, exists
from sys import argv
from pandas import DataFrame, concat
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.externals.joblib import Parallel, delayed
from sklearn.linear_model import SGDClassifier
from nnls import NNLS
import common
def stacked_generalization(fold):
    train_df, train_labels, test_df, test_labels = common.read_fold(path, fold)
    train_df = common.unbag(train_df, bag_count)
    test_df = common.unbag(test_df, bag_count)
    if test_df.shape[0]  < 10:
        return None
    test_predictions = stacker.fit(train_df, train_labels).predict_proba(test_df)[:, 1]
    return DataFrame({'fold': fold, 'id': test_df.index.get_level_values('id'), 'label': test_labels, 'prediction': test_predictions, 'diversity': common.diversity_score(test_df.values)})


path = abspath(argv[1])
assert exists(path)
if not exists('%s/analysis' % path):
    mkdir('%s/analysis' % path)
p = common.load_properties(path)
input_fn = '%s/%s' % (project_path, p['inputFilename'])
assert exists(input_fn)

# generate cross validation values for leave-one-value-out or k-fold
assert ('foldAttribute' in p) or ('foldCount' in p)
if 'foldAttribute' in p:
    headers = load_arff_headers(input_fn)
    fold_values = headers[p['foldAttribute']]
else:
    fold_values = range(int(p['foldCount']))
bag_count = int(p['bagCount'])
stacker = LogisticRegression()

# leave-one-out validataion
for fold in fold_values:
	prediction_df = stacked_generalization(fold)
	if prediction_df is not None:
		prediction_df.to_csv('%s/analysis/%s-predictions.csv' %(path,fold))

#!/usr/bin/env python

"""
    This scirpt is used for stacking using logistic regression in leave-one-species-out validation
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
    try:
	    train_df, train_labels, test_df, test_labels = common.read_fold(path, fold)
    	train_df = common.unbag(train_df, bag_count)
    	test_df = common.unbag(test_df, bag_count)
    	if test_df.shape[0]  < 10:
            return None
        test_predictions = stacker.fit(train_df, train_labels).predict_proba(test_df)[:, 1]
        return DataFrame({'fold': fold, 'id': test_df.index.get_level_values('id'), 'label': test_labels, 'prediction': test_predictions, 'diversity': common.diversity_score(test_df.values)})
    except:
        return None

path = abspath(argv[1])
assert exists(path)
if not exists('%s/analysis' % path):
    mkdir('%s/analysis' % path)
p = common.load_properties(path)
input_fn = '%s/%s' % (path, p['inputFilename'])
assert exists(input_fn)

# generate cross validation values for leave-one-value-out or k-fold
assert ('foldAttribute' in p) or ('foldCount' in p)
if 'foldAttribute' in p:
    headers = common.load_arff_headers(input_fn)
    fold_values = headers[p['foldAttribute']]
else:
    fold_values = range(int(p['foldCount']))

stacker = LogisticRegression()

perf_df = []
for fold in fold_values:
	prediction_df = stacked_generalization(fold)
	if prediction_df is not None:
		prediction_df.to_csv('%s/analysis/%s-predictions.csv' %(path,fold))
		fmax = common.fmax_score(prediction_df.label.tolist(),prediction_df.prediction.tolist())
		perf_df.append(DataFrame(data = [[path.split('/')[-1],fold,fmax]], columns=['data','fold','fmax'],index=[0]))

# Get Fmax value for each fold, and dump to local disk
perf_df = concat(perf_df)
perf_df.to_csv(path + '/analysis/%s_fmax.csv' %path.split('/')[-1])

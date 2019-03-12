"""
    This script is used to get performance for CES, mean ensemble and best base classifier,
"""

from time import time
from os import mkdir
from os.path import abspath, exists
from sys import argv
from numpy import array, column_stack
from numpy.random import choice, seed, append
from pandas import DataFrame, concat
from sklearn.cluster import MiniBatchKMeans
from sklearn.linear_model import LogisticRegression
from sklearn.externals.joblib import Parallel, delayed
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier
import common


def get_cluster_performance(labels, predictions, n_clusters, fold, seedval):
    return {'fold': fold, 'seed': seedval, 'score': common.fmax_score(labels, predictions), 'n_clusters': n_clusters}


def get_performance(df, ensemble, fold, seedval):
    labels          = df.index.get_level_values('label').values
    predictions     = df[ensemble].mean(axis = 1)
    return {'fold': fold, 'seed': seedval, 'score': common.fmax_score(labels, predictions), 'ensemble': ensemble[-1], 'ensemble_size': len(ensemble)}


def get_predictions(df, ensemble, fold, seedval):
    ids             = df.index.get_level_values('id')
    labels          = df.index.get_level_values('label')
    predictions     = df[ensemble].mean(axis = 1)
    diversity       = common.diversity_score(df[ensemble].values)
    return DataFrame({'fold': fold, 'seed': seedval, 'id': ids, 'label': labels, 'prediction': predictions, 'diversity': diversity, 'ensemble_size': len(ensemble)})


def select_candidate_enhanced(train_df, train_labels, best_classifiers, ensemble, i):
    initial_ensemble_size = 2
    max_candidates=50
    if len(ensemble) >= initial_ensemble_size:
        candidates = choice(best_classifiers.index.values, min(max_candidates, len(best_classifiers)), replace = False)
        candidate_scores = [common.score(train_labels, train_df[ensemble + [candidate]].mean(axis = 1)) for candidate in candidates]
        best_candidate = candidates[common.argbest(candidate_scores)]
    else:
        best_candidate = best_classifiers.index.values[i]
    return best_candidate

def select_candidate_greedy(train_df, train_labels, best_classifiers, ensemble, i):
    return best_classifiers.index.values[i]

def selection(fold,seedval,path):
    seed(seedval)
    initial_ensemble_size = 2
    max_ensemble_size = 50
    max_candidates = 50
    max_diversity_candidates = 5
    accuracy_weight = 0.5
    max_clusters = 20
    train_df, train_labels, test_df, test_labels = common.read_fold(path, fold)
    train_df = common.unbag(train_df, 10)
    test_df = common.unbag(test_df, 10)
    #@edited by: Linhua Wang@09/07/2017, numpy order --> sort_values
    best_classifiers = train_df.apply(lambda x: common.fmax_score(train_labels, x)).sort_values(ascending = not common.greater_is_better)
    train_performance = []
    test_performance = []
    ensemble = []
    for i in range(min(max_ensemble_size, len(best_classifiers))):
        best_candidate = select_candidate_enhanced(train_df, train_labels, best_classifiers, ensemble, i)
        ensemble.append(best_candidate)
        train_performance.append(get_performance(train_df, ensemble, fold, seedval))
        test_performance.append(get_performance(test_df, ensemble, fold, seedval))
    train_performance_df = DataFrame.from_records(train_performance)
    best_ensemble_size = common.get_best_performer(train_performance_df).ensemble_size.values
    #@edited by linhua Wang@09/07/2017, item --> item(0)
    best_ensemble = train_performance_df.ensemble[:best_ensemble_size.item(0) + 1]
    return get_predictions(test_df, best_ensemble, fold, seedval), DataFrame.from_records(test_performance)

def CES_fmax(path):
    assert exists(path)
    if not exists('%s/analysis' % path):
        mkdir('%s/analysis' % path)
    method = 'enhanced'
    select_candidate = eval('select_candidate_' + method)
    method_function = selection
    p = common.load_properties(path)
    fold_count = int(p['foldCount'])
    initial_ensemble_size = 2
    max_ensemble_size = 50
    max_candidates = 50
    max_diversity_candidates = 5
    accuracy_weight = 0.5
    max_clusters = 20

    predictions_dfs = []
    performance_dfs = []
    seeds = [0] if method == 'greedy' else range(10)

    for seedval in seeds:
        for fold in range(fold_count):
            pred_df, perf_df = method_function(fold,seedval,path)
            predictions_dfs.append(pred_df)
            performance_dfs.append(perf_df)
    performance_df = concat(performance_dfs)
    performance_df.to_csv('%s/analysis/selection-%s-%s-iterations.csv' % (path, method, 'fmax'), index = False)
    predictions_df = concat(predictions_dfs)
    predictions_df['method'] = method
    predictions_df['metric'] = 'fmax'
    predictions_df.to_csv('%s/analysis/selection-%s-%s.csv' % (path, method, 'fmax'), index = False)
    fmax = '%.3f' %(common.fmax_score(predictions_df.label,predictions_df.prediction))
#    fmax =  '%.3f' %predictions_df.groupby(['fold', 'seed']).apply(lambda x: common.fmax_score(x.label, x.prediction)).mean()
#    print predictions_df.groupby(['fold', 'seed']).apply(lambda x: common.fmax_score(x.label, x.prediction))
    return fmax,predictions_df.ensemble_size.mean()

def mean_fmax(path):
    assert exists(path)
    if not exists('%s/analysis' % path):
        mkdir('%s/analysis' % path)
    p = common.load_properties(path)
    fold_count = int(p['foldCount'])
    predictions = []
    labels = []
    for fold in range(fold_count):
        _,_,test_df,label = common.read_fold(path,fold)
        test_df = common.unbag(test_df, 10)
        predict = test_df.mean(axis=1).values
        predictions = append(predictions,predict)
        labels = append(labels,label)
    fmax = '%.3f' %(common.fmax_score(labels,predictions))
    return fmax

def bestbase_fmax(path):
    assert exists(path)
    if not exists('%s/analysis' % path):
        mkdir('%s/analysis' % path)
    p = common.load_properties(path)
    fold_count = int(p['foldCount'])
    predictions = []
    labels = []
    for fold in range(fold_count):
        _,_,test_df,label = common.read_fold(path,fold)
        test_df = common.unbag(test_df, 10)
        predictions.append(test_df)
        labels = append(labels,label)
    predictions = concat(predictions)
    fmax_list = [common.fmax_score(labels,predictions[col].tolist()) for col in list(predictions)]
    return max(fmax_list)







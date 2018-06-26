"""
    This script calculate the performance for 8 stacking methods, mean ensemble, CES and best base classifiers
    Dump evaluted results into local folder for each data
    Author: Linhua Wang
    Time: 06/26/2018
"""

from os.path import abspath, exists
from sys import argv
from pandas import DataFrame, concat
import pandas as pd
import common
from glob import glob
from sklearn.ensemble import RandomForestClassifier # Random Forest
from sklearn.linear_model import SGDClassifier # SGD
from sklearn.naive_bayes import GaussianNB # Naive Bayes
from sklearn.linear_model import LogisticRegression # Logistic regression
from sklearn.ensemble import AdaBoostClassifier #Adaboost
from sklearn.tree import DecisionTreeClassifier # Decision Tree
from sklearn.ensemble import GradientBoostingClassifier # Logit Boost with parameter(loss='deviance')
from sklearn.neighbors import KNeighborsClassifier # K nearest neighbors (IBk in weka)
import sys
import warnings
import numpy as np
from os import mkdir
import besides_stack
from numpy import mean

sys.path.append('../submit_lsf')

warnings.filterwarnings("ignore")
import progressbar as pb

# Get data path and GO term ID
path = abspath(sys.argv[1])
assert exists(path)
go_term = "GO:%s" %path.split("/")[-1]
category = path.split('/')[-2]
bp_terms = list(pd.read_csv('/sc/orga/projects/pandeg01a/wangl35/projects/GO/scripts/dataInput/ig-iea-pos-neg-bp-10.tsv',sep='\t'))
if go_term in bp_terms:
    category='bp'

# Get data basic stats
apath = abspath(path + '/' + path.split("/")[-1] +'.arff')
df = pd.read_csv(apath,comment='@',header=None)
posNum = df[df.iloc[:,-1] == 1].shape[0]
negNum = df[df.iloc[:,-1] == -1].shape[0]
totalNum = df.shape[0]
pn_ratio = float(posNum) / float(negNum)
p = common.load_properties(path)
fold_count = int(p['foldCount'])
bag_count = int(p['bagCount'])
# Build all stackers
stackers = [RandomForestClassifier(n_estimators = 200, max_depth = 2, bootstrap = False, random_state = 0), SGDClassifier(loss = 'log',random_state = 0),GaussianNB(),LogisticRegression(),AdaBoostClassifier(),DecisionTreeClassifier(),GradientBoostingClassifier(loss='deviance'),KNeighborsClassifier()]
stacker_names = ["RandomForest","SGD","NaiveBayes","LogisticRegression","AdaBoost","DecisionTree","LogitBoost","KNN"]

def stacked_generalization(stacker,fold):
    train_df, train_labels, test_df, test_labels = common.read_fold(path, fold)
    train_df = common.unbag(train_df, 10)
    test_df = common.unbag(test_df, 10)
    test_predictions = stacker.fit(train_df, train_labels).predict_proba(test_df)[:, 1]
    return DataFrame({'fold': fold, 'id': test_df.index.get_level_values('id'), 'label': test_labels, 'prediction': test_predictions, 'diversity': common.diversity_score(test_df.values)})

# Get CES, mean ensemble and best base classifier Fmax scores
ces_fmax = besides_stack.CES_fmax(path)
mean_fmax = besides_stack.mean_fmax(path)
best_base_fmax = besides_stack.bestbase_fmax(path)
method = 'aggregate' # Set default method for baggings to be aggregate
cols = ['GO','category','#pos','#neg','#total','#+/#-','fmax','metaClassifier','best_base_fmax','best_base_learner','CES_size']
dfs = []

# Get Stacking Fmax scores
for i,(stacker_name,stacker) in enumerate(zip(stacker_names,stackers)):
    predictions_dfs = [stacked_generalization(stacker,fold) for fold in range(fold_count)]
    predictions_df = concat(predictions_dfs)
    predictions_df['method'] = method
    fmax = common.fmax_score(predictions_df.label, predictions_df.prediction)
    df = DataFrame(data = [[go_term,category,posNum, negNum, totalNum,pn_ratio,fmax,stacker_name,best_base_fmax,best_base_clsf,ces_size]],columns=cols, index = [0])
    dfs.append(df)

dfs.append(DataFrame(data = [[go_term,category,posNum, negNum, totalNum,pn_ratio,ces_fmax,'CES',best_base_fmax,best_base_clsf,ces_size]], columns=cols, index = [0]))
dfs.append(DataFrame(data = [[go_term,category,posNum, negNum, totalNum,pn_ratio,mean_fmax,'mean',best_base_fmax,best_base_clsf,ces_size]], columns=cols, index = [0]))
dfs = concat(dfs)
stack_fmax = dfs['fmax'].tolist()
base_fmax = dfs['best_base_fmax'].tolist()
delta_fmax = np.subtract(stack_fmax,base_fmax)
dfs['del_fmax'] = delta_fmax
dfs = dfs[cols + ['del_fmax']]

# Save results
dfs.to_csv("%s/analysis/analysis_aggregate.csv" %path, index = False)

"""
	This scirpt is used to check if a single submitted jobs for leave-one-out-species validation succeeded or not,
	if it is incomplete/failed, what's the current progress for this job
"""

from glob import glob
from sys import argv
from common import load_properties, load_arff_headers
from os.path import exists

path = argv[1]
p = load_properties(path)
input_fn = '%s/%s' % (path, p['inputFilename'])
print input_fn
assert exists(input_fn)

# generate cross validation values for leave-one-value-out or k-fold
assert ('foldAttribute' in p) or ('foldCount' in p)
if 'foldAttribute' in p:
    headers = load_arff_headers(input_fn)
    fold_values = headers[p['foldAttribute']]



folders = glob(path + '/weka.classifiers.*')
for folder in folders:
	classifier = folder.split('/')[-1]
	files = glob(folder + '/*')
	if len(files) != 1140:
		print classifier + ': ' + str(len(files))
		validations=[]
		predictions=[]
		for fold in fold_values:
			for inner in range(5):
				for bag in range(10):
					validations.append('%s/validation-%s-%02d-%02d.csv.gz' %(folder,fold,inner,bag))
			for bag in range(10):
				predictions.append('%s/predictions-%s-%02d.csv.gz' %(folder,fold,bag))
		missedFiles = [f for f in validations if f not in files] + [f for f in predictions if f not in files]
		if len(argv) == 3 and argv[2] == 'show':
			for f in missedFiles:
				print f.split('/')[-1]

"""
	This scirpt is used to check how many submitted jobs for leave-one-out-species validation succeeded and how many failed/incomplete,
	if there are incomplete/failed jobs, which are them. If resubmit is needed, we can resubmit failed jobs by adding 'resubmit' in command line argument
"""
from os import listdir
from sys import argv
from glob import glob
from os import system
from os import chdir
path = argv[1]

data = glob("%s/*" %path)
finished = []
notyet = []
resubPath = []
for d in data:
	files = glob("%s/*.gz" %d)
	wekafiles = glob("%s/weka.classifiers.*" %d)
	term = d.split('/')[-1]
	if len(files) == 38 and len(wekafiles) == 12:
		finished.append(term)
	else:
		resubPath.append(d)
		print "Not yet: " + d.split('/')[-1]
		notyet.append(term)

print '#Succeeded jobs: %d\n#Failed jobs: %d' %(len(finished),len(notyet))

if len(argv) > 2 and argv[2] == 'resubmit':
	for d,n in zip(resubPath,notyet):
		system('python submitDatasink.py %s premium 50 30' %d)


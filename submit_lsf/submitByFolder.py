"""
	This script is used to submit a group of jobs, all data should be present in the same folder and this fold only contains data to be trained

	Author: Linhua Wang
	Created at: 06/21/2018
"""
from glob import glob
from os import system
from os.path import abspath,exists
from sys import argv
paths = glob('%s/*' %abspath(argv[1]))

for path in paths:
    path = abspath(path)
    data = path.split('/')[-1]
    system('python submitDatasink.py %s' %data)

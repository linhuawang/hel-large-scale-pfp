from glob import glob
from sys import argv
from os.path import exists
from os import system

#path = argv[1]
#folders = glob(path +'/*')

def checkFolder(f):
    for fold in range(5):
	if not exists('%s/predictions-%d.csv.gz' %(f,fold)):
            return False
        if not exists('%s/validation-%d.csv.gz' %(f,fold)):
            return False
    return True

tc = 0
fc = 0

####### Write the lsf file
script = open('failed22.lsf','w')
script.write('#!/bin/bash\n#BSUB -P acc_pandeg01a\n#BSUB -q expressalloc\n#BSUB -J diabetes\n#BSUB -W 2:00\n#BSUB -n 20\n#BSUB -sp 100\n')
script.write('#BSUB -o std/diabetes.out\n#BSUB -eo std/diabetes.err\n#BSUB -L /bin/bash\n')
script.write('module load python\nmodule load py_packages\nmodule load java\nmodule load groovy\nmodule load selfsched\nmodule load weka\n')
script.write('export _JAVA_OPTIONS=\"-XX:ParallelGCThreads=10\"\nexport JAVA_OPTS=\"-Xmx10g\"\n')

for r in range(1,11):
    print '######### checking round %d ........' %r
    p = '../diabetes/r%d/' %r
    folders = glob(p +'/*')
    for f in folders:
        if not checkFolder(f):
#	        system('python run.py --path %s --time 1:00 --queue expressalloc' %f)
	    script.write('python run.py --path %s --minerva 0 &\n' %f)
	    fc += 1
            print f
print '[NUMBER] of failed jobs: %d' %fc
script.close()

'''
tc = 0
fc = 0
fcf = []
dns = []
for f in folders:
    if checkFolder(f):
        tc += 1
    else:
	fc += 1
        fcf.append(f)
        dns.append(f.split('/')[-1])
	print f.split('/')[-1]

print 'Finished: %d.' %tc
print 'Not done: %d...' %fc


if len(argv)==3 and  argv[2] == 'resub':
    print 'Resubmitting...'
    for fn,dn in zip(fcf,dns):
        system('python run.py --path %s --time 1:00 -queue expressalloc' %fn)
'''

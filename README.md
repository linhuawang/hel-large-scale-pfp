# LargeGOPred: Heterogeneous ensemble learning for large-scale GO term prediction

The scripts in this repository are used to reproduce the results for our recent work on large-scale assessment of heterogeneous ensembles in protein function predicton (PFP) (https://f1000research.com/articles/7-1577/v1). 

To cite this work:
Wang L, Law J, Kale SD et al. Large-scale protein function prediction using heterogeneous ensembles [version 1; referees: awaiting peer review]. F1000Research 2018, 7(ISCB Comm J):1577
(doi: 10.12688/f1000research.16415.1)

## Data availability
The data underlying this study is available from Zenodo. Dataset 1: Data for LargeGOPred (http://doi.org/10.5281/zenodo.1434450). Model training, testing and evaluatoin are based on this dataset. Additional formatting is necessary if you use your own ARFF files. Please cite as the following if you are using this dataset:
* Linhua W: Data for LargeGOPred [Data set]. Zenodo. 2018. http://www.doi.org/10.5281/zenodo.1434450

## Setup environments
The following dependencies are required:
the
* Java
* [Groovy](http://groovy.codehaus.org)
* [Weka](http://www.cs.waikato.ac.nz/~ml/weka/) 3.7.10
* [Python](http://www.python.org) 2.7
* [Cython](http://www.cython.org) 0.19.1
* [pandas](http://pandas.pydata.org) 0.14.1
	* [NumPy](http://www.numpy.org) 1.8.2
* [scikit-learn](http://scikit-learn.org) 0.14
	* [SciPy](http://www.scipy.org) 0.12

Besides, an LSF system is required with built-in module selfsched. Jobs should be submitted using 'bsub' command.

## Data
We have overall > 60,000 sequences coming from 19 pathogentic bacteria and 277 GO term profiles.
All GO terms data are further categorized in to molecular function and biological process based on their ontology categories.
Let's have a look at how we organized the data:
	/path/to/main/src/ > mf/ > GO*******/
	/path/to/main/src/ > bp/ > GO*******/
And, each individual GO term data folder contains following 3 files initially:
* GO*******.arff
* weka.properties
* classifiers.txt

GO*******.arff file contains the attributes for training and testing, weka.properties is the file specified the weka properties in training the data and classifiers.txt lists all needed classifiers and associated parameters.
For more detailed information, please have a look at files in sample_data folder.

## Train base predictors
	cd submit_lsf
	python submitDatasink.py -P /path/to/data (to submit one single job) [other args]

## 5-fold cross-validation
We use 5 fold inner cross-validation to train/test 12 base predictors and 5 fold outer cross-validation to train/test ensembles. Since the training for base predictors and ensembles are independent, the model prevents overfittting. In 5-fold cross-valitaion, for ensemble building, we tried 8 different stackig methods using diverse meta classifiers, ensemble selection method - CES and one naive ensemble method - mean.
* Sample data is in sample_data/GO0000166-5fold/
* Evaluations are using code in folder evaluation




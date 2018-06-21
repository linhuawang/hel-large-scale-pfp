# hel-large-scale-pfp: Heterogeneous ensemble learning for large scale protein function prediction

The scirpts in this repository is used to reproduce the results for our large-scale assessment of heterogeneous ensembles in PFP. 
Heterogeneous enesmble training is based on previous built software: datasink by Sean Whalen (https://github.com/shwhalen/datasink)
The following scripts directly or largely come from Sean's code in datasink:
* Pipeline.groovy (slightly modified)
* common.py 
* combine.py
* generate_jobs.py (largely modified from generate.py in datasink)

## Setup environments
Because this project is on top of datasink, software dependencies are almost them same as datasink, so the followings are required:

* Java
* [Groovy](http://groovy.codehaus.org)
* [Weka](http://www.cs.waikato.ac.nz/~ml/weka/) 3.7.10
* [Python](http://www.python.org) 2.7
* [Cython](http://www.cython.org) 0.19.1
* [pandas](http://pandas.pydata.org) 0.14.1
	* [NumPy](http://www.numpy.org) 1.8.2
* [scikit-learn](http://scikit-learn.org) 0.14
	* [SciPy](http://www.scipy.org) 0.12

On top of datasink environment, an LSF system is required with module selfsched and jobs should be submitted using 'bsub' command.

## Data
We have overall > 60,000 sequences coming from 19 pathogentic bacteria and 277 GO term profiles.
All GO terms data are further categorized in to molecular function and biological process based on their ontology categories.
Let's look at the structure of how we organized the data:
	/path/to/main/src/ > mf/ > GO*******/
	/path/to/main/src/ > bp/ > GO*******/
And, each individual GO term data folder contains following 3 files initially:
* GO*******.arff
* weka.properties
* classifiers.txt

GO*******.arff file contains the attributes for training and testing, weka.properties is the file specified the weka properties in training the data and classifiers.txt lists all needed classifiers and associated parameters.
For more detailed information, please have a look at files in sample_data folder.

## Training base predictors
> cd submit_lsf
> python submitDatasink.py /path/to/data (to submit one single job)
> python submitByFolder.py /path/to/all/data/folder (to submit jobs for all data in one folder:)

## 5-fold cross-validation
We use 5 fold inner cross-validation to train/test 12 base predictors and 5 fold outer cross-validation to train/test ensembles. Since the training for base predictors and ensembles are independent, the model prevents overfittting.
In 5-fold cross-valitaion, for ensemble building, we tried 8 different stackig methods using diverse meta classifiers, ensemble selection method - CES and one naive ensemble method - mean.
Sample data is in sample_data/GO0000166-5fold/
Evaluations are using code in folder evaluation

## leave-one-species-out
Since there are 19 species used in this study, leave-one-species-out validation might infer important biological information.
In every iteration, we used 18 species to train and the left-out species to test. By doing so, if one species has less than 10 samples for testing one GO term, we ignore this GO term testing for this species.
Only Stacking using Logistic Regression is used in leave-one-species-out evaluation because it was the best performed ensemble method in 5-fold cross-validation
Sample data is in sample_data/GO0000166-loso/
Predictions are generated using lrs-loso.py

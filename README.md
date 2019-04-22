# LargeGOPred: a pipeline for efficient and comprehensive learning of a variety of heterogeneous ensemble models.

The scripts in this repository are used to reproduce the results for our recent work on large-scale assessment of heterogeneous ensembles in protein function predicton (PFP) (https://f1000research.com/articles/7-1577/v1).

To cite this work: Wang L, Law J, Kale SD et al. Large-scale protein function prediction using heterogeneous ensembles. F1000Research 2018, 7(ISCB Comm J):1577 (doi: 10.12688/f1000research.16415.1)

## Configurations:
	1. Install Java and groovy.
		This can be done using sdkman (https://sdkman.io/).
	2. Install python environments.
		conda create --name largegopred
		conda install -n largegopred python=2.7.14 cython=0.19.1 pandas=0.23.1 scikit-learn=0.19.1
	3. Download weka.jar to the current directory:

		curl -O -L http://prdownloads.sourceforge.net/weka/weka-3-7-10.zip

## Data:
	1. arff file with a prefix that is the same as the folder name.
	2. classifiers.txt: specifies the list of Weka classifiers and parameter.
	3. weka.properties: list of weka properties. 
	The data underlying this study is available from Zenodo. Dataset 1: Data for LargeGOPred (http://doi.org/10.5281/zenodo.1434450). Model training, testing and evaluatoin are based on this dataset. Additional formatting is necessary if you use your own ARFF files. Please cite as the following if you are using this dataset:
	
	* Linhua W: Data for LargeGOPred [Data set]. Zenodo. 2018. http://www.doi.org/10.5281/zenodo.1434450


## Step 1: Train base classifiers.
	In this step, base classifiers are trained and used to make predictions for later ensembles. Scripts train_base.py is used for this task.	
	
	Arguments of train_base.py:
		--path: Path to data, required.
		--seed: Seed to generate the cross-validation fold, default is 1.
		--minerva: Specify whether use minerva or not, default is true. Following parameters work only when minerva is requested. 
			--queue: minerva queue to be used, default is premium. 
			--node: #nodes to be used, default is 20. 
			--time: walltime, default is 10:00 (10 hours).
			--memory: memory limit, default is 10240 MB.
			--classpath: path to weka file, default is ./weka.jar.
	
	Two options to run the scripts:
		Option 1: Do it locally.

			python train_base.py --path [path] --minerva 0

		Option 2: Do it on Minerva cluster.

			python train_base.py --path [path] --time [time] --queue [queue] --node [node] --memory [memory] ...

## Step 2: Train ensembles and evaluate.
	In this step, we trained and evaluated the following models:
		CES, Mean, best base classifier and 8 stackers:
			Random Forest, SVM, Naive Bayes, Logistic Regression, AdaBoost, Decision Tree, LogitBoost, KNN.

	Arguments of ensemble.py:
		--path: path to data, required.
		--fold: cross validation fold, default is 5.
		--agg: number to aggregate bag predictions, default is 1. 
			If each bagging classifier is treated individually, ignore it.
			Else if bagcount > 1, set -agg = bagcount. 
	
	To run step 2:

		python ensemble.py --path [path] --fold [fold_count] --agg [1 or bag_count]

	F-max scores of these models will be printed and written in the performance.csv file and saved to the analysis folder under the data path.

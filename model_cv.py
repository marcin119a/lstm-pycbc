
import numpy as np
import hickle as hkl
import keras.optimizers as optim

from sklearn.model_selection import KFold, cross_val_score
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.regularizers import l1,l2
from matplotlib import pyplot
import tensorflow as tf
from model import create_model


array_hkl = hkl.load('data/D-SET-norm(100,1200).hkl')
X_train = array_hkl.get('xtrain')
X_test = array_hkl.get('xtest')
y_train = array_hkl.get('ytrain')
y_test = array_hkl.get('ytest')

X_train = X_train.reshape(X_train.shape[0], X_train.shape[2], 1)
X_test =  X_test.reshape(X_test.shape[0], X_test.shape[2], 1)


# remove one dimension
y_test = np.squeeze(y_test)
y_train = np.squeeze(y_train)

   
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import RepeatedKFold
from numpy import mean
from numpy import std
from scipy.stats import sem

def evaluate_model(X,y):
    # prepare the cross-validation procedure
    classifier = KerasRegressor(build_fn = create_model, batch_size = 10, epochs = 20)

    accuracies = cross_val_score(estimator = classifier, X = np.vstack((X_train, X_test)), y = np.vstack((y_train, y_test)), cv = 10)

    return accuracies

# configurations for test
repeats = range(1)
results = list()
for r in repeats:
	# evaluate using a given number of repeats
	accuracies = evaluate_model(X_test, y_test)
	# summarize
	print('>%d mean=%.4f se=%.3f' % (r, mean(accuracies), sem(accuracies)))
	# store
	results.append(accuracies)
# plot the results
pyplot.boxplot(results, labels=[str(r) for r in repeats], showmeans=True)
pyplot.show()
pyplot.savefig('boxplot.png')
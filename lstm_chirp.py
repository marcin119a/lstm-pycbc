from hyperopt.mongoexp import MongoTrials

import keras.optimizers as optim
import hickle as hkl
import numpy as np
import tensorflow as tf 
from model_chirp import create_model
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-parallel", "--pr", type=bool, default=False, help="Parallel computation")
ap.add_argument("-batch_norm", "--bn", type=bool, default=False, help="Batch normalizaction")

args = vars(ap.parse_args())

array_hkl = hkl.load('data/D-SET(100,1200)-chirp.hkl')
X_train = array_hkl.get('xtrain')
X_test = array_hkl.get('xtest')
y_train = array_hkl.get('ytrain')
y_test = array_hkl.get('ytest')

X_train = X_train.reshape(X_train.shape[0], X_train.shape[2], 1)
X_test =  X_test.reshape(X_test.shape[0], X_test.shape[2], 1)

y_train = tf.keras.utils.normalize(y_train)  
y_test = tf.keras.utils.normalize(y_test)  

y_test = np.squeeze(y_test)
y_train = np.squeeze(y_train)




# define a search space
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
import numpy as np

space = {
    'activation':hp.choice('activation', ('relu', 'tanh')),
    'lr':hp.loguniform('lr', np.log(1e-6), np.log(1e-2)), 
    'dropout':hp.uniform('dropout', 0.0, 1.0), 
    'reg':hp.uniform('reg', 1e-6, 1e-3), 
    'num_layers': hp.uniformint('num_layers', 64,1024)
}

# define loss function
def loss(params):
    
    model = create_model(**params)

    _ = model.fit(X_train, y_train, epochs=1, batch_size=32, verbose=0)
    val_loss = model.evaluate(X_test, y_test, verbose=1)
    print('Loss: {}'.format(val_loss))
    
    return {'loss': val_loss, 'status': STATUS_OK}

if __name__ == "__main__":
    print('Begin tuning')
    print('------------')

    if args["pr"]:
        trials = MongoTrials('mongo://localhost:1234/optim/jobs', exp_key='exp1')
    else:
        trials = Trials()

    best_params = fmin(loss,
                    space = space,
                    algo = tpe.suggest,
                    max_evals = 20,
                    trials = trials)
    print('')
    print('Best parameters:')
    print('----------------')
    best_params['activation'] = ['relu', 'tanh'][best_params['activation']]
    for k, v in best_params.items():
        print('{} = {}'.format(k, v))
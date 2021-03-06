from generator import split_dataset, random_dataset
import keras.optimizers as optim
import numpy as np
from model_class import create_model
import argparse
import tensorflow as tf
import mlflow
from utilities import split
import tensorflow.keras.utils as utils
from sklearn.metrics import classification_report
from sklearn import metrics
from matplotlib import pyplot as plt
import seaborn as sns


#import os 
#os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

def model_run(activation, lr, dropout1, dropout2, 
             filters1, filters2, filters3, filters4,
             epochs, batch_size, ts_lenght,
             ):
    #X, y = random_dataset(m1=m1, m2=m2, n_steps=ts_lenght, batch_size=batch_size, channels=3)
    #X_test, X_train, y_test, y_train = split_dataset(X, y)
    file_name = 'training-data-for-cnn-classification/'
    args = {
        'file_name': file_name,
        'file_signal': 'signal_pcrit0_1s_10000_snr8_mtot33-60_noth.hdf5',
        'file_glitch': 'glitches_snr10_1s_10000.hdf5',
        'file_noise':  'noise_pcrit0_1s_10000.hdf5'
    }

    X_test, y_test, X_train, y_train, num_detectors, num_classes, input_shape, LABELS = split(**args)
    
    X_test = X_test.reshape(X_test.shape[0], input_shape)
    X_test = tf.expand_dims(X_test, axis=2) #add channel 
    X_train = tf.expand_dims(X_train, axis=2) #add channel

    y_train = utils.to_categorical(y_train, num_classes) #one hot encoder
    y_test = utils.to_categorical(y_test, num_classes) #one hot encoder


    model = create_model(activation=activation, lr=0.001,
                        dropout1=dropout1, dropout2=dropout2, filters1=filters1, filters2=filters2, 
                        filters3=filters3, filters4=filters4, time_steps=ts_lenght, num_classes=3)
    

    stats = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=epochs, batch_size=batch_size)
    
    val_loss = model.evaluate(X_test, y_test, verbose=1)
    
    y_pred_test = model.predict(X_test)


    max_y_pred_test = np.argmax(y_pred_test, axis=1)
    max_y_test = np.argmax(y_test, axis=1)

    show_confusion_matrix(max_y_test, max_y_pred_test)


    return model, val_loss, stats

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-act", "--activation", type=str, default='tanh', help="Activation")
    ap.add_argument("-lr", "--lr", type=float, default=0.0001, help="Learning Rate")
    ap.add_argument("-reg", "--reg", type=int, default=0, help="Regularizaction")
    ap.add_argument("-dropout1", "--dropout1", type=float, default=0.0621, help="Dropout 1")
    ap.add_argument("-dropout2", "--dropout2", type=float, default=0.007, help="Dropout 2")
    ap.add_argument("-filters1", "--filters1", type=int, default=97, help="Filters")
    ap.add_argument("-filters2", "--filters2", type=int, default=39, help="Filters")
    ap.add_argument("-filters3", "--filters3", type=int, default=20, help="Filters")
    ap.add_argument("-filters4", "--filters4", type=int, default=11, help="Filters")
    ap.add_argument("-ts", "--ts_lenght", type=bool, default=2048, help="Time series lenght")
    ap.add_argument("-epochs", "--num_epoch", type=int, default=166, help="Epochs")
    ap.add_argument("-bs", "--batch_size", type=int, default=162, help="Batch size")

    
    args = vars(ap.parse_args())

    params = {
        'activation': args['activation'],
        'lr' : args['lr'], 
        'epochs': args['num_epoch'],
        'ts_lenght': args['ts_lenght'],
        'dropout1': args['dropout1'],
        'dropout2': args['dropout2'],
        'filters1': args['filters1'], 
        'filters2': args['filters2'],
        'filters3': args['filters3'],
        'filters4': args['filters4'],
        'batch_size': args['batch_size'],
    }
    
    with mlflow.start_run():

        model, val_loss, history = model_run(**params)
        for key, value in params.items():
            mlflow.log_param(key, value)
        
        for step, (macc, mvacc, mloss, mvloss) in enumerate(zip(
                                                    history.history['accuracy'], history.history['val_accuracy'],
                                                    history.history['loss'], history.history['val_loss']
                                                )):
            metrics = {'accuracy': float(macc), 'val_accuracy': float(mvacc), 'loss': float(mloss), 'val_loss': float(mloss)}
            mlflow.log_metrics(metrics, step=step)


            mlflow.keras.log_model(model, "class_model")


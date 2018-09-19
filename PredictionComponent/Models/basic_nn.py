'''
This contains the functions to build a basic LSTM network
for time series data
'''
import tensorflow as tf
from keras import Sequential
from keras.layers import Dense
from keras.layers import Dropout

def get_trained_basic_nn_model(train_x, train_y, num_epochs):
    '''
    Returns a trained basic nn model
    '''
    model = get_model(train_x)
    train_model(train_x, train_y, num_epochs)
    return model

def get_model(train_x):
    '''
    Builds and returns a basic ANN.
    '''
    model = Sequential()
    model.add(Dense(16, activation=tf.nn.relu, input_shape=(len(train_x.columns),)))
    model.add(Dense(16, activation=tf.nn.relu))
    model.add(Dense(16, activation=tf.nn.relu))
    model.add(Dense(16, activation=tf.nn.relu))
    model.add(Dropout(0.4))
    model.add(Dense(4, activation=tf.nn.softmax))

    model.compile(
        optimizer=tf.train.AdamOptimizer(),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def train_model(model, train_x, train_y, num_epochs=5):
    '''
    Trains the basic nn model
    '''
    model.fit(train_x, train_y, epochs=num_epochs)

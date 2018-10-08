'''
This contains functions for a basic LSTM network.
'''
import tensorflow as tf
import pandas as pd
import numpy as np

from keras import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import Dropout

def get_trained_lstm_model(train_x, train_y, timestep, num_epochs):
    '''
    Returns a trained lstm model
    '''
    model = get_model(train_x, timestep)
    train_model(model, timestep, train_x, train_y, num_epochs)
    return model

def encode_time_series_training_data(data, timestep):
    '''
    Encodes the data into a time series format where time steps
    is used to shift the data.
    '''
    original = pd.DataFrame(data)

    columns = [original.shift(i).reset_index() for i in range(1, timestep+1)]
    original = original.reset_index()
    columns.insert(0, original)

    encoded_data = pd.concat(columns, axis=1)
    encoded_data.dropna(inplace=True)
    encoded_data.drop('index', inplace=True, axis=1)

    return encoded_data

def encode_data(train_x, train_y, timestep):
    '''
    Encodes the data into a time series format.
    '''
    train_x = encode_time_series_training_data(train_x, timestep)
    train_x = train_x.values
    train_x = np.reshape(train_x, (-1, timestep+1, 6))
    train_y = train_y.iloc[timestep:]

    return [train_x, train_y]

def get_model(train_x, timestep):
    '''
    Builds the LSTM model
    '''
    model = Sequential()
    model.add(LSTM(32, input_shape=(timestep+1, len(train_x.columns))))
    model.add(Dense(16, activation=tf.nn.relu))
    model.add(Dense(16, activation=tf.nn.relu))
    model.add(Dense(16, activation=tf.nn.relu))
    model.add(Dense(16, activation=tf.nn.relu))
    model.add(Dropout(0.4))
    model.add(Dense(2, activation=tf.nn.softmax))

    model.compile(
        optimizer=tf.train.AdamOptimizer(),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def train_model(model, timestep, train_x, train_y, num_epochs):
    '''
    Encodes the data and trains the model
    '''
    train_x, train_y = encode_data(train_x, train_y, timestep)
    model.fit(train_x, train_y, epochs=num_epochs)

def get_predictions(model, test_x):
    '''
    Returns the prediction and the encoded test data.
    '''
    predictions = list(map(np.argmax, model.predict(test_x)))
    return predictions

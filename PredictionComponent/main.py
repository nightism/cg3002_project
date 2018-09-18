from DummyData import run_walk
import tensorflow as tf
#from DataParsing import data_parser 
from sklearn.model_selection import train_test_split 
#from DataParsing.data_parser import series_to_supervised 
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Recurrent
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
from sklearn.metrics import accuracy_score
import numpy as np
import pandas as pd
import os
from keras.layers import GRU
from keras.models import model_from_json

def process_data_for_lstm2(data, lag=1):
    df = pd.DataFrame(data)
    columns = [df.shift(i).reset_index() for i in range(1, lag+1)]
    columns.insert(0, df)
    df = pd.concat(columns, axis=1)
    df.dropna(inplace=True)
    df.drop('index',inplace=True,axis=1)
    
    return df

def process_data_for_lstm(data, n_in=1, dropnan=True):
    shifted_data = data
    for i in range(1, n_in+1):
        shift_data = pd.DataFrame(data.shift(i)).dropna().reset_index().drop('index', inplace=True, axis=1)
        shift_data.columns = list(map(lambda col_name : col_name + '(t' + str(i-n_in) + ')', shift_data.columns))
        shifted_data = pd.concat([shifted_data, shift_data], axis=0)

    pass

def get_test_data():
    training_data, test_data = run_walk.load_data()

    test_x = test_data.drop('Target Class', axis=1)
    test_y = test_data['Target Class']

    return [test_x, test_y]

def evaluate_model(model, test_x, test_y):
    predictions = list(map(lambda row: np.argmax(row), model.predict(test_x)))
    print(accuracy_score(test_y, predictions))

def load_model(filename):
    json_file = open(os.path.join(os.path.dirname(__file__), filename + '.json'), 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(os.path.join(os.path.dirname(__file__), filename + '.h5'))

    return loaded_model

def train_lstm_model():
    training_data, test_data = run_walk.load_data()

    training_x = training_data.drop('Target Class', axis=1)
    training_y = training_data['Target Class']
    test_x = test_data.drop('Target Class', axis=1)
    test_y = test_data['Target Class']

    TIME_STEP = 3
    training_x = process_data_for_lstm2(training_x, TIME_STEP)
    test_x = process_data_for_lstm2(training_x, TIME_STEP)
    training_x = training_x.values
    training_x = np.reshape(training_x, (-1,TIME_STEP+1,6))
    training_y = training_y.iloc[3:]

    #print(training_x.head())
    #print(len(training_x.loc[0]))
    model = Sequential()
    model.add(LSTM(32, input_shape=(TIME_STEP+1,6)))
    model.add(Dense(16, activation=tf.nn.relu))
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


    model.fit(training_x, training_y, epochs=5)
    test_x = np.reshape(training_x, (-1, 6))
   # evaluate_model(model,test_x, test_y)

    return model

def train_model():
    training_data, test_data = run_walk.load_data()

    training_x = training_data.drop('Target Class', axis=1)
    training_y = training_data['Target Class']
    test_x = test_data.drop('Target Class', axis=1)
    test_y = test_data['Target Class']

    print(training_x.head())
    print(len(training_x.loc[0]))
    model = Sequential()
    model.add(Dense(16, activation=tf.nn.relu, input_shape=(len(training_x.columns),)))
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

    model.fit(training_x, training_y, epochs=5)
    evaluate_model(model,test_x, test_y)

    return model
    
def save_model(file_name, model): 
    model_json = model.to_json()
    with open(file_name + '.json', "w") as json_file:
        json_file.write(model_json)
    model.save_weights(file_name + '.h5')

def load_cycle():
    model = load_model('model1')
    test_x, test_y = get_test_data()
    evaluate_model(model, test_x, test_y)

def evaluate_lstm_model():
    model = load_model('model')
    test_x, test_y = get_test_data()
    TIME_STEP = 3
    test_x = process_data_for_lstm2(test_x, TIME_STEP)
    test_x = test_x.values
    test_x = np.reshape(test_x, (-1,TIME_STEP+1,6))
    test_y = test_y.iloc[TIME_STEP:]
    print(test_x.shape)
    print(test_y.shape)
    evaluate_model(model,test_x, test_y)    

def train_cycle():
    model = train_lstm_model()
    save_model('model1',model)

if __name__ == "__main__":
    evaluate_lstm_model()
    #model = train_lstm_model()
    #save_model('model', model)
    """     training_data, test_data = run_walk.load_data()

    training_x = training_data.drop('Target Class', axis=1)
    training_y = training_data['Target Class']
    test_x = test_data.drop('Target Class', axis=1)
    test_y = test_data['Target Class']
    print(training_x.head())
    print(process_data_for_lstm2(training_x, 3).head()) 
    """
    pass


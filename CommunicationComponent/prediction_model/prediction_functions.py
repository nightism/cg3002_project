import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.preprocessing import OneHotEncoder
import keras
import pickle

import os 

SEQUENCE_LENGTH = 8
NUM_FEATURES = 12
NUM_CLASS = 6

def save_model(model, filename):
    pickle.dump(model, open(filename, 'wb'))

def load_model(filename):
    loaded_model = pickle.load(open(filename, 'rb'))
    return loaded_model

def normalize_data(data):
    count = 0
    for col in data.columns:
        if (count < 6):
            data[col] = data[col] / (2 * 9.81)
        elif (count < 12):
            data[col] = data[col] / 250
        else:
            break
        count = count + 1
    return data

def one_hot_encode_labels(labels, num_class):
    encoded_labels = keras.utils.np_utils.to_categorical(labels, num_class)
    return encoded_labels


def multiply_sequences(raw_data, sequence_length, num_features):
    '''
    Create more batches to train with by offsetting sequences
    '''
    sensor_result = []
    target_result = []
    for i in range(sequence_length):
        data_to_append = raw_data.iloc[i:]
        (rows, cols) = data_to_append.shape
        excess_rows = rows % sequence_length
        data_to_append = data_to_append.iloc[0:rows-excess_rows]

        target_data = data_to_append['target'].iloc[::sequence_length]
        sensor_data = data_to_append.drop(['target'], axis=1)
        
        sensor_data = pd.DataFrame(np.reshape(sensor_data.values, (-1, sequence_length * num_features)))
        
        target_result.append(target_data)
        sensor_result.append(sensor_data)
    sensor_result = pd.concat(sensor_result, axis=0)
    sensor_result.reset_index(drop=True)
    target_result = pd.concat(target_result, axis=0)
    target_result.reset_index(drop=True)
    #print(sensor_result.shape)
    #print(target_result.shape)
    return [sensor_result, target_result]

def get_data(): 
    data_dir = './new_data/'
    data_file_names = os.listdir(data_dir)

    data_x = []
    data_y = []
    for file_name in data_file_names:
        print('reading ' + file_name)
        full_file_name = data_dir + file_name
        data = pd.read_csv(full_file_name)
        [curr_sensor, curr_target] = multiply_sequences(data, SEQUENCE_LENGTH, NUM_FEATURES)
        data_x.append(curr_sensor)
        data_y.append(curr_target)
    data_x = pd.concat(data_x, axis=0)
    data_x.reset_index(drop=True)
    data_y = pd.concat(data_y, axis=0)
    data_y.reset_index(drop=True)
    train_x, test_x, train_y, test_y = train_test_split(data_x, data_y, test_size=0.33, random_state=42, shuffle=True)
    
    print(train_x.shape)
    print(test_x.shape)
    print(train_y.shape)
    print(test_y.shape)
    
    train_y = one_hot_encode_labels(train_y, 6)
    test_y = one_hot_encode_labels(test_y, 6)  

    return [train_x, test_x, train_y, test_y]

def get_trained_model(train_x, train_y):
    mlp = MLPClassifier(hidden_layer_sizes=(128,64,32,16))
    mlp.fit(train_x,train_y)
    return mlp

def train_and_save_model(model_name):
    [train_x, test_x, train_y, test_y] = get_data()
    model = get_trained_model(train_x, train_y)
    save_model(model, model_name)


#mlp = load_model(model_name)
#predictions = mlp.predict(test_x)




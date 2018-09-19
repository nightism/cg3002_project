'''
This module performs saves and loads models.
'''
import os
from keras.models import model_from_json

def save_model(model, filename):
    '''
    Saves the model in filename.json and the model weights in filename.h5
    '''
    model_json = model.to_json()
    with open(os.path.join(os.path.dirname(__file__), filename + '.json'), "w") as json_file:
        json_file.write(model_json)
    model.save_weights(os.path.join(os.path.dirname(__file__), filename + '.h5'))

def load_model(filename):
    '''
    Loads the file from filename.json
    '''
    # Load model
    json_file = open(os.path.join(os.path.dirname(__file__), filename + '.json'), 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    # Load weights
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(os.path.join(os.path.dirname(__file__), filename + '.h5'))

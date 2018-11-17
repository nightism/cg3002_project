import pickle
import sklearn
from CommunicationComponent.prediction_model import prediction_functions
import numpy as np
import pandas as pd

def get_model():
    model_name = "model_final_abs"
    return prediction_functions.load_model(model_name)

def get_predictions(model, data):
    NUM_FEATURES = 12
    NUM_DATA = 16
    data = prediction_functions.normalize_data(pd.DataFrame(data))
    processed_data = np.reshape(data.values, (1, NUM_FEATURES * NUM_DATA))
    prediction = model.predict(processed_data)
    return np.argmax(prediction)

if __name__ == "__main__":
    #[train_x, test_x, train_y, test_y] = prediction_functions.get_data()
    model = get_model()
    data = [
        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],

        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],

        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],

        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3],
        [3,3,3,3,3,3,3,3,3,3,3,3]
    ]
    print(get_predictions(model, data))
    #temp = train_x.iloc[69].values
    #temp = np.reshape(temp, (8, 12))
    #prediction = get_predictions(model, temp)
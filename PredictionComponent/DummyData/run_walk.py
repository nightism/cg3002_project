import numpy as np 
import pandas as pd
from sklearn.model_selection import train_test_split 
import os

def load_data(test_ratio=0.2):
    file_name  = os.path.join(os.path.dirname(__file__), 'run_walk_data.csv')
    data = pd.read_csv(file_name)
    
    # clean up data.
    data['Target Class'] = data.apply(lambda row: row['wrist'] + row['activity'] * 2, axis=1)
    data.drop(['username', 'date', 'wrist', 'activity'], axis=1, inplace=True)
    data.drop('time', axis=1, inplace=True)
    
    training_data, test_data = train_test_split(data, test_size=test_ratio, shuffle=False)

    return [training_data, test_data]

def get_class_labels():
    return ['~W & ~A', 'W & ~A', '~W & A', 'W & A']

if __name__ == "__main__":
    data = load_data()
    print(data.head())

    print(get_class_labels())

from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib

from realdatareader import import_data as reader
from ann import export_ann_model
from ann import ann_model_validation

import time


def train():
    x, y = reader("data.csv")
    ann = export_ann_model.export_ann(x, y)
    joblib.dump(ann, 'ann_model.pkl')


def predict(x):

    ann = joblib.load('ann_model.pkl')

    print("Your dance move is: ")
    print(ann.predict(x))
    print("\n")


if __name__ == '__main__':
    train(1)

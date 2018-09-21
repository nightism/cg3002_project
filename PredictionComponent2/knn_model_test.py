import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.externals import joblib

import import_data as reader


def main():

    x, y = reader.import_data(label_end=5, object_start=4, object_end=5, seg_end=48, seg_start=25)

    knn = joblib.load('knn_model.pkl')

    cm = confusion_matrix(knn.predict(x), y)

    print("Accuracy: ")
    print(knn.score(x, y))
    print("Confusion Metrix: ")
    print(cm)


if __name__ == '__main__':
    main()

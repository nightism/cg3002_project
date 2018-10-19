from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib

import import_data as reader


def main():

    x, y = reader.import_data(label_end=5, object_end=9, seg_end=48, seg_start=25)

    clf = joblib.load('svm_model.pkl')

    cm = confusion_matrix(clf.predict(x), y)

    print("Accuracy: ")
    print(clf.score(x, y))
    print("Confusion Metrix: ")
    print(cm)


if __name__ == '__main__':
    main()

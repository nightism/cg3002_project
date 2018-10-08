from sklearn.externals import joblib
from sklearn import svm

import import_data as reader


def main():

    x, y = reader.import_data(label_end=5, object_end=9, seg_end=25)

    clf = svm.SVC().fit(x, y)
    joblib.dump(clf, 'svm_model.pkl')


if __name__ == '__main__':
    main()

import os
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib

from datareader import import_data as reader
from knn import export_knn_model
from knn import knn_model_validation


def main():

    x_train, y_train = reader.import_data(label_start=1, object_start=1, seg_start=1, label_end=6, object_end=9, seg_end=25)
    x_test, y_test = reader.import_data(label_start=1, object_start=1, seg_start=25, label_end=6, object_end=9, seg_end=41)

    # export_knn_model.export_knn(x_train, y_train)
    knn = export_knn_model.export_knn(x_train, y_train)
    joblib.dump(knn, 'knn_model.pkl')
    knn_model_validation.validate_knn(x_train, y_train)

    # file_name = './knn/knn_model.pkl'
    # file_name = os.path.join(os.path.dirname(__file__), file_name)
    # print(file_name)

    # knn = joblib.load(file_name)

    cm = confusion_matrix(knn.predict(x_test), y_test)

    print("Accuracy: ")
    print(knn.score(x_test, y_test))
    print("Confusion Metrix: ")
    print(cm)


if __name__ == '__main__':
    main()

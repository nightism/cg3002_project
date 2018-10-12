from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib

from datareader import import_data as reader
from ann import export_ann_model
from ann import ann_model_validation

import time


def main():

    x_train, y_train = reader.import_data(label_start=1, object_start=1, seg_start=1,
                                          label_end=11, object_end=9, seg_end=25)
    x_test, y_test = reader.import_data(label_start=1, object_start=1, seg_start=25,
                                        label_end=2, object_end=2, seg_end=27)

    ann = export_ann_model.export_ann(x_train, y_train)
    joblib.dump(ann, 'knn_model.pkl')
    # ann_model_validation.validate_ann(x_train, y_train)

    start_time = time.time()
    cm = confusion_matrix(ann.predict(x_test), y_test)
    print(time.time() - start_time)

    print("Accuracy: ")
    print(ann.score(x_test, y_test))
    print("Confusion Metrix: ")
    print(cm)


if __name__ == '__main__':
    main()

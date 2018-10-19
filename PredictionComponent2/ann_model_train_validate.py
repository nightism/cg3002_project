from sklearn.externals import joblib

from realdatareader import import_data as reader
from ann import export_ann_model
from ann import ann_model_validation
from knn import knn_model_validation


def main():

    x, y = reader.import_data()

    knn_model_validation.validate_knn(x, y)
    # ann_model_validation.validate_ann(x, y)
    #
    # print("Readey to export ANN model ... ...")
    # ann = export_ann_model.export_ann(x, y)
    # joblib.dump(ann, 'ann_model.pkl')


if __name__ == '__main__':
    main()

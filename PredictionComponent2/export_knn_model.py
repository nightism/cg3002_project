from sklearn.externals import joblib
from sklearn.neighbors import KNeighborsClassifier

import import_data as reader


def main():

    x, y = reader.import_data(label_end=5, object_end=9, seg_end=25)

    knn = KNeighborsClassifier(n_neighbors=5).fit(x, y)
    joblib.dump(knn, 'knn_model.pkl')


if __name__ == '__main__':
    main()

from sklearn.externals import joblib
from sklearn.neighbors import KNeighborsClassifier


def export_knn(x, y):

    knn = get_untrained_model().fit(x, y)
    joblib.dump(knn, 'knn_model.pkl')
    return knn


def get_untrained_model():
    return KNeighborsClassifier(n_neighbors=5)

from sklearn.externals import joblib
from sklearn.neighbors import KNeighborsClassifier


def export_knn(x, y):

    knn = KNeighborsClassifier(n_neighbors=5).fit(x, y)
    joblib.dump(knn, 'knn_model.pkl')
    return knn

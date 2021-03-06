from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier


def export_ann(x, y):

    ann = get_untrained_model().fit(x, y)
    joblib.dump(ann, 'ann_model.pkl')
    assert isinstance(ann, MLPClassifier)
    return ann


def get_untrained_model():
    ann = MLPClassifier(solver='lbfgs', hidden_layer_sizes=(100, 100), random_state=1)
    return ann

import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold
from sklearn.neural_network import MLPClassifier


def validate_ann(x, y):

    # K Fold
    kfold = KFold(n_splits=10, shuffle=True, random_state=50)

    # using k fold validation
    index = 0
    with open('./analysis.txt', 'w') as outfile:
        outfile.close()

    for train, test in kfold.split(x):
        ann = MLPClassifier(solver='lbfgs',
                            hidden_layer_sizes=(100, 100), random_state=1).fit(x[train], y[train])
        prediction = ann.predict(x[test])
        accuracy = accuracy_score(prediction, y[test])
        cm = confusion_matrix(prediction, y[test])

        with open('./analysis.txt', 'a') as outfile:
            outfile.write("\n\nIn Fold %i, the classification accuracy is %f,\n" %(index, accuracy))
            print("In Fold %i, the classification accuracy is %f,\n" %(index, accuracy))
            outfile.write("and the confusion matrix is:\n")
            print("and the confusion matrix is:\n")
            outfile.close()
        with open('./analysis.txt', 'ab') as outfile:
            np.savetxt(outfile, cm, fmt="%d")
            print(cm)
            print("\n")
            outfile.close()
        index += 1
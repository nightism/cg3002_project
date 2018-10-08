import numpy as np
# import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
# from sklearn import preprocessing
from sklearn import svm

import import_data as reader


def main():

    x, y = reader.import_data(label_end=10, object_end=9, seg_end=25)

    # train_test_split
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=26)

    # K Fold
    kfold = KFold(n_splits=10, shuffle=True, random_state=26)

    # using train test split method
    clf = svm.SVC()
    clf.fit(x_train, y_train)
    cm = confusion_matrix(clf.predict(x_test), y_test)

    print("Accuracy: ")
    print(clf.score(x_test, y_test))
    print("Confusion Metrix: ")
    print(cm)

    # using k fold validation
    index = 0
    with open('./analysis.txt', 'w') as outfile:
        outfile.close()

    for train, test in kfold.split(x):
        clf = svm.SVC(decision_function_shape='ovo').fit(x[train], y[train])
        prediction = clf.predict(x[test])
        accuracy = accuracy_score(prediction, y[test])
        cm = confusion_matrix(prediction, y[test])

        with open('./analysis.txt', 'a') as outfile:
            outfile.write("\n\nIn Fold %i, the classification accuracy is %f,\n" %(index, accuracy))
            print("In Fold %i, the classification accuracy is %f,\n" %(index, accuracy))
            outfile.write("and the confusion matrix is:\n")
            print("and the confusion matrix is:\n")
            outfile.close()
        with open('./analysis.txt', 'ab') as outfile:
            np.savetxt(outfile, cm, fmt = "%d")
            print(cm)
            print("\n")
            outfile.close()
        index += 1


if __name__ == '__main__':
    main()

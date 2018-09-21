import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
# from sklearn import preprocessing
from sklearn import svm

import import_data as reader


def main():

    x, y = reader.import_data(label_end=5, object_end=9, seg_end=25)

    # K Fold
    kfold = KFold(n_splits=10, shuffle=True, random_state=50)

    # using k fold validation
    index = 0
    with open('./analysis.txt', 'w') as outfile:
        outfile.close()

    for train, test in kfold.split(x):
        knn = KNeighborsClassifier(n_neighbors=5).fit(x[train], y[train])
        prediction = knn.predict(x[test])
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
            outfile.close()
        index += 1


if __name__ == '__main__':
    main()

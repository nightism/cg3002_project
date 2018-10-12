import numpy as np
import pandas as pd
import os
# data from http://archive.ics.uci.edu/ml/datasets/Daily+and+Sports+Activities#


def import_data(label, file_name):

    x = None
    y = None

    file_name = os.path.join(os.path.dirname(__file__), file_name)
    x = pd.read_csv(file_name, header=None).values
    x = normalize(x)

    y = np.empty(x.shape[0])
    y.fill(label)

    return x, y


def normalize(data):
    df = pd.DataFrame(data, columns=['x1', 'y1', 'z1',
                                     'x2', 'y2', 'z2',
                                     'x3', 'y3', 'z3',
                                     'x4', 'y4', 'z4',
                                     'x5', 'y5', 'z5',
                                     'g1', 'g2', 'g3'])

    colnames = list(df.columns)

    for i in colnames[0:15]:
        df[i] = df[i] / 2

    for i in colnames[15:18]:
        df[i] = df[i] / 250

    return df.values


if __name__ == '__main__':
    normalize([[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100],
               [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100]])


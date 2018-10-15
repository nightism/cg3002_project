import pandas as pd
import os
# data from http://archive.ics.uci.edu/ml/datasets/Daily+and+Sports+Activities#


def import_data(file_name):

    x = None
    y = None

    file_name = os.path.join(os.path.dirname(__file__), file_name)
    x = pd.read_csv(file_name, header=None).values
    x = normalize(x)

    y = x[, 72:]
    x = x[, 0:72]

    return x, y


def normalize(data):
    df = pd.DataFrame(data)

    colnames = list(df.columns)

    for i in colnames[0:15]:
        df[i] = df[i] / 2

    for i in colnames[15:18]:
        df[i] = df[i] / 250

    for i in colnames[18:33]:
        df[i] = df[i] / 2

    for i in colnames[33:36]:
        df[i] = df[i] / 250

    for i in colnames[36:51]:
        df[i] = df[i] / 2

    for i in colnames[51:54]:
        df[i] = df[i] / 250

    for i in colnames[54:69]:
        df[i] = df[i] / 2

    for i in colnames[69:72]:
        df[i] = df[i] / 250

    return df.values


def segment(data):
    return data


if __name__ == '__main__':
    print(normalize([[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100,
                      1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100,
                      1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100,
                      1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0],
                    [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100,
                     1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100,
                     1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100,
                     1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0]]))


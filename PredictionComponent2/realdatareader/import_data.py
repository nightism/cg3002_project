import numpy as np
import pandas as pd
import os
# data from http://archive.ics.uci.edu/ml/datasets/Daily+and+Sports+Activities#


def import_data():
    # x_1, y_1 = process_data('./realdatareader/realdata/sean1.csv')
    # x_2 = pd.read_csv('./realdatareader/realdata/emil2.csv')
    x_3, y_3 = process_data('./realdatareader/realdata/emil3.csv')
    x_4, y_4 = process_data('./realdatareader/realdata/emil4.csv')

    x = x_3 + x_4
    y = y_3 + y_4
    y = sum(y, [])

    return np.asarray(x), np.asarray(y)


def process_data(filename):

    x = pd.read_csv(filename)

    x = np.array(normalize(segment(x)))

    # print(x)

    y = x[:, 72:]
    x = x[:, 0:72]

    return x.tolist(), y.tolist()


def normalize(data):
    df = pd.DataFrame(data)

    colnames = list(df.columns)

    for i in colnames[0:15]:
        df[i] = df[i] / 2 / 9.81

    for i in colnames[15:18]:
        df[i] = df[i] / 250

    for i in colnames[18:33]:
        df[i] = df[i] / 2 / 9.81

    for i in colnames[33:36]:
        df[i] = df[i] / 250

    for i in colnames[36:51]:
        df[i] = df[i] / 2 / 9.81

    for i in colnames[51:54]:
        df[i] = df[i] / 250

    for i in colnames[54:69]:
        df[i] = df[i] / 2 / 9.81

    for i in colnames[69:72]:
        df[i] = df[i] / 250

    return df.values


def segment(data):
    data = np.array(data)

    for i in range(0, len(data) - 3):
        this_x_one = data[i, 0:18]
        this_x_two = data[i+1, 0:18]
        this_x_three = data[i+2, 0:18]
        this_x_four = data[i+3, 0:18]

        this_y_one = data[i, 18]
        this_y_two = data[i+1, 18]
        this_y_three = data[i+2, 18]
        this_y_four = data[i+3, 18]

        if this_y_one == this_y_two and this_y_two == this_y_three:
            this_y = this_y_one
        elif this_y_four == this_y_two and this_y_two == this_y_three:
            this_y = this_y_four
        else:
            continue

        this_row = np.concatenate((this_x_one, this_x_two), axis=None)
        this_row = np.concatenate((this_row, this_x_three), axis=None)
        this_row = np.concatenate((this_row, this_x_four), axis=None)
        this_row = np.concatenate((this_row, this_y), axis=None)

        if i == 0:
            result = this_row
        else:
            # result = np.column_stack((result, this_row), axis=0)
            result = np.vstack((result, this_row))

    return result.tolist()


if __name__ == '__main__':
    import_data()
    # print(np.array(normalize(segment([[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0],
    #                  [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0],
    #                  [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0],
    #                  [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0],
    #                  [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0],
    #                  [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0],
    #                  [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0],
    #                  [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 100, 200, 100, 0]]))))



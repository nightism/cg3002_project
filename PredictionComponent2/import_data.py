import numpy as np
import pandas as pd

# data from http://archive.ics.uci.edu/ml/datasets/Daily+and+Sports+Activities#


def import_data():

    x = None
    y = None

    for i in range(1, 20):  # from 01 to 19
        folder_name = str('{num:02d}'.format(num=i))
        for j in range(1, 2):  # from 1 to 9
            subfolder_name = str(j)
            for k in range(1, 8):  # from 01 to 60
                file_num = str('{num:02d}'.format(num=k))
                this_x = pd.read_csv("./data/a" + folder_name + "/p" + subfolder_name + "/s" + file_num + ".txt").values
                this_y = np.empty(len(this_x))
                this_y.fill(i)

                if x is None:
                    x = this_x
                    y = this_y
                else:
                    x = np.concatenate((x, this_x), axis=0)
                    y = np.concatenate((y, this_y), axis=0)
    return x, y


if __name__ == '__main__':
    x, y = import_data()
    print(len(x))
    print(len(y))

import numpy as np
import pandas as pd

import preprocess_data as pre

# data from http://archive.ics.uci.edu/ml/datasets/Daily+and+Sports+Activities#


def import_data(label_end=4, object_end=9, seg_end=25, label_start=1, object_start=1, seg_start=1):

    x = None
    y = None

    for i in range(label_start, label_end):  # from 01 to 20, labels
        folder_name = str('{num:02d}'.format(num=i))
        this_label_x = []

        for j in range(object_start, object_end):  # from 1 to 9, objects
            subfolder_name = str(j)
            for k in range(seg_start, seg_end):  # from 01 to 61, segments
                file_num = str('{num:02d}'.format(num=k))
                this_x = pd.read_csv("./data/a" + folder_name + "/p" + subfolder_name + "/s" + file_num + ".txt", header = None).values
                # print(this_x.shape[0])
                # print(this_x.shape[1])
                # print(this_x)
                # this_x = this_x.reshape(1, 125 * 45)
                this_label_x = np.append(this_label_x, this_x)

        this_label_x = this_label_x.reshape((object_end - object_start) * (seg_end - seg_start) * 125, 45)
        this_label_x = pre.preprocess_data(this_label_x)

        this_y = np.empty(this_label_x.shape[0])
        this_y.fill(i)

        if x is None:
            x = this_label_x
            y = this_y
        else:
            x = np.concatenate((x, this_label_x), axis=0)
            y = np.concatenate((y, this_y), axis=0)

    return x, y


if __name__ == '__main__':
    x, y = import_data(label_end=4, object_end=9, seg_end=25)
    print(len(x))
    print(len(y))

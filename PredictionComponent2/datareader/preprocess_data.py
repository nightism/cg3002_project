import numpy as np
import math
# from sklearn import preprocessing
# import import_data as reader


def segmentation(data):

    num_of_row = data.shape[0]
    num_of_col = data.shape[1]

    # print(num_of_row)

    window_size = 250
    half_window_size = int(math.floor(window_size / 2))
    num_of_windows = int(math.floor(num_of_row / half_window_size - 1))

    # print(num_of_windows)

    segmented_data = []

    for i in range(0, num_of_windows):
        this_segment = data[i * half_window_size: i * half_window_size + 250]
        segmented_data = np.append(segmented_data, this_segment)

    segmented_data = segmented_data.reshape(num_of_windows, num_of_col * window_size)
    # print(segmented_data)

    return segmented_data


def normalization(data, axis=1):
    # data = preprocessing.normalize(data, axis=axis)
    return data


def feature_extraction(data):
    # unit = 1125  # 45 * 25Hz
    # num_of_feature = 6
    #
    # num_of_row = data.shape[0]
    # num_of_col = data.shape[1]

    features = data

    # features = []
    #
    # for i in range(0, num_of_row):
    #     for j in range(0, num_of_col, unit):
    #         this_unit = data[i, j: j + unit]
    #         std = np.std(this_unit)
    #         mean = np.mean(this_unit)
    #         median = np.mean(this_unit)
    #         min = np.amin(this_unit)
    #         max = np.amax(this_unit)
    #         energy = np.sum(this_unit**2) / unit
    #         features = np.append(features, [std])
    #         features = np.append(features, [mean])
    #         features = np.append(features, [median])
    #         features = np.append(features, [min])
    #         features = np.append(features, [max])
    #         features = np.append(features, [energy])
    #
    # features = features.reshape(num_of_row, num_of_col / unit * num_of_feature)

    # print(features.shape[0])
    # print(features.shape[1])

    return features


def preprocess_data(data):
    return feature_extraction(normalization(segmentation(data)))


if __name__ == '__main__':
    # x, y = reader.import_data()
    # feature_extraction(normalization(segmentation(x)))
    print("This module cannot be used independently.")
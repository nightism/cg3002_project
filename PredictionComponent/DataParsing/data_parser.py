import numpy as np 
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def normalize_data(data, identifier, min_val=0, max_val=1):
    '''
    Normalize the data in the column with column name 'identifier' to values between
    0 and 1.
    '''
    data_scaler = MinMaxScaler(feature_range=(min_val,max_val))
    data_scaler = data_scaler.fit(pd.DataFrame(data[identifier]))
    data[identifier] = data_scaler.transform(pd.DataFrame(data[identifier]))

def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    '''
    Taken from https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/
    This function covnerts the time series data into data that can be used for supervised learning
    '''

    n_vars = 1 if type(data) is list else data.shape[1]
    df = pd.DataFrame()
    cols, names = list(), list()
	
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]

    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]

    # put it all together
    #pd.concat([df cols])
    #agg = df.concat([df pd.DataFrame(cols)], axis=1)
    #agg.columns = names
    #print(agg)
    # drop rows with NaN values
    #if dropnan:
	  #  agg.dropna(inplace=True)
	
    #return agg

if __name__ == "__main__":
    data = pd.DataFrame(data=np.array([[1,2],[3,4],[5,6]]), columns = ['test1', 'test2'])
    print(data.head())
    normalize_data(data, 'test1')
    print(data.head())

# -*- coding: utf-8 -*-
"""Stock Price Predication kaggle

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oEM81pT20-feH4qeHTH-lvSgbKyNH60h

```
Stock Market Prediction And Forecasting Using Stacked LSTM
```

1.Import : required library
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 

import pandas as pd
import io
import requests
import datetime

"""2. Read Dataset"""

df = pd.read_csv("NSE-TATAGLOBAL.csv")
df.head()

#shape of data
df.shape

"""3.Gathering information about the data"""

df.info()

df.describe()

df.dtypes

"""4.Data Cleaning"""

from numpy.lib.function_base import percentile
#Total percentage of data is missing

missing_values_count = df.isnull().sum()

total_cells = np.product(df.shape)

total_missing = missing_values_count.sum()

percentage_missing = (total_missing/total_cells)*100

print(percentage_missing)

NAN = [(c,df[c].isnull().mean()*100)for c in df]
NAN = pd.DataFrame(NAN,columns=['column_name','percentage'])
NAN

"""5.Data Visualization"""

sns.set(rc={'figure.figsize':(20,5)})
df['Open'].plot(linewidth = 1, color='blue')

df.columns

cols_plot = ['Open','High',"Low","Last","Close"]
axes = df[cols_plot].plot(alpha = 1, figsize=(20,30),subplots = True)

for ax in axes:
  ax.set_ylabel("Variation")
  ax.set_title("Variation of Attribute")

"""Sort the dataset on date time and filter “Date” and “Open” columns"""

df['Date']=pd.to_datetime(df.Date,format ="%Y-%m-%d")
df.index = df['Date']
df

del df['Date']

df.dtypes

"""6. 7 day rolling mean"""

df.rolling(7).mean().head(10)

df['Open'].plot(figsize=(20,8),alpha=1)
df.rolling(window=30).mean()['Close'].plot(alpha=1)

df['Close: 30 Day Mean'] = df['Close'].rolling(window=30).mean()
df[['Close','Close: 30 Day Mean']].plot(figsize=(20,8),alpha=1)

"""Optional specify a minimum numbe2of periods"""

df['Close'].expanding(min_periods=1).mean().plot(figsize=(20,8),alpha=1)

df2 = df.reset_index()['Open']
df2

plt.plot(df2)

"""**`6.LSTM are sensitive to the scale of the data. so we apply MinMax scaler`**"""

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0,1))
df2 = scaler.fit_transform(np.array(df2).reshape(-1,1))

print(df2)

"""7.splitting dataset into train and test split"""

train_size = int(len(df2)*0.75)
test_size = len(df2)-train_size

train_data, test_data = df2[0:train_size,:],df2[train_size:len(df2),:1]

train_size, test_size

train_data, test_data

"""8.convert an array of values into a dataset matrix"""

from matplotlib import numpy
def create_dataset(dataset, time_step=1):
  train_X, train_Y = [], []
  for i in range(len(dataset)-time_step-1):
    a = dataset[i:(i+time_step), 0]         ## i = 0, 0,1,2,3,4,5------99, 100
    train_X.append(a)
    train_Y.append(dataset[i+time_step,0])
  return numpy.array(train_X), numpy.array(train_Y)

"""9.reshape into X=t,t+1,t+2,t+3 and Y=t+4"""

import numpy
time_step = 100
X_train, y_train = create_dataset(train_data, time_step)

X_test, ytest=create_dataset(test_data, time_step)

print(X_train.shape), print(y_train.shape)

"""10. Reshape input to be [samples, time steps, features] which is required for LSTM"""

X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1],1)

"""11. Create the Stacked LSTM model"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM

model = Sequential()

model.add(LSTM(50, return_sequences=True, input_shape=(100,1)))

model.add(LSTM(50, return_sequences=True))

model.add(LSTM(50))

model.add(Dense(1))

model.compile(loss='mean_squared_error',optimizer='adam')

model.summary()

model.fit(X_train, y_train, validation_data=(X_test,ytest),epochs=100,batch_size=64, verbose=1)

import tensorflow as tf

"""12. Lets Do the prediction and check performance metrics"""

train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

train_predict = scaler.inverse_transform(train_predict)

test_predict = scaler.inverse_transform(test_predict)

"""13.Calculate RMSE performance metrics"""

import math
from sklearn.metrics import mean_squared_error
math.sqrt(mean_squared_error(y_train,train_predict))

"""14.Test data RMSE"""

math.sqrt(mean_squared_error(ytest,test_predict))

"""15.Shift Train prediction for plotting"""

look_back = 100
trainPredictplot = numpy.empty_like(df2)
trainPredictplot[:,:] = numpy.nan
trainPredictplot[len(train_predict)+(look_back*2)+1:len(df2)-1,:] = test_predict

"""16.Shift test predication for plotting """

testPredictplot = numpy.empty_like(df2)
testPredictplot[:,:] = numpy.nan
testPredictplot[len(train_predict)+(look_back*2)+1:len(df2)-1, :] = test_predict

"""17.Plot baseline and predications """

pred = scaler.inverse_transform(df2)
plt.plot(pred,color='blue')
plt.show()

plt.plot(trainPredictplot, color='red')
plt.show()
plt.plot(testPredictplot, color = 'green')
plt.show()

plt.plot(pred,color = 'blue')
plt.plot(trainPredictplot, color='red')
plt.plot(testPredictplot, color = 'green')
plt.show()

len(test_data)

x_input = test_data[341:].reshape(1,-1)
x_input.shape

"""18.Save the model"""

model.save("saved_model.h5")
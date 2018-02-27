from math import pi
from time import time
from poloniex import Poloniex
import pandas as pd
from bokeh.plotting import figure, output_file, show
import numpy as np
from sklearn import linear_model
from bokeh.models import HoverTool, BoxSelectTool
import matplotlib.pyplot as plt
import datetime as dt
from pandas_datareader import data
#change the number to move the left bound left and right if needed
numOfDaysToGet = 17000
numOfCandleSticksToPredict = 1
currencyToGet = 'USDT_BTC'
windowLength = 14

#api call with poloniex
api = Poloniex(timeout=None, jsonNums=float)

#change the number to move the right bound left and right if needed
NumOfDaysToMoveBackFromToday = time() - api.DAY*0

#period of candlesticks to recieve: 24, 4, 2, 0.5, 0.25, or  0.083
period = api.HOUR * 24

#api call
raw = api.returnChartData(currencyToGet, period=period, start=time() - api.DAY*numOfDaysToGet, end= NumOfDaysToMoveBackFromToday)

#load dataframe with infrom from api call
df = pd.DataFrame(raw)


#create date column and convert epoch time from api call to date
df['date'] = pd.to_datetime(df["date"], unit='s')
df['date']= df['date'].map(dt.datetime.toordinal)

#calculate hui hubel liquidty rates
df['liquidity'] = ((df['high'] - df['low']) / df['low']) / (df['volume'] / (df['weightedAverage'] * df['quoteVolume']))


#Calculates a relative strength index with an exponetial moving average as EMA better shows price movements - Tortise vs Heir example
close = df['close']
delta = close.diff()
delta = delta[1:]
up, down = delta.copy(), delta.copy()
up[up < 0] = 0
down[down > 0] = 0
roll_up1 = pd.stats.moments.ewma(up, windowLength)
roll_down1 = pd.stats.moments.ewma(down.abs(), windowLength)
RS1 = roll_up1 / roll_down1
df['rsi'] = 100.0 - (100.0 / (1.0 + RS1))


#drop outliers
df.dropna(inplace=True)

#reassign column layouts
df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'rsi', 'quoteVolume','liquidity' ,'weightedAverage']]



dependentYVariable = 'rsi'


dates = []
prices = []
dates = df['date'].values
prices = df[[dependentYVariable]].values

def show_plot(dates,prices):
	linear_mod = linear_model.LinearRegression()
	dates = np.reshape(dates,(len(dates),1)) # converting to matrix of n X 1
	prices = np.reshape(prices,(len(prices),1))
	linear_mod.fit(dates,prices) #fitting the data points in the model
	plt.scatter(dates,prices,color='black') #plotting the initial datapoints 
	plt.plot(dates,linear_mod.predict(dates),color='blue',linewidth=3) #plotting the line made by linear regression
	plt.show()
	return


def predict_price(dates,prices,x):
	linear_mod = linear_model.LinearRegression() #defining the linear regression model
	dates = np.reshape(dates,(len(dates),1)) # converting to matrix of n X 1
	prices = np.reshape(prices,(len(prices),1))
	linear_mod.fit(dates,prices) #fitting the data points in the model
	predicted_price =linear_mod.predict(x)
	rSquared = linear_mod.score(dates, prices)
	return predicted_price[0][0],linear_mod.coef_[0][0] ,linear_mod.intercept_[0], rSquared


predicted_price, coefficient, constant, rSquared = predict_price(dates,prices,dates[-1] + numOfCandleSticksToPredict)
print("Average " , dependentYVariable ,": ", df[[dependentYVariable]].mean())
print ("The predicted ", dependentYVariable ," for 4 candle sticks: " , str(predicted_price))
print("R^2: ", rSquared)


print(df.head())
show_plot(dates,prices)

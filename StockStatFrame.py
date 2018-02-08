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
from stockstats import StockDataFrame as Sdf



#change the number to move the left bound left and right if needed
numOfDaysToGet = 70
numOfCandleSticksToPredict = 1
currencyToGet = 'USDT_BTC'

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


#calculate hui hubel liquidty rates
df['liquidity'] = ((df['high'] - df['low']) / df['low']) / (df['volume'] / (df['weightedAverage'] * df['quoteVolume']))


#calculate RSI
stock_df = Sdf.retype(df)
df['rsi']=stock_df['rsi_14']
del df['close_-1_s']
del df['close_-1_d']
del df['rs_14']
del df['rsi_14']

#drop outliers
df.dropna(inplace=True)

columnsTitles = ['date', 'open', 'close', 'high', 'low', 'volume', 'rsi', 'quoteVolume', 'liquidity','weightedAverage']

#reassign column layouts
df.reindex(columns=columnsTitles)

print(df.tail())

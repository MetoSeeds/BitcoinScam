from math import pi
from time import time
from poloniex import Poloniex
import pandas as pd
from bokeh.plotting import figure, output_file, show
import numpy as np
from sklearn.linear_model import LinearRegression
from bokeh.models import HoverTool, BoxSelectTool
import matplotlib.pyplot as plt
from pandas_datareader import data

#change the number to move the left bound left and right if needed
numOfDaysToGet = 30
windowLength = 14

currencyToGet = 'USDT_BTC'
#api call with poloniex
api = Poloniex(timeout=None, jsonNums=float)

#change the number to move the right bound left and right if needed
NumOfDaysToMoveBackFromToday = time() - api.DAY*0

#period of candlesticks to recieve: 24, 4, 2, 0.5, 0.25, or  0.083
period = api.HOUR * 4

#api call
raw = api.returnChartData(currencyToGet, period=period, start=time() - api.DAY*numOfDaysToGet, end= NumOfDaysToMoveBackFromToday)

#load dataframe with infrom from api call
df = pd.DataFrame(raw)

#create date column and convert epoch time from api call to date
df['date'] = pd.to_datetime(df["date"], unit='s')

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

#print out last 15 results and correlations 
print(df.corr())
print(df.tail())


#tools listed on the graph
tools = "pan,wheel_zoom,box_zoom,reset,save, hover"

#outputs to a html file 
output_file(currencyToGet + ".html", title= currencyToGet + "-Poloniex")

#generate figure/graph 
p = figure(x_axis_type="datetime", tools=tools, plot_width=1900, title=currencyToGet)
p.xaxis.major_label_orientation = pi / 4
p.grid.grid_line_alpha = 0.7

#determines if the candle stick is red or green 
inc = df.close > df.open
dec = df.open > df.close

#creates shadows 
p.segment(df.date, df.high, df.date, df.low, color="black")

#width of candle sticks
w = (period * 1000) - 5000

#create green or red candle sticks 
p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="green", line_color="black")
p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="red", line_color="black")


#opens in browser
show(p)

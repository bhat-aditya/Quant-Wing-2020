#implementing backtest strategy on Apple Stock with a base of 1500 USD over the course of approx. 700 days

import pandas as pd
import numpy as np
import yfinance as yf
from ta.trend import ADXIndicator
import matplotlib.pyplot as plt

def plot_graph(data, ylabel, xlabel):
    plt.figure(figsize = (10,7))
    plt.grid()
    plt.plot(data)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

def RSI(price_data):
    delta = price_data.diff()
    up = delta.copy()
    down = delta.copy()
    
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up = up.mean()
    roll_down = down.abs().mean()
    RS  = roll_up / roll_down
    RSI = (100 - (100/(1.0 + RS)))[0]
    
    if (RSI > 70):
        return -1
    elif (RSI < 30):
        return 1
    else:
        return 0 

aapl = yf.download('AAPL', '2017-1-1','2019-12-18')

aapl['Adj Open'] = aapl.Open * aapl['Adj Close']/aapl['Close']
aapl['Adj High'] = aapl.High * aapl['Adj Close']/aapl['Close']
aapl['Adj Low']  = aapl.Low  * aapl['Adj Close']/aapl['Close']
aapl.dropna(inplace = True)

adxI = ADXIndicator(aapl['Adj High'], aapl['Adj Low'], aapl['Adj Close'], 14, False)
aapl['pos_DI'] = adxI.adx_pos()
aapl['neg_DI'] = adxI.adx_neg()
aapl['adx'] = adxI.adx()

appleclosingprice = aapl.filter(['Adj Close'], axis = 1)
appleclosingprice = appleclosingprice.tail(717)
applestock = aapl.filter(['Adj Open', 'Adj High', 'Adj Low', 'Adj Close', 'pos_DI', 'neg_DI', 'adx'])

nav = applestock.filter(['adx', 'pos_DI', 'neg_DI', 'Adj Close'], axis = 1)
nav = nav[nav['adx'] > 0]
nav = nav.assign(rsi = np.zeros(718), leftover = np.zeros(718), stock = np.zeros(718))

for index, row in nav.iloc[1:].iterrows():
    nav.loc[index, 'rsi'] = RSI(appleclosingprice.loc[:index].tail(14))

portfolio = 1500  
nav = nav.tail(717).head(717)
nav.iloc[0,5] = portfolio
prev_signal = 0
signal = 0
    
for index, row in nav.iloc[1:].iterrows():
    
    adx       = nav.loc[:index].tail(2).head(1).iloc[0,0]
    pos_DI    = nav.loc[:index].tail(2).head(1).iloc[0,1]
    neg_DI    = nav.loc[:index].tail(2).head(1).iloc[0,2]
    rsi       = nav.loc[:index].tail(2).head(1).iloc[0,4]
    leftover  = nav.loc[:index].tail(2).head(1).iloc[0,5]
    invested  = nav.loc[:index].tail(2).head(1).iloc[0,6]
    
    
    signal = np.sign(signal + rsi)
    
    if(index == 0):
        continue
    else:
        adj_close = nav.loc[:index].tail(1).iloc[0,3]
    
    
    if ((adx > 65) and (pos_DI > neg_DI)):        
        
        if   (leftover > (3 * adj_close)):
            leftover = leftover - (3 * adj_close) 
            invested = invested + 3
            
        elif (leftover > (2 * adj_close)):
            leftover = leftover - (2 * adj_close) 
            invested = invested + 2
            
        elif(leftover > (1 * adj_close)):
            leftover = leftover - (1 * adj_close) 
            invested = invested + 1
            
        else:
            leftover = leftover
            invested = invested
            
            
    elif((adx > 30) and (pos_DI > neg_DI)):
        
        if   (prev_signal == 0 and signal == 1 and (leftover > adj_close)):
            leftover = leftover - adj_close
            invested = invested + 1
            
        elif (prev_signal == 1 and signal == 0 and (invested > 1)):
            leftover = leftover + adj_close
            invested = invested - 1
            
        else:
            leftover = leftover
            invested = invested
            
            
    elif((adx < 25) and (pos_DI < neg_DI)):
        
        if  (invested > 1 and (prev_signal == 1 and signal == 0)):
            leftover = leftover + adj_close
            invested = invested - 1
        else:
            leftover = leftover
            invested = invested
            
            
    else:
        leftover = leftover
        invested = invested
        
    
    nav.loc[index, 'leftover'] = leftover 
    nav.loc[index, 'stock'] = invested        
    prev_signal = signal
    
    
portfoliomanager = nav.filter(['Adj Close', 'leftover', 'stock'], axis = 1)
print(portfoliomanager)

#After investing 1500 USD across approx. 700 days, our net worth now stands at 3147.48 USD

plot_graph(nav['Adj Close'], 'Closing Price', 'Date')
plot_graph(nav['adx'], 'Adx', 'Date')

nav['trend'] = np.where(nav['adx'] > 40, nav['Adj Close'], np.nan)
nav['trend_signal'] = np.where(nav['adx'] > 40, 1, 0)

plt.figure(figsize = (10,7))
plt.grid()
plt.plot(nav['Adj Close'])
plt.plot(nav['trend'])
plt.ylabel('Price')
plt.xlabel('Date')

#Strong trends in stock occurs when ADX > 40, using this strategy in our backtesting model
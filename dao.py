import pandas as pd
from talib import RSI, BBANDS, ADX, MACD, CCI, RSI, STOCH, ULTOSC, WILLR
import matplotlib.pyplot as plt

import os.path


def get_new_data_ticker(ticker, filename):
    import quandl
    quandl.ApiConfig.api_key = 'xa93DjxVwVe5DU2yi-ir'
    data = quandl.get(ticker)
    data.to_csv(filename, sep=",")


def apply_technical_indicators_to_file(filename, filename_ind):
    prices = pd.read_csv(filename, sep=",")
    prices['rsi'] = RSI(prices['Adj. Close'], timeperiod=14)
    prices['bband_up'], prices['bband_mid'], prices['bband_low'] = BBANDS(prices['Adj. Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    prices['bbp'] = (prices['Adj. Close'] - prices['bband_low']) / (prices['bband_up'] - prices['bband_low'])
    prices['adx'] = ADX(prices['Adj. High'], prices['Adj. Low'], prices['Adj. Close'], timeperiod=14)
    prices['macd'], macdsignal, macdhist = MACD(prices['Adj. Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    prices['cci'] = CCI(prices['Adj. High'], prices['Adj. Low'], prices['Adj. Close'], timeperiod=14)
    prices['rsi'] = RSI(prices['Adj. Close'], timeperiod=14)
    prices['slowk'], prices['slowd'] = STOCH(prices['Adj. High'], prices['Adj. Low'], prices['Adj. Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    prices['ultosc'] = ULTOSC(prices['Adj. High'], prices['Adj. Low'], prices['Adj. Close'], timeperiod1=7, timeperiod2=14, timeperiod3=28)
    prices['willr'] = WILLR(prices['Adj. High'], prices['Adj. Low'], prices['Adj. Close'], timeperiod=14)
    prices.to_csv(filename_ind, sep=",")

def get_ind_file(ticker):
    filename = 'data/{}_data.csv'.format(ticker.replace("/", "_"))
    if not os.path.isfile(filename):
        get_new_data_ticker(ticker, filename)

    filename_ind = 'data/{}_ind.csv'.format(ticker.replace("/", "_"))
    if not os.path.isfile(filename_ind):
        apply_technical_indicators_to_file(filename, filename_ind)

    return pd.read_csv(filename_ind, sep=",").dropna()


# if __name__ == "__main__":
#     ticker = "WIKI/APPL"
#     get_ind_file(ticker)

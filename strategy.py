import copy
import random
import sys
import time
from enum import Enum
from functools import partial

import deap
import numpy
import pandas as pd
from deap import algorithms, base, creator, gp, tools


class Position(Enum):
    NONE = 0
    BUY = 1
    SELL = 2
    

def progn(*args):
    for arg in args:
        arg()

def prog2(out1, out2): 
    return partial(progn,out1,out2)

def prog3(out1, out2, out3):     
    return partial(progn,out1,out2,out3)

def if_then_else(condition, out1, out2):
    out1() if condition() else out2()

class StrategySimulator(object):
    def __init__(self, data):
        self.data = data
        self.index = 0
        self.max_iter = self.data.shape[0] - 1
        self.portfolio_value = 10000
        self.trade_value = 10
        self.active_position = Position.NONE
        self.routine = None
        self.buying_state = 0
        self.selling_state = 0
        self.leverage = 1.3

    def _reset(self):
        self.index = 0
        self.portfolio_value = 10000
        self.active_position = Position.NONE
        self.buying_state = 0
        self.selling_state = 0

    def update_index(self):
        self.index = min(self.index + 1, self.max_iter-1)

    def buy(self):
        if self.active_position == Position.NONE:
            self.portfolio_value - self.trade_value
            self.buying_state = self.index
            self.active_position = Position.BUY

        if self.active_position == Position.SELL:
            difference = self.data.iloc[self.selling_state]['Adj. Close'] - self.data.iloc[self.index]['Adj. Close']
            self.portfolio_value += self.leverage * self.trade_value * difference
            self.active_position = Position.NONE
            self.buying_state = 0

    def sell(self):
        if self.active_position == Position.NONE:
            self.portfolio_value - self.trade_value
            self.selling_state = self.index
            self.active_position = Position.SELL

        if self.active_position == Position.BUY:
            difference = self.data.iloc[self.index]['Adj. Close'] - self.data.iloc[self.buying_state]['Adj. Close']
            self.portfolio_value += self.leverage * self.trade_value * difference
            self.active_position = Position.NONE
            self.buying_state = 0

    def do_buy(self):
        if self.active_position in [Position.SELL, Position.NONE]:
            self.buy()

    def do_sell(self):
        if self.active_position in [Position.BUY, Position.NONE]:
            self.sell()

    def do_nothing(self):
        pass

    def check_rsi_under_limit(self):
        return self.data.iloc[self.index]['rsi'] < 30

    def check_rsi_over_limit(self):
        return self.data.iloc[self.index]['rsi'] > 70

    def if_rsi_under_limit(self, out1, out2):
        return partial(if_then_else, self.check_rsi_over_limit, out1, out2)

    def if_rsi_over_limit(self, out1, out2):
        return partial(if_then_else, self.check_rsi_over_limit, out1, out2)

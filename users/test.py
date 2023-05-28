from abc import ABCMeta, abstractmethod, abstractstaticmethod

class AbstractClass(metaclass=ABCMeta):
    a = 1
    b = 2

    @abstractmethod
    def add(self) -> None:
        pass

class ChildClass(AbstractClass):
    def add(self) -> None:
        print(self.a + self.b)

import MetaTrader5 as mt
from credentials import login_cred
from DataClass import MetaTraderData
from deployable_strategies import *
import time
import pandas as pd

algo = ExecutionEngine(RSIStrategy, 0.1, login_cred, 'ETHUSD', mt.TIMEFRAME_M1, 1, 5, 100, False, rsi_period = 420, ma_period = 420, tp_bar = 69, sl_bar = 69, bar_gap = 3.14159)
algo.execute()


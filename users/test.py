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
import time
import pandas as pd

# mt.login(login_cred['login'], login_cred['password'], login_cred['server'])
# mt.initialize()
# print(mt.positions_get(ticket=5043699217)[0]._asdict())
#print(mt.positions_get(5043699217)[0]._asdict())

data_obj = MetaTraderData(login_cred, 'EURUSD')

once = False
df = pd.DataFrame()
while True:
    if not once:
        df = data_obj.get_data(500, mt.TIMEFRAME_M1)
        print(df)
        once = True
    next_df =data_obj.get_data(1, mt.TIMEFRAME_M1)
    if df.index[-1] != next_df.index[-1]:
        df = pd.concat([df, next_df], axis=0)
        print(df)
        break
    time.sleep(1)
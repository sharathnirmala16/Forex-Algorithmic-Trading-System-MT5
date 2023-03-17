import socket
import numpy as np
import pandas as pd
import MetaTrader5 as mt
from datetime import datetime

class MetaTraderData:
    __symbol = ''
    #Constructor
    def __init__(self, login_cred : dict, symbol : str, print_acc_info = False, 
                 print_error = False) -> None:
        try:
            if MetaTraderData.internet_connection():
                mt.initialize()
                if mt.symbol_info(symbol) != None:
                    self.__symbol = symbol
                else:
                    raise Exception('Invalid Symbol.')
                mt.login(login_cred['login'], login_cred['password'], login_cred['server'])

                if print_acc_info:
                    print(mt.account_info())
            else:
                raise Exception('No internet connection.')
        except Exception as e:
            if print_error:
                print(e)

    #checks for internet connection
    @staticmethod
    def internet_connection():
        #if there is no internet connection, 127.0.0.1 is returned which is the address of localhost
        if socket.gethostbyname(socket.gethostname()) == '127.0.0.1':
            return False
        else:
            return True

    #Used for getting historical data
    def get_historical_data(self, utc_from : datetime, 
                 utc_to : datetime, timeframe = mt.TIMEFRAME_D1,
                 print_error = False) -> pd.DataFrame:
        data = pd.DataFrame()
        try:
            if MetaTraderData.internet_connection():
                mt.initialize()
                rates = mt.copy_rates_range(self.__symbol, timeframe, utc_from, utc_to)
                data = pd.DataFrame(rates)
                data['time'] = pd.to_datetime(data['time'], unit = 's')
                data = data[['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread']].copy()
                data = data.rename(columns = {'time':'datetime'})
            else:
                raise Exception('No internet connection.')
            
            if data.empty:
                raise Exception('Invalid parameters passed, unable to obtain data.')
        except Exception as e:
            if print_error:
                print(e)
        return data
    
    #get recent data
    def get_data(self, count : int, timeframe = mt.TIMEFRAME_D1,
                 print_error = False) -> pd.DataFrame:
        data = pd.DataFrame()
        try:
            if MetaTraderData.internet_connection():
                mt.initialize()
                rates = mt.copy_rates_from_pos(self.__symbol, timeframe, 0, count)
                data = pd.DataFrame(rates)
                data['time'] = pd.to_datetime(data['time'], unit = 's')
                data = data[['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread']].copy()
                data = data.rename(columns = {'time':'datetime'})
            else:
                raise Exception('No internet connection.')
            
            if data.empty:
                raise Exception('Invalid parameters passed, unable to obtain data.')
        except Exception as e:
            if print_error:
                print(e)
        return data
    
    #get bid price—highest price buyer is willing to buy for
    def get_bid(self, print_error = False) -> float:
        try:
            if MetaTraderData.internet_connection():
                return mt.symbol_info_tick(self.__symbol).bid
            else:
                raise Exception('No internet connection.')
        except Exception as e:
            if print_error:
                print(e)
        return -1

    #get ask price—lowest price seller is willing to sell for
    def get_ask(self, print_error = False) -> float:
        try:
            if MetaTraderData.internet_connection():
                return mt.symbol_info_tick(self.__symbol).ask
            else:
                raise Exception('No internet connection.')
        except Exception as e:
            if print_error:
                print(e)
        return -1
        
    #getter and setter methods
    @property
    def symbol(self) -> str:
        return self.__symbol
    
    @symbol.setter
    def symbol(self, sym : str, print_error = False) -> str:
        if mt.symbol_info(sym) != None:
            self.__symbol = sym
        elif print_error:
            print('Invalid Symbol')

    #Destructor
    def __del__(self):
        mt.shutdown()
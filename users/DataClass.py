import socket
import numpy as np
import pandas as pd
import MetaTrader5 as mt
from typing import Union
from datetime import datetime

class MetaTraderData:
    __symbol = ''
    timeframes = {
        mt.TIMEFRAME_M1:'1 Minute',
        mt.TIMEFRAME_M2:'2 Minutes',
        mt.TIMEFRAME_M3:'3 Minutes',
        mt.TIMEFRAME_M4:'4 Minutes',
        mt.TIMEFRAME_M5:'5 Minutes',
        mt.TIMEFRAME_M6:'6 Minutes',
        mt.TIMEFRAME_M10:'10 Minutes',
        mt.TIMEFRAME_M12:'12 Minutes',
        mt.TIMEFRAME_M15:'15 Minutes',
        mt.TIMEFRAME_M20:'20 Minutes',
        mt.TIMEFRAME_M30:'30 Minutes',
        mt.TIMEFRAME_H1:'1 Hour',
        mt.TIMEFRAME_H2:'2 Hours',
        mt.TIMEFRAME_H3:'3 Hours',
        mt.TIMEFRAME_H4:'4 Hours',
        mt.TIMEFRAME_H6:'6 Hours',
        mt.TIMEFRAME_H8:'8 Hours',
        mt.TIMEFRAME_H12:'12 Hours',
        mt.TIMEFRAME_D1:'1 Day',
        mt.TIMEFRAME_W1:'1 Week',
        mt.TIMEFRAME_MN1:'1 Month',
    }

    currency_pairs = {
        'EURUSD': 'Euro vs. US Dollar',
        'GBPUSD': 'British Pound vs. US Dollar',
        'USDJPY': 'US Dollar vs. Japanese Yen',
        'USDCHF': 'US Dollar vs. Swiss Franc',
        'AUDUSD': 'Australian Dollar vs. US Dollar',
        'NZDUSD': 'New Zealand Dollar vs. US Dollar',
        'USDCAD': 'US Dollar vs. Canadian Dollar',
        'EURGBP': 'Euro vs. British Pound',
        'EURJPY': 'Euro vs. Japanese Yen',
        'EURCHF': 'Euro vs. Swiss Franc',
        'EURAUD': 'Euro vs. Australian Dollar',
        'EURNZD': 'Euro vs. New Zealand Dollar',
        'EURCAD': 'Euro vs. Canadian Dollar',
    }

    #Constructor
    def __init__(self, login_cred : dict, symbol : str, print_acc_info = False, print_error = False) -> None:
        try:
            if MetaTraderData.internet_connection():
                mt.initialize()
                if mt.symbol_info(symbol) != None:
                    self.__symbol = symbol
                else:
                    raise Exception('Invalid Symbol.')
                login_ok = mt.login(login_cred['login'], login_cred['password'], login_cred['server'])
                if not login_ok:
                    raise Exception('Failed to connect to account.')
                if print_acc_info:
                    print(mt.account_info())
            else:
                raise Exception('No internet connection.')
        except Exception as e:
            if print_error:
                print(e)
                print(mt.last_error())

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
                 timezone = 'Asia/Kolkata', print_error = False,
                 upper_case_cols = True) -> Union[pd.DataFrame, None]:
        try:
            if MetaTraderData.internet_connection():
                mt.initialize()
                rates = mt.copy_rates_range(self.__symbol, timeframe, utc_from, utc_to)
                data = pd.DataFrame(rates)
                data['time'] = pd.to_datetime(data['time'], unit = 's')
                data = data[['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread']].copy()
                data = data.rename(columns = {'time':'datetime'})
                #NOTE change timezone
            else:
                raise Exception('No internet connection.')
            
            if data.empty:
                raise Exception('Invalid parameters passed, unable to obtain data.')
            
            if upper_case_cols:
                data = data.rename(columns = {'datetime':'Date', 'open':'Open', 'high':'High', 'low':'Low', 'close':'Close'})

            return data
        
        except Exception as e:
            if print_error:
                print(e)
                print(mt.last_error())
            else:
                return None
    
    #get recent data
    def get_data(self, count : int, timeframe = mt.TIMEFRAME_D1,
                 timezone = 'Asia/Kolkata', print_error = False, 
                 upper_case_cols = True, datetime_index = True) -> Union[pd.DataFrame, None]:
        try:
            if MetaTraderData.internet_connection():
                mt.initialize()
                rates = mt.copy_rates_from_pos(self.__symbol, timeframe, 0, count)
                data = pd.DataFrame(rates)
                data['time'] = pd.to_datetime(data['time'], unit = 's')
                data = data[['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread']].copy()
                data = data.rename(columns = {'time':'datetime'})
                #NOTE change timezone
            else:
                raise Exception('No internet connection.')
            
            if data.empty:
                raise Exception('Invalid parameters passed, unable to obtain data.')
            
            if upper_case_cols:
                data = data.rename(columns = {'datetime':'Date', 'open':'Open', 'high':'High', 'low':'Low', 'close':'Close'})
                if datetime_index:
                    data = data.set_index('Date')
            elif datetime_index:
                data = data.set_index('datetime')

            return data
        
        except Exception as e:
            if print_error:
                print(e)
                print(mt.last_error())
            else:
                return None
    
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
                print(mt.last_error())
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
                print(mt.last_error())
        return -1
        
    #getter and setter methods
    @property
    def symbol(self) -> str:
        return self.__symbol
    
    @symbol.setter
    def symbol(self, sym : str, print_error = False) -> None:
        if mt.symbol_info(sym) != None:
            self.__symbol = sym
        elif print_error:
            print('Invalid Symbol')

    #Destructor
    def __del__(self) -> None:
        mt.shutdown()
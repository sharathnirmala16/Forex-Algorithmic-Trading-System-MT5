import ta
import numpy as np
import pandas as pd
import MetaTrader5 as mt

from DataClass import MetaTraderData
from abc import ABCMeta, abstractmethod, abstractstaticmethod

class DeployableStrategy(metaclass = ABCMeta):
    _lot_size : float = None
    _login_cred : dict = None
    _currency_pair : str = None
    _timeframe : int = None
    repeat_time : int = None
    _deviation : int = None
    _strategy_name : str = 'Deployable Strategy Abstract Class'

    def __init__(self, lot_size : float, login_cred : dict, currency_pair : str, timeframe : int, repeat_time : int,deviation : int, print_error : bool = False) -> None:
        self._lot_size = lot_size
        self._login_cred = login_cred
        self._currency_pair = currency_pair
        self._timeframe = timeframe
        self.repeat_time = repeat_time
        self._deviation = deviation

        try:
            login_ok = mt.login(self._login_cred['login'], self._login_cred['password'], self._login_cred['server'])
            if not login_ok:
                raise Exception('Failed to connect to account.')
            self.data_obj = MetaTraderData(self._login_cred, self._currency_pair)
        except Exception as e:
            if print_error:
                print(e)
                print(mt.last_error())

    def _new_order(self, buy : bool, price : float = None, position : int = None, tp : float = None, sl : float = None, order_size : float = None, comment = '') -> dict:
        if order_size is None:
            order_size = self._lot_size

        order_request = {
            'action':mt.TRADE_ACTION_DEAL, #specifies market order
            'symbol':self._currency_pair,
            'volume':order_size,
            'deviation':self._deviation,
            'type_time':mt.ORDER_TIME_GTC, #Order has to be manually cancelled
            'type_filling': mt.ORDER_FILLING_FOK, #Fill or Kill type order
            'comment': comment
        }
        if buy:
            order_request['type'] = mt.ORDER_TYPE_BUY
        else:
            order_request['type'] = mt.ORDER_TYPE_SELL

        if price is not None:
            order_request['price'] = price
        else:
            if buy:
                order_request['price'] = self.data_obj.get_bid()
            else:
                order_request['price'] = self.data_obj.get_ask()

        if tp is not None:
            order_request['tp'] = tp
        
        if sl is not None:
            order_request['sl'] = sl

        if position is not None:
            order_request['position'] = position

        return order_request

    #market buy order
    def buy(self, price : float = None, tp : float = None, sl : float = None, order_size : float = None, comment : str = '', print_error = False) -> dict:
        order = None
        order_request = self._new_order(
            buy=True,
            price=price,
            order_size=order_size,
            tp=tp,
            sl=sl,
            comment=comment
        )

        try:
            order = mt.order_send(order_request)._asdict()
        except Exception as e:
            if print_error:
                print(e)
                print(mt.last_error())
            order = {}

        return order
        
    #market sell order
    def sell(self, price : float = None, tp : float = None, sl : float = None, order_size : float = None, comment : str = '', print_error = False) -> dict:
        order = None
        order_request = self._new_order(
            buy=False,
            price=price,
            order_size=order_size,
            tp=tp,
            sl=sl,
            comment=comment,
        )

        try:
            order = mt.order_send(order_request)._asdict()
        except Exception as e:
            if print_error:
                print(e)
                print(mt.last_error())
            order = {}

        return order

    #close position
    def close(self, position, price : float = None, order_size : float = None, comment = '', print_error = False) -> dict:
        trade_details : dict = mt.positions_get(ticket=position)[0]._asdict()
        
        if order_size is None:
            order_size = trade_details['volume']

        order_request = {}
        if trade_details['type'] == 0:
            order_request = self._new_order(
                buy=False,
                price=price,
                position=position,
                order_size=order_size,
                comment=comment
            )
        else:
            order_request = self._new_order(
                buy=False,
                price=price,
                position=position,
                order_size=order_size,
                comment=comment
            )

        order = None

        try:
            order = mt.order_send(order_request)._asdict()
        except Exception as e:
            if print_error:
                print(e)
                print(mt.last_error())
            order = {}

        return order
        
    @abstractmethod
    def init(self) -> None:
        pass

    @abstractmethod
    def next(self) -> None:
        pass

class BuySellTest(DeployableStrategy):
    
    def __init__(self, lot_size: float, login_cred: dict, currency_pair: str, timeframe: int, repeat_time: int, deviation: int, print_error: bool = False) -> None:
        super().__init__(lot_size, login_cred, currency_pair, timeframe, repeat_time, deviation, print_error)
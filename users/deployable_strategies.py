import ta
import time
import numpy as np
import pandas as pd
import tensorflow as tf
import MetaTrader5 as mt
from .DataClass import MetaTraderData
from abc import ABCMeta, abstractmethod
from sklearn.preprocessing import MinMaxScaler

class AbstractStrategy(metaclass = ABCMeta):
    _lot_size : float = None
    _login_cred : dict = None
    _currency_pair : str = None
    _timeframe : int = None
    repeat_time : int = None
    _deviation : int = None
    _dataframe_size : int = None
    _print_error : bool = None
    _active_trades : list = []

    def __init__(
            self, 
            lot_size : float, 
            login_cred : dict, 
            currency_pair : str, 
            timeframe : int, 
            repeat_time : int, 
            deviation : int, 
            dataframe_size : int, 
            print_error : bool = False) -> None:
        self._lot_size = lot_size
        self._login_cred = login_cred
        self._currency_pair = currency_pair
        self._timeframe = timeframe
        self.repeat_time = repeat_time
        self._deviation = deviation
        self._dataframe_size = dataframe_size
        self._print_error = print_error

        mt.login(self._login_cred['login'], self._login_cred['password'], self._login_cred['server'])
        self.data_obj = MetaTraderData(self._login_cred, self._currency_pair)
        self._data = self.data_obj.get_data(count=self._dataframe_size, timeframe=self._timeframe, print_error=print_error)

    def _new_order(
            self, 
            buy : bool, 
            price : float = None, 
            position : int = None, 
            tp : float = None, 
            sl : float = None, 
            order_size : float = None, 
            comment = '') -> dict:
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
    def buy(self, 
            price : float = None, 
            tp : float = None, 
            sl : float = None, 
            order_size : float = None, 
            comment : str = '', 
            print_error = False) -> dict:
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
    def sell(
            self, 
            price : float = None, 
            tp : float = None, 
            sl : float = None, 
            order_size : float = None, 
            comment : str = '', 
            print_error = False) -> dict:
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
    def close(
            self, 
            position, 
            price : float = None, 
            order_size : float = None, 
            comment = '', 
            print_error = False) -> dict:
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
                buy=True,
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
    
    def _load_kwargs_to_static(self, **kwargs) -> None:
        static_vars = {
            param: value 
            for param, value in vars(self.__class__).items() 
            if param not in vars(super.__class__).keys() and 
            (type(value) is int or type(value) is float)
        }
        for param, value in static_vars.items():
            setattr(self.__class__, param, kwargs.pop(param, value))
    
    def _refresh(self) -> None:
        self._data = self.data_obj.get_data(count=self._dataframe_size, timeframe=self._timeframe)
        self.apply_indicators()
        self._active_trades = [trade._asdict() for trade in mt.positions_get(symbol=self._currency_pair)] 

    @abstractmethod
    def apply_indicators(self) -> None:
        pass
        
    @abstractmethod
    def init(self) -> None:
        pass

    @abstractmethod
    def next(self) -> None:
        pass

class ExecutionEngine:
    def __init__(
            self, 
            strategy_class : AbstractStrategy, 
            lot_size: float, 
            login_cred: dict, 
            currency_pair: str, 
            timeframe: int, 
            repeat_time: int, 
            deviation: int, 
            dataframe_size: int, 
            print_error: bool = False,
            *args, **kwargs) -> None:
        self.__strategy_class = strategy_class

        self.__instance : AbstractStrategy = self.__strategy_class(
            lot_size = lot_size,
            login_cred = login_cred,
            currency_pair = currency_pair,
            timeframe = timeframe,
            repeat_time = repeat_time,
            deviation = deviation,
            dataframe_size = dataframe_size,
            print_error = print_error,
            *args, **kwargs
        )

        self.__instance._load_kwargs_to_static(**kwargs)
        self.__instance.init()

    def execute(self) -> None:
        while True:
            self.__instance._refresh()
            self.__instance.next()
            time.sleep(self.__instance.repeat_time)

class BuySellTestDeployable(AbstractStrategy):
    strategy_name = 'Buy and Sell Test Algorithm'
    wait_calls : int = None
    def __init__(
            self, 
            lot_size: float, 
            login_cred: dict, 
            currency_pair: str, 
            timeframe: int, 
            repeat_time: int, 
            deviation: int, 
            dataframe_size: int, 
            print_error: bool = False,
            *args, **kwargs) -> None:
        super().__init__(lot_size, login_cred, currency_pair, timeframe, repeat_time, deviation, dataframe_size, print_error)
        self.wait_calls = kwargs.pop('wait_calls', 10)
        

    def init(self) -> None:
        self.long = True
        self.current_calls = 0

    def apply_indicators(self) -> None:
        pass

    def next(self) -> None:
        if len(self._active_trades) == 0:
            if self.long:
                self.buy()
                self.long = False
            else:
                self.sell()
                self.long = True
        else:
            if self.current_calls < self.wait_calls:
                self.current_calls += 1
            else:
                self.current_calls = 0
                self.close(self._active_trades[0]['ticket'])


class RSIStrategyDeployable(AbstractStrategy):
    strategy_name = 'Simple RSI Strategy'
    rsi_period = 14
    ma_period = 50
    tp_bar = 2
    sl_bar = 20
    bar_gap = 0.0005

    def __init__(
            self, 
            lot_size: float, 
            login_cred: dict, 
            currency_pair: str, 
            timeframe: int, 
            repeat_time: int, 
            deviation: int, 
            dataframe_size: int, 
            print_error: bool = False,
            *args, **kwargs) -> None:
        super().__init__(lot_size, login_cred, currency_pair, timeframe, repeat_time, deviation, dataframe_size, print_error)

    def init(self) -> None:
        pass
    
    def apply_indicators(self) -> None:
        self._data['rsi'] = ta.momentum.rsi(self._data['Close'], self.rsi_period)
        self._data['ma'] = ta.trend.sma_indicator(self._data['Close'], self.ma_period)

    def next(self) -> None:
        if len(self._active_trades) == 0:
            pass
        else:
            price = self._data['Close'][-1]
            if self._data['rsi'][-1] >= 70 and self._data['ma'][-1] <= price:
                self.sell(sl = price + (self.sl_bar * self.bar_gap), tp = price - (self.tp_bar * self.bar_gap))
            elif self._data['rsi'][-1] <= 30 and self._data['ma'][-1] >= price:
                self.buy(sl = price - (self.sl_bar * self.bar_gap), tp = price + (self.tp_bar * self.bar_gap))
        
class StaticGridStrategyDeployable(AbstractStrategy):
    strategy_name = 'Static Grid Strategy'
    line_count = 8
    grid_gap = 0.005

    def __init__(
            self, 
            lot_size: float, 
            login_cred: dict, 
            currency_pair: str, 
            timeframe: int, 
            repeat_time: int, 
            deviation: int, 
            dataframe_size: int, 
            print_error: bool = False,
            *args, **kwargs) -> None:
        super().__init__(lot_size, login_cred, currency_pair, timeframe, repeat_time, deviation, dataframe_size, print_error)
        self.line_count = kwargs.pop('line_count')
        self.grid_gap = kwargs.pop('grid_gap')

    def init(self) -> None:
        self.__restart_grid = True
        self.__size = self._lot_size // self.line_count

    def apply_indicators(self) -> None:
        pass

    def next(self) -> None:
        price = self._data['Close'][-1]
        
        if self.__restart_grid:
            self.grid_lines = list()
            for i in range(self.line_count, 0, -1):
                self.grid_lines.append(price - (i * self.grid_gap))

            for i in range(0, self.line_count + 1):
                self.grid_lines.append(price + (i * self.grid_gap))

            if len(self.grid_lines) != (2 * self.line_count) + 1:
                raise Exception("Grid Lines not placed properly")
            
            self.grid_dict = dict.fromkeys(tuple(self.grid_lines), False) 
            self.__restart_grid = False
            
        elif not self.__restart_grid:
            for i in range(self.line_count + 1, len(self.grid_lines) - 1):
                if (
                        price >= self.grid_lines[i] and 
                        price < self.grid_lines[i + 1] and
                        not self.grid_dict[self.grid_lines[i]]
                ):
                    self.sell(
                        size = self.__size,
                        sl = self.grid_lines[-1], 
                        tp = self.grid_lines[self.line_count]
                    )
                    self.grid_dict[self.grid_lines[i]] = True
                    break

            for i in range(self.line_count - 1, 0, -1):
                if (
                        price <= self.grid_lines[i] and 
                        price > self.grid_lines[i - 1] and
                        not self.grid_dict[self.grid_lines[i]]
                ):
                    self.buy(
                        size = self.__size,
                        sl = self.grid_lines[0], 
                        tp = self.grid_lines[self.line_count]
                    )
                    self.grid_dict[self.grid_lines[i]] = True
                    break

            if price < self.grid_lines[0] or price > self.grid_lines[-1]:
                self.__restart_grid = True

class LSTMStrategyDeployable(AbstractStrategy):
    strategy_name = 'LSTM Strategy'
    ma_period = 10
    target_pips = 5

    def __init__(
            self, 
            lot_size: float, 
            login_cred: dict, 
            currency_pair: str, 
            timeframe: int, 
            repeat_time: int, 
            deviation: int, 
            dataframe_size: int, 
            print_error: bool = False,
            *args, **kwargs) -> None:
        super().__init__(lot_size, login_cred, currency_pair, timeframe, repeat_time, deviation, dataframe_size, print_error)
        self.ma_period = kwargs.pop('ma_period')
        self.target_pips = kwargs.pop('target_pips')

    @staticmethod
    def __return_series(arr : np.array, size : int) -> pd.Series:
        add_ser = pd.Series(np.concatenate((np.full(size-len(arr), np.nan), arr.T[0])))
        return add_ser

    def init(self) -> None:
        self.model = tf.keras.models.load_model('users\\ml_models\\basic_model.h5')

    def apply_indicators(self) -> None:
        close = pd.Series(self._data['Close']).values
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_data = scaler.fit_transform(close.reshape(-1, 1))
        X_test = []
        for i in range(60, len(scaled_data)):
            X_test.append(scaled_data[i-60:i, 0])
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
        predictions = self.model.predict(X_test)
        predictions = scaler.inverse_transform(predictions)
        self._data['pred'] = self.__return_series(predictions, self._data.shape[0])
        self._data['ma'] = ta.trend.sma_indicator(self._data['Close'], self.ma_period)

    def next(self) -> None:
        if len(self._active_trades) > 0:
            pass
        else:
            price = self._data['Close'][-1]
            if self._data['pred'][-1] > price + (self.target_pips * 1e-4) and price > self._data['ma'][-1]:
                self.buy(price=price, tp=self._data['pred'][-1], sl=self._data['ma'][-1])
            elif self._data['pred'][-1] < price - (self.target_pips * 1e-4) and price < self._data['ma'][-1]:
                self.sell(price=price, tp=self._data['pred'][-1], sl=self._data['ma'][-1]) 
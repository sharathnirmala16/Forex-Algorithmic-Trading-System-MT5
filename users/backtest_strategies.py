import ta
import numpy as np
import pandas as pd
import tensorflow as tf
from backtesting import Strategy
from sklearn.preprocessing import MinMaxScaler

class MACrossover(Strategy):
    strategy_name = 'Moving Average Crossover Strategy'
    fast_ma_period = 10
    slow_ma_period = 40

    def init(self) -> None:
        close = self.data['Close']
        self.fast_ma = self.I(ta.trend.sma_indicator, pd.Series(close), self.fast_ma_period)
        self.slow_ma = self.I(ta.trend.sma_indicator, pd.Series(close), self.slow_ma_period)

    def next(self) -> None:
        if self.position:
            pass
        else:
            if self.fast_ma[-1] > self.slow_ma[-1]:
                self.buy()
            else:
                self.sell()

#<Strategy RSIStrategyTA(rsi_period=20,ma_period=31,tp_bar=7,sl_bar=13)>
class RSIStrategy(Strategy):
    strategy_name = 'Simple RSI Strategy'
    rsi_period = 14
    ma_period = 50
    tp_bar = 2
    sl_bar = 20
    bar_gap = 5e-4

    def init(self) -> None:
        close = self.data['Close']
        self.rsi = self.I(ta.momentum.rsi, pd.Series(close), self.rsi_period)
        self.ma = self.I(ta.trend.sma_indicator, pd.Series(close), self.ma_period)

    def next(self) -> None:
        if self.position:
            pass
        else:
            price = self.data['Close'][-1]
            if self.rsi[-1] >= 70 and self.ma[-1] <= price:
                self.sell(sl = price + (self.sl_bar * self.bar_gap), tp = price - (self.tp_bar * self.bar_gap))
            elif self.rsi[-1] <= 30 and self.ma[-1] >= price:
                self.buy(sl = price - (self.sl_bar * self.bar_gap), tp = price + (self.tp_bar * self.bar_gap))

#<Strategy StaticGridStrategy(line_count=7,grid_gap=0.0025583121776463665,rsi_period=93)>
class StaticGridStrategy(Strategy):
    strategy_name = 'Static Grid Strategy'
    line_count=8
    grid_gap=0.005
    __restart_grid = True

    def init(self) -> None:
        self.size = (self._broker._cash * self._broker._leverage * 0.9) // int(self.line_count * self.data['Close'].mean())
    
    def next(self) -> None:
        price = self.data['Close'][-1]
        
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
                        size = self.size,
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
                        size = self.size,
                        sl = self.grid_lines[0], 
                        tp = self.grid_lines[self.line_count]
                    )
                    self.grid_dict[self.grid_lines[i]] = True
                    break

            if price < self.grid_lines[0] or price > self.grid_lines[-1]:
                self.__restart_grid = True

class LSTMStrategy(Strategy):
    strategy_name = 'LSTM Strategy'
    ma_period = 10
    target_pips = 5

    @staticmethod
    def __return_series(arr : np.array, size : int) -> pd.Series:
        add_ser = pd.Series(np.concatenate((np.full(size-len(arr), np.nan), arr.T[0])))
        return add_ser

    def init(self) -> None:
        model = tf.keras.models.load_model('users\\ml_models\\basic_model.h5')
        close = pd.Series(self.data['Close']).values
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_data = scaler.fit_transform(close.reshape(-1, 1))
        X_test = []

        for i in range(60, len(scaled_data)):
            X_test.append(scaled_data[i-60:i, 0])
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
        predictions = model.predict(X_test)
        predictions = scaler.inverse_transform(predictions)
        self.pred = self.I(self.__return_series, predictions, self.data.df.shape[0])
        self.ma = self.I(ta.trend.sma_indicator, pd.Series(self.data['Close']), self.ma_period)

    def next(self) -> None:
        if self.position:
            pass
        else:
            price = self.data['Close'][-1]
            if self.pred[-1] > price + (self.target_pips * 1e-4) and price > self.ma[-1]:
                self.buy(tp=self.pred[-1], sl=self.ma[-1])
            elif self.pred[-1] < price - (self.target_pips * 1e-4) and price < self.ma[-1]:
                self.sell(tp=self.pred[-1], sl=self.ma[-1]) 


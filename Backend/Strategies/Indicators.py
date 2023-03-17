import numpy as np
import pandas as pd
from stocktrends import Renko
from datetime import timedelta
from datetime import datetime as dt

#This class can be used to add various technical indicators to the dataframe
class Indicators:

    #simple moving average
    @staticmethod
    def MA(price_series : pd.Series, n) -> pd.Series:
        return price_series.rolling(n).mean()

    #exponential moving average
    @staticmethod
    def EMA(price_series : pd.Series, n, com = True) -> pd.Series:
        if com:
            return price_series.ewm(com=n, min_periods=n).mean()
        else:
            return price_series.ewm(span=n, min_periods=n).mean()

    #Adds the MACD Indicator to the dataframe
    @staticmethod
    def MACD(dataframe : pd.DataFrame, fast = 12, slow = 26, signal = 9) -> pd.DataFrame:
        df = dataframe.copy()
        ema_fast = Indicators.EMA(df['close'], n = fast, com = False)
        ema_slow = Indicators.EMA(df['close'], n = slow, com = False)

        line_name, signal_name, histogram_name = (
                                                    f'macd_line_({fast},{slow},{signal})', 
                                                    f'macd_signal_({fast},{slow},{signal})', 
                                                    f'macd_histogram_({fast},{slow},{signal})'
                                                 )

        df[line_name] =  ema_fast - ema_slow
        df[signal_name] = Indicators.MA(df[line_name], signal)
        df[histogram_name] = df[line_name].to_numpy() - df[signal_name].to_numpy()
        return df
    
    #Adds Relative Strength Index to the data frame
    @staticmethod
    def RSI(dataframe : pd.DataFrame, n = 14) -> pd.DataFrame:
        df = dataframe.copy()
        index = df.index
        prices = pd.Series(df['close'].to_numpy().flatten())

        change_series = prices - prices.shift(-1)
        gain_series = pd.Series(np.where(change_series >= 0, change_series, 0))
        loss_series = pd.Series(np.where(change_series < 0, -1 * change_series, 0))
        avg_gain_series = gain_series.ewm(alpha = 1 / n, min_periods = n).mean()
        avg_loss_series = loss_series.ewm(alpha = 1 / n, min_periods = n).mean()
        rs_series = avg_gain_series / avg_loss_series
        rsi_series = 100 - (100/(1 + rs_series))
        rsi_series.index = index

        df[f'rsi_({n})'] = rsi_series
        return df
    
    #Adds Bollinger Bands indicator to the dataframe
    @staticmethod
    def BOLLINGER_BANDS(dataframe : pd.DataFrame, n = 14, deviations = 2) -> pd.DataFrame:
        df = dataframe.copy()
        index = df.index
        prices = pd.Series(df['close'].to_numpy().flatten())
        
        mb_series = Indicators.MA(prices, n)
        ub_series = mb_series + deviations * prices.rolling(n).std(ddof=0)
        lb_series = mb_series - deviations * prices.rolling(n).std(ddof=0)
        bb_width_series = ub_series - lb_series
        mb_series.index, ub_series.index, lb_series.index, bb_width_series.index = index, index, index, index
        
        df[f'bb_mb_({n},{deviations})'] = mb_series
        df[f'bb_ub_({n},{deviations})'] = ub_series
        df[f'bb_lb_({n},{deviations})'] = lb_series
        df[f'bb_width_({n},{deviations})'] = bb_width_series
        return df
    
    #Adds Stochastic Oscillator indicator to the dataframe
    @staticmethod
    def STOCHASTIC_OSCILLATOR(dataframe : pd.DataFrame, n = 14, d = 3):
        df = dataframe.copy()
        index = df.index
        prices_close = pd.Series(df['close'].to_numpy().flatten())
        prices_high = pd.Series(df['high'].to_numpy().flatten())
        prices_low = pd.Series(df['low'].to_numpy().flatten())

        n_high_series = prices_high.rolling(n).max()
        n_low_series = prices_low.rolling(n).min()
        mod_K = ((prices_close - n_low_series) * 100) / (n_high_series - n_low_series)
        mod_D = Indicators.MA(mod_K, d)
        mod_K.index, mod_D.index = index, index

        df[f'stoch_osc_%K_({n},{d})'] = mod_K
        df[f'stoch_osc_%D_({n},{d})'] = mod_D
        return df
    
    #Adds the Average True Range indicator to the dataframe
    @staticmethod
    def ATR(dataframe : pd.DataFrame, n = 14) -> pd.DataFrame:
        df = dataframe.copy()
        index = df.index
        high_series, low_series, close_series = (
                                                    pd.Series(df['high'].to_numpy().flatten()),
                                                    pd.Series(df['low'].to_numpy().flatten()),
                                                    pd.Series(df['close'].to_numpy().flatten())
                                                )
        
        df1 = pd.DataFrame()
        df1['H-L'] = high_series - low_series
        df1['H-PC'] = np.abs(high_series - close_series.shift(1))
        df1['L-PC'] = np.abs(low_series - close_series.shift(1))
        df1['TR'] = df1[['H-L','H-PC','L-PC']].max(axis=1, skipna=False)
        df1['ATR'] = Indicators.EMA(df1['TR'], n, com=True)

        atr_series = df1['ATR']
        atr_series.index = index
        df[f'atr_({n})'] = df1['ATR']
        return df
    
    #Adds the Average Directional Movement Index
    @staticmethod
    def ADX(dataframe : pd.DataFrame, n = 14) -> pd.DataFrame:
        df = dataframe.copy()
        df1 = dataframe.copy()
        df1 = Indicators.ATR(df1, n)
        high_series, low_series, atr_series = (
                                                    pd.Series(df['high'].to_numpy().flatten()),
                                                    pd.Series(df['low'].to_numpy().flatten()),
                                                    pd.Series(df1[f'atr_({n})'].to_numpy().flatten())
                                                )

        upmove_series = high_series - high_series.shift(1)
        downmove_series = low_series.shift(1) - low_series
        pdm_series = np.where((upmove_series > downmove_series) & (upmove_series > 0), upmove_series, 0)
        ndm_series = np.where((downmove_series > upmove_series) & (downmove_series > 0), downmove_series, 0)
        pdi_series = 100 * Indicators.EMA((pdm_series / atr_series), n, com = True)
        ndi_series = 100 * Indicators.EMA((ndm_series / atr_series), n, com = True)
        adx_series = 100 * Indicators.EMA(np.abs((pdi_series - ndi_series) / (pdi_series + ndi_series)), n, com = False)
        
        adx_series.index = df.index
        df[f'adx_({n})'] = adx_series
        return df

    #Creates a new dataframe that can be used to make a renko chart
    #NOTE Only thing is the lack of support for the volume and spread, to be integrated in FUTURE PATCHES
    @staticmethod
    def RENKO(dataframe : pd.DataFrame, brick_size) -> pd.DataFrame:
        df = dataframe[['datetime', 'open', 'high', 'low', 'close', 'tick_volume']].copy(deep=True)
        df = df.rename(columns = {'datetime':'date', 'tick_volume':'volume'})
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

        df = Renko(df)
        df.brick_size = brick_size
        
        renko_df = df.get_ohlc_data()
        renko_df = renko_df.rename(columns = {'date':'datetime'})
        renko_df = renko_df.set_index('datetime', drop = True)
        return renko_df

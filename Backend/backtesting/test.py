import pytz
import MetaTrader5 as mt
from datetime import datetime
from credentials import login_cred
from DataClass import MetaTraderData as Data
from Strategies.Indicators import Indicators

symbol = 'USDJPY'
data_usdjpy = Data(login_cred, symbol)

timezone = pytz.timezone("ETC/Gmt")
utc_from = datetime(2023, 1, 10, tzinfo = timezone)
utc_to = datetime(2023, 3, 15, tzinfo = timezone)

df = data_usdjpy.get_data(300, timeframe=mt.TIMEFRAME_M1)
df = df.rename(columns = {'datetime':'Datetime', 'open':'Open', 'high':'High', 'low':'Low', 'close':'Close'})
df = Indicators.RENKO(dataframe=df, brick_size=0.002)

print(df)

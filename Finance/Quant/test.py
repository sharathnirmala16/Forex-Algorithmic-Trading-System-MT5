from credentials import login_credentials
from DataClass import MetaTraderData as DataClass
from Strategies.Indicators import Indicators

symbol = 'USDJPY'

data_usdjpy = DataClass(
    login_cred = login_credentials,
    symbol=symbol,
    print_acc_info = False,
    print_error = False
)

print(data_usdjpy.get_ask())
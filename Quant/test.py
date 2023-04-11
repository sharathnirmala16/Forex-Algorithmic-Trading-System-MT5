from DataClass import MetaTraderData as DataClass
from Strategies.Indicators import Indicators

symbol = 'USDJPY'

login_credentials = {
    'login':'89779274',
    'password':'jUJu#AqE',
    'server':'OctaFX-Demo'
}

data_usdjpy = DataClass(
    login_cred = login_credentials,
    symbol=symbol,
    print_acc_info = False,
    print_error = False
)

print(data_usdjpy.get_ask())
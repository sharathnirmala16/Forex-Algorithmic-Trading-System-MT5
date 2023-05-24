from DataClass import MetaTraderData
import MetaTrader5 as mt

class Test:
    login_cred = {
        'login': 89779274,
        'password': 'jUJu#AqE',
        'server': 'OctaFX-Demo'  
    }

    def func(self):
        data_instance = MetaTraderData(self.login_cred, 'EURUSD')
        data = data_instance.get_data(50000, 30)
        print(data) 

    

res = Test().func()
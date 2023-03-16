import time
import numpy as np
import pandas as pd
import MetaTrader5 as mt
from datetime import datetime

class MetaTraderData:
    
    #Constructor
    def __init__(self, login_cred : dict, print_acc_info = False) -> None:
        mt.initialize()
        mt.login(login_cred['login'], login_cred['password'], login_cred['server'])

        if print_acc_info:
            print(mt.account_info())

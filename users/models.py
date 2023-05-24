from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_init
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.utils.module_loading import import_string
from .managers import CustomUserManager
from dotenv import load_dotenv
from .backtest_strategies import *
from .DataClass import *
from backtesting import Backtest, Strategy
import os
import sys
import cryptocode
load_dotenv()

# Create your models here.
#NOTE this class is DEPRECATED and doesn't work properly, just kept to not cause issues during migration
class CustomPasswordField(models.CharField):
    description = "Custom Encrypted Password Field"
    
    def __init__(self, *args, **kwargs):
        self.__password_key = os.getenv('PASSWORD_KEY_STRING')
        super().__init__(*args, **kwargs)
    
    def get_prep_value(self, value: str) -> str:
        return cryptocode.encrypt(value, self.__password_key)
    
    def from_db_value(self, value : str, expression, connection) -> str:
        if value is None:
            return value
        dec = cryptocode.decrypt(value, self.__password_key)
        if type(dec) == str:
            return dec
    
    def to_python(self, value: str) -> str:
        if value is None:
            return value
        dec = cryptocode.decrypt(value, self.__password_key)
        if type(dec) == str:
            return dec

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=20)
    last_name = models.CharField(_('last name'), max_length=20)
    phone_number = models.CharField(_('phone number'), max_length=14)

    demo_login = models.CharField(_('demo login'), blank=False, null=False, max_length=12)
    demo_password = models.CharField(_('demo password'), blank=False, null=False, max_length=255)
    demo_server = models.CharField(_('demo server'), blank=False, null=False, max_length=20)

    live_login = models.CharField(_('live login'), blank=False, null=False, max_length=12)
    live_password = models.CharField(_('live password'), blank=False, null=False, max_length=255)
    live_server = models.CharField(_('live server'), blank=False, null=False, max_length=20)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name', 'last_name', 'phone_number', 
        'demo_login', 'demo_password', 'demo_server',
        'live_login', 'live_password', 'live_server'
    ]

    objects = CustomUserManager()

    def save(self, *args, **kwargs) -> None:
        if not self.pk:
            self.demo_password = cryptocode.encrypt(self.demo_password, os.getenv('PASSWORD_KEY_STRING'))
            self.live_password = cryptocode.encrypt(self.demo_password, os.getenv('PASSWORD_KEY_STRING'))
        super().save(*args, **kwargs)

    def get_demo_password(self):
        return cryptocode.decrypt(self.demo_password, os.getenv('PASSWORD_KEY_STRING'))

    def get_live_password(self):
        return cryptocode.decrypt(self.live_password, os.getenv('PASSWORD_KEY_STRING'))

class BacktestStrategyClasses(models.Model):
    class Meta:
        managed = False

    @staticmethod
    def __get_classes_from_file(file) -> list:
        current_module = sys.modules[BacktestStrategyClasses.__module__]
        module_name = current_module.__name__.rsplit('.', 1)[0] + f".{file}"
        module = import_string(module_name)
        class_list = [item for item in dir(module) if isinstance(getattr(module, item), type)]
        return class_list
    
    def load_strategy_classes(self) -> None:
        strategies_list = BacktestStrategyClasses.__get_classes_from_file('backtest_strategies')
        strategies_list.remove('Strategy')
        current_module = sys.modules[BacktestStrategyClasses.__module__]
        self.strategies_dict = {}
        for strategy in strategies_list:
            strategy_class = getattr(current_module, strategy)
            name = getattr(strategy_class, 'strategy_name')
            self.strategies_dict[strategy] = name
    
class BacktestStrategyParameters(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def load_parameters(self, strategy_class : str) -> None:
        self.strategy_class = strategy_class
        current_module = sys.modules[BacktestStrategyParameters.__module__]
        base_class = getattr(current_module, 'Strategy')
        base_class_attr = { 
            attr: getattr(base_class, attr) 
            for attr in dir(base_class) 
            if not callable(getattr(base_class, attr)) and 
            not attr.startswith('__') and 
            not attr.startswith('_')
        }

        self.strategy_class = getattr(current_module, self.strategy_class)
        self.strategy_params = {
            attr: getattr(self.strategy_class, attr) 
            for attr in dir(self.strategy_class)
            if not callable(getattr(self.strategy_class, attr)) and 
            not attr.startswith('__') and 
            not attr.startswith('_') and
            attr not in base_class_attr and
            attr != 'strategy_name'
        }
        self.currency_pairs = MetaTraderData.currency_pairs
        self.timeframes = MetaTraderData.timeframes

    def perform_backtest(
        self, strategy_class : str, currency_pair : str, timeframe : int,
        cash : float, commission : float, margin : float, trade_on_close: bool,
        hedging : bool, exclusive_orders : bool, **kwargs) -> dict:

        #initializing data object
        login_cred = { 'login':self.user.demo_login, 'password':self.user.get_demo_password(), 'server':self.user.demo_server }
        data_instance = MetaTraderData(login_cred, currency_pair)
        data = data_instance.get_data(50000, timeframe)
        
        #creating an object of the string class
        class_obj = globals()[strategy_class]
        #creating a backtesting class object
        bt = Backtest(data, class_obj)

        #performing backtest and storing results
        results = dict(bt.run(**kwargs))
        results.pop('_strategy')
        results.pop('_equity_curve')
        results.pop('_trades')

        return results
    
def backtest_strategy_post_init(sender, instance, **kwargs):
    instance.load_strategy_classes()

post_init.connect(backtest_strategy_post_init, sender=BacktestStrategyClasses)
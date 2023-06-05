from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth import authenticate
from .models import *

#used to register a new user
class CustomUserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Email Address',
        'class' : 'app-form-control'
    }))

    first_name = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'First Name',
        'class' : 'app-form-control'
    }))

    last_name = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Last Name',
        'class' : 'app-form-control'
    }))

    phone_number = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Phone Number',
        'class' : 'app-form-control'
    }))

    demo_login = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Demo Account Login',
        'class' : 'app-form-control'
    }))

    demo_password = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={
        'placeholder':'Demo Account Password',
        'class' : 'app-form-control'
    }))

    demo_server = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Demo Account Server',
        'class' : 'app-form-control'
    }))

    live_login = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Live Account Login',
        'class' : 'app-form-control'
    }))

    live_password = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={
        'placeholder':'Live Account Password',
        'class' : 'app-form-control'
    }))

    live_server = forms.CharField(required=True, label='', widget=forms.TextInput(attrs={
        'placeholder':'Live Account Server',
        'class' : 'app-form-control'
    }))

    password1 = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={
        'placeholder':'PipProphet Password',
        'class' : 'app-form-control'
    }))
    
    password2 = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={
        'placeholder':'Password Confirmation',
        'class' : 'app-form-control'
    }))

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 
                  'demo_login', 'demo_password', 'demo_server',
                  'live_login', 'live_password', 'live_server',
                  'password1', 'password2']

#used to login a user  
class CustomUserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # Check if email and password are valid
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Invalid email or password')
            elif not user.is_active:
                raise forms.ValidationError('This account is inactive')
            cleaned_data['user'] = user
        return cleaned_data
    
class BacktestStrategyClassesForm(forms.ModelForm):
    strategies_combobox = forms.ChoiceField(label='Strategy: ', choices=[], required=False)

    def __init__(self, *args, **kwargs) -> None:
        strategies_dict : dict = kwargs.pop('strategies_dict')
        super().__init__(*args, **kwargs)
        
        if strategies_dict:
            self.fields['strategies_combobox'].choices = strategies_dict.items()

    class Meta:
        model = BacktestStrategyClasses
        fields = []

class BacktestStrategyParametersForm(forms.ModelForm):
    currency_pairs_combobox = forms.ChoiceField(label='Currency Pair', choices=[])
    timeframes_combobox = forms.ChoiceField(label='Timeframe', choices=[])
    cash_field = forms.CharField(label='Cash', initial=10000)
    commission_field = forms.CharField(label='Commission', initial=0.0002)
    margin_field = forms.CharField(label='Margin', initial=1)
    trade_on_close_field = forms.BooleanField(label='Trade on Close', initial=False, required=False)
    hedging_field = forms.BooleanField(label='Hedging' , initial=False, required=False)
    exclusive_orders_field = forms.BooleanField(label='Exclusive Orders', initial=False, required=False)

    def __init__(self, *args, **kwargs) -> None:
        strategy_params : dict = kwargs.pop('strategy_params')
        currency_pairs : dict = kwargs.pop('currency_pairs')
        timeframes : dict = kwargs.pop('timeframes')
        super().__init__(*args, **kwargs)

        if currency_pairs:
            self.fields['currency_pairs_combobox'].choices = currency_pairs.items()
        if timeframes:
            self.fields['timeframes_combobox'].choices = timeframes.items()
        for param, value in strategy_params.items():
            self.fields[param] = forms.CharField(label=param, required=True)
            self.initial[param] = value


    class Meta:
        model = BacktestStrategyParameters
        fields = []

class BacktestStrategyOptimizeForm(forms.ModelForm):
    maximize_combobox = forms.ChoiceField(label='Maximize', choices=[])
    technique_combobox = forms.ChoiceField(label='Optimization Technique', choices=[])
    constraint_function_field = forms.CharField(
        label='Python Lambda Functions', 
        widget=forms.Textarea(attrs={
            'placeholder':'For Advanced Users. Enter Lambda Functions to act as constraints.'
        }), required=False)

    @staticmethod
    def __list_to_lt(inp_list) -> list:
        out_dict = {}
        for element in inp_list:
            out_dict[element] = element
        return out_dict.items()

    def __init__(self, *args, **kwargs) -> None:
        strategy_params : dict = kwargs.pop('strategy_params')
        super().__init__(*args, **kwargs)

        self.fields['maximize_combobox'].choices = BacktestStrategyOptimizeForm.__list_to_lt([
            'Exposure Time [%]', 'Return [%]', 'Sharpe Ratio', 
            'Win Rate [%]', 'Profit Factor','Expectancy [%]','SQN'
        ])
        self.fields['technique_combobox'].choices = {
            'grid':'Cartesian Grid Search',
            'skopt':'Bayesian Optimization',
        }.items()

        for param, value in strategy_params.items():
            self.fields[param] = forms.CharField(label=param, required=True)


    class Meta:
        model = BacktestStrategyOptimization
        fields = []

class DeployableStrategyClassesForm(forms.ModelForm):
    strategies_combobox = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs) -> None:
        strategies_dict : dict = kwargs.pop('strategies_dict')
        super().__init__(*args, **kwargs)
        
        if strategies_dict:
            self.fields['strategies_combobox'].choices = strategies_dict.items()

    class Meta:
        model = DeployableStrategyClasses
        fields = []

class DeployableStrategyParametersForm(forms.ModelForm):
    currency_pairs_combobox = forms.ChoiceField(label='Currency Pair', choices=[])
    timeframes_combobox = forms.ChoiceField(label='Timeframe', choices=[])
    lots_field = forms.CharField(label='Lots', initial=10000)
    account_choice = forms.ChoiceField(label='Account Choice', choices = [])

    def __init__(self, *args, **kwargs) -> None:
        strategy_params : dict = kwargs.pop('strategy_params')
        currency_pairs : dict = kwargs.pop('currency_pairs')
        timeframes : dict = kwargs.pop('timeframes')
        super().__init__(*args, **kwargs)

        self.fields['account_choice'].choices = {'Demo':'Demo Account', 'Live':'Live Account'}.items()

        if currency_pairs:
            self.fields['currency_pairs_combobox'].choices = currency_pairs.items()
        if timeframes:
            self.fields['timeframes_combobox'].choices = timeframes.items()
        for param, value in strategy_params.items():
            self.fields[param] = forms.CharField(label=param, required=True)
            self.initial[param] = value


    class Meta:
        model = DeployableStrategyParameters
        fields = []
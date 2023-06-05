from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.utils.module_loading import import_string
from django.views.generic import CreateView, TemplateView, View
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .forms import *
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import logout
from .backtest_strategies import *
from backtesting import Strategy
from .DataClass import *

import sys

class SignUpView(CreateView):
    form_class = CustomUserSignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

class HomeView(TemplateView):
    template_name = 'home.html'
    def get(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        form = CustomUserLoginForm()
        return render(request, self.template_name, {'form': form})

    def get(self, request : HttpResponse) -> HttpResponse:
        form = CustomUserLoginForm()
        return render(request, self.template_name, {'form': form})

class LoginView(View):
    template_name = 'login.html'

    def get(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        form = CustomUserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        return render(request, self.template_name, {'form': form})

class DashboardView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_to = 'dashboard.html'

    def get(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.redirect_to)
    
    def post(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        pass

class BacktestStrategyClassesView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_to = 'backtests.html'
    bt_strategy_model = BacktestStrategyClasses()

    def get(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        bt_strategy_form = BacktestStrategyClassesForm(
            request.GET, 
            strategies_dict = self.bt_strategy_model.strategies_dict
        )
        return render(request, self.redirect_to, {'bt_strategy_form':bt_strategy_form})
    
    def post(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        bt_strategy_form = BacktestStrategyClassesForm(
            request.POST, 
            strategies_dict = self.bt_strategy_model.strategies_dict
        )
        if bt_strategy_form.is_valid():
            selected_strategy = bt_strategy_form.cleaned_data['strategies_combobox']
            return redirect(reverse_lazy('edit_backtest_strategy', args=[selected_strategy]))
        
        return render(request, self.redirect_to, {'bt_strategy_form':bt_strategy_form})
    
class StrategyParametersView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_to = 'edit_backtest_strategy.html'

    def get(self, request : HttpRequest, strategy_class : str, *args, **kwargs) -> HttpResponse:
        bt_params_model = BacktestStrategyParameters(user = request.user)
        bt_params_model.load_parameters(strategy_class)
        bt_params_form = BacktestStrategyParametersForm(
            request.GET,
            strategy_params = bt_params_model.strategy_params,
            currency_pairs = bt_params_model.currency_pairs,
            timeframes = bt_params_model.timeframes
        )
        return render(request, self.redirect_to, {'bt_params_form':bt_params_form})
    
    @staticmethod
    def __conv_values(inp_dict) -> dict:
        out_dict = {}
        for key, value in inp_dict.items():
            if value.find('.') != -1:
                out_dict[key] = float(value)
            else:
                out_dict[key] = int(value)
        return out_dict
        
    def post(self, request : HttpRequest, strategy_class : str, *args, **kwargs) -> HttpResponse:
        self.bt_params_model = BacktestStrategyParameters(user = request.user)
        self.bt_params_model.load_parameters(strategy_class)
        bt_params_form = BacktestStrategyParametersForm(
            request.POST,
            strategy_params = self.bt_params_model.strategy_params,
            currency_pairs = self.bt_params_model.currency_pairs,
            timeframes = self.bt_params_model.timeframes
        )
        if request.POST.get('Backtest'):
            if bt_params_form.is_valid():
                data : dict = bt_params_form.cleaned_data
                try:
                    self.bt_params_model.store_backtest_params(
                        strategy_class=strategy_class,
                        currency_pair=data.pop('currency_pairs_combobox'),
                        timeframe=int(data.pop('timeframes_combobox')),
                        cash=float(data.pop('cash_field')),
                        commission=float(data.pop('commission_field')),
                        margin=float(data.pop('margin_field')),
                        trade_on_close=bool(data.pop('trade_on_close_field')),
                        hedging=bool(data.pop('hedging_field')),
                        exclusive_orders=bool(data.pop('exclusive_orders_field')),
                    )
                    res = self.bt_params_model.perform_backtest(**StrategyParametersView.__conv_values(data))
                    return render(request, self.redirect_to, {'bt_params_form':bt_params_form, 'results':res})
                except Exception as e:
                    res = {'Error': e}
                    return render(request, self.redirect_to, {'bt_params_form':bt_params_form, 'results':res})
        elif request.POST.get('Plot'):
            cwd = os.getcwd()
            file_name = 'users\\templates\\html_files\\plot.html'
            file_path = os.path.join(cwd, file_name)
            html_content = ''
            with open(file_path, 'r') as file:
                html_content = file.read()
            return HttpResponse(html_content)
        elif request.POST.get('Optimize'):
            if bt_params_form.is_valid():
                data = bt_params_form.cleaned_data
                data = {
                    'strategy_class':strategy_class,
                    'timeframe': int(data.pop('timeframes_combobox')),
                    'currency_pair':data.pop('currency_pairs_combobox'),
                    'cash': float(data.pop('cash_field')),
                    'commission': float(data.pop('commission_field')),
                    'margin': float(data.pop('margin_field')),
                    'trade_on_close': bool(data.pop('trade_on_close_field')),
                    'hedging': bool(data.pop('hedging_field')),
                    'exclusive_orders': bool(data.pop('exclusive_orders_field')),
                }
                request.session['bt_params'] = data
                return redirect(reverse_lazy('optimize', kwargs = {'strategy_class': strategy_class}))
        return render(request, self.redirect_to, {'bt_params_form':bt_params_form})
    
class StrategyOptimizationView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_to = 'optimize.html'

    def get(self, request : HttpRequest, strategy_class : str, *args, **kwargs) -> HttpResponse:
        bt_params_model = BacktestStrategyParameters(user = request.user)
        bt_params_model.load_parameters(strategy_class)
        params_instance : BacktestStrategyParameters = request.session.get('bt_params', {})
        bt_optimize_form = BacktestStrategyOptimizeForm(
            request.GET,
            strategy_params = bt_params_model.strategy_params
        )
        return render(request, self.redirect_to, {'bt_optimize_form':bt_optimize_form})
    
    def post(self, request : HttpRequest, strategy_class : str, *args, **kwargs) -> HttpResponse:
        bt_params_model = BacktestStrategyParameters(user = request.user)
        bt_params_model.load_parameters(strategy_class)
        params_instance : BacktestStrategyParameters = request.session.get('bt_params', {})
        bt_optimize_form = BacktestStrategyOptimizeForm(
            request.POST,
            strategy_params = bt_params_model.strategy_params
        )
        if bt_optimize_form.is_valid():
            data : dict = bt_optimize_form.cleaned_data
            for key in data.keys():
                params_instance[key] = data[key]
            for key in bt_params_model.strategy_params:
                params_instance[key] = [float(ele) if '.' in ele else int(ele) for ele in params_instance[key].split(',')]
            bt_optimize_model = BacktestStrategyOptimization(user = request.user)
            res = bt_optimize_model.optimize_strategy(**params_instance)
        return render(request, self.redirect_to, {'bt_optimize_form':bt_optimize_form, 'value_check':res})
    
class DeployableStrategySelectView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_to = 'deploy.html'
    dp_strategy_model = DeployableStrategyClasses()

    def get(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        dp_strategy_form = DeployableStrategyClassesForm(
            request.GET,
            strategies_dict = self.dp_strategy_model.strategies_dict
        )
        return render(request, self.redirect_to, {'dp_strategy_form':dp_strategy_form})
    
    def post(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        dp_strategy_form = BacktestStrategyClassesForm(
            request.POST, 
            strategies_dict = self.dp_strategy_model.strategies_dict
        )
        if dp_strategy_form.is_valid():
            selected_strategy = dp_strategy_form.cleaned_data['strategies_combobox']
            return redirect(reverse_lazy('edit_deployable_strategy', args=[selected_strategy]))
        
        return render(request, self.redirect_to, {'dp_strategy_form':dp_strategy_form})
    
class DeployableStrategyParametersView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_to = 'edit_deployable_strategy.html'

    def get(self, request : HttpRequest, strategy_class : str, *args, **kwargs) -> HttpResponse:
        dp_params_model = DeployableStrategyParameters(user = request.user)
        dp_params_model.load_parameters(strategy_class)
        dp_params_form = DeployableStrategyParametersForm(
            request.GET,
            strategy_params = dp_params_model.strategy_params,
            currency_pairs = dp_params_model.currency_pairs,
            timeframes = dp_params_model.timeframes
        )
        return render(request, self.redirect_to, {'dp_params_form':dp_params_form})
    
    def post(self, request : HttpRequest, strategy_class : str, *args, **kwargs) -> HttpResponse:
        dp_params_model = DeployableStrategyParameters(user = request.user)
        dp_params_model.load_parameters(strategy_class)
        dp_params_form = DeployableStrategyParametersForm(
            request.POST,
            strategy_params = dp_params_model.strategy_params,
            currency_pairs = dp_params_model.currency_pairs,
            timeframes = dp_params_model.timeframes
        )
        if dp_params_form.is_valid():
            params_dict = dp_params_form.cleaned_data
            params_dict['strategy_class'] = strategy_class
            dp_params_model.deploy_model(**params_dict)
        return render(request, self.redirect_to, {'dp_params_form':dp_params_form})
    
class LogoutView(View):
    def get(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        logout(request)
        return redirect('home')

    

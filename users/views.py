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
            return redirect(reverse_lazy('edit_strategy', args=[selected_strategy]))
        
        return render(request, self.redirect_to, {'bt_strategy_form':bt_strategy_form})
    
class StrategyParametersView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_to = 'edit_strategy.html'

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
        
    def post(self, request : HttpRequest, strategy_class : str, *args, **kwargs) -> HttpResponse:
        bt_params_model = BacktestStrategyParameters(user = request.user)
        bt_params_model.load_parameters(strategy_class)
        bt_params_form = BacktestStrategyParametersForm(
            request.POST,
            strategy_params = bt_params_model.strategy_params,
            currency_pairs = bt_params_model.currency_pairs,
            timeframes = bt_params_model.timeframes
        )
        if request.POST.get('Backtest'):
            if bt_params_form.is_valid():
                bt_params_model.perform_backtest()
            return render(request, self.redirect_to, {'bt_params_form':bt_params_form})
        elif request.POST.get('Optimize'):
            pass
        return render(request, self.redirect_to, {'bt_params_form':bt_params_form})
    
class LogoutView(View):
    def get(self, request : HttpRequest, *args, **kwargs) -> HttpResponse:
        logout(request)
        return redirect('home')

    

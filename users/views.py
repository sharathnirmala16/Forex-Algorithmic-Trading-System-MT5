from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
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
from .strategies import *
from backtesting import Strategy

import sys
import inspect

class SignUpView(CreateView):
    form_class = CustomUserSignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

class HomeView(TemplateView):
    template_name = 'home.html'
    def get(self, request : HttpResponse) -> HttpResponse:
        form = CustomUserLoginForm()
        return render(request, self.template_name, {'form': form})

class LoginView(View):
    template_name = 'login.html'

    def get(self, request : HttpResponse) -> HttpResponse:
        form = CustomUserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request : HttpRequest) -> HttpResponse:
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

    def get(self, request : HttpResponse) -> HttpResponse:
        return render(request, self.redirect_to)
    
    def post(self, request : HttpResponse) -> HttpResponse:
        pass

class BacktestsView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_to = 'backtests.html'

    @staticmethod
    def __get_classes_from_file(file) -> list:
        current_module = sys.modules[BacktestsView.__module__]
        module_name = current_module.__name__.rsplit('.', 1)[0] + f".{file}"
        module = import_string(module_name)
        class_list = [item for item in dir(module) if isinstance(getattr(module, item), type)]
        return class_list

    def get(self, request : HttpResponse) -> HttpResponse:
        strategies_list = BacktestsView.__get_classes_from_file('strategies')
        #Removing the Abstract class
        strategies_list.remove('Strategy')
        strategies_static_vars = {}
        current_module = sys.modules[BacktestsView.__module__]
        base_class = getattr(current_module, 'Strategy')
        base_class_attr = { 
            attr: getattr(base_class, attr) 
            for attr in dir(base_class) 
            if not callable(getattr(base_class, attr)) and 
            not attr.startswith('__') and 
            not attr.startswith('_')
        }
        for strategy in strategies_list:
            strategy_class = getattr(current_module, strategy)
            strategies_static_vars[strategy] = {
                attr: getattr(strategy_class, attr) 
                for attr in dir(strategy_class)
                if not callable(getattr(strategy_class, attr)) and 
                not attr.startswith('__') and 
                not attr.startswith('_') and
                attr not in base_class_attr
            }
        return render(request, self.redirect_to, {'strategies_objects': strategies_static_vars})
    
    #NOTE Not working yet
    def post(self, request : HttpResponse) -> HttpResponse:
        pass
    
class LogoutView(View):
    def get(self, request : HttpRequest) -> HttpResponse:
        logout(request)
        return redirect('home')

    

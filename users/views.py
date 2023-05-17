from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
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

    def get(self, request : HttpResponse) -> HttpResponse:
        return render(request, self.redirect_to)
    
    #NOTE Not working yet
    def post(self, request : HttpResponse) -> HttpResponse:
        selected_strategy = request.POST.get('strategySelection')
        # Logic to handle each strategy option
        if selected_strategy == 'execution':
            form_title = 'Execution Testing Form'
            form_fields = [
                {'label': 'Parameter 1:', 'name': 'executionParam1'},
                {'label': 'Parameter 2:', 'name': 'executionParam2'}
            ]

        return render(request, self.redirect_to, {
            'form_title': form_title,
            'form_fields': form_fields,
            'selected_strategy': selected_strategy
        })
    
class LogoutView(View):
    def get(self, request : HttpRequest) -> HttpResponse:
        logout(request)
        return redirect('home')

    

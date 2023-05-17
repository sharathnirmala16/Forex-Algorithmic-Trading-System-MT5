from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name = 'signup'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('dashboard/', DashboardView.as_view(), name = 'dashboard'),
    path('backtests/', BacktestsView.as_view(), name = 'backtests'),
]
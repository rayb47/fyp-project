from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from . import views

app_name = 'login'

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('', RedirectView.as_view(pattern_name='login:signin', permanent=False)),
]
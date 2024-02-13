from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'mainsite'

urlpatterns = [
    path('home', views.home, name='home'),
    path('signout', views.signout, name='signout'),
    path('quiz', views.quiz, name='quiz'),
    path('submit_answer', views.submit_answer, name='submit_answer'),
]
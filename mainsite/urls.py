from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'mainsite'

urlpatterns = [
    path('home', views.home, name='home'),
    path('signout', views.signout, name='signout'),
    path('architecture', views.architecture, name='architecture'),
    path('vocab', views.vocab, name='vocab'),
    path('quiz/<int:unit_id>/<int:quiz_id>/', views.quiz, name='quiz'),
    path('get_quiz_data', views.get_quiz_data, name='get_quiz_data'),
    path('quiz2', views.quiz2, name='quiz2'),
    path('quiz3', views.quiz3, name='quiz3'),
    path('quiz4', views.quiz4, name='quiz4'),
    path('lesson/<int:lesson_id>/', views.lesson, name='lesson'),
    path('save_word/', views.save_word, name='save_word'),
    path('search_word/', views.search_word, name='search_word'),
    path('submit_answer', views.submit_answer, name='submit_answer'),
    path('text-to-speech/', views.text_to_speech, name='text_to_speech'),
    path('process_audio/', views.process_audio, name='process_audio'),
    path('weather_data', views.weather_data, name='weather_data'),
]
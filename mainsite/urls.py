from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'mainsite'

urlpatterns = [
    path('home', views.home, name='home'),
    path('signout', views.signout, name='signout'),
    path('architecture', views.architecture, name='architecture'),
    path('festivals', views.festivals, name='festivals'),
    path('testdiacritics', views.testdiacritics, name='testdiacritics'),
    path('diacritics', views.diacritics, name='diacritics'),
    path('get_unit_details/<str:unit_id>/', views.get_unit_details, name='get_unit_details'),
    path('get-questions/<str:unit_id>/', views.get_incorrect_questions, name='get_incorrect_questions'),
    path('media', views.media, name='media'),
    path('vocab', views.vocab, name='vocab'),
    path('vocab_search', views.vocab_search, name='vocab_search'),
    path('quiz/<int:unit_id>/<int:quiz_id>/', views.quiz, name='quiz'),
    path('get_quiz_data', views.get_quiz_data, name='get_quiz_data'),
     path('submit_feedback', views.submit_feedback, name='submit_feedback'),
    path('download_table', views.download_table, name='download_table'),
    path('save_settings', views.save_settings, name='save_settings'),
    path('delete_all_saved_words', views.delete_all_saved_words, name='delete_all_saved_words'),
    path('test_session', views.test_session, name='test_session'),
    path('quiz2', views.quiz2, name='quiz2'),
    path('quiz3', views.quiz3, name='quiz3'),
    path('quiz4', views.quiz4, name='quiz4'),
    path('analytics', views.analytics, name='analytics'),
    path('settings', views.settings, name='settings'),
    path('store_page_number', views.store_page_number, name='store_page_number'),
    path('lesson/<int:lesson_id>/', views.lesson, name='lesson'),
    path('save_word/', views.save_word, name='save_word'),
    path('search_word/', views.search_word, name='search_word'),
    path('submit_answer', views.submit_answer, name='submit_answer'),
    path('text-to-speech/', views.text_to_speech, name='text_to_speech'),
    path('process_audio/', views.process_audio, name='process_audio'),
    path('weather_data', views.weather_data, name='weather_data'),
]
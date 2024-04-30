from django.urls import path
from django.views.generic import RedirectView
from . import views
from .views import CustomPasswordResetConfirmView

app_name = 'login'

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('', RedirectView.as_view(pattern_name='mainsite:home', permanent=False)),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password_reset', views.password_reset, name='password_reset'),
    path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm')
]
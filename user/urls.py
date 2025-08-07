from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user-signup'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('me/', UserMeView.as_view(), name='user-me'),
]
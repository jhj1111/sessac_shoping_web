from django.urls import path
from . views import *
from .views import CustomLoginView ,RegisterView ,CustomLogoutView

app_name = 'accounts'


urlpatterns=[
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',CustomLoginView.as_view(),name='login'),

    path('logout/', CustomLogoutView.as_view(), name='logout'),
]

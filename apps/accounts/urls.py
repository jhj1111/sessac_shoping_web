from django.urls import path
from . views import *
from . import views




urlpatterns=[
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',CustomLoginView.as_view(),name='login'),
    path('mypage/',views.home,name='mypage'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]

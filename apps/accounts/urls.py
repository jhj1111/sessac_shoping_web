from django.urls import path
from . views import *
from . import views


urlpatterns = [
    # 회원 관리 URL
    path('signup/', views.UserRegistrationView.as_view(), name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('address/', views.AddressManageView.as_view(), name='address_manage'),
]

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    # 회원 관리 URL
    path('signup/', views.UserRegistrationView.as_view(), name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('address/', views.AddressManageView.as_view(), name='address_manage'),

    # 마이페이지 URL
    path('mypage/', views.MyPageDashboardView.as_view(), name='mypage_dashboard'),
    path('mypage/orders/', views.MyPageOrderListView.as_view(), name='mypage_orders'),
    path('mypage/reviews/', views.MyPageReviewListView.as_view(), name='mypage_reviews'),
    path('mypage/favorites/', views.MyPageFavoriteListView.as_view(), name='mypage_favorites'),
    path('mypage/support/', views.MyPageSupportHistoryView.as_view(), name='mypage_support'),
]

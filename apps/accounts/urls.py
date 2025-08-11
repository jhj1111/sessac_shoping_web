from django.urls import path
from . views import *
from . import views


#app_name = 'accounts'


urlpatterns=[
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',CustomLoginView.as_view(),name='login'),
    path('mypage/',views.home,name='mypage'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    ## 마이페이지 URL

    path('mypage/dashboard/', views.MyPageDashboardView.as_view(), name='mypage_dashboard'),
    path('mypage/orders/', views.MyPageOrderListView.as_view(), name='mypage_orders'),
    path('mypage/reviews/', views.MyPageReviewListView.as_view(), name='mypage_reviews'),
    path('mypage/favorites/', views.MyPageFavoriteListView.as_view(), name='mypage_favorites'),
    path('mypage/support/', views.MyPageSupportHistoryView.as_view(), name='mypage_support'),
]

from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    # 마이페이지 URL
    # path('', views.MyPageMaindView.as_view(), name='mypage_main'),
    path('orders/', views.MyPageOrderListView.as_view(), name='mypage_orders'),
    path('reviews/', views.MyPageReviewListView.as_view(), name='mypage_reviews'),
    path('favorites/', views.MyPageFavoriteListView.as_view(), name='mypage_favorites'),
    path('support/', views.MyPageSupportHistoryView.as_view(), name='mypage_support'),
]

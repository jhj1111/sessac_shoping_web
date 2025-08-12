from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = 'mypage'

urlpatterns = [
    # 마이페이지 URL
    path('', views.MyPageMainView.as_view(), name='mypage_main'),
    path('orders/', views.MyPageOrderListView.as_view(), name='mypage_orders'),
    path('reviews/', views.MyPageReviewListView.as_view(), name='mypage_reviews'),
    path('favorites/', views.MyPageFavoriteListView.as_view(), name='mypage_favorites'),
    path('support/', views.MyPageSupportHistoryView.as_view(), name='mypage_support'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('password/', auth_views.PasswordChangeView.as_view(
        template_name='mypage/password_change.html',
        success_url=reverse_lazy('mypage:password_change_done')
    ), name='password_change'),
    path('password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='mypage/password_change_done.html'
    ), name='password_change_done'),
    path('delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    path('reviews/', views.MyPageReviewListView.as_view(), name='my_review_list'),

]

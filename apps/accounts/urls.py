from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('mypage/', views.MyPageMainView.as_view(), name='mypage_main'),
    # path('mypage/info/', views.mypage_info, name='mypage_info'),
    # path('mypage/benefits/', views.mypage_benefits, name='mypage_benefits'), 
    # path('mypage/activity/', views.mypage_activity, name='mypage_activity'),
    
    # # 세부 페이지들
    # path('mypage/coupons/', views.mypage_coupons, name='mypage_coupons'),
    # path('mypage/mileage/', views.mypage_mileage, name='mypage_mileage'),
    # path('mypage/inquiries/', views.mypage_inquiries, name='mypage_inquiries'),
]
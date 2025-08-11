from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    # 가게 목록 (메인 페이지)
    # /restaurants/
    path('', views.RestaurantListView.as_view(), name='restaurant_list'),

    # 가게 상세 정보
    # /restaurants/1/
    path('<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant_detail'),

    # 리뷰 작성
    # /restaurants/1/review/create/
    path('<int:restaurant_pk>/review/create/', views.ReviewCreateView.as_view(), name='review_create'),

    # 주문 생성 (API)
    # /restaurants/order/create/
    path('order/create/', views.OrderCreateView.as_view(), name='order_create'),

    # 사용자 주문 목록
    # /restaurants/orders/
    path('orders/', views.UserOrderListView.as_view(), name='order_list'),

    # 주문 상세 정보
    # /restaurants/orders/1/
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
]
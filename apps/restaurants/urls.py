from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'restaurants'
urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('restaurants/', views.RestaurantListView.as_view(), name='restaurant_list'),
    path('main-detail/', views.MainDetailView.as_view(), name='main-detail'),
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
    path('review/<int:review_pk>/comment/', views.comment_create, name='comment_create'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart_view'),
    path('cart/delete_all/', views.CartDeleteView.as_view(), name='cart_clear'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('api/create/', views.OrderAPIView.as_view(), name='order_api_create'), # API 뷰 URL 추가
    path('api/cancel/<int:order_id>/', views.OrderCancelAPIView.as_view(), name='order_cancel_api'),
    # 메뉴 목록 (레스토랑별)
    path('menu/<int:restaurant_pk>/', views.MenuListView.as_view(), name='menu_list'),

    # 새로 추가할 장바구니 API URLs
    # path('api/cart/add/', views.CartAddAPIView.as_view(), name='cart_add_api'),
    path('api/cart/update/', views.CartUpdateAPIView.as_view(), name='cart_update_api'),
    path('api/cart/remove/', views.CartRemoveAPIView.as_view(), name='cart_remove_api'),
    # path('api/cart/data/', views.CartDataAPIView.as_view(), name='cart_data_api'),
    # path('api/cart/clear/', views.CartClearAPIView.as_view(), name='cart_clear_api'),


    # path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    # path('<int:pk>/status/', views.OrderStatusView.as_view(), name='order_status'),
    # 예시: 주문 완료, 주문 목록 페이지
    # path('complete/', TemplateView.as_view(template_name="orders/order_complete.html"), name='order_complete'),
    # path('', OrderListView.as_view(), name='order_list'),
    # path('cancel/<int:order_id>/', views.CancelOrderView.as_view(), name='cancel_order'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
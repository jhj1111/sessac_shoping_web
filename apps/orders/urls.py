from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart_view'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('api/create/', views.OrderAPIView.as_view(), name='order_api_create'), # API 뷰 URL 추가

    # path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    # path('<int:pk>/status/', views.OrderStatusView.as_view(), name='order_status'),
    # 예시: 주문 완료, 주문 목록 페이지
    # path('complete/', TemplateView.as_view(template_name="orders/order_complete.html"), name='order_complete'),
    # path('', OrderListView.as_view(), name='order_list'),
    # path('cancel/<int:order_id>/', views.CancelOrderView.as_view(), name='cancel_order'),
]

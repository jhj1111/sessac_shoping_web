from django.urls import path
from . import views # views.py 파일을 import

# 이 urls.py 파일이 어떤 앱에 속하는지 명시 (권장)


urlpatterns = [
    # 함수 기반 뷰 연결 예시
    # URL 경로: /restaurants/1/
    # 뷰 함수: views.py의 restaurant_detail 함수
    # URL 이름: 'detail' (템플릿 등에서 이 이름으로 URL을 쉽게 찾을 수 있음)
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='detail'),

]
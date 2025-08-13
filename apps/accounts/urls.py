from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . views import *
from .views import CustomLoginView ,RegisterView ,CustomLogoutView
from . import views
app_name = 'accounts'


urlpatterns=[
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',CustomLoginView.as_view(),name='login'),

    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('mypage/reviews/', views.MyReviewListView.as_view(), name='my_reviews'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
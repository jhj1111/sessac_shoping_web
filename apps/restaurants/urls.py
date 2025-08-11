from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'restaurants'
urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('main-detail/', views.MainDetailView.as_view(), name='main-detail'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



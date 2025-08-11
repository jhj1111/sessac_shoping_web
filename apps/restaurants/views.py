from django.shortcuts import render
from django.views.generic import ListView, DetailView
from apps.restaurants.models import Post
from django.shortcuts import render
from django.views.generic import TemplateView






def post_list(request):
    return render(request, template_name='main/base.html')


# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = 'main/post_list.html'



class MainDetailView(TemplateView):
    #model = Post
    template_name = 'main/post_main_detail.html'
    # 특정 상세 페이지가 아니라서 이렇게만 하면 이동
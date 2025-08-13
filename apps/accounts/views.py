from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, ListView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from .forms import RegisterForm
from django.contrib.auth.views import LogoutView
from apps.restaurants.models import Review

# from .models import CustomUser, Address


from ..orders.models import Order
# from ..reviews.models import Review
# from ..favorites.models import Favorite
# from ..support.models import Inquiry

# --- 회원 관리 Views ---
class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('restaurants:post-list')
    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('restaurants:post-list')



class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('restaurants:post-list')

class MyReviewListView(LoginRequiredMixin, ListView):
    # 사용할 모델은 Review 모델입니다.
    model = Review
    # 보여줄 HTML 템플릿 파일을 지정합니다.
    template_name = 'accounts/my_review_list.html'
    # 템플릿에서 사용할 객체 리스트의 이름을 'reviews'로 지정합니다.
    context_object_name = 'reviews'
    # 한 페이지에 10개의 리뷰를 보여주는 페이지네이션 기능입니다.
    paginate_by = 10

    def get_queryset(self):
        """
        [핵심] 현재 로그인한 유저가 작성한 리뷰만 필터링합니다.
        """
        # self.request.user를 통해 현재 로그인한 유저 정보에 접근할 수 있습니다.
        queryset = Review.objects.filter(user=self.request.user).select_related('restaurant').order_by('-created_at')
        return queryset





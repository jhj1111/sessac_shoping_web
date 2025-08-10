from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, ListView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta

from .models import User, Address
from .forms import UserRegistrationForm, ProfileUpdateForm, AddressForm

from ..orders.models import Order
# from ..reviews.models import Review
# from ..favorites.models import Favorite
# from ..support.models import Inquiry

# --- 회원 관리 Views ---

class UserRegistrationView(CreateView):
    """회원가입 View"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # form.save()를 통해 사용자가 생성됨
        response = super().form_valid(form)
        # 추가적인 작업 (e.g. 환영 이메일 발송)
        return response

class UserLoginView(LoginView):
    """로그인 View"""
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        return reverse_lazy('home') # 로그인 성공 시 홈으로 이동

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """프로필 수정 View"""
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:mypage_dashboard')

    def get_object(self, queryset=None):
        # 현재 로그인한 사용자를 객체로 반환
        return self.request.user

class AddressManageView(LoginRequiredMixin, View):
    """주소록 관리 View"""
    template_name = 'accounts/address_manage.html'

    def get(self, request, *args, **kwargs):
        addresses = request.user.addresses.all()
        form = AddressForm()
        return render(request, self.template_name, {'addresses': addresses, 'form': form})

    def post(self, request, *args, **kwargs):
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('accounts:address_manage')
        
        addresses = request.user.addresses.all()
        return render(request, self.template_name, {'addresses': addresses, 'form': form})


# --- 마이페이지 Views ---

class MyPageDashboardView(LoginRequiredMixin, TemplateView):
    """마이페이지 대시보드"""
    # template_name = 'accounts/mypage_dashboard.html'
    template_name = 'accounts/mypage_main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Get filter parameter from GET request, default to 'all'
        selected_filter = self.request.GET.get('filter', 'all')
        context['selected_filter'] = selected_filter # Pass to template

        all_orders = Order.objects.filter(user=user).order_by('-order_time')

        # Apply filtering based on selected_filter
        if selected_filter == 'recent_15_days':
            start_date = timezone.now() - timedelta(days=15)
            all_orders = all_orders.filter(order_time__gte=start_date)
        elif selected_filter == '1_month':
            start_date = timezone.now() - timedelta(days=30) # Approx 1 month
            all_orders = all_orders.filter(order_time__gte=start_date)
        elif selected_filter == '3_months':
            start_date = timezone.now() - timedelta(days=90) # Approx 3 months
            all_orders = all_orders.filter(order_time__gte=start_date)
        elif selected_filter == '6_months':
            start_date = timezone.now() - timedelta(days=180) # Approx 6 months
            all_orders = all_orders.filter(order_time__gte=start_date)
        elif selected_filter == 'test_2hours':
            start_date = timezone.now() - timedelta(hours=2) # Approx 6 months
            all_orders = all_orders.filter(order_time__gte=start_date)
        # 'all' filter means no date filtering, so no 'else' needed here

        orders_with_grouped_items = [] 
        for order in all_orders:
            grouped_items = order.group_items_by_restaurant()
            orders_with_grouped_items.append({
                'order': order,
                'grouped_items': grouped_items
            })

            # print(f"restaurnat : {order.restaurants[0]}")
            # print(f"order.status : {order.status}")
        
        order_status_counts = user.get_order_status_counts()
        
        context['orders_with_grouped_items'] = orders_with_grouped_items
        context['order_status_counts'] = order_status_counts
        context['user_grade'] = user.get_grade_display()
        context['user_points'] = user.get_points_balance()
        return context

class MyPageOrderListView(LoginRequiredMixin, ListView):
    """주문 내역 조회"""
    model = Order 
    template_name = 'accounts/mypage_order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        # return Order.objects.filter(user=self.request.user).order_by('-order_time')
        return [] # 임시

class MyPageReviewListView(LoginRequiredMixin, ListView):
    """작성 리뷰 조회"""
    # model = Review
    template_name = 'accounts/mypage_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        # return Review.objects.filter(user=self.request.user).order_by('-created_at')
        return [] # 임시

class MyPageFavoriteListView(LoginRequiredMixin, ListView):
    """즐겨찾기 조회"""
    # model = Favorite
    template_name = 'accounts/mypage_favorite_list.html'
    context_object_name = 'favorites'
    paginate_by = 10

    def get_queryset(self):
        # return Favorite.objects.filter(user=self.request.user)
        return [] # 임시

class MyPageSupportHistoryView(LoginRequiredMixin, ListView):
    """고객 지원 내역 조회"""
    # model = Inquiry
    template_name = 'accounts/mypage_support_list.html'
    context_object_name = 'inquiries'
    paginate_by = 10

    def get_queryset(self):
        # return Inquiry.objects.filter(user=self.request.user).order_by('-created_at')
        return [] # 임시

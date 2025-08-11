from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.views.generic import CreateView, UpdateView, TemplateView, ListView, View, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout

from django.utils import timezone
from datetime import timedelta

from ..orders.models import Order
from ..accounts.models import CustomUser
from ..accounts.forms import UserProfileForm
# from ..reviews.models import Review
# from ..favorites.models import Favorite
# from ..support.models import Inquiry

# Create your views here.
class MyPageMainView(LoginRequiredMixin, TemplateView):
    template_name = 'mypage/mypage_main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Add user information to the context
        context['user_info'] = user
        context['user_grade'] = user.get_grade_display()
        context['user_points'] = user.get_points_balance()
        context['user_coupons'] = user.get_coupon_count()
        context['grade_icon_url'] = user.get_grade_icon()
        context['order_status_counts'] = user.get_order_status_counts()
        
        # For recent orders, let's fetch a few recent ones.
        recent_orders = Order.objects.filter(user=user).order_by('-order_time')[:5]
        
        orders_with_grouped_items = [] 
        for order in recent_orders:
            grouped_items = order.group_items_by_restaurant()
            orders_with_grouped_items.append({
                'order': order,
                'grouped_items': grouped_items
            })
        
        context['recent_orders'] = orders_with_grouped_items
        
        return context
class MyPageOrderListView(LoginRequiredMixin, TemplateView):
    """마이페이지 대시보드"""
    # template_name = 'mypage/mypage_dashboard.html'
    template_name = 'mypage/mypage_orders.html'

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

class MyPageReviewListView(LoginRequiredMixin, ListView):
    """작성 리뷰 조회"""
    # model = Review
    template_name = 'mypage/mypage_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        # return Review.objects.filter(user=self.request.user).order_by('-created_at')
        return [] # 임시

class MyPageFavoriteListView(LoginRequiredMixin, ListView):
    """즐겨찾기 조회"""
    # model = Favorite
    template_name = 'mypage/mypage_favorite_list.html'
    context_object_name = 'favorites'
    paginate_by = 10

    def get_queryset(self):
        # return Favorite.objects.filter(user=self.request.user)
        return [] # 임시

class MyPageSupportHistoryView(LoginRequiredMixin, ListView):
    """고객 지원 내역 조회"""
    # model = Inquiry
    template_name = 'mypage/mypage_support_list.html'
    context_object_name = 'inquiries'
    paginate_by = 10

    def get_queryset(self):
        # return Inquiry.objects.filter(user=self.request.user).order_by('-created_at')
        return [] # 임시

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'mypage/profile_edit.html'
    success_url = reverse_lazy('mypage:mypage_main')

    def get_object(self, queryset=None):
        return self.request.user

class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'mypage/account_delete.html'
    success_url = reverse_lazy('restaurants:post-list')

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        logout(request)
        response = super().post(request, *args, **kwargs)
        return response
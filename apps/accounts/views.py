from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.contrib import messages

# class MyPageMainView(LoginRequiredMixin, TemplateView):
class MyPageMainView(TemplateView):
    template_name = 'accounts/mypage_main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 사용자 기본 정보
        context.update({
            'user_grade': user.get_grade_display(),
            'user_points': user.get_points_balance(),
            'barcode_number': f"017200{user.id:08d}40",  # 예시 바코드 생성
        })
        
        return context

# @login_required
# def mypage_info(request):
#     """MY 정보 페이지"""
#     return render(request, 'accounts/mypage_info.html')

# @login_required
# def mypage_benefits(request):
#     """MY 쇼핑혜택 페이지"""
#     return render(request, 'accounts/mypage_benefits.html')

# @login_required
# def mypage_activity(request):
#     """MY 쇼핑활동 페이지"""
#     return render(request, 'accounts/mypage_activity.html')
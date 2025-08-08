from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.utils import timezone
from django.templatetags.static import static

class User(AbstractUser):
    GRADE_CHOICES = [
        ('BRONZE', 'BRONZE+'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
    ]
    
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default='BRONZE')
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def get_points_balance(self):
        """현재 포인트 잔액 계산"""
        from ..payments.models import Point
        balance = Point.objects.filter(user=self).aggregate(
            total=Sum('amount')
        )['total'] or 0
        return balance
    
    def get_coupon_count(self):
        """사용 가능한 쿠폰 개수"""
        from ..payments.models import UserCoupon
        return UserCoupon.objects.filter(
            user=self, 
            is_used=False,
            coupon__valid_until__gt=timezone.now()
        ).count()
    
    def get_mileage_count(self):
        """마일리지 개수 (예시)"""
        # 실제 마일리지 시스템에 따라 구현
        return 0

    def get_grade_icon(self):
        """사용자 등급에 따른 아이콘 경로를 반환합니다."""
        icon_map = {
            'BRONZE': 'bronze.png',
            'SILVER': 'silver.png',
            'GOLD': 'gold.png',
            'PLATINUM': 'platinum.png',
        }
        icon_filename = icon_map.get(self.grade, 'default.png')  # 등급에 맞는 아이콘이 없으면 기본 아이콘 반환
        return static(f'accounts/{icon_filename}')
    
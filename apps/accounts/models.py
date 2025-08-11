from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.utils import timezone
from django.templatetags.static import static

class User(AbstractUser):
    """
    Django의 AbstractUser를 상속받아 확장한 커스텀 유저 모델
    """
    GRADE_CHOICES = [
        ('BRONZE', 'BRONZE+'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
    ]
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    ]
    
    # 기본 정보 (username, email, password 등은 AbstractUser에 포함)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default='BRONZE')

    def get_full_name(self):
        """사용자의 전체 이름을 반환합니다."""
        return super().get_full_name()

    def get_grade_benefits(self):
        """사용자 등급에 따른 혜택 정보를 반환합니다."""
        # 등급별 혜택 로직 구현
        return f"{self.grade} 등급 혜택 내용"

    def update_profile(self, **kwargs):
        """프로필 정보를 업데이트합니다."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    # --- 기존에 있던 유용한 메서드들 ---
    def get_points_balance(self):
        """현재 포인트 잔액 계산"""
        from ..payments.models import Point # 순환 참조 주의
        balance = Point.objects.filter(user=self).aggregate(
            total=Sum('amount')
        )['total'] or 0
        return balance
        return 0 # 임시
    
    def get_coupon_count(self):
        """사용 가능한 쿠폰 개수"""
        # from ..payments.models import UserCoupon
        # return UserCoupon.objects.filter(
        #     user=self, 
        #     is_used=False,
        #     coupon__valid_until__gt=timezone.now()
        # ).count()
        return 0 # 임시

    def get_grade_icon(self):
        """사용자 등급에 따른 아이콘 경로를 반환합니다."""
        icon_map = {
            'BRONZE': 'icon_bronze.png',
            'SILVER': 'icon_silver.png',
            'GOLD': 'icon_gold.png',
            'PLATINUM': 'icon_platinum.png',
        }
        icon_filename = icon_map.get(self.grade, 'default.png')
        return static(f'accounts/{icon_filename}')

    def get_order_status_counts(self):
        """자신의 주문을 상태별로 집계하여 개수를 반환합니다."""
        from django.db.models import Count
        from apps.orders.models import Order # 메서드 안에서 import

        # 모든 주문 상태의 초기값을 0으로 설정
        # status_counts = {status_name: 0 for status_value, status_name in Order.OrderStatus.choices}
        status_counts = {status_name: 0 for status_value, status_name in Order.ORER_STATUS}
        # get_order_status_name = {status_value: status_name for status_value, status_name in Order.OrderStatus.choices}
        get_order_status_name = {status_value: status_name for status_value, status_name in Order.ORER_STATUS}

        # 사용자의 주문 상태별 개수를 집계
        user_orders_counts = Order.objects.filter(user=self) \
            .values('status') \
            .annotate(count=Count('status'))

        # 결과를 딕셔너리에 업데이트
        for item in user_orders_counts:
            # status_counts[item['status']] = item['count']
            status_counts[get_order_status_name[item['status']]] = item['count']

        return status_counts


class Address(models.Model):
    """
    사용자의 배송지 정보를 저장하는 모델
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100, help_text="집, 회사 등 주소 별칭")
    full_address = models.TextField()
    zip_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def set_as_default(self):
        """이 주소를 기본 배송지로 설정합니다."""
        self.user.addresses.update(is_default=False)
        self.is_default = True
        self.save()

    def get_distance_from(self, lat, lon):
        """특정 좌표로부터의 거리를 계산합니다."""
        # 거리 계산 로직 구현 (예: haversine 공식)
        return 0.0

    def __str__(self):
        return f"{self.user.username}의 주소: {self.name}"


class PaymentMethod(models.Model):
    """
    사용자의 결제 수단을 저장하는 모델
    """
    TYPE_CHOICES = [
        ('card', '신용/체크카드'),
        ('bank', '계좌이체'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='card')
    card_name = models.CharField(max_length=50, blank=True)
    card_number = models.CharField(max_length=19, blank=True) # XXXX-XXXX-XXXX-XXXX
    expiry_date = models.DateField(null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def mask_card_number(self):
        """카드 번호를 마스킹 처리하여 반환합니다."""
        if self.type == 'card' and self.card_number:
            parts = self.card_number.split('-')
            if len(parts) == 4:
                return f"{parts[0]}-{parts[1]}-****-{parts[3]}"
        return self.card_number

    def is_expired(self):
        """카드의 만료 여부를 확인합니다."""
        if self.type == 'card' and self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    def __str__(self):
        return f"{self.user.username}의 결제수단: {self.get_type_display()}"
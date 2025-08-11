from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.templatetags.static import static
from apps.orders.models import Order
from django.db.models import Count



class CustomUser(AbstractUser):

    address = models.CharField(max_length=200, blank=True, null=True)
    detail_address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def get_order_status_counts(self):
        """자신의 주문을 상태별로 집계하여 개수를 반환합니다."""
        # Order 모델의 ORER_STATUS를 참조해야 합니다.
        status_counts = {status_name: 0 for status_value, status_name in Order.ORER_STATUS}
        get_order_status_name = {status_value: status_name for status_value, status_name in Order.ORER_STATUS}

        user_orders_counts = Order.objects.filter(user=self) \
            .values('status') \
            .annotate(count=Count('status'))

        for item in user_orders_counts:
            status_counts[get_order_status_name[item['status']]] = item['count']

        return status_counts


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


    grade = models.CharField(max_length=10, choices=GRADE_CHOICES, default='BRONZE')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def get_full_name(self):
        """사용자의 전체 이름을 반환합니다."""
        return super().get_full_name()

    def get_grade_benefits(self):
        """사용자 등급에 따른 혜택 정보를 반환합니다."""
        return f"{self.grade} 등급 혜택 내용"

    def update_profile(self, **kwargs):
        """프로필 정보를 업데이트합니다."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def get_points_balance(self):

        return 0  # 임시

    def get_coupon_count(self):
        """사용 가능한 쿠폰 개수"""
        return 0  # 임시

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
        from apps.orders.models import Order
        status_counts = {status_name: 0 for status_value, status_name in Order.ORER_STATUS}
        get_order_status_name = {status_value: status_name for status_value, status_name in Order.ORER_STATUS}
        user_orders_counts = Order.objects.filter(user=self).values('status').annotate(count=Count('status'))
        for item in user_orders_counts:
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
    card_number = models.CharField(max_length=19, blank=True)
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
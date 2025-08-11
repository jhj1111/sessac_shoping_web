from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Payment(models.Model):
    """결제 정보 모델"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', '결제 대기'),
        ('paid', '결제 완료'),
        ('failed', '결제 실패'),
        ('cancelled', '결제 취소'),
    ]

    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment', verbose_name='주문')
    payment_method = models.CharField(max_length=50, verbose_name='결제 수단')
    amount = models.PositiveIntegerField(verbose_name='결제 금액')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='결제 상태')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name='거래 ID')
    pg_company = models.CharField(max_length=50, blank=True, verbose_name='PG사')
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name='결제 완료 일시')
    cancelled_at = models.DateTimeField(blank=True, null=True, verbose_name='결제 취소 일시')

    class Meta:
        verbose_name = '결제'
        verbose_name_plural = '결제 목록'

    def __str__(self):
        return f"{self.order.id}의 결제 정보"

    def is_paid(self):
        """결제가 완료되었는지 확인합니다."""
        return self.status == 'paid'

    def can_cancel(self):
        """결제를 취소할 수 있는지 확인합니다."""
        return self.is_paid() and self.order.can_be_cancelled()

    def process_refund(self):
        """환불을 처리합니다."""
        if self.can_cancel():
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
            self.save()
            # 실제 PG사 환불 로직 호출 필요
            return True
        return False


class Coupon(models.Model):
    """쿠폰 모델"""
    DISCOUNT_TYPE_CHOICES = [
        ('fixed_amount', '정액 할인'),
        ('percentage', '정률 할인'),
    ]

    name = models.CharField(max_length=100, verbose_name='쿠폰 이름')
    description = models.TextField(blank=True, verbose_name='설명')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, verbose_name='할인 유형')
    discount_value = models.PositiveIntegerField(verbose_name='할인 값')
    minimum_order_amount = models.PositiveIntegerField(default=0, verbose_name='최소 주문 금액')
    valid_from = models.DateTimeField(verbose_name='유효 시작일')
    valid_until = models.DateTimeField(verbose_name='유효 종료일')
    max_usage = models.PositiveIntegerField(default=1, verbose_name='최대 사용 횟수')
    current_usage = models.PositiveIntegerField(default=0, verbose_name='현재 사용 횟수')

    class Meta:
        verbose_name = '쿠폰'
        verbose_name_plural = '쿠폰 목록'

    def __str__(self):
        return self.name

    def is_valid(self):
        """쿠폰이 현재 유효한지 확인합니다."""
        now = timezone.now()
        return self.valid_from <= now <= self.valid_until and self.current_usage < self.max_usage

    def can_use(self, order_amount):
        """쿠폰을 사용할 수 있는지 확인합니다."""
        return self.is_valid() and order_amount >= self.minimum_order_amount

    def calculate_discount(self, order_amount):
        """할인 금액을 계산합니다."""
        if self.discount_type == 'fixed_amount':
            return self.discount_value
        elif self.discount_type == 'percentage':
            return int(order_amount * (Decimal(self.discount_value) / 100))
        return 0


class UserCoupon(models.Model):
    """사용자 보유 쿠폰 모델"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupons', verbose_name='사용자')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='user_coupons', verbose_name='쿠폰')
    is_used = models.BooleanField(default=False, verbose_name='사용 여부')
    used_at = models.DateTimeField(blank=True, null=True, verbose_name='사용 일시')
    received_at = models.DateTimeField(auto_now_add=True, verbose_name='발급 일시')

    class Meta:
        verbose_name = '사용자 쿠폰'
        verbose_name_plural = '사용자 쿠폰 목록'
        unique_together = ('user', 'coupon')

    def __str__(self):
        return f"{self.user.username}의 {self.coupon.name} 쿠폰"

    def use_coupon(self):
        """쿠폰을 사용 처리합니다."""
        if not self.is_used and self.coupon.is_valid():
            self.is_used = True
            self.used_at = timezone.now()
            self.coupon.current_usage += 1
            self.save()
            self.coupon.save()
            return True
        return False

    def is_expired(self):
        """쿠폰이 만료되었는지 확인합니다."""
        return not self.coupon.is_valid()


class Point(models.Model):
    """포인트 모델"""
    POINT_TYPE_CHOICES = [
        ('earned', '적립'),
        ('used', '사용'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='points', verbose_name='사용자')
    amount = models.IntegerField(verbose_name='포인트 금액')
    type = models.CharField(max_length=20, choices=POINT_TYPE_CHOICES, verbose_name='유형')
    description = models.CharField(max_length=255, blank=True, verbose_name='설명')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='소멸 예정일')

    class Meta:
        verbose_name = '포인트'
        verbose_name_plural = '포인트 내역'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 {self.get_type_display()} 포인트: {self.amount}"

    def is_expired(self):
        """포인트가 만료되었는지 확인합니다."""
        return self.expiry_date and self.expiry_date < timezone.now().date()
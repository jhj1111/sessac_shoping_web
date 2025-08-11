import datetime
from django.db import models
from django.db.models import Avg
from django.conf import settings
from django.utils import timezone  # timezone.now() 사용을 위해 추가


# I. 음식점 정보 (Restaurant Information)
class Restaurant(models.Model):
    # --- 기본 정보 ---
    name = models.CharField("가게명", max_length=20)
    notice = models.TextField("사장님 공지", blank=True)
    # 개선: CharField -> JSONField로 변경하여 정형화된 데이터 관리
    # 예: {"MON": ["09:00", "21:00"], "TUE": ["09:00", "21:00"], ...}
    operating_hours = models.JSONField("운영시간", default=dict, blank=True)
    address = models.CharField("주소", max_length=40)
    min_order_price = models.PositiveIntegerField("최소 주문 금액", default=15000)
    delivery_tip = models.PositiveIntegerField("배달 팁", default=4000)
    origin_info = models.TextField("원산지 정보", blank=True)

    # --- 지도 정보 ---
    latitude = models.DecimalField("위도", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("경도", max_digits=9, decimal_places=6, null=True, blank=True)

    # --- 개선: 성능 최적화를 위한 캐시 필드 ---
    # 리뷰가 추가/삭제될 때마다 업데이트하여 불필요한 DB 조회를 방지
    review_count = models.PositiveIntegerField("리뷰 개수", default=0)
    average_rating = models.FloatField("평균 별점", default=0.0)

    @property
    def operating_status(self):
        """
        JSONField로 저장된 운영 시간을 바탕으로 현재 영업 상태를 반환합니다.
        """
        now = timezone.now()
        current_time_str = now.strftime("%H:%M")
        weekday_str = now.strftime("%a").upper()
        print(f"[{self.name}] 현재 시간(Django 인식): {current_time_str}, 요일: {weekday_str}")

        today_hours = self.operating_hours.get(weekday_str)
        if not today_hours or len(today_hours) != 2:
            return "영업 정보 없음"

        start_time_str, end_time_str = today_hours

        # 자정을 넘어가는 시간 처리 (예: 22:00 ~ 02:00)
        if start_time_str > end_time_str:
            if current_time_str >= start_time_str or current_time_str < end_time_str:
                return "영업 중"
            else:
                return "영업 준비 중"
        # 일반적인 시간 처리
        else:
            if start_time_str <= current_time_str < end_time_str:
                return "영업 중"
            else:
                return "영업 준비 중"

    # 개선: 매번 쿼리하는 대신 캐시된 필드를 사용하도록 변경
    # @property
    # def total_reviews(self):
    #     return self.reviews.count()
    #
    # @property
    # def average_rating(self):
    #     return self.reviews.aggregate(avg=Avg('rating'))['avg'] or 0.0

    def update_review_statistics(self):
        """리뷰 통계(개수, 평균 별점)를 업데이트합니다."""
        reviews = self.reviews.all()
        self.review_count = reviews.count()
        self.average_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0.0
        self.save(update_fields=['review_count', 'average_rating'])

    def __str__(self):
        return self.name


# II. 메뉴 및 옵션 (Menu & Options)
class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_categories')
    name = models.CharField("카테고리명", max_length=20)
    order = models.PositiveIntegerField("표시 순서", default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "메뉴 카테고리"
        verbose_name_plural = "메뉴 카테고리들"

    def __str__(self):
        return f'[{self.restaurant.name}] {self.name}'


class Menu(models.Model):
    # 개선: MenuCategory를 통해 Restaurant에 접근 가능하므로 중복되는 restaurant 필드 제거 (데이터 정규화)
    # restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='menus')
    name = models.CharField("메뉴명", max_length=20)
    description = models.TextField("메뉴 설명", blank=True)
    image = models.ImageField("메뉴 사진", upload_to='menu_images/', blank=True)
    price = models.PositiveIntegerField("가격")
    is_signature = models.BooleanField("대표 메뉴 여부", default=False)
    is_popular = models.BooleanField("인기 메뉴 여부", default=False)

    def __str__(self):
        return self.name


class OptionGroup(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='option_groups')
    name = models.CharField("옵션 그룹명", max_length=20)
    is_mandatory = models.BooleanField("필수 선택 여부", default=False)

    def __str__(self):
        return f'{self.menu.name} - {self.name}'


class Option(models.Model):
    option_group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE, related_name='options')
    name = models.CharField("옵션명", max_length=20)
    extra_price = models.PositiveIntegerField("추가 금액", default=0)

    def __str__(self):
        return f'{self.option_group.name} - {self.name} (+{self.extra_price}원)'


# III. 별점 및 리뷰 (Rating & Reviews)
class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    # 추가: 주문과 리뷰를 연결하면 "주문한 사람만 리뷰" 기능 구현 가능
    # order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, related_name='review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.DecimalField("별점", max_digits=2, decimal_places=1)
    content = models.TextField("리뷰 내용")
    image = models.ImageField("리뷰 사진", upload_to='review_images/', blank=True, null=True)
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return f'{self.restaurant.name} 리뷰: {self.user.username} ({self.rating})'

    # 개선: save/delete 메서드를 오버라이드하여 레스토랑 통계 자동 업데이트
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.restaurant.update_review_statistics()

    def delete(self, *args, **kwargs):
        restaurant = self.restaurant
        super().delete(*args, **kwargs)
        restaurant.update_review_statistics()


class ReviewComment(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='comment')
    content = models.TextField("댓글 내용")
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    def __str__(self):
        return f'{self.review}에 대한 사장님 댓글'


# IV. 주문 (Order) - 신규 추가
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', '주문 대기'
        ACCEPTED = 'ACCEPTED', '주문 접수'
        REJECTED = 'REJECTED', '주문 거절'
        COOKING = 'COOKING', '조리 중'
        DELIVERING = 'DELIVERING', '배달 중'
        COMPLETED = 'COMPLETED', '배달 완료'
        CANCELED = 'CANCELED', '주문 취소'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name='orders')
    address = models.ForeignKey(
        'accounts.Address',  # 문자열로 모델을 지정하여 순환 참조 방지
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="배달 주소"
    )
    status = models.CharField("주문 상태", max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.PositiveIntegerField("총 주문 금액")
    delivery_tip = models.PositiveIntegerField("배달팁")
    final_price = models.PositiveIntegerField("최종 결제 금액")
    created_at = models.DateTimeField("주문일", auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'주문번호 {self.id} ({self.user.username} - {self.restaurant.name})'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT)  # 메뉴가 삭제되어도 주문 내역은 남도록 PROTECT
    quantity = models.PositiveIntegerField("수량")
    # 주문 시점의 가격/옵션 정보를 저장하기 위해 필요
    price_per_item = models.PositiveIntegerField("개당 가격")
    options = models.JSONField("선택 옵션", default=dict)  # 예: {"치즈 추가": 1000, "콜라": 2000}

    def __str__(self):
        return f'[주문 {self.order.id}] {self.menu.name} x {self.quantity}'